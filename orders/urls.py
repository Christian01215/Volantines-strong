from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("checkout/", views.checkout_submit, name="checkout"),
    path("generar/", views.generate_order_from_cart, name="generate"),
    path("pedido/", views.order_track, name="track"),
    path("pedido/<str:code>/confirmado/", views.checkout_success, name="success"),
    path("pedido/<str:code>/", views.order_track_detail, name="track_detail"),
    path("admin/", views.admin_order_list, name="admin_list"),
    path("admin/<str:order_code>/update/", views.admin_order_update, name="admin_update"),
]
