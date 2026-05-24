from django.db import models
from django.conf import settings
from django.utils import timezone


class PaymentSettings(models.Model):
    """Singleton model — admin stores their Payme & Click merchant credentials here."""
    # Payme credentials
    payme_merchant_id = models.CharField(max_length=200, blank=True, verbose_name="Payme Merchant ID")
    payme_secret_key = models.CharField(max_length=200, blank=True, verbose_name="Payme Secret Key")
    payme_is_test = models.BooleanField(default=True, verbose_name="Payme Test Mode")

    # Click credentials
    click_merchant_id = models.CharField(max_length=200, blank=True, verbose_name="Click Merchant ID")
    click_service_id = models.CharField(max_length=200, blank=True, verbose_name="Click Service ID")
    click_secret_key = models.CharField(max_length=200, blank=True, verbose_name="Click Secret Key")
    click_is_test = models.BooleanField(default=True, verbose_name="Click Test Mode")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Settings"
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return "Payment Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton — only one row allowed
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name="Plan Name")
    description = models.TextField(blank=True, verbose_name="Description")
    price_uzs = models.PositiveIntegerField(verbose_name="Price (UZS)")
    duration_days = models.PositiveIntegerField(verbose_name="Duration (days)")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price_uzs']
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} — {self.price_uzs:,} UZS / {self.duration_days} days"

    @property
    def price_tiyin(self):
        """Payme uses tiyin (1 UZS = 100 tiyin)."""
        return self.price_uzs * 100


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.user} — {self.plan} (expires {self.expires_at.strftime('%d.%m.%Y')})"

    @property
    def is_valid(self):
        return self.is_active and self.expires_at > timezone.now()

    @classmethod
    def has_active(cls, user):
        return cls.objects.filter(user=user, is_active=True, expires_at__gt=timezone.now()).exists()


class Payment(models.Model):
    PROVIDER_PAYME = 'payme'
    PROVIDER_CLICK = 'click'
    PROVIDER_CHOICES = [
        (PROVIDER_PAYME, 'Payme'),
        (PROVIDER_CLICK, 'Click'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_WAITING_SMS = 'waiting_sms'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_WAITING_SMS, 'Waiting SMS'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    amount_uzs = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Card info (masked for display only — never store full card)
    card_number_masked = models.CharField(max_length=20, blank=True)

    # Provider-specific transaction tokens/IDs
    provider_token = models.CharField(max_length=500, blank=True)   # card token from Payme/Click
    provider_transaction_id = models.CharField(max_length=200, blank=True)  # receipt/transaction ID
    provider_receipt_id = models.CharField(max_length=200, blank=True)      # Payme receipt ID

    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.user} | {self.provider.upper()} | {self.amount_uzs:,} UZS | {self.status}"

    @property
    def amount_tiyin(self):
        return self.amount_uzs * 100
