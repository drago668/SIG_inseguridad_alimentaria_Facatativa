# app_capas/services.py
import os
import zipfile
import tempfile
from django.contrib.gis.gdal import DataSource, GDALException
from django.contrib.gis.geos import GEOSGeometry
from .models import CapaEspacial, ElementoVectorial

def procesar_capa_vectorial(capa_id):
    """
    Lee cualquier archivo vectorial soportado por GDAL/OGR (SHP zip, GeoJSON, GPKG, KML, GPX, GML)
    y llena la tabla ElementoVectorial en PostGIS.
    """
    capa = CapaEspacial.objects.get(id=capa_id)
    ruta_archivo = capa.archivo.path
    temp_dir = None

    try:
        # Manejo de Shapefiles comprimidos en .ZIP
        if capa.formato == 'SHP' and ruta_archivo.endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Buscar el archivo .shp extraído
            shp_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No se encontró ningún archivo .shp dentro del ZIP.")
            target_path = shp_files[0]
        else:
            target_path = ruta_archivo

        # Abrir con GDAL / OGR
        ds = DataSource(target_path)
        layer = ds[0]

        elementos_a_crear = []
        
        for feature in layer:
            geom_gdal = feature.geom
            # Convertir a GEOSGeometry y asegurar reproyección a WGS84 (EPSG:4326) para Leaflet
            geos_geom = GEOSGeometry(geom_gdal.wkt, srid=layer.srs.srid if layer.srs else 4326)
            if geos_geom.srid != 4326:
                geos_geom.transform(4326)

            # Extraer tabla de atributos
            atributos = {field: feature.get(field) for field in layer.fields}

            elementos_a_crear.append(
                ElementoVectorial(
                    capa=capa,
                    geometria=geos_geom,
                    atributos=atributos
                )
            )

        # Inserción masiva en PostGIS
        ElementoVectorial.objects.bulk_create(elementos_a_crear)

        # Actualizar metadatos de la capa
        capa.num_registros = len(elementos_a_crear)
        capa.procesado_exitoso = True
        capa.srid_origen = layer.srs.srid if layer.srs else 4326
        capa.save()

    except Exception as e:
        capa.procesado_exitoso = False
        capa.mensaje_error = str(e)
        capa.save()
        raise e