from django.db import models
from visor_grafico.models import Municipios

# Create your models here.
class ActividadUltimoMes(models.Model):
    id_actividad = models.IntegerField(primary_key=True)
    nombre_actividad = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'actividad_ultimo_mes'


class AfiliacionSeguridadSocial(models.Model):
    id_afiliacion = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    regimen = models.ForeignKey('Regimen', models.DO_NOTHING, db_column='regimen', blank=True, null=True)
    eps = models.ForeignKey('Eps', models.DO_NOTHING, db_column='eps', blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)
    sexo = models.ForeignKey('Sexo', models.DO_NOTHING, db_column='sexo', blank=True, null=True)
    curso_vida = models.ForeignKey('CursoVida', models.DO_NOTHING, db_column='curso_vida', blank=True, null=True)

    municipio = models.ForeignKey(
        Municipios,
        to_field='mpio_cdpmp',
        db_column='municipio', # Nombre exact
        on_delete=models.PROTECT
    )

    class Meta:
        managed = True
        db_table = 'afiliacion_seguridad_social'


class BajoPesoNacer(models.Model):
    id_registro_peso = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    etapa_vida_madre = models.ForeignKey('EtapaVidaMadre', models.DO_NOTHING, db_column='etapa_vida_madre', blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)

    municipio = models.ForeignKey(
        Municipios,
        to_field='mpio_cdpmp',
        db_column='municipio', # Nombre exact
        on_delete=models.PROTECT
    )

    class Meta:
        managed = True
        db_table = 'bajo_peso_nacer'


class BajoPesoRegimen(models.Model):
    id_bajo_peso_regimen = models.IntegerField(primary_key=True)
    numero_afectados = models.IntegerField(blank=True, null=True)
    regimen = models.ForeignKey('Regimen', models.DO_NOTHING, db_column='regimen', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'bajo_peso_regimen'


class CatNivelEducativo(models.Model):
    id_nivel_educativo = models.IntegerField(primary_key=True)
    nombre_nivel = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_nivel_educativo'


class CombustibleParaCocinar(models.Model):
    id_combustible = models.IntegerField(primary_key=True)
    nombre_combustible = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'combustible_para_cocinar'


class Corte(models.Model):
    id_corte = models.IntegerField(primary_key=True)
    nombre_corte = models.CharField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'corte'


class CursoVida(models.Model):
    id_curso_vida = models.IntegerField(primary_key=True)
    nombre_curso = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'curso_vida'


class DesnutricionAguda(models.Model):
    id_registro = models.IntegerField(primary_key=True)
    edad = models.IntegerField(blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)

    municipio = models.ForeignKey(
        Municipios,
        to_field='mpio_cdpmp',
        db_column='municipio', # Nombre exact
        on_delete=models.PROTECT
    )

    class Meta:
        managed = True
        db_table = 'desnutricion_aguda'


class Eps(models.Model):
    id_eps = models.IntegerField(primary_key=True)
    nombre_eps = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'eps'


class EtapaVidaMadre(models.Model):
    id_etapa = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    curso_vida = models.ForeignKey(CursoVida, models.DO_NOTHING, db_column='curso_vida', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'etapa_vida_madre'


class FuenteObtencionAgua(models.Model):
    id_fuente = models.IntegerField(primary_key=True)
    nombre_fuente = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'fuente_obtencion_agua'


class Hogar(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_hogar')
    agua_llega_7_dias = models.BooleanField(blank=True, null=True)
    cocina = models.BooleanField(blank=True, null=True)
    nevera = models.BooleanField(blank=True, null=True)
    jefe_hogar = models.ForeignKey('JefeHogar', models.DO_NOTHING, db_column='jefe_hogar', blank=True, null=True, related_name='hogares_asociados' )
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
    cantidad_ninos = models.IntegerField(blank=True, null=True)
    cantidad_adultos_mayores = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'hogar'


class JefeHogar(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_jefe_hogar')
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
        managed = True
        db_table = 'jefe_hogar'


class MaterialVivienda(models.Model):
    id_material = models.IntegerField(primary_key=True)
    nombre_material = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'material_vivienda'


class MortalidadDesnutricion(models.Model):
    id_mortalidad = models.IntegerField(primary_key=True)
    anio = models.IntegerField(blank=True, null=True)
    nacionalidad = models.ForeignKey('Nacionalidad', models.DO_NOTHING, db_column='nacionalidad', blank=True, null=True)

    municipio = models.ForeignKey(
        Municipios,
        to_field='mpio_cdpmp',
        db_column='municipio', # Nombre exact
        on_delete=models.PROTECT
    )

    class Meta:
        managed = True
        db_table = 'mortalidad_desnutricion'


class MortalidadInfantilPorEdad(models.Model):
    id_mortalidad_edad = models.IntegerField(primary_key=True)
    edad = models.IntegerField(blank=True, null=True)
    defunciones = models.IntegerField(blank=True, null=True)
    mortalidad = models.ForeignKey(MortalidadDesnutricion, models.DO_NOTHING, db_column='mortalidad', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mortalidad_infantil_por_edad'


class Nacionalidad(models.Model):
    id_nacionalidad = models.IntegerField(primary_key=True)
    pais_origen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'nacionalidad'


class ProgramaSocial(models.Model):
    id_programa_social = models.IntegerField(primary_key=True)
    nombre_programa = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'programa_social'


class ProgramaSocialZonaGeografica(models.Model):
    pk = models.CompositePrimaryKey('id_zona', 'id_programa')
    id_zona = models.ForeignKey('ZonaGeografica', models.DO_NOTHING, db_column='id_zona')
    id_programa = models.ForeignKey(ProgramaSocial, models.DO_NOTHING, db_column='id_programa')

    class Meta:
        managed = True
        db_table = 'programa_social_zona_geografica'


class Regimen(models.Model):
    id_regimen = models.IntegerField(primary_key=True)
    nombre_regimen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'regimen'


class Sexo(models.Model):
    id_sexo = models.IntegerField(primary_key=True)
    nombre_sexo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sexo'


class TipoVivienda(models.Model):
    id_tipo_vivienda = models.IntegerField(primary_key=True)
    nombre_tipo_vivienda = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tipo_vivienda'


class TratamientoAguaConsumo(models.Model):
    id_tratamiento_agua = models.IntegerField(primary_key=True)
    nombre_tratamiento = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tratamiento_agua_consumo'


class Vivienda(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_vivienda')
    material_vivienda = models.ForeignKey(MaterialVivienda, models.DO_NOTHING, db_column='material_vivienda', blank=True, null=True)
    alcantarillado = models.BooleanField(blank=True, null=True)
    acueducto = models.BooleanField(blank=True, null=True)
    corte = models.ForeignKey(Corte, models.DO_NOTHING, db_column='corte', blank=True, null=True)
    llave = models.CharField(blank=True, null=True, db_column='llave')

    class Meta:
        managed = True
        db_table = 'vivienda'


class ZonaGeografica(models.Model):
    id_zona_geografica = models.IntegerField(primary_key=True)
    nombre_zona = models.CharField(max_length=255, blank=True, null=True)
    casos_inseguridad_alimentaria = models.IntegerField(blank=True, null=True)
    fex = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)

    municipio = models.ForeignKey(
        Municipios,
        to_field='mpio_cdpmp',
        db_column='municipio', # Nombre exacto de la columna VARCHAR(5) en la BD
        on_delete=models.DO_NOTHING
    )
    

    class Meta:
        managed = True
        db_table = 'zona_geografica'