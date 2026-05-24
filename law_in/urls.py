from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

admin.site.site_header = "⚖️ Law In Administration"
admin.site.site_title = "Law In Admin"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('admin/bulk-upload/', include('tests_app.bulk_urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
    path('', include('tests_app.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
