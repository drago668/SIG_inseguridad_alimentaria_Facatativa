from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_usuario_view, name='registrar_usuario'),
]