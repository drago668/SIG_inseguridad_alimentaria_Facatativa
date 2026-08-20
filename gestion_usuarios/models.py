from django.contrib.auth.models import AbstractUser, BaseUserManager
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table ='usuario'

    def __str__(self):
        return f"{self.email} ({self.get_rol_display()})"

"""
class Administrador(models.Model):
    id_administrador = models.IntegerField(primary_key=True)
    nombre_usuario = models.CharField(max_length=255, blank=True, null=True)
    contrasena = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'administrador'


class RolesUsuario(models.Model):
    id_rol_usuario = models.IntegerField(primary_key=True)
    nombre_rol = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles_usuario'


class Usuario(models.Model):
    id_usuario = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    contrasena = models.CharField(max_length=255, blank=True, null=True)
    entidad = models.CharField(max_length=255, blank=True, null=True)
    id_rol_usuario = models.ForeignKey(RolesUsuario, models.DO_NOTHING, db_column='id_rol_usuario', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'

"""