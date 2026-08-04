import json
from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.gdal import SpatialReference
from .models import Vias
from .models import Municipios
from .models import Veredas

def mapa_facatativa_page(request):
    listado_municipios = Municipios.objects.order_by('mpio_cnmbr')
    listado_veredas = Veredas.objects.order_by('nombre_ver').filter(dptompio='25269')

    contexto = {
        'municipios': listado_municipios,
        'veredas': listado_veredas,
    }
    return render(request, 'visor_grafico/mapa_facatativa.html', contexto)

def facatativa_geojson_api(request):
    """
    Vista API: Retorna el polígono de Facatativá en formato GeoJSON WGS84 (EPSG:4326).
    Código DANE de Cundinamarca = '25'
    Código DANE de Facatativá = '25269'
    """
    try:
        mpio = request.GET.get('mpio', None)
        if mpio != None:
            facatativa_qs = Municipios.objects.filter(mpio_cdpmp= mpio)
        else:
            facatativa_qs = Municipios.objects.filter(mpio_cdpmp='25269')

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
        mpio = request.GET.get('mpio', None)
        if mpio != None:
            facatativa = Municipios.objects.filter(mpio_cdpmp= mpio).first()
        else:
            facatativa = Municipios.objects.filter(mpio_cdpmp='25269').first()
        
        if not facatativa or not facatativa.geom:
            return JsonResponse({'error': 'No se encontró el municipio de Facatativá'}, status=404)

        tipo_via = request.GET.get('tipo', None)
        if tipo_via != None:
            vias_qs =Vias.objects.filter(
                fclass=tipo_via,
                wkb_geometry__intersects=facatativa.geom
                )
        else :
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


def veredas_facatativa_geojson(request):
    try:
        vda = request.GET.get('vda', None)
        if vda != None:
            veredas_qs = Veredas.objects.filter(
                dptompio='25269',
                codigo_ver=vda,
                )
        elif(vda == '0'):
            veredas_qs = Veredas.objects.filter(dptompio='25269')
        else:
            veredas_qs = Veredas.objects.filter(dptompio='25269')

        ref_origen = SpatialReference(9377)   # Origen Único de Colombia
        ref_destino = SpatialReference(4326)  # WGS84 para Leaflet

        for vereda in veredas_qs:
            if vereda.geom:
                vereda.geom.srid = ref_origen.srid

        geojson_data = serialize (
            'geojson',
            veredas_qs,
            geometry_field='geom',
            srid=ref_destino.srid,
            fields=('nom_dep','nom_mpio','nombre_ver', 'area_ha', 'cod_dpto')
        )
        return HttpResponse(geojson_data, content_type='application/json')
    except Exception as e:
        return JsonResponse({'error':str(e)}, statu=500)

