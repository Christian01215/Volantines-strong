from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("producto/<slug:slug>/", views.product_detail, name="detail"),
]
