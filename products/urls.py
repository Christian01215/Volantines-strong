from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("producto/<slug:slug>/", views.product_detail, name="detail"),
    path("personalizar/<slug:slug>/", views.customize, name="customize"),
    path("personalizar/<slug:slug>/subir/", views.customize_upload, name="customize_upload"),
]
