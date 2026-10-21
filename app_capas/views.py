from django.views.decorators.http import require_POST, require_http_methods, require_GET
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from .models import CapaEspacial, ElementoVectorial
from .forms import CapaEspacialForm
from .services import procesar_capa_vectorial


@csrf_protect
@require_http_methods(["GET", "POST"])
def cargar_capa(request):
    mostrar_modal_exito = False
    if request.method == 'POST':
        form = CapaEspacialForm(request.POST, request.FILES)
        if form.is_valid():
            capa = form.save()
            mostrar_modal_exito = True
            if capa.formato not in ['WFS', 'GEOTIFF'] and capa.archivo:
                try:
                    procesar_capa_vectorial(capa.id)
                except Exception as e:
                    print(f"Error procesando la capa: {e}")
            messages.success(request, "¡La capa espacial se ha procesado y cargado correctamente!", extra_tags="modal_exito")

            return redirect(request.META.get('HTTP_REFERER', '/mapa_facatativa.html/'))
    else:
        form = CapaEspacialForm()
    
    context = {
        'form': form,
        'mostrar_modal_exito': mostrar_modal_exito,
    }
    return render(request, 'capas/cargar.html', context)

@require_GET
def listar_capas_api(request):
    """
    Retorna la lista de capas procesadas exitosamente para consumirlas desde el JS del mapa.
    """
    capas = CapaEspacial.objects.filter(procesado_exitoso=True).values(
        'id', 'nombre', 'formato', 'tipo_geometria', 'num_registros', 'fecha_creacion'
    )
    return JsonResponse({'capas': list(capas)})


@require_GET
def obtener_geojson_capa(request, capa_id):
    """
    Endpoint que retorna los elementos vectoriales guardados en PostGIS 
    como un FeatureCollection GeoJSON apto para Leaflet.
    """
    capa = get_object_or_404(CapaEspacial, id=capa_id)
    elementos = ElementoVectorial.objects.filter(capa=capa)

    features = []
    for elem in elementos:
        features.append({
            "type": "Feature",
            "geometry": json.loads(elem.geometria.geojson),
            "properties": elem.atributos
        })

    geojson_data = {
        "type": "FeatureCollection",
        "name": capa.nombre,
        "features": features
    }

    return JsonResponse(geojson_data)

@require_POST
def eliminar_capa_api(request, capa_id):
    """
    Elimina una CapaEspacial. Gracias a on_delete=models.CASCADE, 
    sus ElementoVectorial asociados en PostGIS se borran automáticamente.
    """
    try:
        capa = get_object_or_404(CapaEspacial, id=capa_id)
        capa.delete()  # Elimina geometrías (cascade) y archivo físico (override delete)
        return JsonResponse({'status': 'ok', 'message': 'Capa eliminada correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@require_GET
def geojson_politicas_seguridad_alimentaria(request):
    """
    Endpoint provisional: GeoJSON de la capa 'Implementación de políticas de inseguridad alimentaria' (ID 30),
    filtrado/coloreado por el campo f22 (política de seguridad alimentaria).
    """
    # Capa fija ID 30: "Implementación de políticas de inseguridad alimentaria"
    capa_id = request.GET.get('capa_id', '30')
    capa = get_object_or_404(CapaEspacial, id=capa_id, procesado_exitoso=True)
    
    # Campo en atributos JSON: f22 = política de seguridad alimentaria
    campo_f22 = 'f22'
    
    # Filtro opcional: solo los que NO sean "No hay Política Pública"
    solo_con_politica = request.GET.get('solo_con_politica', 'true').lower() == 'true'
    
    queryset = ElementoVectorial.objects.filter(capa=capa)
    
    if solo_con_politica:
        # Excluir los que dicen "No hay Política Pública" (case-insensitive)
        queryset = queryset.exclude(
            **{f"atributos__{campo_f22}__icontains": "no hay política pública"}
        )
    
    # Límite opcional
    limit = request.GET.get('limit')
    if limit:
        try:
            queryset = queryset[:int(limit)]
        except ValueError:
            pass
    
    # Mapeo de colores por valor de f22
    COLOR_MAP = {
        'en formulación': '#f59e0b',      
        'formulación': '#f59e0b',
        'aprobada': '#16a34a',            
        'aprobado': '#16a34a',
        'ejecutada': '#16a34a',
        'ejecutando': '#3b82f6',          
        'en ejecución': '#3b82f6',
        'en ejecucion': '#3b82f6',
        'pendiente': '#6366f1',           
        'planificada': '#6366f1',
        'no hay política pública': '#9ca3af',  
        'no hay politica pública': '#9ca3af',
        'no hay política': '#9ca3af',
        'sin política': '#9ca3af',
        'sin politica': '#9ca3af',
    }
    
    DEFAULT_COLOR = '#6b7280'  
    
    features = []
    stats = {}
    
    for elem in queryset:
        attrs = elem.atributos
        valor_f22 = attrs.get(campo_f22, '')
        valor_lower = str(valor_f22).strip().lower()
        
        # Color basado en valor
        color = DEFAULT_COLOR
        for key, col in COLOR_MAP.items():
            if key in valor_lower:
                color = col
                break
        
        # Contar para stats
        stats[valor_f22] = stats.get(valor_f22, 0) + 1
        
        # Propiedades para el popup
        props = {
            **attrs,
            '_color_sugerido': color,
            '_valor_f22': valor_f22,
            '_capa_origen': capa.nombre,
        }
        
        features.append({
            "type": "Feature",
            "geometry": json.loads(elem.geometria.geojson),
            "properties": props
        })
    
    geojson_data = {
        "type": "FeatureCollection",
        "name": f"Políticas Seguridad Alimentaria - {capa.nombre}",
        "capa_id": capa.id,
        "capa_nombre": capa.nombre,
        "campo_filtrado": campo_f22,
        "total_features": len(features),
        "stats_por_valor": stats,
        "features": features
    }
    
    return JsonResponse(geojson_data)