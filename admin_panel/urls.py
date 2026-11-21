from django.urls import path
from . import views

app_name = "admin_panel"
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='home'),
    path('productos/', views.dashboard, name='product_list'),
    path('productos/guardar/', views.product_save, name='product_save'),
    path('productos/<int:product_id>/editar/', views.product_edit, name='product_edit'),
    path('productos/<int:product_id>/eliminar/', views.product_delete, name='product_delete'),
    path('pedidos/', views.dashboard, name='order_list'),
    path('pedidos/<str:order_code>/status/', views.order_status_update, name='order_status_update'),
    path('pedidos/<str:order_code>/notificar/', views.order_notify, name='order_notify'),
    path('pedidos/<str:order_code>/eliminar/', views.order_delete, name='order_delete'),
]
