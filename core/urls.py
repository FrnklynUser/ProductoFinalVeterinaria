from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs para Mascotas
    path('mascotas/', views.mascota_list, name='mascota_list'),
    path('mascotas/crear/', views.mascota_create, name='mascota_create'),
    path('mascotas/<int:pk>/editar/', views.mascota_edit, name='mascota_edit'),
    path('mascotas/<int:pk>/eliminar/', views.mascota_delete, name='mascota_delete'),
    
    # URLs para Propietarios
    path('propietarios/', views.propietario_list, name='propietario_list'),
    path('propietarios/crear/', views.propietario_create, name='propietario_create'),
    path('propietarios/<int:pk>/editar/', views.propietario_edit, name='propietario_edit'),
    path('propietarios/<int:pk>/eliminar/', views.propietario_delete, name='propietario_delete'),
    
    # URLs para Historial Clínico
    path('historial/', views.historial_list, name='historial_list'),
    path('historial/crear/', views.historial_create, name='historial_create'),
    path('historial/<int:pk>/editar/', views.historial_edit, name='historial_edit'),
    path('historial/<int:pk>/eliminar/', views.historial_delete, name='historial_delete'),
    
    # URLs para Citas
    path('citas/', views.cita_list, name='cita_list'),
    path('citas/crear/', views.cita_create, name='cita_create'),
    path('citas/<int:pk>/editar/', views.cita_edit, name='cita_edit'),
    path('citas/<int:pk>/eliminar/', views.cita_delete, name='cita_delete'),
    path('citas/<int:pk>/', views.cita_detail, name='cita_detail'),


    # URLs para Facturación
    path('facturas/', views.factura_list, name='factura_list'),
    path('facturas/crear/', views.factura_create, name='factura_create'),
    path('facturas/<int:pk>/', views.factura_detail, name='factura_detail'),
    path('facturas/<int:pk>/editar/', views.factura_edit, name='factura_edit'),
    path('facturas/<int:pk>/anular/', views.factura_anular, name='factura_anular'),
    
    # URLs para Reportes
    path('reportes/', views.reporte_dashboard, name='reporte_dashboard'),
    path('reportes/ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reportes/citas/', views.reporte_citas, name='reporte_citas'),
]