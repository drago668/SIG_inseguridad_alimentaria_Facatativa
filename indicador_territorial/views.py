from django.shortcuts import render
import pandas as pd
import statsmodels.api as sm
from django.http import JsonResponse
from django.db.models import Avg, Sum, Count, Case, When, Value, IntegerField,FloatField, F, ExpressionWrapper
from .models import Hogar

def dashboard_view(request):
    zona_id = request.GET.get('zona')
    hogares = Hogar.objects.select_related('vivienda', 'jefe_hogar', 'zona_geografica')

    # 1. Calculamos los pesos individuales de privación por hogar (Igual que antes)
    hogares_con_pesos = hogares.annotate(
        w_nevera=Case(When(nevera=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
        w_cocina=Case(When(cocina=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
        w_acueducto=Case(When(vivienda__acueducto=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_alcantarillado=Case(When(vivienda__alcantarillado=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_agua_7_dias=Case(When(agua_llega_7_dias=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_combustible=Case(When(combustible_para_cocinar__id_combustible__gte=6, then=Value(33.34)), default=Value(0), output_field=FloatField()),
    )

    # 2. Calculamos el índice base por hogar Y generamos el producto (Índice * FEX) por fila
    hogares_calculados = hogares_con_pesos.annotate(
        indice_inseguridad=F('w_nevera') + F('w_cocina') + F('w_acueducto') + F('w_alcantarillado') + F('w_agua_7_dias') + F('w_combustible')
    ).annotate(
        indice_por_fex=ExpressionWrapper(F('indice_inseguridad') * F('zona_geografica__fex'), output_field=FloatField())
    )
    
    # CORRECCIÓN 1: El conteo de críticos reales expandidos es la SUMA de sus factores de expansión
    total_criticos_expandidos = hogares_calculados.filter(indice_inseguridad__gte=33.3).aggregate(
        total_criticos=Sum('zona_geografica__fex')
    )['total_criticos'] or 0

    # 3. CORRECCIÓN 2: Métricas Macro utilizando promedio ponderado (Suma del producto / Suma del FEX)
    metricas = hogares_calculados.aggregate(
        suma_indice_fex=Sum('indice_por_fex'),
        total_poblacion_fex=Sum('zona_geografica__fex'),
    )
    
    total_encuestados_fex = metricas['total_poblacion_fex'] or 1
    promedio_general_ponderado = (metricas['suma_indice_fex'] or 0) / round(total_encuestados_fex)

    # 4. CORRECCIÓN 3: Agrupación Geográfica Ponderada para ApexCharts (Barras)
    datos_grafico_crudo = hogares_calculados.values('zona_geografica__nombre_zona').annotate(
        suma_indice_zona=Sum('indice_por_fex'),
        suma_fex_zona=Sum('zona_geografica__fex')
    )
    
    datos_grafico = []
    for item in datos_grafico_crudo:
        fex_zona = item['suma_fex_zona'] or 1
        datos_grafico.append({
            'zona_geografica__nombre_zona': item['zona_geografica__nombre_zona'],
            'promedio_zona': item['suma_indice_zona'] / round(fex_zona)
        })
    # Ordenamos de mayor a menor promedio ponderado
    datos_grafico = sorted(datos_grafico, key=lambda x: x['promedio_zona'], reverse=True)

    # 5. CORRECCIÓN 4: Distribución de sexo expandida por FEX para la gráfica de torta
    datos_sex_jefe_hogar = hogares_calculados.values('jefe_hogar__id_sexo__nombre_sexo').annotate(
        conteo_expandido_sexo=Sum('zona_geografica__fex')
    )
    
    categorias_pie = ["Jefe Hombre", "Jefe Mujer"]
    valores_pie = [
        next((round(item['conteo_expandido_sexo']) for item in datos_sex_jefe_hogar if item['jefe_hogar__id_sexo__nombre_sexo'] == 'Hombre'), 0),
        next((round(item['conteo_expandido_sexo']) for item in datos_sex_jefe_hogar if item['jefe_hogar__id_sexo__nombre_sexo'] == 'Mujer'), 0)
    ]

    promedio_urbano = next(
        (item['promedio_zona'] for item in datos_grafico if item['zona_geografica__nombre_zona'] == 'Cabecera'), 
        0
    )
    promedio_rural = next(
        (item['promedio_zona'] for item in datos_grafico if item['zona_geografica__nombre_zona'] == 'Centro poblado, Rural disperso'), 
        0
    )

    # Convertimos a listas nativas para Javascript
    categorias_javascript = [item['zona_geografica__nombre_zona'] or "Sin Especificar" for item in datos_grafico]
    valores_javascript = [round(item['promedio_zona'] or 0, 1) for item in datos_grafico]

    context = {
        'valores_pie': valores_pie,
        'categorias_pie': categorias_pie,
        'promedio_general': round(promedio_general_ponderado, 2),
        'total_encuestados': round(total_encuestados_fex),
        'total_inseguros': round(total_criticos_expandidos),
        'categorias_grafico': categorias_javascript,
        'valores_grafico': valores_javascript,
        'promedio_urbano': round(promedio_urbano, 1),
        'promedio_rural': round(promedio_rural, 1),
        'porcentaje_inseguros': round((total_criticos_expandidos / total_encuestados_fex * 100), 2),
    }
    
    return render(request, 'indicador_territorial/dashboard.html', context)


def regresion_inseguridad(request):
    hogares_calculados = Hogar.objects.select_related('vivienda', 'jefe_hogar').annotate(
        # Dimensión 1: Soporte Alimentario (16.66% cada una)
        w_nevera=Case(When(nevera=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
        w_cocina=Case(When(cocina=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
        w_acueducto=Case(When(vivienda__acueducto=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_alcantarillado=Case(When(vivienda__alcantarillado=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_agua_7_dias=Case(When(agua_llega_7_dias=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
        w_combustible=Case(When(combustible_para_cocinar__id_combustible__gte=6, then=Value(33.34)), default=Value(0), output_field=FloatField()),
        ).annotate(
        indice_inseguridad=F('w_nevera') + F('w_cocina') + F('w_acueducto') + F('w_alcantarillado') + F('w_agua_7_dias') + F('w_combustible')
        )

    filas = []
    for h in hogares_calculados:
        if h.jefe_hogar and h.jefe_hogar.id_sexo:
            filas.append({
                'id': h.id,
                'indice': h.indice_inseguridad,
                'fex': h.zona_geografica.fex or 1,
                'sexo': h.jefe_hogar.id_sexo.nombre_sexo,
                'nombre_zona': h.zona_geografica.nombre_zona, 
                'personas_hogar': h.total_personas_hogar or 1,
                'trabajo_informal': h.jefe_hogar.trabajo_informal or 0,
                'desempleo_larga_duracion':h.jefe_hogar.desempleo_larga_duracion or 0,
                'actividad': h.jefe_hogar.actividad.id_actividad,
                'ninos_hogar':h.cantidad_ninos,
                'adultos_mayores_hogar': h.cantidad_adultos_mayores,
            })

    df = pd.DataFrame(filas)

    if df.empty:
        return JsonResponse({"error": "No hay datos suficientes"}, status=400)

    df['jefe_mujer'] = (df['sexo'] == 'Mujer').astype(int) # Concepto de variable dummy [3.20]
    df['buscando_trabajo'] =(df['actividad'] == 3).astype(int) # buscando trabajo
    df['desempleo_estructural'] = ((df['actividad'] == 3) & (df['desempleo_larga_duracion'] == 1)).astype(int)
    df['desempleo_ninos'] = ((df['ninos_hogar'] > 0) & (df['desempleo_larga_duracion'] == 1)).astype(int)
    df['es_zona_rural'] = (df['nombre_zona'] == 'Centro poblado, Rural disperso').astype(int)

    Y = df['indice'].astype(float)

    X = (df[['jefe_mujer', 'trabajo_informal', 'ninos_hogar', 'personas_hogar', 'es_zona_rural']]).astype(int)    
    X = sm.add_constant(X)
    X = X.astype(float)

    # EXTRAEMOS EL VECTOR DE PESOS DE EXPANSION DEMOGRÁFICA
    pesos_fex = df['fex'].astype(float)

    # CORRECCIÓN CLAVE: Cambiamos OLS por WLS (Weighted Least Squares) aplicando los pesos
    modelo = sm.WLS(Y, X, weights=pesos_fex).fit()

    resultados = {
        "R_cuadrado_Ajustado": round(modelo.rsquared_adj, 4),
        "Coeficientes": {
            "Constante_Intercepto": round(modelo.params['const'], 2),
            "Efecto_Jefe_Mujer": round(modelo.params['jefe_mujer'], 2),
            "Efecto_Trabajo_Informal": round(modelo.params['trabajo_informal'], 2),
            "Efecto_Personas_Hogar": round(modelo.params['personas_hogar'], 2),
            #"Efecto_Actividad": round(modelo.params['buscando_trabajo'], 2),
            #"Efecto_desempleo_larga_duracion":round(modelo.params['desempleo_larga_duracion'],2),
            #"Efecto_desempleo_estructural":round(modelo.params['desempleo_estructural'],2),
            "Efecto_Por_Cada_Nino": round(modelo.params['ninos_hogar'], 2),
            #"Efecto_desempleo_y_Ninos": round(modelo.params['desempleo_ninos'], 2),
            #"Efecto_Por_Cada_Adulto_Mayor": round(modelo.params['adultos_mayores_hogar'], 2),
            "Efecto_Zona_Rural": round(modelo.params['es_zona_rural'], 2),
        },
        "P_Valores_Significancia": {
            "Constante_p": float(modelo.pvalues['const']),
            "Jefe_Mujer_es_significativo": bool(modelo.pvalues['jefe_mujer'] < 0.05), # True si el sexo realmente impacta
            "Trabajo_Informal_es_significativo": bool(modelo.pvalues['trabajo_informal'] < 0.05),
            "Personas_hogar_es_significativo" :bool(modelo.pvalues['personas_hogar']<0.05),
            #"Actividad_es_significativo": bool(modelo.pvalues['buscando_trabajo'] < 0.05),
            #"Desempleo_larga_duracion_es_sisgnificativo" :bool(modelo.pvalues['desempleo_larga_duracion']<0.05),
            #"Desempleo_estructural_es_sisgnificativo" :bool(modelo.pvalues['desempleo_estructural']<0.05),
            "Ninos_es_significativo": bool(modelo.pvalues['ninos_hogar'] < 0.05),
            #"Desempleo_y_Ninos_es_significativo": bool(modelo.pvalues['desempleo_ninos'] < 0.05),
            #"Adultos_Mayores_es_significativo": bool(modelo.pvalues['adultos_mayores_hogar'] < 0.05),
            "Zona_Rural_es_significativo": bool(modelo.pvalues['es_zona_rural'] < 0.05),
        }
    }

    return JsonResponse(resultados)