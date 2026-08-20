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
from indicador_territorial.models import Hogar

def mapa_facatativa_page(request):
    es_entidad_o_admin = request.user.is_authenticated and request.user.rol in [
        'ADMIN', 'ENTIDAD'
    ]
    administrador = request.user.is_authenticated and request.user.rol in ['ADMIN']

    es_autenticado =request.user.is_authenticated
    listado_municipios = Municipios.objects.order_by('mpio_cnmbr')
    listado_veredas = Veredas.objects.order_by('nombre_ver').filter(dptompio='25269').values('codigo_ver','nombre_ver')

    contexto = {
        'municipios': listado_municipios,
        'veredas': listado_veredas,
        'administracion': es_entidad_o_admin,
        'autenticado': es_autenticado,
        'es_administrador': administrador,
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

    # API Unificada Eficiente: Utiliza exclusivamente la capa de Veredas.
    # Dibuja la zona rural por polígonos y extrae el anillo interior (hueco) 
    # para aislar y pintar la cabecera urbana de Facatativá de forma exacta.

    try:
        # 1. Tu matriz analítica del Sisbén IV (Idéntica)
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

        ref_origen = SpatialReference(9377)   # Origen Único de Colombia
        ref_destino = SpatialReference(4326)  # WGS84 para Leaflet

        # 2. Procesamos las Veredas y guardamos sus geometrías
        veredas_qs = Veredas.objects.filter(dptompio='25269')
        features = []
        geometrias_totales = []

        for vda in veredas_qs:
            if vda.geom:
                vda.geom.srid = ref_origen.srid
                geometrias_totales.append(vda.geom)
                
                # Transformamos la vereda rural individual para Leaflet
                geom_copia = vda.geom.clone()
                geom_copia.transform(ref_destino.srid)
                
                features.append({
                    "type": "Feature",
                    "id": f"rural_{vda.codigo_ver}",
                    "geometry": json.loads(geom_copia.geojson),
                    "properties": {
                        "nombre_zona": vda.nombre_ver or f"Vereda {vda.id}",
                        "tipo_zona": "Rural",
                        "promedio_indice": round(m_rural['promedio_indice'] or 0, 1) if m_rural else 0.0,
                        "total_hogares": round(m_rural['total_hogares']) if m_rural else 0,
                        "promedio_ninos": round(m_rural['promedio_ninos'] or 0, 1) if m_rural else 0.0,
                        "tasa_informalidad": round(m_rural['tasa_informalidad'] or 0, 1) if m_rural else 0.0
                    }
                })

        # ==========================================================================
        # EXTRACCIÓN AUTOMÁTICA DEL HUECO URBANO (EL ANILLO INTERIOR)
        # ==========================================================================
        if geometrias_totales:
            # 3.1. Creamos la silueta exterior unificada (esta sí se genera bien)
            silueta_total = geometrias_totales[0]
            for g in geometrias_totales[1:]:
                silueta_total = silueta_total.union(g)
            
            # 3.2. Para evitar que los bordes compartidos "tapen" el hueco central,
            # tomamos la silueta exterior completa como nuestro molde base...
            zona_urbana_geom = silueta_total
            
            # ...y le restamos CADA vereda de forma individual.
            # Al restarlas una a una, el hueco central queda expuesto obligatoriamente,
            # sin importar los desfases de precisión entre fuentes distintas.
            for vda_geom in geometrias_totales:
                if zona_urbana_geom and not zona_urbana_geom.empty:
                    zona_urbana_geom = zona_urbana_geom.difference(vda_geom)

            # 3.3. Si el resultado contiene múltiples fragmentos debido a imperfecciones en los bordes,
            # nos quedamos únicamente con el fragmento central, que será por mucho el de mayor área.
            if zona_urbana_geom and not zona_urbana_geom.empty:
                if hasattr(zona_urbana_geom, 'geom_type') and zona_urbana_geom.geom_type == 'MultiPolygon':
                    # Seleccionamos el polígono más grande de la colección (el casco urbano)
                    zona_urbana_geom = max(zona_urbana_geom, key=lambda x: x.area)

                # Validamos que sea un polígono con un área representativa para la cabecera (ej: mayor a 10 hectáreas)
                # Como estamos en el SRID 9377 (metros cuadrados), 100.000 m² = 10 hectáreas.
                if zona_urbana_geom.area > 100000:
                    # Transformamos a WGS84 para Leaflet
                    zona_urbana_geom.transform(ref_destino.srid)
                
                    features.append({
                        "type": "Feature",
                        "id": "urbano_cabecera",
                        "geometry": json.loads(zona_urbana_geom.geojson),
                        "properties": {
                            "nombre_zona": "Cabecera Urbana (Facatativá Centro)",
                            "tipo_zona": "Urbana",
                            "promedio_indice": round(m_urbano['promedio_indice'] or 0, 1) if m_urbano else 0.0,
                            "total_hogares": round(m_urbano['total_hogares']) if m_urbano else 0,
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

