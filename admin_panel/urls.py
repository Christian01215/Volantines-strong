from django.urls import path
from . import views

app_name = "admin_panel"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', views.product_list, name='product_list'),
    path('productos/crear/', views.product_create, name='product_create'),
    path('productos/<int:product_id>/editar/', views.product_edit, name='product_edit'),
    path('pedidos/', views.order_list, name='order_list'),
    path('pedidos/<str:order_code>/status/', views.order_status_update, name='order_status_update'),
]
