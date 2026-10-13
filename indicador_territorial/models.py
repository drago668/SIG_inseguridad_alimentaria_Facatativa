from django.db import models
from visor_grafico.models import Municipios

class ActividadUltimoMes(models.Model):
    id_actividad = models.IntegerField(primary_key=True)
    nombre_actividad = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'actividad_ultimo_mes'

    def __str__(self):
        return f"{self.id_actividad} - {self.nombre_actividad}"


class CatNivelEducativo(models.Model):
    id_nivel_educativo = models.IntegerField(primary_key=True)
    nombre_nivel = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_nivel_educativo'

    def __str__(self):
        return f"{self.id_nivel_educativo} - {self.nombre_nivel}"


class CombustibleParaCocinar(models.Model):
    id_combustible = models.IntegerField(primary_key=True)
    nombre_combustible = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'combustible_para_cocinar'

    def __str__(self):
        return f"{self.id_combustible} - {self.nombre_combustible}"


class Corte(models.Model):
    id_corte = models.IntegerField(primary_key=True)
    nombre_corte = models.CharField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'corte'

    def __str__(self):
        return self.nombre_corte or f"Corte {self.id_corte}"


class FuenteObtencionAgua(models.Model):
    id_fuente = models.IntegerField(primary_key=True)
    nombre_fuente = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'fuente_obtencion_agua'

    def __str__(self):
        return f"{self.id_fuente} - {self.nombre_fuente}"


class MaterialVivienda(models.Model):
    id_material = models.IntegerField(primary_key=True)
    nombre_material = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'material_vivienda'

    def __str__(self):
        return f"{self.id_material} - {self.nombre_material}"


class Regimen(models.Model):
    id_regimen = models.IntegerField(primary_key=True)
    nombre_regimen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'regimen'

    def __str__(self):
        return f"{self.id_regimen} - {self.nombre_regimen}"


class Sexo(models.Model):
    id_sexo = models.IntegerField(primary_key=True)
    nombre_sexo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sexo'

    def __str__(self):
        return f"{self.id_sexo} - {self.nombre_sexo}"


class TipoVivienda(models.Model):
    id_tipo_vivienda = models.IntegerField(primary_key=True)
    nombre_tipo_vivienda = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tipo_vivienda'

    def __str__(self):
        return f"{self.id_tipo_vivienda} - {self.nombre_tipo_vivienda}"


class TratamientoAguaConsumo(models.Model):
    id_tratamiento_agua = models.IntegerField(primary_key=True)
    nombre_tratamiento = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tratamiento_agua_consumo'

    def __str__(self):
        return f"{self.id_tratamiento_agua} - {self.nombre_tratamiento}"


class CatMaterialPisos(models.Model):
    """P4015: Material predominante de los pisos (7 opciones DANE).
    NOTA: MaterialVivienda se usa para paredes (P4005); los códigos DANE
    de pisos significan cosas distintas, por eso necesita tabla propia."""
    id_material_pisos = models.IntegerField(primary_key=True)
    nombre_material_pisos = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_material_pisos'

    def __str__(self):
        return f"{self.id_material_pisos} - {self.nombre_material_pisos}"


class CatCotizaPension(models.Model):
    """P6920: ¿Cotiza actualmente a pensión? (1=Sí, 2=No, 3=Ya es pensionado).
    No puede ser booleano porque tiene 3 estados."""
    id_cotiza_pension = models.IntegerField(primary_key=True)
    nombre_cotiza_pension = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_cotiza_pension'

    def __str__(self):
        return f"{self.id_cotiza_pension} - {self.nombre_cotiza_pension}"


class CatTamanoEmpresa(models.Model):
    """P8632: Personas en la empresa/negocio donde trabaja (9 rangos)"""
    id_tamano_empresa = models.IntegerField(primary_key=True)
    nombre_tamano_empresa = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_tamano_empresa'

    def __str__(self):
        return f"{self.id_tamano_empresa} - {self.nombre_tamano_empresa}"


class CatRazonNoAfiliacion(models.Model):
    """P768: Razón principal de no estar afiliado a salud (9 opciones)"""
    id_razon_no_afiliacion = models.IntegerField(primary_key=True)
    nombre_razon = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_razon_no_afiliacion'

    def __str__(self):
        return f"{self.id_razon_no_afiliacion} - {self.nombre_razon}"


class CatNivelDificultad(models.Model):
    """P1906S4-S8: Nivel de dificultad funcional (4 opciones).
    UNA sola tabla compartida por las 5 variables de discapacidad."""
    id_nivel_dificultad = models.IntegerField(primary_key=True)
    nombre_nivel_dificultad = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cat_nivel_dificultad'

    def __str__(self):
        return f"{self.id_nivel_dificultad} - {self.nombre_nivel_dificultad}"


