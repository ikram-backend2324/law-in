"""
Click Cards API (direct card integration).
Docs: https://docs.click.uz
Flow:
  1. card/token  → get card token
  2. card/otp    → send OTP SMS
  3. card/verify → confirm OTP → card verified
  4. payment/create → create payment
  5. payment/confirm → charge the card
"""
import requests
import hashlib
import time
from .models import PaymentSettings


def _base_url(test_mode=True):
    # Click has a single endpoint; test transactions use test credentials
    return "https://api.click.uz/v2/merchant"


def _get_auth(test_mode=True):
    cfg = PaymentSettings.get()
    merchant_id = cfg.click_merchant_id
    service_id = cfg.click_service_id
    secret_key = cfg.click_secret_key
    timestamp = str(int(time.time()))
    digest = hashlib.sha1(f"{timestamp}{secret_key}".encode()).hexdigest()
    return {
        "Auth": f"{merchant_id}:{service_id}:{digest}:{timestamp}",
        "Content-Type": "application/json",
    }


def _post(endpoint, payload, test_mode=True):
    url = f"{_base_url(test_mode)}{endpoint}"
    try:
        resp = requests.post(url, json=payload, headers=_get_auth(test_mode), timeout=15)
        data = resp.json()
        error_code = data.get("error_code", -1)
        if error_code != 0:
            return None, data.get("error_note", "Click error")
        return data, None
    except Exception as e:
        return None, str(e)


def create_card(card_number, expire_month, expire_year, test_mode=True):
    """
    Step 1: Register card. expire_month/year as strings e.g. '03','25'
    Returns card token.
    """
    cfg = PaymentSettings.get()
    payload = {
        "service_id": cfg.click_service_id,
        "card_number": card_number.replace(" ", ""),
        "expire_date": f"{expire_month}{expire_year}",
        "temporary": 0,
    }
    result, error = _post("/card/token", payload, test_mode)
    if error:
        return None, error
    return result.get("card_token"), None


def send_sms(card_token, test_mode=True):
    """Step 2: Send OTP to card's phone."""
    cfg = PaymentSettings.get()
    payload = {
        "service_id": cfg.click_service_id,
        "card_token": card_token,
    }
    result, error = _post("/card/otp", payload, test_mode)
    if error:
        return False, error
    phone = result.get("phone_mask", "")
    return phone or True, None


def verify_card(card_token, otp, test_mode=True):
    """Step 3: Confirm OTP → verified card token."""
    cfg = PaymentSettings.get()
    payload = {
        "service_id": cfg.click_service_id,
        "card_token": card_token,
        "sms_code": otp,
    }
    result, error = _post("/card/verify", payload, test_mode)
    if error:
        return None, error
    if result.get("verified") == 1:
        return card_token, None
    return None, "OTP verification failed"


def create_payment(amount_uzs, order_id, description, card_token, test_mode=True):
    """Step 4 + 5 combined: create and immediately confirm payment."""
    cfg = PaymentSettings.get()
    payload = {
        "service_id": cfg.click_service_id,
        "card_token": card_token,
        "amount": float(amount_uzs),
        "payment_option": "card",
        "description": description,
        "param2": str(order_id),
    }
    result, error = _post("/payment/create", payload, test_mode)
    if error:
        return None, None, error
    payment_id = result.get("payment_id")
    transaction_id = result.get("click_trans_id")
    return payment_id, transaction_id, None


def confirm_payment(payment_id, test_mode=True):
    """Confirm (capture) a Click payment."""
    cfg = PaymentSettings.get()
    payload = {
        "service_id": cfg.click_service_id,
        "payment_id": payment_id,
    }
    result, error = _post("/payment/confirm", payload, test_mode)
    if error:
        return False, error
    if result.get("payment_status") == 2:  # 2 = success
        return True, None
    return False, f"Unexpected status: {result.get('payment_status')}"
