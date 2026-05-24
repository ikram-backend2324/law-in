from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import PaymentSettings, SubscriptionPlan, Subscription, Payment


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('💳 Payme Credentials', {
            'fields': ('payme_merchant_id', 'payme_secret_key', 'payme_is_test'),
            'description': 'Get these from your Payme merchant cabinet at merchant.paycom.uz',
        }),
        ('💳 Click Credentials', {
            'fields': ('click_merchant_id', 'click_service_id', 'click_secret_key', 'click_is_test'),
            'description': 'Get these from your Click merchant cabinet at my.click.uz',
        }),
    )

    def has_add_permission(self, request):
        # Only allow editing the singleton; disable add if one already exists
        return not PaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Auto-redirect to edit page since it's a singleton
        obj, _ = PaymentSettings.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        return redirect(f'/admin/payments/paymentsettings/{obj.pk}/change/')


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_display', 'duration_days', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_display_links = ('name',)
    fields = ('name', 'description', 'price_uzs', 'duration_days', 'is_active')

    def price_display(self, obj):
        return format_html('<strong>{:,} UZS</strong>', obj.price_uzs)
    price_display.short_description = 'Price'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'started_at', 'expires_at', 'status_display')
    list_filter = ('is_active', 'plan')
    search_fields = ('user__username', 'user__full_name', 'user__email')
    readonly_fields = ('user', 'plan', 'started_at', 'expires_at')
    ordering = ('-started_at',)

    def status_display(self, obj):
        if obj.is_valid:
            days_left = (obj.expires_at - timezone.now()).days
            return format_html(
                '<span style="color:green;font-weight:bold">✅ Active ({} days left)</span>', days_left
            )
        return format_html('<span style="color:red">❌ Expired</span>')
    status_display.short_description = 'Status'

    def has_add_permission(self, request):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider_badge', 'amount_display', 'card_number_masked', 'status_badge', 'created_at')
    list_filter = ('provider', 'status', 'plan')
    search_fields = ('user__username', 'user__full_name', 'card_number_masked', 'provider_transaction_id')
    readonly_fields = (
        'user', 'plan', 'provider', 'amount_uzs', 'card_number_masked',
        'provider_token', 'provider_transaction_id', 'provider_receipt_id',
        'error_message', 'created_at', 'updated_at', 'status',
    )
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def provider_badge(self, obj):
        colors = {'payme': '#00A651', 'click': '#0099CC'}
        color = colors.get(obj.provider, '#888')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:4px;font-weight:bold">{}</span>',
            color, obj.provider.upper()
        )
    provider_badge.short_description = 'Provider'

    def amount_display(self, obj):
        return format_html('<strong>{:,} UZS</strong>', obj.amount_uzs)
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': ('#FFA500', '⏳'),
            'waiting_sms': ('#2196F3', '📱'),
            'paid': ('#4CAF50', '✅'),
            'failed': ('#F44336', '❌'),
            'cancelled': ('#9E9E9E', '🚫'),
        }
        color, icon = colors.get(obj.status, ('#888', '?'))
        return format_html(
            '<span style="color:{};font-weight:bold">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
