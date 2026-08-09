from django.urls import path

from . import views

urlpatterns = [
    path('mapa-facatativa/', views.mapa_facatativa_page, name='mapa_facatativa'),
    path('api/facatativa-geojson/', views.facatativa_geojson_api, name='facatativa_geojson'),
    path('api/vias-geojson/', views.vias_facatativa_geojson, name='vias_geojson'),
    path('api/veredas-geojson',views.veredas_facatativa_geojson, name='veredas_geojson'),
    path('api/veredas-filter-geojson', views.obtener_veredas_por_municipio, name='veredas_filter_geojson')
]