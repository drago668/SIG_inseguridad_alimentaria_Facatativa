from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from .models import CapaEspacial, ElementoVectorial
from .forms import CapaEspacialForm
from .services import procesar_capa_vectorial

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


def listar_capas_api(request):
    """
    Retorna la lista de capas procesadas exitosamente para consumirlas desde el JS del mapa.
    """
    capas = CapaEspacial.objects.filter(procesado_exitoso=True).values(
        'id', 'nombre', 'formato', 'tipo_geometria', 'num_registros', 'fecha_creacion'
    )
    return JsonResponse({'capas': list(capas)})


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
        messages.success(request, "¡La capa espacial se ha eliminado correctamente!", extra_tags="modal_borrado")
        return JsonResponse({'status': 'ok', 'message': 'Capa eliminada correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
