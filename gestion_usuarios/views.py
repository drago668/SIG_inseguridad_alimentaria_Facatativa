from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegistroUsuarioForm, CustomLoginForm
from .decorators import rol_requerido
from .models import Usuario

def login_view(request):
    """Maneja el inicio de sesión mediante correo y contraseña."""
    if request.user.is_authenticated:
        return redirect('mapa_facatativa')  # Ajusta a tu URL principal

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido(a), {user.email}')
            return redirect('mapa_facatativa')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'gestion_usuarios/login.html', {'form': form})

def logout_view(request):
    """Cierra la sesión activa."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


@rol_requerido(roles_permitidos=[Usuario.Rol.ADMINISTRADOR])
def registrar_usuario_view(request):
    """Exclusivo para Administradores: permite crear cuentas para otros Admins o Entidades."""
    mostrar_modal_exito = False
    usuario_creado_email = ""

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():  
            usuario_creado = form.save()
            mostrar_modal_exito = True
            usuario_creado_email = usuario_creado.email
            # Reiniciamos el formulario limpio tras el éxito
            form = RegistroUsuarioForm()
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = RegistroUsuarioForm()
    
    context = {
        'form': form,
        'mostrar_modal_exito': mostrar_modal_exito,
        'usuario_creado_email': usuario_creado_email,
    }
    
    return render(request, 'gestion_usuarios/registrar_usuario.html', context)