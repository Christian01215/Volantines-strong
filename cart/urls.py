from django.urls import path
from . import views

app_name = "cart"
urlpatterns = [
    path("carrito/", views.view_cart, name="view"),
    path("agregar/<int:product_id>/", views.add_to_cart, name="add"),
    path("quitar/<int:product_id>/", views.remove_from_cart, name="remove"),
    path("checkout/", views.checkout, name="checkout"),
]
