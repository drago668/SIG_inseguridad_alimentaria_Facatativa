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



"""
#conversion de template a txto para enviarla en el correo
user = 'usuario de prueba'
html_message = render_to_string('template.html', {'user': user})

subject ='titulo del correo'
text_content = 'cuerpo del correo para motores de correo que solo reciben texto plano'
html_message = '<p> aqui en caso de motores que <strong>si rendericen html</strong></p>'
# Como se envian correos
msg = EmailMultiAlternatives(subject, text_content, 'sig.inseguridad.alimentaria@gmail.com', ['danielestebanriveragomez03@gmail.com'])
# Aqui se agrega el contenido html
msg.attach_alternative(html_message, "text/html")
msg.send()
"""
