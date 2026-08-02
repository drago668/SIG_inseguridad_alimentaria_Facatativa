import json
from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.gdal import SpatialReference
from .models import Vias

# Importa tu modelo de Municipios (ajusta la importación según tu app)
from .models import Municipios


def mapa_facatativa_page(request):
    """
    Vista HTML: Renderiza la plantilla del mapa en el navegador.
    """
    return render(request, 'visor_grafico/mapa_facatativa.html')


def facatativa_geojson_api(request):
    """
    Vista API: Retorna el polígono de Facatativá en formato GeoJSON WGS84 (EPSG:4326).
    Código DANE de Cundinamarca = '25'
    Código DANE de Facatativá = '25269'
    """
    try:
        # Reproyectamos la geometría usando Transform dentro de annotate
        facatativa_qs = Municipios.objects.filter(mpio_cdpmp='25269')
        # facatativa_qs = Municipios.objects.all()
        ref_origen = SpatialReference(9377)   # Origen Único de Colombia
        ref_destino = SpatialReference(4326)  # WGS84 para Leaflet

        # Forzamos temporalmente a las geometrías del queryset a reconocer que su SRID real es 9377
        for municipio in facatativa_qs:
            if municipio.geom:
                municipio.geom.srid = ref_origen.srid
        
        geojson_data = serialize(
            'geojson',
            facatativa_qs,
            geometry_field='geom',
            srid=ref_destino.srid,   
            fields=('mpio_cdpmp', 'mpio_cnmbr','dpto_ccdgo')
        )

        return HttpResponse(geojson_data, content_type='application/json')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def vias_facatativa_geojson(request):
    try:
        facatativa = Municipios.objects.filter(mpio_cdpmp='25269').first()
        
        if not facatativa or not facatativa.geom:
            return JsonResponse({'error': 'No se encontró el municipio de Facatativá'}, status=404)

        vias_qs= Vias.objects.filter(wkb_geometry__intersects=facatativa.geom)

        geojson_data = serialize(
            'geojson',
            vias_qs,    
            geometry_field='wkb_geometry',
            srid= 4326,
            fields=('name', 'fclass', 'maxspeed', 'oneway', 'ref')
        )
        return HttpResponse(geojson_data, content_type='application/json')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)