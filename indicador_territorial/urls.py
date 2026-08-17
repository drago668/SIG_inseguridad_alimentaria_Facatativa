from django.urls import path
from .views import dashboard_view, regresion_inseguridad

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/regresion', regresion_inseguridad, name='regresion')
]
