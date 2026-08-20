from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import Usuario

def rol_requerido(roles_permitidos=[]):
    """Decorador para restringir el acceso a vistas según el rol del usuario."""
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol in roles_permitidos or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator