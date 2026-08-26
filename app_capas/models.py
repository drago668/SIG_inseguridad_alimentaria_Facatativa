from django.contrib.gis.db import models
import os

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
        
    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico almacenado en disco antes de borrar el registro
        if self.archivo and os.path.isfile(self.archivo.path):
            os.remove(self.archivo.path)
        super().delete(*args, **kwargs)

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
    geometria = models.GeometryField(srid=4326, verbose_name="Geometría PostGIS")
    atributos = models.JSONField(default=dict, blank=True, verbose_name="Atributos de la Entidad (Tabla de Atributos)")

    class Meta:
        indexes = [
            models.Index(fields=['capa']),
        ]