class ZonaGeografica(models.Model):
    id_zona_geografica = models.IntegerField(primary_key=True)
    nombre_zona = models.CharField(max_length=255, blank=True, null=True)

    municipio = models.ForeignKey(
        Municipios,
        to_field='mpio_cdpmp',
        db_column='municipio', # Nombre exacto de la columna VARCHAR(5) en la BD
        on_delete=models.DO_NOTHING
    )
    

    class Meta:
        managed = True
        db_table = 'zona_geografica'

    def __str__(self):
        return f"{self.id_zona_geografica} - {self.nombre_zona}"


class HogarECV(models.Model):
    directorio = models.BigIntegerField(db_index=True)
    secuencia_p = models.IntegerField()
    corte = models.ForeignKey(Corte, on_delete=models.CASCADE)

    municipio = models.ForeignKey(
        Municipios, 
        to_field='mpio_cdpmp', 
        on_delete=models.CASCADE
    )
    clase = models.IntegerField(choices=[(1, 'Cabecera'), (2, 'Rural')])              #categorica, se puede relacionar con una tabla adicional zona geografica
    fex_c = models.FloatField(help_text="Factor de expansión")

    class Meta:
        unique_together = ('directorio', 'secuencia_p', 'corte')
        db_table = 'hogar_ecv'

    def __str__(self):
        return f"Hogar {self.directorio}-{self.secuencia_p} ({self.corte})"

class DimViviendaServicios(models.Model):
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='vivienda')

    # ── Categóricas (FK a catálogos existentes) ──
    p1070 = models.ForeignKey('TipoVivienda', on_delete=models.PROTECT,
                                db_column='p1070', null=True, blank=True, related_name='+')   # Tipo de vivienda
    p4005 = models.ForeignKey('MaterialVivienda', on_delete=models.PROTECT,
                                db_column='p4005', null=True, blank=True, related_name='+')   # Material paredes
    p4015 = models.ForeignKey('CatMaterialPisos', on_delete=models.PROTECT,
                                db_column='p4015', null=True, blank=True, related_name='+')   # Material pisos
    p8530 = models.ForeignKey('FuenteObtencionAgua', on_delete=models.PROTECT,
                                db_column='p8530', null=True, blank=True, related_name='+')   # Agua para preparar alimentos
    p5069 = models.ForeignKey('TratamientoAguaConsumo', on_delete=models.PROTECT,
                                db_column='p5069', null=True, blank=True, related_name='+')   # Agua para beber principalmente
    p8536 = models.ForeignKey('CombustibleParaCocinar', on_delete=models.PROTECT,
                                db_column='p8536', null=True, blank=True, related_name='+')   # Combustible para cocinar

    # ── Booleanas ──
    p1077S2 = models.BooleanField(null=True, blank=True)  # nevera
    p8520S3 = models.BooleanField(null=True, blank=True)  # alcantarillado
    p8520S5 = models.BooleanField(null=True, blank=True)  # acueducto
    p5047   = models.BooleanField(null=True, blank=True)  # agua 7 días 24 horas
    p1698   = models.BooleanField(null=True, blank=True)  # 🆕 otro combustible (la usa el ML)

    class Meta:
        managed = True
        db_table = 'dim_vivienda_servicios'


class DimTrabajoIngresos(models.Model):
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='trabajo')

    p6240 = models.ForeignKey('ActividadUltimoMes', on_delete=models.PROTECT,
                                db_column='p6240', null=True, blank=True, related_name='+')   # Actividad principal
    p6920 = models.ForeignKey('CatCotizaPension', on_delete=models.PROTECT,
                                db_column='p6920', null=True, blank=True, related_name='+')   # Cotiza pensión (3 estados)
    p8632 = models.ForeignKey('CatTamanoEmpresa', on_delete=models.PROTECT,
                                db_column='p8632', null=True, blank=True, related_name='+')   # Tamaño empresa (9 rangos)

    p6990 = models.BooleanField(null=True, blank=True)  # ARL (9→None)

    p8624 = models.FloatField(null=True, blank=True)    # Ingresos mes pasado
    p7250 = models.FloatField(null=True, blank=True)    # 🆕 semanas buscando trabajo (la usa el ML)
    p416  = models.FloatField(null=True, blank=True)    # horas trabajadas semana pasada

    class Meta:
        managed = True
        db_table = 'dim_trabajo_ingresos'


class DimEducacion(models.Model):
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='educacion')

    p6160 = models.BooleanField(null=True, blank=True)  # sabe leer y escribir
    p8586 = models.BooleanField(null=True, blank=True)  # actualmente estudia
    p8612 = models.BooleanField(null=True, blank=True)  # subsidio para estudiar
    p8587 = models.ForeignKey('CatNivelEducativo', on_delete=models.PROTECT, db_column='p8587', null=True, blank=True, related_name='+')   # Nivel educativo

    class Meta:
        managed = True
        db_table = 'dim_educacion'


