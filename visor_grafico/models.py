from django.contrib.gis.db import models
import os
"""
class CapaEspacial(models.Model):
    TIPO_FORMATO = [
        ('SHP', 'Shapefile (.zip)'),
        ('GPKG', 'GeoPackage (.gpkg)'),
        ('GEOJSON', 'GeoJSON / JSON'),
        ('KML', 'KML / KMZ'),
        ('GPX', 'GPX'),
        ('GML', 'GML'),
        ('GEOTIFF', 'GeoTIFF (.tif / .tiff)'),
        ('WFS', 'Servicio WFS (URL)'),
    ]

    TIPO_GEOMETRIA = [
        ('POINT', 'Punto / MultiPunto'),
        ('LINESTRING', 'Línea / MultiLínea'),
        ('POLYGON', 'Polígono / MultiPolígono'),
        ('RASTER', 'Ráster / Malla'),
        ('UNKNOWN', 'Desconocido / WFS'),
    ]

    nombre = models.CharField(max_length=150, verbose_name="Nombre de la Capa")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    formato = models.CharField(max_length=10, choices=TIPO_FORMATO, verbose_name="Formato de Origen")
    tipo_geometria = models.CharField(max_length=15, choices=TIPO_GEOMETRIA, default='UNKNOWN')
    
    # Campo para archivos físicos (Zip de SHP, GPKG, GeoJSON, TIFF, etc.)
    archivo = models.FileField(upload_to='capas_espaciales/', blank=True, null=True, verbose_name="Archivo Espacial")
    
    # Campo para enlaces WFS externos
    url_wfs = models.URLField(blank=True, null=True, verbose_name="URL del Servicio WFS")
    capa_wfs_layer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre de la capa WFS")

    # Metadatos del Procesamiento
    srid_origen = models.IntegerField(default=4326, verbose_name="SRID / EPSG Origen")
    num_registros = models.IntegerField(default=0, verbose_name="Número de Objetos/Pixeles")
    procesado_exitoso = models.BooleanField(default=False)
    mensaje_error = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Capa Espacial"
        verbose_name_plural = "Capas Espaciales"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} ({self.get_formato_display()})"


class ElementoVectorial(models.Model):

    #Tabla genérica PostGIS para almacenar las geometrías vectoriales parseadas 
    # de cualquier formato (SHP, GPKG, GeoJSON, KML, GPX, GML) normalizadas a SRID 4326.

    capa = models.ForeignKey(CapaEspacial, on_delete=models.CASCADE, related_name='elementos')
    geometria = models.GeometryField(srs=4326, verbose_name="Geometría PostGIS")
    atributos = models.JSONField(default=dict, blank=True, verbose_name="Atributos de la Entidad (Tabla de Atributos)")

    class Meta:
        indexes = [
            models.Index(fields=['capa']),
        ]
"""
# visor espacial
class Departamentos(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    dpto_ccdgo = models.CharField(max_length=5, unique=True, verbose_name="Código DANE Depto")  # Código DIVIPOLA (ej. '25')
    dpto_cnmbr = models.CharField(max_length=250, blank=True, null=True, verbose_name="Nombre Depto") # Nombre (ej. 'CUNDINAMARCA')
    geom = models.MultiPolygonField(srid=9377, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'departamentos'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return f"{self.dpto_ccdgo} - {self.dpto_cnmbr}"

class Municipios(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    mpio_cdpmp = models.CharField(max_length=5, unique=True, verbose_name="Código DANE Municipio") # Ej: '05001
    mpio_cnmbr = models.CharField(max_length=250, blank=True, null=True, verbose_name="Nombre Municipio")

    # Relación con la tabla Departamentos mediante el código DANE (2 dígitos)
    dpto_ccdgo = models.ForeignKey(
        Departamentos,
        to_field='dpto_ccdgo',
        db_column='dpto_ccdgo',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    
    # MultiPolygonField para soportar municipios con múltiples polígonos/islas
    geom = models.MultiPolygonField(srid=9377, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'municipios'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'

    def __str__(self):
        return f"{self.mpio_cdpmp} - {self.mpio_cnmbr}"

class Vias(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    wkb_geometry = models.MultiLineStringField(srid=4326, blank=True, null=True)
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
        db_table='public"."vias'

        def __str__(self):
            return f"{self.name}"


class Veredas(models.Model):
    ogc_fid = models.AutoField(primary_key=True)
    geom = models.MultiPolygonField(srid=900914, blank=True, null=True)
    fid = models.FloatField(blank=True, null=True)
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

    class Meta:
        managed = False
        db_table = 'veredas'