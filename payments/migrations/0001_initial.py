from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payme_merchant_id', models.CharField(blank=True, max_length=200, verbose_name='Payme Merchant ID')),
                ('payme_secret_key', models.CharField(blank=True, max_length=200, verbose_name='Payme Secret Key')),
                ('payme_is_test', models.BooleanField(default=True, verbose_name='Payme Test Mode')),
                ('click_merchant_id', models.CharField(blank=True, max_length=200, verbose_name='Click Merchant ID')),
                ('click_service_id', models.CharField(blank=True, max_length=200, verbose_name='Click Service ID')),
                ('click_secret_key', models.CharField(blank=True, max_length=200, verbose_name='Click Secret Key')),
                ('click_is_test', models.BooleanField(default=True, verbose_name='Click Test Mode')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Payment Settings', 'verbose_name_plural': 'Payment Settings'},
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Plan Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('price_uzs', models.PositiveIntegerField(verbose_name='Price (UZS)')),
                ('duration_days', models.PositiveIntegerField(verbose_name='Duration (days)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Subscription Plan', 'verbose_name_plural': 'Subscription Plans', 'ordering': ['price_uzs']},
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.subscriptionplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Subscription', 'verbose_name_plural': 'Subscriptions', 'ordering': ['-started_at']},
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('payme', 'Payme'), ('click', 'Click')], max_length=20)),
                ('amount_uzs', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('waiting_sms', 'Waiting SMS'), ('paid', 'Paid'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('card_number_masked', models.CharField(blank=True, max_length=20)),
                ('provider_token', models.CharField(blank=True, max_length=500)),
                ('provider_transaction_id', models.CharField(blank=True, max_length=200)),
                ('provider_receipt_id', models.CharField(blank=True, max_length=200)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.subscriptionplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Payment', 'verbose_name_plural': 'Payments', 'ordering': ['-created_at']},
        ),
    ]
