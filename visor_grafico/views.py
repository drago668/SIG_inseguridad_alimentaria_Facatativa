import json
from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.geos import Polygon, MultiPolygon
from django.db.models import Avg, Sum, Count, Case, When, Value, IntegerField,FloatField, F
from .models import Vias
from .models import Municipios
from .models import Veredas
from .models import ZonaUrbana
from indicador_territorial.models import Hogar,Corte
from app_capas.forms import CapaEspacialForm
def mapa_facatativa_page(request):
    es_entidad_o_admin = request.user.is_authenticated and request.user.rol in [
        'ADMIN', 'ENTIDAD'
    ]
    cortes = Corte.objects.order_by('id_corte')
    nombre_user = f"{request.user.first_name} {request.user.last_name}" if request.user.is_authenticated else None
    administrador = request.user.is_authenticated and request.user.rol in ['ADMIN']
    form = CapaEspacialForm()
    es_autenticado =request.user.is_authenticated
    listado_municipios = Municipios.objects.order_by('mpio_cnmbr')
    listado_veredas = Veredas.objects.order_by('nombre_ver').filter(dptompio='25269').values('codigo_ver','nombre_ver')

    contexto = {
        'form':form,
        'cortes': cortes,
        'municipios': listado_municipios,
        'veredas': listado_veredas,
        'administracion': es_entidad_o_admin,
        'autenticado': es_autenticado,
        'es_administrador': administrador,
        'nombre_user':nombre_user,
    }
    return render(request, 'visor_grafico/mapa_facatativa.html', contexto)


def obtener_veredas_por_municipio(request):
    mpio = request.GET.get("mpio", None)
    veredas = Veredas.objects.order_by('nombre_ver').filter(dptompio= mpio).values('codigo_ver','nombre_ver')
    return JsonResponse(list(veredas), safe=False)


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

        mpio = request.GET.get('mpio', None)
        if mpio != None:
            municipio = Municipios.objects.filter(mpio_cdpmp= mpio).first()
        else:
            municipio = Municipios.objects.filter(mpio_cdpmp='25269').first()
        
        if not municipio or not municipio.geom:
            return JsonResponse({'error': 'No se encontró el municipio'}, status=404)
    
        vda = request.GET.get('vda', None)
        if vda != None:
            veredas_qs = Veredas.objects.filter(
                codigo_ver=vda,
                dptompio=municipio.mpio_cdpmp
                )
        elif(vda == '0'):
            veredas_qs = Veredas.objects.filter(dptompio=municipio.mpio_cdpmp)
        else:
            veredas_qs = Veredas.objects.filter(dptompio=municipio.mpio_cdpmp)

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


def _obtener_estadisticas_inseguridad():

    hogares = Hogar.objects.select_related('vivienda', 'jefe_hogar')
    hogares_calculados = hogares.annotate(
        w_nevera=Case(When(nevera=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
        w_cocina=Case(When(cocina=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
        w_acueducto=Case(When(vivienda__acueducto=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_alcantarillado=Case(When(vivienda__alcantarillado=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_agua_7_dias=Case(When(agua_llega_7_dias=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_combustible=Case(When(combustible_para_cocinar__id_combustible__gte=6, then=Value(33.34)), default=Value(0), output_field=FloatField()),
    ).annotate(
        indice_inseguridad=F('w_nevera') + F('w_cocina') + F('w_acueducto') + F('w_alcantarillado') + F('w_agua_7_dias') + F('w_combustible')
    )

    datos_zonas = hogares_calculados.values('zona_geografica__nombre_zona').annotate(
        promedio_indice=Avg('indice_inseguridad'),
        total_hogares=Sum('zona_geografica__fex'),
        promedio_ninos=Avg('cantidad_ninos'),
        tasa_informalidad=Avg(Case(When(jefe_hogar__trabajo_informal=1, then=Value(100.0)), default=Value(0.0), output_field=FloatField()))
    )

    m_urbano = next((z for z in datos_zonas if z['zona_geografica__nombre_zona'] == 'Cabecera'), None)
    m_rural = next((z for z in datos_zonas if z['zona_geografica__nombre_zona'] == 'Centro poblado, Rural disperso'), None)

    return m_urbano,m_rural


def _construir_geojson(queryset, estadisticas, tipo_zona_nombre, prefijo_id):
    ref_origen = SpatialReference(9377)   # Origen Único de Colombia
    ref_destino = SpatialReference(4326)  # WGS84 para Leaflet
    features = []

    for zona in queryset:
        if zona.geom:
            zona.geom.srid = ref_origen.srid
            geom_copia = zona.geom.clone()
            geom_copia.transform(ref_destino.srid)
            
            features.append({
                "type": "Feature",
                "id": f"{prefijo_id}_{zona.zu_ccnct}",
                "geometry": json.loads(geom_copia.geojson),
                "properties": {
                    "nombre_zona": zona.zu_cnmbre,
                    "tipo_zona": tipo_zona_nombre,
                    "promedio_indice": round(estadisticas['promedio_indice'] or 0, 1) if estadisticas else 0.0,
                    "total_hogares": round(estadisticas['total_hogares']) if estadisticas else 0,
                    "promedio_ninos": round(estadisticas['promedio_ninos'] or 0, 1) if estadisticas else 0.0,
                    "tasa_informalidad": round(estadisticas['tasa_informalidad'] or 0, 1) if estadisticas else 0.0
                }
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def geojson_inseguridad_rural(request):
    try:
        _, m_rural = _obtener_estadisticas_inseguridad()
        veredas_qs = ZonaUrbana.objects.filter(mpio_cdpmp='25269').exclude(zu_cnmbre='FACATATIVÁ')
        
        geojson_final = _construir_geojson(veredas_qs, m_rural, "Rural", "rural")
        return JsonResponse(geojson_final, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def geojson_inseguridad_urbana(request):
    try:
        m_urbano, _ = _obtener_estadisticas_inseguridad()
        zona_urbana_qs = ZonaUrbana.objects.filter(mpio_cdpmp='25269', zu_cnmbre='FACATATIVÁ')
        
        geojson_final = _construir_geojson(zona_urbana_qs, m_urbano, "Cabecera urbana", "urbano")
        return JsonResponse(geojson_final, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
