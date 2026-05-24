from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tests/', views.test_list, name='test_list'),
    path('tests/<int:test_id>/take/', views.take_test, name='take_test'),
    path('tests/submit/<int:attempt_id>/', views.submit_test, name='submit_test'),
    path('tests/result/<int:attempt_id>/', views.test_result, name='test_result'),
    path('tests/my-results/', views.my_results, name='my_results'),
    path('tests/<int:test_id>/admin/', views.test_detail_admin, name='test_detail_admin'),
]
