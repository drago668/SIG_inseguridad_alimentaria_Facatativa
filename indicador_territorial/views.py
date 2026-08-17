from django.shortcuts import render
import pandas as pd
import statsmodels.api as sm
from django.http import JsonResponse
from django.db.models import Avg, Sum, Count, Case, When, Value, IntegerField,FloatField, F
from .models import Hogar

def dashboard_view(request):
    # 1. Filtro por zona geográfica opcional si viene en la URL
    zona_id = request.GET.get('zona')
    hogares = Hogar.objects.select_related('vivienda', 'jefe_hogar')
    #if zona_id:
    #hogares = hogares.filter(zona_geografica_id=2)

    hogares_con_pesos = hogares.annotate(
            # Dimensión 1: Soporte Alimentario (16.66% cada una)
            w_nevera=Case(When(nevera=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
            w_cocina=Case(When(cocina=0, then=Value(16.66)), default=Value(0), output_field=FloatField()),
            
            # Dimensión 2: Saneamiento y Agua (11.11% cada una)
            w_acueducto=Case(When(vivienda__acueducto=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
            w_alcantarillado=Case(When(vivienda__alcantarillado=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
            w_agua_7_dias=Case(When(agua_llega_7_dias=0, then=Value(11.11)), default=Value(0), output_field=FloatField()),
            
            # Dimensión 3: Energía para Cocción (33.34%)
            w_combustible=Case(When(combustible_para_cocinar__id_combustible__gte=6, then=Value(33.34)), default=Value(0), output_field=FloatField()),
        )
    

    # Sumamos algebraicamente las privaciones de cada fila. Esto genera un número entero por hogar, NO un agregado.
    hogares_calculados = hogares_con_pesos.annotate(
        indice_inseguridad=F('w_nevera') + F('w_cocina') + F('w_acueducto') + F('w_alcantarillado') + F('w_agua_7_dias') + F('w_combustible'))
    
    total_criticos = hogares_calculados.filter(indice_inseguridad__gte=33.3).count()

    # 3. Métricas Macro (Aquí sí aplicamos promedios sobre el campo lineal 'indice_inseguridad')
    metricas = hogares_calculados.aggregate(
        promedio_general=Avg('indice_inseguridad'),
        total_encuestados=Sum('zona_geografica__fex'),
    )

    # 4. Agrupamos por Zona Geográfica para la gráfica de barras de ApexCharts
    datos_grafico = hogares_calculados.values('zona_geografica__nombre_zona').annotate(
        promedio_zona=Avg('indice_inseguridad')
    ).order_by('-promedio_zona')
    # sexo ----------------------------------------------------------------------------------------------------------------------------------------
    datos_sex_jefe_hogar = hogares_calculados.values('jefe_hogar__id_sexo__nombre_sexo').annotate(
        promedio_sexo =Count('id')
    )
    categorias_pie = ["Jefe Hombre", "Jefe Mujer"]
    valores_pie = []
    valores_pie.append(next((item['promedio_sexo'] for item in datos_sex_jefe_hogar if item['jefe_hogar__id_sexo__nombre_sexo'] == 'Hombre'), 0))
    valores_pie.append(next((item['promedio_sexo'] for item in datos_sex_jefe_hogar if item['jefe_hogar__id_sexo__nombre_sexo'] == 'Mujer'), 0))

    promedio_urbano = next(
        (item['promedio_zona'] for item in datos_grafico if item['zona_geografica__nombre_zona'] == 'Cabecera'), 
        0
    )
    promedio_rural = next(
        (item['promedio_zona'] for item in datos_grafico if item['zona_geografica__nombre_zona'] == 'Centro poblado, Rural disperso'), 
        0
    )

    # Convertimos los resultados a listas que JavaScript entiende de forma nativa------------------------------------------------------------------
    categorias_javascript = [item['zona_geografica__nombre_zona'] or "Sin Especificar" for item in datos_grafico]
    valores_javascript = [round(item['promedio_zona'] or 0, 1) for item in datos_grafico]

    context = {
        'valores_pie': valores_pie,
        'categorias_pie': categorias_pie,
        'promedio_general': round(metricas['promedio_general'] or 0, 2),
        'total_encuestados': round(metricas['total_encuestados']),
        'total_inseguros':total_criticos,
        'categorias_grafico': categorias_javascript,
        'valores_grafico': valores_javascript,
        'promedio_urbano': round(promedio_urbano, 1),
        'promedio_rural': round(promedio_rural, 1),
        'porcentaje_inseguros':round((total_criticos / round(metricas['total_encuestados']) * 100), 2) ,
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
                'sexo': h.jefe_hogar.id_sexo.nombre_sexo,
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

    Y = df['indice'].astype(float)

    X = (df[['jefe_mujer', 'trabajo_informal', 'ninos_hogar', 'personas_hogar']]).astype(int)    
    X = sm.add_constant(X)
    X = X.astype(float)

    modelo = sm.OLS(Y, X).fit()

    resultados = {
        "R_cuadrado_Ajustado": round(modelo.rsquared_adj, 4),
        "Coeficientes": {
            "Constante_Intercepto": round(modelo.params['const'], 2),
            "Efecto_Jefe_Mujer": round(modelo.params['jefe_mujer'], 2),
            "Efecto_Trabajo_Informal": round(modelo.params['trabajo_informal'], 2),
            "Efecto_Personas_Hogar": round(modelo.params['personas_hogar'], 2),
            "Efecto_Por_Cada_Nino": round(modelo.params['ninos_hogar'], 2),
        }
    }

    return JsonResponse(resultados)