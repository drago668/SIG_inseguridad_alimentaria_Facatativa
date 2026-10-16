from django.contrib import admin

from django.contrib import admin
from .models import (
    # Catálogos
    TipoVivienda, MaterialVivienda, CatMaterialPisos, FuenteObtencionAgua,
    TratamientoAguaConsumo, CombustibleParaCocinar, CatNivelEducativo,
    ActividadUltimoMes, CatCotizaPension, CatTamanoEmpresa, Sexo, Regimen,
    CatRazonNoAfiliacion, CatNivelDificultad,
    # Hechos
    Corte, ZonaGeografica, HogarECV,
    # Dimensiones
    DimViviendaServicios, DimTrabajoIngresos, DimEducacion, DimDemografia,
    DimSaludDiscapacidad, DimDesastres, DimFIES,
)


def _registrar_catalogo(modelo, campo_nombre):
    @admin.register(modelo)
    class CatalogoAdmin(admin.ModelAdmin):
        list_display = ('pk', campo_nombre)
        search_fields = ('pk', campo_nombre)
        ordering = ('pk',)
    return CatalogoAdmin


_registrar_catalogo(TipoVivienda, 'nombre_tipo_vivienda')
_registrar_catalogo(MaterialVivienda, 'nombre_material')
_registrar_catalogo(CatMaterialPisos, 'nombre_material_pisos')
_registrar_catalogo(FuenteObtencionAgua, 'nombre_fuente')
_registrar_catalogo(TratamientoAguaConsumo, 'nombre_tratamiento')
_registrar_catalogo(CombustibleParaCocinar, 'nombre_combustible')
_registrar_catalogo(CatNivelEducativo, 'nombre_nivel')
_registrar_catalogo(ActividadUltimoMes, 'nombre_actividad')
_registrar_catalogo(CatCotizaPension, 'nombre_cotiza_pension')
_registrar_catalogo(CatTamanoEmpresa, 'nombre_tamano_empresa')
_registrar_catalogo(Sexo, 'nombre_sexo')
_registrar_catalogo(Regimen, 'nombre_regimen')
_registrar_catalogo(CatRazonNoAfiliacion, 'nombre_razon')
_registrar_catalogo(CatNivelDificultad, 'nombre_nivel_dificultad')



@admin.register(Corte)
class CorteAdmin(admin.ModelAdmin):
    list_display = ('id_corte', 'nombre_corte')
    ordering = ('id_corte',)


@admin.register(ZonaGeografica)
class ZonaGeograficaAdmin(admin.ModelAdmin):
    list_display = ('id_zona_geografica', 'nombre_zona', 'municipio')
    search_fields = ('nombre_zona', 'municipio__mpio_cnmbr')
    list_filter = ('municipio',)


class _InlineBase(admin.StackedInline):
    extra = 0
    can_delete = False
    classes = ('collapse',)  

class DimViviendaInline(_InlineBase):
    model = DimViviendaServicios
    verbose_name_plural = '🏠 Vivienda y Servicios'

class DimTrabajoInline(_InlineBase):
    model = DimTrabajoIngresos
    verbose_name_plural = '💼 Trabajo e Ingresos'

class DimEducacionInline(_InlineBase):
    model = DimEducacion
    verbose_name_plural = '📚 Educación'

class DimDemografiaInline(_InlineBase):
    model = DimDemografia
    verbose_name_plural = '👨‍👩‍👧 Demografía'

class DimSaludInline(_InlineBase):
    model = DimSaludDiscapacidad
    verbose_name_plural = '🏥 Salud y Discapacidad'

class DimDesastresInline(_InlineBase):
    model = DimDesastres
    verbose_name_plural = '🌊 Desastres'

class DimFIESInline(_InlineBase):
    model = DimFIES
    verbose_name_plural = '🍽️ FIES (real y modelo)'


@admin.register(HogarECV)
class HogarECVAdmin(admin.ModelAdmin):
    list_display = ('directorio', 'secuencia_p', 'corte', 'municipio', 'clase', 'fex_c')
    list_filter = ('corte', 'clase')
    search_fields = ('=directorio', 'municipio__mpio_cdpmp', 'municipio__mpio_cnmbr')
    ordering = ('corte', 'directorio')
    inlines = [
        DimViviendaInline, DimTrabajoInline, DimEducacionInline,
        DimDemografiaInline, DimSaludInline, DimDesastresInline, DimFIESInline,
    ]