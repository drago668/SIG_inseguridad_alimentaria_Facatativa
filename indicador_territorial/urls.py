from django.urls import path
from .views import (
    dashboard_view, obtener_dimensiones_municipales, obtener_dimensiones_zonales,
    cargar_ecv_view, obtener_prevalencia_zonales_bd,
    )

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/dimensiones-municipales/', obtener_dimensiones_municipales, name='dimensiones_municipales'),
    path('api/dimensiones-zonales/', obtener_dimensiones_zonales, name='dimensiones_zonales'),
    path('api/prevalencia-zonales-bd/', obtener_prevalencia_zonales_bd, name='prevalencia_zonales_bd'),
    path('cargar-ecv/', cargar_ecv_view, name='cargar_ecv'),

]
