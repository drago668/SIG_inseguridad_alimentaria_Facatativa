# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class ActividadUltimoMes(models.Model):
    id_actividad = models.IntegerField(primary_key=True)
    nombre_actividad = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actividad_ultimo_mes'


class Administrador(models.Model):
    id_administrador = models.IntegerField(primary_key=True)
    nombre_usuario = models.CharField(max_length=255, blank=True, null=True)
    contrasena = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'administrador'


class AfiliacionSeguridadSocial(models.Model):
    id_afiliacion = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING, db_column='municipio', to_field='mpio_cdpmp', blank=True, null=True)
    regimen = models.ForeignKey('Regimen', models.DO_NOTHING, db_column='regimen', blank=True, null=True)
    eps = models.ForeignKey('Eps', models.DO_NOTHING, db_column='eps', blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)
    sexo = models.ForeignKey('Sexo', models.DO_NOTHING, db_column='sexo', blank=True, null=True)
    curso_vida = models.ForeignKey('CursoVida', models.DO_NOTHING, db_column='curso_vida', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'afiliacion_seguridad_social'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BajoPesoNacer(models.Model):
    id_registro_peso = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    etapa_vida_madre = models.ForeignKey('EtapaVidaMadre', models.DO_NOTHING, db_column='etapa_vida_madre', blank=True, null=True)
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING, db_column='municipio', to_field='mpio_cdpmp', blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bajo_peso_nacer'


class BajoPesoRegimen(models.Model):
    id_bajo_peso_regimen = models.IntegerField(primary_key=True)
    numero_afectados = models.IntegerField(blank=True, null=True)
    regimen = models.ForeignKey('Regimen', models.DO_NOTHING, db_column='regimen', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bajo_peso_regimen'


class CatNivelEducativo(models.Model):
    id_nivel_educativo = models.IntegerField(primary_key=True)
    nombre_nivel = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cat_nivel_educativo'


class CombustibleParaCocinar(models.Model):
    id_combustible = models.IntegerField(primary_key=True)
    nombre_combustible = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'combustible_para_cocinar'


class Corte(models.Model):
    id_corte = models.AutoField(primary_key=True)
    nombre_corte = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corte'


class Cultivo(models.Model):
    id_cultivo = models.IntegerField(primary_key=True)
    nombre_cultivo = models.CharField(max_length=255, blank=True, null=True)
    subgrupo_cultivo = models.ForeignKey('SubgrupoCultivo', models.DO_NOTHING, db_column='subgrupo_cultivo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cultivo'


class CursoVida(models.Model):
    id_curso_vida = models.IntegerField(primary_key=True)
    nombre_curso = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'curso_vida'


class Departamentos(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(srid=900914, blank=True, null=True)
    dpto_ccdgo = models.CharField(unique=True, blank=True, null=True)
    dpto_cnmbr = models.CharField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    stctnencue = models.FloatField(blank=True, null=True)
    stp3_1_si = models.FloatField(blank=True, null=True)
    stp3_2_no = models.FloatField(blank=True, null=True)
    stp3a_ri = models.FloatField(blank=True, null=True)
    stp3b_tcn = models.FloatField(blank=True, null=True)
    stp4_1_si = models.FloatField(blank=True, null=True)
    stp4_2_no = models.FloatField(blank=True, null=True)
    stp9_1_uso = models.FloatField(blank=True, null=True)
    stp9_2_uso = models.FloatField(blank=True, null=True)
    stp9_3_uso = models.FloatField(blank=True, null=True)
    stp9_4_uso = models.FloatField(blank=True, null=True)
    stp9_2_1_m = models.FloatField(blank=True, null=True)
    stp9_2_2_m = models.FloatField(blank=True, null=True)
    stp9_2_3_m = models.FloatField(blank=True, null=True)
    stp9_2_4_m = models.FloatField(blank=True, null=True)
    stp9_2_9_m = models.FloatField(blank=True, null=True)
    stp9_3_1_n = models.FloatField(blank=True, null=True)
    stp9_3_2_n = models.FloatField(blank=True, null=True)
    stp9_3_3_n = models.FloatField(blank=True, null=True)
    stp9_3_4_n = models.FloatField(blank=True, null=True)
    stp9_3_5_n = models.FloatField(blank=True, null=True)
    stp9_3_6_n = models.FloatField(blank=True, null=True)
    stp9_3_7_n = models.FloatField(blank=True, null=True)
    stp9_3_8_n = models.FloatField(blank=True, null=True)
    stp9_3_9_n = models.FloatField(blank=True, null=True)
    stp9_3_10 = models.FloatField(blank=True, null=True)
    stp9_3_99 = models.FloatField(blank=True, null=True)
    stvivienda = models.FloatField(blank=True, null=True)
    stp14_1_ti = models.FloatField(blank=True, null=True)
    stp14_2_ti = models.FloatField(blank=True, null=True)
    stp14_3_ti = models.FloatField(blank=True, null=True)
    stp14_4_ti = models.FloatField(blank=True, null=True)
    stp14_5_ti = models.FloatField(blank=True, null=True)
    stp14_6_ti = models.FloatField(blank=True, null=True)
    stp15_1_oc = models.FloatField(blank=True, null=True)
    stp15_2_oc = models.FloatField(blank=True, null=True)
    stp15_3_oc = models.FloatField(blank=True, null=True)
    stp15_4_oc = models.FloatField(blank=True, null=True)
    tsp16_hog = models.FloatField(blank=True, null=True)
    stp19_ec_1 = models.FloatField(blank=True, null=True)
    stp19_es_2 = models.FloatField(blank=True, null=True)
    stp19_ee_1 = models.FloatField(blank=True, null=True)
    stp19_ee_2 = models.FloatField(blank=True, null=True)
    stp19_ee_3 = models.FloatField(blank=True, null=True)
    stp19_ee_4 = models.FloatField(blank=True, null=True)
    stp19_ee_5 = models.FloatField(blank=True, null=True)
    stp19_ee_6 = models.FloatField(blank=True, null=True)
    stp19_ee_9 = models.FloatField(blank=True, null=True)
    stp19_acu1 = models.FloatField(blank=True, null=True)
    stp19_acu2 = models.FloatField(blank=True, null=True)
    stp19_alc1 = models.FloatField(blank=True, null=True)
    stp19_alc2 = models.FloatField(blank=True, null=True)
    stp19_gas1 = models.FloatField(blank=True, null=True)
    stp19_gas2 = models.FloatField(blank=True, null=True)
    stp19_gas9 = models.FloatField(blank=True, null=True)
    stp19_rec1 = models.FloatField(blank=True, null=True)
    stp19_rec2 = models.FloatField(blank=True, null=True)
    stp19_int1 = models.FloatField(blank=True, null=True)
    stp19_int2 = models.FloatField(blank=True, null=True)
    stp19_int9 = models.FloatField(blank=True, null=True)
    stp27_pers = models.FloatField(blank=True, null=True)
    stperson_l = models.FloatField(blank=True, null=True)
    stperson_s = models.FloatField(blank=True, null=True)
    stp32_1_se = models.FloatField(blank=True, null=True)
    stp32_2_se = models.FloatField(blank=True, null=True)
    stp34_1_ed = models.FloatField(blank=True, null=True)
    stp34_2_ed = models.FloatField(blank=True, null=True)
    stp34_3_ed = models.FloatField(blank=True, null=True)
    stp34_4_ed = models.FloatField(blank=True, null=True)
    stp34_5_ed = models.FloatField(blank=True, null=True)
    stp34_6_ed = models.FloatField(blank=True, null=True)
    stp34_7_ed = models.FloatField(blank=True, null=True)
    stp34_8_ed = models.FloatField(blank=True, null=True)
    stp34_9_ed = models.FloatField(blank=True, null=True)
    stp51_prim = models.FloatField(blank=True, null=True)
    stp51_secu = models.FloatField(blank=True, null=True)
    stp51_supe = models.FloatField(blank=True, null=True)
    stp51_post = models.FloatField(blank=True, null=True)
    stp51_13_e = models.FloatField(blank=True, null=True)
    stp51_99_e = models.FloatField(blank=True, null=True)
    shape_leng = models.FloatField(blank=True, null=True)
    shape_area = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departamentos'


class DesnutricionAguda(models.Model):
    id_registro = models.IntegerField(primary_key=True)
    edad = models.IntegerField(blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING, db_column='municipio', to_field='mpio_cdpmp', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'desnutricion_aguda'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Eps(models.Model):
    id_eps = models.IntegerField(primary_key=True)
    nombre_eps = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eps'


class EtapaVidaMadre(models.Model):
    id_etapa = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    curso_vida = models.ForeignKey(CursoVida, models.DO_NOTHING, db_column='curso_vida', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'etapa_vida_madre'


class FuenteObtencionAgua(models.Model):
    id_fuente = models.IntegerField(primary_key=True)
    nombre_fuente = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fuente_obtencion_agua'


class GrupoCultivo(models.Model):
    id_grupo = models.IntegerField(primary_key=True)
    nombre_cultivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grupo_cultivo'


class Hogar(models.Model):
    id_hogar = models.AutoField(primary_key=True)
    agua_llega_7_dias = models.BooleanField(blank=True, null=True)
    cocina = models.BooleanField(blank=True, null=True)
    nevera = models.BooleanField(blank=True, null=True)
    jefe_hogar = models.ForeignKey('JefeHogar', models.DO_NOTHING, db_column='jefe_hogar', blank=True, null=True)
    afiliacion_seguridad_social = models.ForeignKey(AfiliacionSeguridadSocial, models.DO_NOTHING, db_column='afiliacion_seguridad_social', blank=True, null=True)
    zona_geografica = models.ForeignKey('ZonaGeografica', models.DO_NOTHING, db_column='zona_geografica', blank=True, null=True)
    fuente_agua = models.ForeignKey(FuenteObtencionAgua, models.DO_NOTHING, db_column='fuente_agua', blank=True, null=True)
    tratamiento_agua = models.ForeignKey('TratamientoAguaConsumo', models.DO_NOTHING, db_column='tratamiento_agua', blank=True, null=True)
    combustible_para_cocinar = models.ForeignKey(CombustibleParaCocinar, models.DO_NOTHING, db_column='combustible_para_cocinar', blank=True, null=True)
    total_personas_hogar = models.IntegerField(blank=True, null=True)
    corte = models.ForeignKey(Corte, models.DO_NOTHING, db_column='corte', blank=True, null=True)
    tipo_vivienda = models.ForeignKey('TipoVivienda', models.DO_NOTHING, db_column='tipo_vivienda', blank=True, null=True)
    llave = models.CharField(blank=True, null=True)
    hogar = models.CharField(blank=True, null=True)
    vivienda = models.ForeignKey('Vivienda', models.DO_NOTHING, db_column='vivienda', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hogar'


class JefeHogar(models.Model):
    id_jefe_hogar = models.AutoField(primary_key=True)
    desempleo_larga_duracion = models.BooleanField(blank=True, null=True)
    trabajo_informal = models.BooleanField(blank=True, null=True)
    actividad = models.ForeignKey(ActividadUltimoMes, models.DO_NOTHING, db_column='actividad', blank=True, null=True)
    nivel_educativo = models.ForeignKey(CatNivelEducativo, models.DO_NOTHING, db_column='nivel_educativo', blank=True, null=True)
    id_sexo = models.ForeignKey('Sexo', models.DO_NOTHING, db_column='id_sexo', blank=True, null=True)
    grupo_sisben = models.CharField(blank=True, null=True)
    nivel_sisben = models.IntegerField(blank=True, null=True)
    corte = models.ForeignKey(Corte, models.DO_NOTHING, db_column='corte', blank=True, null=True)
    llave = models.CharField(blank=True, null=True)
    hogar = models.CharField(blank=True, null=True)
    orden = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jefe_hogar'


class MaterialVivienda(models.Model):
    id_material = models.IntegerField(primary_key=True)
    nombre_material = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_vivienda'


class MortalidadDesnutricion(models.Model):
    id_mortalidad = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING, db_column='municipio', to_field='mpio_cdpmp', blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mortalidad_desnutricion'


class MortalidadInfantilPorEdad(models.Model):
    id_mortalidad_edad = models.IntegerField(primary_key=True)
    edad = models.IntegerField(blank=True, null=True)
    defunciones = models.IntegerField(blank=True, null=True)
    mortalidad = models.ForeignKey(MortalidadDesnutricion, models.DO_NOTHING, db_column='mortalidad', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mortalidad_infantil_por_edad'


class Municipios(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(srid=900914, blank=True, null=True)
    dpto_ccdgo = models.CharField(blank=True, null=True)
    mpio_ccdgo = models.CharField(blank=True, null=True)
    mpio_cnmbr = models.CharField(blank=True, null=True)
    mpio_cdpmp = models.CharField(unique=True, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    area = models.FloatField(blank=True, null=True)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    stctnencue = models.FloatField(blank=True, null=True)
    stp3_1_si = models.FloatField(blank=True, null=True)
    stp3_2_no = models.FloatField(blank=True, null=True)
    stp3a_ri = models.FloatField(blank=True, null=True)
    stp3b_tcn = models.FloatField(blank=True, null=True)
    stp4_1_si = models.FloatField(blank=True, null=True)
    stp4_2_no = models.FloatField(blank=True, null=True)
    stp9_1_uso = models.FloatField(blank=True, null=True)
    stp9_2_uso = models.FloatField(blank=True, null=True)
    stp9_3_uso = models.FloatField(blank=True, null=True)
    stp9_4_uso = models.FloatField(blank=True, null=True)
    stp9_2_1_m = models.FloatField(blank=True, null=True)
    stp9_2_2_m = models.FloatField(blank=True, null=True)
    stp9_2_3_m = models.FloatField(blank=True, null=True)
    stp9_2_4_m = models.FloatField(blank=True, null=True)
    stp9_2_9_m = models.FloatField(blank=True, null=True)
    stp9_3_1_n = models.FloatField(blank=True, null=True)
    stp9_3_2_n = models.FloatField(blank=True, null=True)
    stp9_3_3_n = models.FloatField(blank=True, null=True)
    stp9_3_4_n = models.FloatField(blank=True, null=True)
    stp9_3_5_n = models.FloatField(blank=True, null=True)
    stp9_3_6_n = models.FloatField(blank=True, null=True)
    stp9_3_7_n = models.FloatField(blank=True, null=True)
    stp9_3_8_n = models.FloatField(blank=True, null=True)
    stp9_3_9_n = models.FloatField(blank=True, null=True)
    stp9_3_10 = models.FloatField(blank=True, null=True)
    stp9_3_99 = models.FloatField(blank=True, null=True)
    stvivienda = models.FloatField(blank=True, null=True)
    stp14_1_ti = models.FloatField(blank=True, null=True)
    stp14_2_ti = models.FloatField(blank=True, null=True)
    stp14_3_ti = models.FloatField(blank=True, null=True)
    stp14_4_ti = models.FloatField(blank=True, null=True)
    stp14_5_ti = models.FloatField(blank=True, null=True)
    stp14_6_ti = models.FloatField(blank=True, null=True)
    stp15_1_oc = models.FloatField(blank=True, null=True)
    stp15_2_oc = models.FloatField(blank=True, null=True)
    stp15_3_oc = models.FloatField(blank=True, null=True)
    stp15_4_oc = models.FloatField(blank=True, null=True)
    tsp16_hog = models.FloatField(blank=True, null=True)
    stp19_ec_1 = models.FloatField(blank=True, null=True)
    stp19_es_2 = models.FloatField(blank=True, null=True)
    stp19_ee_1 = models.FloatField(blank=True, null=True)
    stp19_ee_2 = models.FloatField(blank=True, null=True)
    stp19_ee_3 = models.FloatField(blank=True, null=True)
    stp19_ee_4 = models.FloatField(blank=True, null=True)
    stp19_ee_5 = models.FloatField(blank=True, null=True)
    stp19_ee_6 = models.FloatField(blank=True, null=True)
    stp19_ee_9 = models.FloatField(blank=True, null=True)
    stp19_acu1 = models.FloatField(blank=True, null=True)
    stp19_acu2 = models.FloatField(blank=True, null=True)
    stp19_alc1 = models.FloatField(blank=True, null=True)
    stp19_alc2 = models.FloatField(blank=True, null=True)
    stp19_gas1 = models.FloatField(blank=True, null=True)
    stp19_gas2 = models.FloatField(blank=True, null=True)
    stp19_gas9 = models.FloatField(blank=True, null=True)
    stp19_rec1 = models.FloatField(blank=True, null=True)
    stp19_rec2 = models.FloatField(blank=True, null=True)
    stp19_int1 = models.FloatField(blank=True, null=True)
    stp19_int2 = models.FloatField(blank=True, null=True)
    stp19_int9 = models.FloatField(blank=True, null=True)
    stp27_pers = models.FloatField(blank=True, null=True)
    stperson_l = models.FloatField(blank=True, null=True)
    stperson_s = models.FloatField(blank=True, null=True)
    stp32_1_se = models.FloatField(blank=True, null=True)
    stp32_2_se = models.FloatField(blank=True, null=True)
    stp34_1_ed = models.FloatField(blank=True, null=True)
    stp34_2_ed = models.FloatField(blank=True, null=True)
    stp34_3_ed = models.FloatField(blank=True, null=True)
    stp34_4_ed = models.FloatField(blank=True, null=True)
    stp34_5_ed = models.FloatField(blank=True, null=True)
    stp34_6_ed = models.FloatField(blank=True, null=True)
    stp34_7_ed = models.FloatField(blank=True, null=True)
    stp34_8_ed = models.FloatField(blank=True, null=True)
    stp34_9_ed = models.FloatField(blank=True, null=True)
    stp51_prim = models.FloatField(blank=True, null=True)
    stp51_secu = models.FloatField(blank=True, null=True)
    stp51_supe = models.FloatField(blank=True, null=True)
    stp51_post = models.FloatField(blank=True, null=True)
    stp51_13_e = models.FloatField(blank=True, null=True)
    stp51_99_e = models.FloatField(blank=True, null=True)
    shape_leng = models.FloatField(blank=True, null=True)
    shape_area = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'municipios'


class Nacionalidad(models.Model):
    id_nacionalidad = models.IntegerField(primary_key=True)
    pais_origen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nacionalidad'


class Precio(models.Model):
    id_precio = models.IntegerField(primary_key=True)
    precio = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    cultivo = models.ForeignKey(Cultivo, models.DO_NOTHING, db_column='cultivo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'precio'


class ProduccionAgricola(models.Model):
    id_produccion = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    periodo = models.IntegerField(blank=True, null=True)
    area_sembrada = models.FloatField(blank=True, null=True)
    area_cosechada = models.FloatField(blank=True, null=True)
    produccion = models.FloatField(blank=True, null=True)
    rendimiento = models.FloatField(blank=True, null=True)
    ciclo = models.IntegerField(blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    cultivo = models.ForeignKey(Cultivo, models.DO_NOTHING, db_column='cultivo', blank=True, null=True)
    municipio = models.ForeignKey(Municipios, models.DO_NOTHING, db_column='municipio', to_field='mpio_cdpmp', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'produccion_agricola'


class ProgramaSocial(models.Model):
    id_programa_social = models.IntegerField(primary_key=True)
    nombre_programa = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programa_social'


class ProgramaSocialZonaGeografica(models.Model):
    pk = models.CompositePrimaryKey('id_zona', 'id_programa')
    id_zona = models.ForeignKey('ZonaGeografica', models.DO_NOTHING, db_column='id_zona')
    id_programa = models.ForeignKey(ProgramaSocial, models.DO_NOTHING, db_column='id_programa')

    class Meta:
        managed = False
        db_table = 'programa_social_zona_geografica'


class Regimen(models.Model):
    id_regimen = models.IntegerField(primary_key=True)
    nombre_regimen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'regimen'


class RolesUsuario(models.Model):
    id_rol_usuario = models.IntegerField(primary_key=True)
    nombre_rol = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles_usuario'


class Sexo(models.Model):
    id_sexo = models.IntegerField(primary_key=True)
    nombre_sexo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sexo'


class SubgrupoCultivo(models.Model):
    id_subgrupo = models.IntegerField(primary_key=True)
    nombre_subcultivo = models.CharField(max_length=255, blank=True, null=True)
    grupo_cultivo = models.ForeignKey(GrupoCultivo, models.DO_NOTHING, db_column='grupo_cultivo', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subgrupo_cultivo'


class TipoVivienda(models.Model):
    id_tipo_vivienda = models.IntegerField(primary_key=True)
    nombre_tipo_vivienda = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_vivienda'


class TratamientoAguaConsumo(models.Model):
    id_tratamiento_agua = models.IntegerField(primary_key=True)
    nombre_tratamiento = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tratamiento_agua_consumo'


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


class Veredas(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(srid=900914, blank=True, null=True)
    fid = models.FloatField(blank=True, null=True)
    name = models.CharField(blank=True, null=True)
    descriptio = models.CharField(blank=True, null=True)
    timestamp = models.CharField(blank=True, null=True)
    begin = models.CharField(blank=True, null=True)
    end = models.CharField(blank=True, null=True)
    altitudemo = models.CharField(blank=True, null=True)
    tessellate = models.BigIntegerField(blank=True, null=True)
    extrude = models.BigIntegerField(blank=True, null=True)
    visibility = models.BigIntegerField(blank=True, null=True)
    draworder = models.BigIntegerField(blank=True, null=True)
    icon = models.CharField(blank=True, null=True)
    objectid = models.CharField(blank=True, null=True)
    dptompio = models.CharField(blank=True, null=True)
    codigo_ver = models.CharField(blank=True, null=True)
    nom_dep = models.CharField(blank=True, null=True)
    nomb_mpio = models.CharField(blank=True, null=True)
    nombre_ver = models.CharField(blank=True, null=True)
    vigencia = models.CharField(blank=True, null=True)
    fuente = models.CharField(blank=True, null=True)
    descripcio = models.CharField(blank=True, null=True)
    seudonimos = models.CharField(blank=True, null=True)
    area_ha = models.FloatField(blank=True, null=True)
    cod_dpto = models.CharField(blank=True, null=True)
    observacio = models.CharField(blank=True, null=True)
    conseje = models.CharField(blank=True, null=True)
    orig_fid = models.CharField(blank=True, null=True)
    shape_leng = models.FloatField(blank=True, null=True)
    shape_area = models.FloatField(blank=True, null=True)
    layer = models.CharField(blank=True, null=True)
    path = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'veredas'


class Vias(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    wkb_geometry = models.MultiLineStringField(blank=True, null=True)
    osm_id = models.CharField(max_length=12, blank=True, null=True)
    code = models.DecimalField(max_digits=4, decimal_places=0, blank=True, null=True)
    fclass = models.CharField(max_length=28, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    ref = models.CharField(max_length=20, blank=True, null=True)
    oneway = models.CharField(max_length=1, blank=True, null=True)
    maxspeed = models.DecimalField(max_digits=3, decimal_places=0, blank=True, null=True)
    layer = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    bridge = models.CharField(max_length=1, blank=True, null=True)
    tunnel = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vias'


class Vivienda(models.Model):
    id_vivienda = models.AutoField(primary_key=True)
    material_vivienda = models.ForeignKey(MaterialVivienda, models.DO_NOTHING, db_column='material_vivienda', blank=True, null=True)
    alcantarillado = models.BooleanField(blank=True, null=True)
    acueducto = models.BooleanField(blank=True, null=True)
    corte = models.ForeignKey(Corte, models.DO_NOTHING, db_column='corte', blank=True, null=True)
    llave = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vivienda'


class ZonaGeografica(models.Model):
    id_zona_geografica = models.AutoField(primary_key=True)
    nombre_zona = models.CharField(max_length=255, blank=True, null=True)
    casos_inseguridad_alimentaria = models.IntegerField(blank=True, null=True)
    municipio = models.ForeignKey(Municipios, models.DO_NOTHING, db_column='municipio', to_field='mpio_cdpmp', blank=True, null=True)
    fex = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'zona_geografica'
