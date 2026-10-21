from django.urls import path
from .views import cargar_capa, obtener_geojson_capa, listar_capas_api, eliminar_capa_api, geojson_politicas_seguridad_alimentaria

urlpatterns = [
    path('cargar/', cargar_capa, name='cargar_capa'),
    path('api/listar/', listar_capas_api, name='listar_capas_api'),
    path('api/geojson/<int:capa_id>/', obtener_geojson_capa, name='obtener_geojson_capa'),
    path('api/eliminar/<int:capa_id>/', eliminar_capa_api, name='eliminar_capa_api'),
    path('api/politicas-seguridad-alimentaria/', geojson_politicas_seguridad_alimentaria, name='politicas_seguridad_alimentaria'),
]
