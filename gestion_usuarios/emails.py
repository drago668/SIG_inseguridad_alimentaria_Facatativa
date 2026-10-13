import environ, os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def correo_bienvenida(contexto):
    html_content = render_to_string('gestion_usuarios/bienvenida_usuario.html', contexto)
    text_content = f"Bienvenido a SIG Facatativá. Tu usuario es: {contexto['email']} y tu contraseña es: {contexto['password']}"
    msg = EmailMultiAlternatives(
        subject='Credenciales de acceso - SIG Facatativá',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[contexto['email']]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


