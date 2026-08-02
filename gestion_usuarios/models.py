from django.db import models

# Create your models here.

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