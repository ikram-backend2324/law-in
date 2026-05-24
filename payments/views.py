import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import SubscriptionPlan, Subscription, Payment, PaymentSettings
from . import payme as payme_api
from . import click as click_api


@login_required
def pricing(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    has_sub = Subscription.has_active(request.user)
    active_sub = None
    if has_sub:
        active_sub = Subscription.objects.filter(
            user=request.user, is_active=True, expires_at__gt=timezone.now()
        ).first()
    return render(request, 'payments/pricing.html', {
        'plans': plans,
        'has_subscription': has_sub,
        'active_subscription': active_sub,
    })


@login_required
def checkout(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    cfg = PaymentSettings.get()

    # Determine which providers are configured
    payme_enabled = bool(cfg.payme_merchant_id and cfg.payme_secret_key)
    click_enabled = bool(cfg.click_merchant_id and cfg.click_secret_key)

    if request.method == 'POST':
        provider = request.POST.get('provider')
        card_number = request.POST.get('card_number', '').replace(' ', '')
        expire = request.POST.get('expire', '').replace('/', '')  # e.g. '0325'

        if not provider or provider not in ('payme', 'click'):
            messages.error(request, 'Please select a payment provider.')
            return redirect('checkout', plan_id=plan_id)

        if len(card_number) < 16:
            messages.error(request, 'Please enter a valid 16-digit card number.')
            return redirect('checkout', plan_id=plan_id)

        if len(expire) < 4:
            messages.error(request, 'Please enter card expiry in MM/YY format.')
            return redirect('checkout', plan_id=plan_id)

        # Create a pending payment record
        payment = Payment.objects.create(
            user=request.user,
            plan=plan,
            provider=provider,
            amount_uzs=plan.price_uzs,
            status=Payment.STATUS_PENDING,
            card_number_masked=f"**** **** **** {card_number[-4:]}",
        )

        # Step 1: Register card & get token
        if provider == 'payme':
            token, error = payme_api.create_card(card_number, expire, test_mode=cfg.payme_is_test)
        else:
            month = expire[:2]
            year = expire[2:]
            token, error = click_api.create_card(card_number, month, year, test_mode=cfg.click_is_test)

        if error or not token:
            payment.status = Payment.STATUS_FAILED
            payment.error_message = error or "Failed to register card"
            payment.save()
            messages.error(request, f'Card error: {error or "Could not register card. Check card details."}')
            return redirect('checkout', plan_id=plan_id)

        # Save token to payment record
        payment.provider_token = token
        payment.status = Payment.STATUS_PENDING
        payment.save()

        # Step 2: Trigger SMS
        if provider == 'payme':
            phone_or_true, error = payme_api.send_sms(token, test_mode=cfg.payme_is_test)
        else:
            phone_or_true, error = click_api.send_sms(token, test_mode=cfg.click_is_test)

        if error:
            payment.status = Payment.STATUS_FAILED
            payment.error_message = error
            payment.save()
            messages.error(request, f'Could not send SMS: {error}')
            return redirect('checkout', plan_id=plan_id)

        payment.status = Payment.STATUS_WAITING_SMS
        payment.save()

        # Store payment ID in session for the verify step
        request.session['pending_payment_id'] = payment.id

        phone_display = phone_or_true if isinstance(phone_or_true, str) else ""
        return redirect('verify_payment', payment_id=payment.id)

    return render(request, 'payments/checkout.html', {
        'plan': plan,
        'payme_enabled': payme_enabled,
        'click_enabled': click_enabled,
    })


@login_required
def verify_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status == Payment.STATUS_PAID:
        return redirect('payment_success')

    if payment.status not in (Payment.STATUS_WAITING_SMS, Payment.STATUS_PENDING):
        messages.error(request, 'This payment session has expired or failed.')
        return redirect('pricing')

    cfg = PaymentSettings.get()

    if request.method == 'POST':
        code = request.POST.get('sms_code', '').strip()
        if not code:
            messages.error(request, 'Please enter the SMS code.')
            return render(request, 'payments/verify.html', {'payment': payment})

        # Step 3: Verify card with SMS
        if payment.provider == Payment.PROVIDER_PAYME:
            verified_token, error = payme_api.verify_card(payment.provider_token, code, test_mode=cfg.payme_is_test)
        else:
            verified_token, error = click_api.verify_card(payment.provider_token, code, test_mode=cfg.click_is_test)

        if error or not verified_token:
            messages.error(request, f'Invalid code: {error or "Verification failed. Try again."}')
            return render(request, 'payments/verify.html', {'payment': payment})

        payment.provider_token = verified_token

        # Step 4+5: Create receipt/payment and charge
        if payment.provider == Payment.PROVIDER_PAYME:
            receipt_id, error = payme_api.create_receipt(
                payment.amount_tiyin,
                payment.id,
                f"Law In — {payment.plan.name}",
                test_mode=cfg.payme_is_test,
            )
            if error or not receipt_id:
                payment.status = Payment.STATUS_FAILED
                payment.error_message = error or "Failed to create receipt"
                payment.save()
                messages.error(request, f'Payment failed: {error}')
                return redirect('pricing')

            payment.provider_receipt_id = receipt_id
            payment.save()

            success, error = payme_api.pay_receipt(receipt_id, verified_token, test_mode=cfg.payme_is_test)

        else:  # click
            pay_id, trans_id, error = click_api.create_payment(
                payment.amount_uzs,
                payment.id,
                f"Law In — {payment.plan.name}",
                verified_token,
                test_mode=cfg.click_is_test,
            )
            if error or not pay_id:
                payment.status = Payment.STATUS_FAILED
                payment.error_message = error or "Failed to create payment"
                payment.save()
                messages.error(request, f'Payment failed: {error}')
                return redirect('pricing')

            payment.provider_transaction_id = str(pay_id)
            payment.provider_receipt_id = str(trans_id or '')
            payment.save()

            success, error = click_api.confirm_payment(pay_id, test_mode=cfg.click_is_test)

        if success:
            payment.status = Payment.STATUS_PAID
            payment.save()
            # Create subscription
            plan = payment.plan
            expires_at = timezone.now() + timedelta(days=plan.duration_days)
            Subscription.objects.create(
                user=payment.user,
                plan=plan,
                expires_at=expires_at,
            )
            return redirect('payment_success')
        else:
            payment.status = Payment.STATUS_FAILED
            payment.error_message = error or "Charge failed"
            payment.save()
            messages.error(request, f'Payment could not be completed: {error}')
            return redirect('payment_failed')

    return render(request, 'payments/verify.html', {'payment': payment})


@login_required
def resend_sms(request, payment_id):
    """Resend SMS OTP for an existing payment."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    if payment.status != Payment.STATUS_WAITING_SMS:
        messages.error(request, 'Cannot resend SMS for this payment.')
        return redirect('verify_payment', payment_id=payment_id)

    cfg = PaymentSettings.get()
    if payment.provider == Payment.PROVIDER_PAYME:
        _, error = payme_api.send_sms(payment.provider_token, test_mode=cfg.payme_is_test)
    else:
        _, error = click_api.send_sms(payment.provider_token, test_mode=cfg.click_is_test)

    if error:
        messages.error(request, f'Could not resend SMS: {error}')
    else:
        messages.success(request, 'SMS code has been resent.')
    return redirect('verify_payment', payment_id=payment_id)


@login_required
def payment_success(request):
    sub = Subscription.objects.filter(
        user=request.user, is_active=True, expires_at__gt=timezone.now()
    ).first()
    return render(request, 'payments/success.html', {'subscription': sub})


@login_required
def payment_failed(request):
    return render(request, 'payments/failed.html')
