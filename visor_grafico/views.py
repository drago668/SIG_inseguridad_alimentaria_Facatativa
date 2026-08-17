import json
from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.gdal import SpatialReference
from django.db.models import Avg, Sum, Count, Case, When, Value, IntegerField,FloatField, F
from .models import Vias
from .models import Municipios
from .models import Veredas

def mapa_facatativa_page(request):
    listado_municipios = Municipios.objects.order_by('mpio_cnmbr')
    listado_veredas = Veredas.objects.order_by('nombre_ver').filter(dptompio='25269').values('codigo_ver','nombre_ver')

    contexto = {
        'municipios': listado_municipios,
        'veredas': listado_veredas,
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


def geojson_inseguridad_y_mapa(request):
    """
    API Unificada: Construye el GeoJSON en EPSG:4326 uniendo las veredas 
    e infiriendo el casco urbano mediante diferencia espacial, inyectando 
    los promedios de inseguridad alimentaria del Sisbén IV.
    """
    try:
        # 1. Recuperamos y calculamos el índice multidimensional del Sisbén IV
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

        # Agrupamos por el texto de la zona geográfica para separar urbana de rural
        datos_zonas = hogares_calculados.values('zona_geografica__nombre_zona').annotate(
            promedio_indice=Avg('indice_inseguridad'),
            total_hogares=Count('id'),
            promedio_ninos=Avg('cantidad_ninos'),
            tasa_informalidad=Avg(Case(When(jefe_hogar__trabajo_informal=1, then=Value(100.0)), default=Value(0.0), output_field=FloatField()))
        )

        m_urbano = next((z for z in datos_zonas if z['zona_geografica__nombre_zona'] == 'Cabecera'), None)
        m_rural = next((z for z in datos_zonas if z['zona_geografica__nombre_zona'] == 'Centro poblado, Rural disperso'), None)

        # 2. Configuración de Sistemas de Referencia Espacial (SRID)
        ref_origen = SpatialReference(9377)   # Origen Único de Colombia de tu BD [4.14]
        ref_destino = SpatialReference(4326)  # WGS84 para Leaflet [4.14]

        # 3. Procesamiento de Veredas (Zona Rural)
        veredas_qs = Veredas.objects.filter(dptompio='25269') # Facatativá fijo [4.14]
        features = []
        geometrias_veredas = []

        for vda in veredas_qs:
            if vda.geom:
                vda.geom.srid = ref_origen.srid  # Forzamos reconocimiento de proyección nativa [4.14]
                geometrias_veredas.append(vda.geom)
                
                # Transformamos la geometría en caliente a WGS84 para pasarla a Javascript
                geom_copia = vda.geom.clone()
                geom_copia.transform(ref_destino.srid)
                geometria_dict = json.loads(geom_copia.geojson)

                features.append({
                    "type": "Feature",
                    "id": f"rural_{vda.codigo_ver}",
                    "geometry": geometria_dict,
                    "properties": {
                        "nombre_zona": vda.nombre_ver or "Zona Rural",
                        "tipo_zona": "Rural",
                        "promedio_indice": round(m_rural['promedio_indice'] or 0, 1) if m_rural else 0.0,
                        "total_hogares": m_rural['total_hogares'] if m_rural else 0,
                        "promedio_ninos": round(m_rural['promedio_ninos'] or 0, 1) if m_rural else 0.0,
                        "tasa_informalidad": round(m_rural['tasa_informalidad'] or 0, 1) if m_rural else 0.0
                    }
                })

        # 4. Procesamiento de Cabecera Urbana por Diferencia Espacial (Municipio - Veredas)
        municipio_obj = Municipios.objects.filter(mpio_cdpmp='25269').first() # Facatativá [4.14]
        
        if municipio_obj and municipio_obj.geom and geometrias_veredas:
            municipio_obj.geom.srid = ref_origen.srid
            
            # Unimos todas las veredas en un solo polígono regional sólido en 9377
            union_rural = geometrias_veredas[0]
            for g in geometrias_veredas[1:]:
                union_rural = union_rural.union(g)
            
            # Restamos el bloque rural al municipio general para aislar el "hueco" del centro urbano
            geometria_urbana = municipio_obj.geom.difference(union_rural)
            
            if geometria_urbana:
                # Transformamos el polígono resultante a WGS84 para Leaflet
                geometria_urbana.transform(ref_destino.srid)
                
                features.append({
                    "type": "Feature",
                    "id": "urbano_cabecera",
                    "geometry": json.loads(geometria_urbana.geojson),
                    "properties": {
                        "nombre_zona": "Cabecera Urbana (Facatativá Centro)",
                        "tipo_zona": "Urbana",
                        "promedio_indice": round(m_urbano['promedio_indice'] or 0, 1) if m_urbano else 0.0,
                        "total_hogares": m_urbano['total_hogares'] if m_urbano else 0,
                        "promedio_ninos": round(m_urbano['promedio_ninos'] or 0, 1) if m_urbano else 0.0,
                        "tasa_informalidad": round(m_urbano['tasa_informalidad'] or 0, 1) if m_urbano else 0.0
                    }
                })

        geojson_final = {
            "type": "FeatureCollection",
            "features": features
        }

        return JsonResponse(geojson_final, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
