from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electronico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', Usuario.Rol.ADMINISTRADOR)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMINISTRADOR ='ADMIN', 'Administrador'
        ENTIDAD = 'ENTIDAD', 'Entidad'
        CIUDADANO = 'CIUDADANO', 'Ciudadano (Invitado)'

    username = None
    email = models.EmailField('Correo Electronico', unique=True)
    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.CIUDADANO
    )
    direccion = models.CharField('Dirección de Residencia', max_length=255, blank=True, null=True)
    
    validador_telefono = RegexValidator(
        regex=r'^\+?1?\d{7,15}$',
        message="El número de teléfono debe ingresarse en formato: '+573001234567'. De 7 a 15 dígitos."
    )
    telefono = models.CharField(
        'Teléfono de Contacto',
        validators=[validador_telefono],
        max_length=16,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table ='usuario'

    def __str__(self):
        return f"{self.email} ({self.get_rol_display()})"
