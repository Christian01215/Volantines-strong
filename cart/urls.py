from django.urls import path
from . import views

app_name = "cart"
urlpatterns = [
    path("carrito/", views.view_cart, name="view"),
    path("agregar/<int:product_id>/", views.add_to_cart, name="add"),
    path("actualizar/<int:product_id>/", views.set_cart_quantity, name="set_quantity"),
    path("quitar/<int:product_id>/", views.remove_from_cart, name="remove"),
    path("checkout/", views.checkout, name="checkout"),
    # API JSON consumida por el drawer
    path("api/", views.cart_api, name="api"),
    path("api/agregar/", views.cart_api_add, name="api_add"),
    path("api/actualizar/", views.cart_api_update, name="api_update"),
    path("api/quitar/", views.cart_api_remove, name="api_remove"),
    path("api/vaciar/", views.cart_api_clear, name="api_clear"),
]
