from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('verify/<int:payment_id>/', views.verify_payment, name='verify_payment'),
    path('resend-sms/<int:payment_id>/', views.resend_sms, name='resend_sms'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]
