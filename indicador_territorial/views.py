from django.shortcuts import render
import pandas as pd
import numpy as np
import io, tempfile, os
import statsmodels.api as sm
from django.http import JsonResponse
from gestion_usuarios.decorators import rol_requerido
from gestion_usuarios.models import Usuario
from django.conf import settings
from django.contrib import messages
from indicador_territorial.services.cargador_ecv import cargar_desde_csv
from django.db.models import Sum, F, FloatField, Value, Case, When
from django.db.models.functions import Cast
from indicador_territorial.models import HogarECV
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_protect


@require_GET 
def dashboard_view(request):
    es_entidad_o_admin = request.user.is_authenticated and request.user.rol in [
        'ADMIN', 'ENTIDAD'
    ]
    nombre_user = f"{request.user.first_name} {request.user.last_name}" if request.user.is_authenticated else None
    administrador = request.user.is_authenticated and request.user.rol in ['ADMIN']

    context = {
        'autenticado': es_entidad_o_admin,
        'es_administrador': administrador,
        'nombre_user':nombre_user,
    }
    
    return render(request, 'indicador_territorial/dashboard.html', context)



# Variable global o atributo de clase para caché en memoria
CACHE_DIMENSIONES_2025 = None
@require_GET 
def obtener_dimensiones_municipales(request):
    """
    Endpoint API: Retorna los aportes SHAP por dimensión y prevalencia base 
    agrupados por municipio (DIVIPOLA a 5 dígitos).
    """
    global CACHE_DIMENSIONES_2025
    try:
        if CACHE_DIMENSIONES_2025 is not None:
            return JsonResponse({'status': 'success', 'data': CACHE_DIMENSIONES_2025, 'cached': True})
        ruta_csv = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets', 'dimensiones_municipales_2025.csv')
        if not os.path.exists(ruta_csv):
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontró dimensiones_municipales_2025.csv en ml_assets/'
            }, status=404)
        df_dim = pd.read_csv(ruta_csv)
        # Asegurar formato DIVIPOLA a 5 dígitos (ej. "05001", "25269")
        df_dim['DIVIPOLA_SIG'] = df_dim['DIVIPOLA_SIG'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(5)
        columnas_deseadas = [
            'DIVIPOLA_SIG', 
            'prevalencia_total',
            'aporte_Salud_y_Discapacidad',
            'aporte_Vivienda_y_Servicios',
            'aporte_Trabajo_e_Ingresos',
            'aporte_Educacion',
            'aporte_Demografia',
            'aporte_Desastres',
        ]
        
        # Filtrar columnas existentes y redondear a 2 decimales
        df_salida = df_dim[[c for c in columnas_deseadas if c in df_dim.columns]].copy()
        columnas_numericas = df_salida.select_dtypes(include=['float', 'float64']).columns
        df_salida[columnas_numericas] = df_salida[columnas_numericas].round(2)
        CACHE_DIMENSIONES_2025 = df_salida.to_dict(orient='records')
        return JsonResponse({'status': 'success', 'data': CACHE_DIMENSIONES_2025, 'cached': False})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ─── Dimensiones Zonales (Dashboard DSS) ──────────────────────────────────────
CACHE_DIMENSIONES_ZONALES_2025 = None
@require_GET 
def obtener_dimensiones_zonales(request):
    """
    Sirve los datos del CSV dimensiones_zonales_2025.csv (nivel Zona Urbana/Rural).
    Incluye dimensiones macro (radares) y métricas micro SHAP (filtros y simulación DSS).
    """
    global CACHE_DIMENSIONES_ZONALES_2025
    try:
        if CACHE_DIMENSIONES_ZONALES_2025 is not None:
            return JsonResponse({'status': 'success', 'data': CACHE_DIMENSIONES_ZONALES_2025, 'cached': True})

        ruta_csv = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets', 'dimensiones_zonales_2025.csv')
        if not os.path.exists(ruta_csv):
            return JsonResponse({
                'status': 'error',
                'message': 'No se encontró dimensiones_zonales_2025.csv en visor_grafico/ml_assets/'
            }, status=404)

        df_zonal = pd.read_csv(ruta_csv)

        # Normalizar DIVIPOLA: quitar ".0" y rellenar a 5 dígitos
        df_zonal['DIVIPOLA_SIG'] = (
            df_zonal['DIVIPOLA_SIG']
            .astype(str)
            .str.replace(r'\.0$', '', regex=True)
            .str.zfill(5)
        )

        # Lista completa de columnas necesarias para el Dashboard DSS
        columnas_dss = [
            # Identificadores y Totales
            'DIVIPOLA_SIG', 'Zona', 'total_hogares_zona', 'prevalencia_zona',
            
            # Dimensiones Macro (Radares Chart.js)
            'Vivienda_y_Servicios', 'Trabajo_e_Ingresos', 'Salud_y_Discapacidad', 'Educacion', 'Demografia',
            'aporte_Salud_y_Discapacidad', 'aporte_Vivienda_y_Servicios',
            'aporte_Trabajo_e_Ingresos', 'aporte_Educacion', 'aporte_Demografia', 'aporte_Desastres',
            
            # Focalización / Filtros (%)
            'pct_jefatura_femenina', 'pct_hogar_hacinado',
            
            # Micro SHAP (Síntomas y Simuladores de Intervención)
            'shap_desempleo', 'shap_nevera', 'shap_agua_saneamiento', 'shap_educacion', 'shap_salud'
        ]

        # Seleccionar las columnas disponibles en el CSV
        columnas_existentes = [c for c in columnas_dss if c in df_zonal.columns]
        df_salida = df_zonal[columnas_existentes].copy()

        # Reemplazar valores nulos/infinitos para evitar fallos de JsonResponse
        df_salida = df_salida.replace([np.inf, -np.inf], np.nan).fillna(0)

        # Redondear columnas numéricas a 2 decimales
        cols_float = df_salida.select_dtypes(include=['float', 'float64']).columns
        df_salida[cols_float] = df_salida[cols_float].round(2)

        CACHE_DIMENSIONES_ZONALES_2025 = df_salida.to_dict(orient='records')
        return JsonResponse({'status': 'success', 'data': CACHE_DIMENSIONES_ZONALES_2025, 'cached': False})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


MAX_MB_CARGA = 300  
@csrf_protect
@require_http_methods(["GET", "POST"])
@rol_requerido(['ADMIN'])
def cargar_ecv_view(request):

    contexto = {'anios_opciones': range(2022, 2031)}

    if request.method == 'POST':
        anio = request.POST.get('anio', '').strip()
        archivo = request.FILES.get('archivo_csv')

        # ── Validaciones ──
        if not anio.isdigit():
            messages.error(request, 'Debes indicar un año válido (ej: 2025).')
        elif not archivo:
            messages.error(request, 'Debes seleccionar un archivo CSV.')
        elif not archivo.name.lower().endswith('.csv'):
            messages.error(request, 'El archivo debe tener extensión .csv.')
        elif archivo.size > MAX_MB_CARGA * 1024 * 1024:
            messages.error(request, f'El archivo supera el máximo de {MAX_MB_CARGA} MB.')
        else:
            ruta_tmp = None
            try:
                # Guardar el archivo subido a un temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                    for chunk in archivo.chunks():
                        tmp.write(chunk)
                    ruta_tmp = tmp.name

                # Capturar el log del cargador en memoria
                buffer = io.StringIO()
                resultado = cargar_desde_csv(ruta_tmp, int(anio), out=buffer.write)
                contexto['resultado'] = resultado
                contexto['log'] = buffer.getvalue()
                messages.success(
                    request,
                    f"Carga {anio} finalizada: {resultado['cargados']:,} hogares procesados."
                )
            except Exception as e:
                messages.error(request, f'Error durante la carga: {e}')
            finally:
                if ruta_tmp and os.path.exists(ruta_tmp):
                    os.remove(ruta_tmp)

    return render(request, 'indicador_territorial/cargar_ecv.html', contexto)

@require_GET 
def obtener_prevalencia_zonales_bd(request):
    """
    Prevalencia real y del modelo por municipio y zona, calculada EN VIVO
    desde hogar_ecv + dim_fies + dim_demografia, ponderada por fex_c.
    Param: ?corte=2025
    """
    try:
        corte = int(request.GET.get('corte', 2025))

        qs = (HogarECV.objects
            .filter(corte__id_corte=corte, fies__isnull=False)
            .values('municipio_id', 'municipio__mpio_cnmbr', 'clase')
            .annotate(
                total_hogares=Sum('fex_c'),
                fex_modelo=Sum(F('fex_c') * Coalesce('fies__prob_calibrada',
                                                    'fies__prob_riesgo_modelo'),
                                output_field=FloatField()),
                fex_real=Sum(F('fex_c') * Case(
                    When(fies__inseguridad_mod_grave=True, then=Value(1.0)),
                    default=Value(0.0),
                    output_field=FloatField())),
                fex_predicho=Sum(F('fex_c') * Case(
                    When(fies__predicho_mod_grave=True, then=Value(1.0)),
                    default=Value(0.0),
                    output_field=FloatField())),
                fex_jefatura=Sum(Case(
                    When(demografia__p6020_id=2, then=F('fex_c')),
                    default=Value(0.0), output_field=FloatField())),
                fex_hacinado=Sum(Case(
                    When(demografia__cant_personas_hogar__gte=5, then=F('fex_c')),
                    default=Value(0.0), output_field=FloatField())),
            ))

        data = []
        for r in qs:
            tot = r['total_hogares'] or 0
            if tot <= 0:
                continue
            data.append({
                # Mismos nombres de campo que el CSV → fusión transparente en el JS
                'DIVIPOLA_SIG': r['municipio_id'],
                'nombre_municipio': r['municipio__mpio_cnmbr'],
                'Zona': 'Urbana' if r['clase'] == 1 else 'Rural',
                'total_hogares_zona': round(tot, 1),
                'prevalencia_zona': (round(r['fex_modelo'] / tot * 100, 2)
                                    if r['fex_modelo'] is not None else None),
                'prevalencia_real': round((r['fex_real'] or 0) / tot * 100, 2),
                'hogares_predichos_pct': (round(r['fex_predicho'] / tot * 100, 2)
                                        if r['fex_predicho'] is not None else None),
                'pct_jefatura_femenina': round((r['fex_jefatura'] or 0) / tot, 4),
                'pct_hogar_hacinado': round((r['fex_hacinado'] or 0) / tot, 4),
            })

        return JsonResponse({'status': 'success', 'corte': corte, 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
