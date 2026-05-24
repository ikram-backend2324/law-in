from django.urls import path
from .bulk_views import bulk_upload_view, download_template

urlpatterns = [
    path('', bulk_upload_view, name='bulk_upload'),
    path('template/<str:fmt>/', download_template, name='download_template'),
]
