# app_capas/services.py
import os
import zipfile
import tempfile
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from .models import CapaEspacial, ElementoVectorial

def procesar_capa_vectorial(capa_id):
    capa = CapaEspacial.objects.get(id=capa_id)
    ruta_archivo = capa.archivo.path
    temp_dir = None

    try:
        # Manejo de Shapefiles comprimidos en .ZIP
        if capa.formato == 'SHP' and ruta_archivo.endswith('.zip'):
            temp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Búsqueda recursiva del archivo .shp en todas las subcarpetas
            shp_path = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.lower().endswith('.shp'):
                        shp_path = os.path.join(root, file)
                        break
                if shp_path:
                    break

            if not shp_path:
                raise Exception("No se encontró ningún archivo .shp válido dentro del ZIP o sus subcarpetas.")
            
            target_path = shp_path
        else:
            target_path = ruta_archivo

        # Abrir dataset vectorial con GDAL / OGR
        ds = DataSource(target_path)
        layer = ds[0]

        elementos_a_crear = []
        srid_origen = layer.srs.srid if (layer.srs and layer.srs.srid) else 4326
        
        for feature in layer:
            geom_gdal = feature.geom
            # Transformación de coordenadas a EPSG:4326 para Leaflet
            geos_geom = GEOSGeometry(geom_gdal.wkt, srid=srid_origen)
            if geos_geom.srid != 4326:
                geos_geom.transform(4326)

            # Construir diccionario de atributos
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

        # Actualizar estado de éxito en el modelo
        capa.num_registros = len(elementos_a_crear)
        capa.procesado_exitoso = True
        capa.srid_origen = srid_origen
        capa.mensaje_error = None
        capa.save()

    except Exception as e:
        capa.procesado_exitoso = False
        capa.mensaje_error = str(e)
        capa.save()
        raise e