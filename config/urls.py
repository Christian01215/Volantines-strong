"""URL configuration for config project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    """Endpoint mínimo para smoke checks y monitorización."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health', health, name='health'),
    path('admin/', admin.site.urls),
    path('', include('products.urls', namespace='products')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