class DimDemografia(models.Model):
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='demografia')

    cant_personas_hogar = models.IntegerField(null=True, blank=True)  # personas por hogar
    p6020 = models.ForeignKey('Sexo', on_delete=models.PROTECT, db_column='p6020', null=True, blank=True, related_name='+')   # Sexo al nacer
    p6040 = models.IntegerField(null=True, blank=True)  # edad

    class Meta:
        managed = True
        db_table = 'dim_demografia'


class DimSaludDiscapacidad(models.Model):  # 🆕 NUEVA — dimensión Salud del modelo ML
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='salud')

    p6090 = models.BooleanField(null=True, blank=True)  # afiliado a salud (9→None)
    p6100 = models.ForeignKey('Regimen', on_delete=models.PROTECT, db_column='p6100', null=True, blank=True, related_name='+')   # Régimen de salud
    p768  = models.ForeignKey('CatRazonNoAfiliacion', on_delete=models.PROTECT, db_column='p768', null=True, blank=True, related_name='+')    # Razón no afiliación

    # Las 5 dificultades funcionales apuntan al MISMO catálogo
    p1906S4 = models.ForeignKey('CatNivelDificultad', on_delete=models.PROTECT, db_column='p1906s4', null=True, blank=True, related_name='+')  # mover el cuerpo
    p1906S5 = models.ForeignKey('CatNivelDificultad', on_delete=models.PROTECT, db_column='p1906s5', null=True, blank=True, related_name='+')  # agarrar objetos
    p1906S6 = models.ForeignKey('CatNivelDificultad', on_delete=models.PROTECT, db_column='p1906s6', null=True, blank=True, related_name='+')  # entender/decidir
    p1906S7 = models.ForeignKey('CatNivelDificultad', on_delete=models.PROTECT, db_column='p1906s7', null=True, blank=True, related_name='+')  # comer/vestirse
    p1906S8 = models.ForeignKey('CatNivelDificultad', on_delete=models.PROTECT, db_column='p1906s8', null=True, blank=True, related_name='+')  # relacionarse

    class Meta:
        managed = True
        db_table = 'dim_salud_discapacidad'


class DimDesastres(models.Model):
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='desastres')

    # Eventos climáticos que afectaron al hogar (últimos 12 meses)
    p3173   = models.BooleanField(null=True, blank=True)  # sufrió eventos climáticos
    p3174S1 = models.BooleanField(null=True, blank=True)  # disponibilidad de agua
    p3174S2 = models.BooleanField(null=True, blank=True)  # enfermedades tropicales
    p3174S3 = models.BooleanField(null=True, blank=True)  # enfermedades respiratorias
    p3174S4 = models.BooleanField(null=True, blank=True)  # pérdida de cultivos o animales
    p3174S5 = models.BooleanField(null=True, blank=True)  # calidad de suelos o erosión

    # Afectaciones a la vivienda (últimos 12 meses)
    p4065S1 = models.BooleanField(null=True, blank=True)  # inundaciones, crecientes
    p4065S2 = models.BooleanField(null=True, blank=True)  # avalanchas, derrumbes
    p4065S3 = models.BooleanField(null=True, blank=True)  # hundimiento del terreno
    p4065S4 = models.BooleanField(null=True, blank=True)  # ventarrones, tormentas, granizada
    p4065S5 = models.BooleanField(null=True, blank=True)  # sismo o temblor

    class Meta:
        managed = True
        db_table = 'dim_desastres'


class DimFIES(models.Model):
    hogar = models.OneToOneField(HogarECV, on_delete=models.CASCADE, related_name='fies')

    # 8 preguntas FIES (en el ABT ya vienen como 1/0)
    p3516s1 = models.BooleanField(null=True, blank=True)
    p3516s2 = models.BooleanField(null=True, blank=True)
    p3516s3 = models.BooleanField(null=True, blank=True)
    p3516s4 = models.BooleanField(null=True, blank=True)
    p3516s5 = models.BooleanField(null=True, blank=True)
    p3516s6 = models.BooleanField(null=True, blank=True)
    p3516s7 = models.BooleanField(null=True, blank=True)
    p3516s8 = models.BooleanField(null=True, blank=True)

    # Resultado REAL
    puntaje_fies = models.IntegerField(null=True, blank=True)  # puntaje 0-8
    inseguridad_mod_grave = models.BooleanField(default=False)  # real: mod o grave

    # 🆕 Resultado del MODELO ML (contraste real vs predicho a nivel hogar)
    prob_riesgo_modelo = models.FloatField(null=True, blank=True)   # probabilidad XGBoost
    predicho_mod_grave = models.BooleanField(null=True, blank=True) # predicción del modelo
    prob_calibrada = models.FloatField(null=True, blank=True,
                                        verbose_name='Probabilidad calibrada (Platt)')

    class Meta:
        managed = True
        db_table = 'dim_fies'