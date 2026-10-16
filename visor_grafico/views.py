import json
import pandas as pd
import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.gdal import SpatialReference
from .models import Vias, Municipios, Veredas, ZonaUrbana
from indicador_territorial.models import Corte
from app_capas.forms import CapaEspacialForm
from .apps import VisorGraficoConfig
from django.views.decorators.http import require_GET


@require_GET 
def mapa_facatativa_page(request):
    es_entidad_o_admin = request.user.is_authenticated and request.user.rol in [
        'ADMIN', 'ENTIDAD'
    ]
    cortes = Corte.objects.order_by('id_corte')
    nombre_user = f"{request.user.first_name} {request.user.last_name}" if request.user.is_authenticated else None
    administrador = request.user.is_authenticated and request.user.rol in ['ADMIN']
    form = CapaEspacialForm()
    es_autenticado =request.user.is_authenticated
    listado_municipios = Municipios.objects.filter(dpto_ccdgo='25').order_by('mpio_cnmbr')
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


@require_GET 
def obtener_veredas_por_municipio(request):
    mpio = request.GET.get("mpio", None)
    veredas = Veredas.objects.order_by('nombre_ver').filter(dptompio= mpio).values('codigo_ver','nombre_ver')
    return JsonResponse(list(veredas), safe=False)


@require_GET 
def facatativa_geojson_api(request):
    """
    Vista API: Retorna el polígono de Facatativá en formato GeoJSON WGS84 (EPSG:4326).
    Código DANE de Cundinamarca = '25'
    Código DANE de Facatativá = '25269'
    """
    try:
        mpio = request.GET.get('mpio', None)
        depto = request.GET.get('depto', '25')
        if mpio != None:
            facatativa_qs = Municipios.objects.filter(mpio_cdpmp= mpio)
        else:
            # facatativa_qs = Municipios.objects.filter(mpio_cdpmp='25269')
            facatativa_qs = Municipios.objects.filter(mpio_cdpmp__startswith=depto)

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


@require_GET 
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


@require_GET 
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
        return JsonResponse({'error':str(e)}, status=500)

# ==============================================================================
# CAPAS ESPACIALES BASE (RURAL Y URBANA)
# ==============================================================================


def _construir_geojson(queryset, tipo_zona_nombre, prefijo_id):
    ref_origen = SpatialReference(9377)
    ref_destino = SpatialReference(4326)
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
                }
            })

    return {"type": "FeatureCollection", "features": features}


@require_GET 
def geojson_inseguridad_rural(request):
    try:
        mpio = request.GET.get('mpio', '25269')
        veredas_qs = ZonaUrbana.objects.filter(mpio_cdpmp=mpio).exclude(zu_cnmbre='FACATATIVÁ')
        return JsonResponse(_construir_geojson(veredas_qs, "Rural", "rural"), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET 
def geojson_inseguridad_urbana(request):
    try:
        mpio = request.GET.get('mpio', '25269')
        zona_urbana_qs = ZonaUrbana.objects.filter(mpio_cdpmp=mpio, zu_cnmbre='FACATATIVÁ')
        return JsonResponse(_construir_geojson(zona_urbana_qs, "Cabecera urbana", "urbano"), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET 
def obtener_datos_mapa_2025(request):
    try:
        # 1. Si ya se calculó previamente, devolver inmediatamente desde la memoria (Caché en 1ms)
        if VisorGraficoConfig.cache_fies_2025 is not None:
            return JsonResponse({'status': 'success', 'data': VisorGraficoConfig.cache_fies_2025, 'cached': True})

        # 2. Verificar que el modelo y las columnas estén cargados
        if VisorGraficoConfig.ml_model is None or VisorGraficoConfig.ml_columns is None:
            return JsonResponse({
                'status': 'error', 
                'message': 'El modelo XGBoost o las columnas no están cargados en memoria.'
            }, status=500)

        # 3. Validar existencia del archivo CSV
        ruta_csv = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets', 'X_test_2025.csv')
        if not os.path.exists(ruta_csv):
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontró el archivo X_test_2025.csv en visor_grafico/ml_assets/'
            }, status=404)

        # 4. Cargar microdatos
        df_test = pd.read_csv(ruta_csv)

        # 5. Normalizar DIVIPOLA a 5 dígitos y extraer factor de expansión (FEX)
        divipola_serie = df_test['DIVIPOLA'].astype(int).astype(str).str.zfill(5)
        fex_serie = df_test['FEX_C_num']

        # 6. Alinear columnas estrictamente con el orden de entrenamiento
        df_alineado = df_test.reindex(columns=VisorGraficoConfig.ml_columns, fill_value=0)

        # 7. Inferencia con XGBoost (probabilidad de inseguridad moderada o severa)
        probabilidades = VisorGraficoConfig.ml_model.predict_proba(df_alineado)[:, 1]

        # 8. Cálculo de prevalencia FIES municipal vectorizado (rápido y oficial DANE)
        df_calculo = pd.DataFrame({
            'DIVIPOLA': divipola_serie,
            'FEX_C_num': fex_serie,
            'producto_ponderado': fex_serie * probabilidades
        })

        agrupado = df_calculo.groupby('DIVIPOLA').agg({
            'producto_ponderado': 'sum',
            'FEX_C_num': 'sum'
        }).reset_index()

        agrupado['prevalencia_fies'] = ((agrupado['producto_ponderado'] / agrupado['FEX_C_num']) * 100).round(2)

        # 9. Guardar en caché de memoria para todas las futuras peticiones
        datos_json = agrupado[['DIVIPOLA', 'prevalencia_fies']].to_dict(orient='records')
        VisorGraficoConfig.cache_fies_2025 = datos_json

        return JsonResponse({'status': 'success', 'data': datos_json, 'cached': False})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


