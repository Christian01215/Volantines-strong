from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("generar/", views.generate_order_from_cart, name="generate"),
    path("admin/", views.admin_order_list, name="admin_list"),
    path("admin/<str:order_code>/update/", views.admin_order_update, name="admin_update"),
]
