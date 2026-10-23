"""
URL configuration for sig_inseguridad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from gestion_usuarios.views import login_view, logout_view
from django.contrib.auth import views as auth_views
from visor_grafico.views import mapa_facatativa_page

urlpatterns = [
    path('', mapa_facatativa_page,name='inicio'),
    path("visor_grafico/", include("visor_grafico.urls")),
    path('admin/', admin.site.urls),
    path('indicador_territorial/', include('indicador_territorial.urls')),
    path('auth/', include('gestion_usuarios.urls')),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('capas/', include('app_capas.urls')),
    path('recuperar-password/', 
        auth_views.PasswordResetView.as_view(
            template_name='gestion_usuarios/password_reset.html',
            email_template_name='correos/password_reset_email.html', # Versión texto
            html_email_template_name='correos/password_reset_email.html', # Versión HTML
            subject_template_name='correos/password_reset_subject.txt'
        ), 
        name='password_reset'),
    path('recuperar-password/enviado/', auth_views.PasswordResetDoneView.as_view(template_name='correos/password_reset_done.html'), 
        name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='correos/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    path('recuperar-password/completo/', auth_views.PasswordResetCompleteView.as_view(template_name='correos/password_reset_complete.html'), 
        name='password_reset_complete'),
]
