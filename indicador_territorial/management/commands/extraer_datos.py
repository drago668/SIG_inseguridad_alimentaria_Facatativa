from django.core.management.base import BaseCommand
from indicador_territorial.models import Hogar
import json
import pandas as pd

class Command(BaseCommand):
    help ="Prueba de extraccion de datos para dashboard"

    def handle(self, *args, **options):
        hogares_queryset = Hogar.objects.select_related('jefe_hogar', 'vivienda', 'zona_geografica').all().iterator()
        
        # Aquí guardaremos filas planas para el dashboard
        datos_para_dashboard = []
        contador = 0

        for hogar in hogares_queryset:
            contador += 1
            if not hogar.vivienda or not hogar.jefe_hogar:
                continue
                
            # --- CÁLCULO DE PRIVACIONES (La lógica que definimos al inicio) ---
            p_nevera = 25 if hogar.nevera == 0 else 0
            p_agua_7 = 15 if hogar.agua_llega_7_dias == 0 else 0
            p_combustible = 15 if (hogar.combustible_para_cocinar_id and hogar.combustible_para_cocinar_id >= 3) else 0
            p_informal = 25 if (hogar.jefe_hogar.trabajo_informal == 1 or hogar.jefe_hogar.desempleo_larga_duracion == 1) else 0
            p_acueducto = 20 if hogar.vivienda.acueducto == 0 else 0
            
            # Índice final del hogar
            indice_inseguridad = p_nevera + p_agua_7 + p_combustible + p_informal + p_acueducto
            
            # Extraemos los nombres de las zonas geográficas
            zona = hogar.zona_geografica.nombre_zona if hogar.zona_geografica else "No especificada"
            fex = float(hogar.zona_geografica.fex) if (hogar.zona_geografica and hogar.zona_geografica.fex) else 1.0

            # Datos para el calculo estadistico
            genero_jefe = hogar.jefe_hogar.id_sexo.nombre_sexo
            id_vivienda = hogar.vivienda.id
            material_vivienda = hogar.vivienda.material_vivienda.nombre_material
            fuente_obtencion_agua =hogar.fuente_agua.nombre_fuente

            # Guardamos un diccionario plano (ideal para análisis de datos)
            datos_para_dashboard.append({
                "id_hogar": hogar.id,
                "id_vivienda": id_vivienda,
                "material_vivienda": material_vivienda,
                "zona_geografica": zona,
                "fex": fex,
                "indice_inseguridad": indice_inseguridad,
                "sin_nevera": hogar.nevera == 0,
                "sin_acueducto": hogar.vivienda.acueducto == 0,
                "obtencion_agua": fuente_obtencion_agua,
                "personas_hogar": hogar.total_personas_hogar or 1,
                "genero_jefe": genero_jefe,
            })

            if contador % 500 == 0:
                self.stdout.write(f"Procesados {contador} registros...")

        # Convertimos la lista en un DataFrame de Pandas y la guardamos en un CSV
        df = pd.DataFrame(datos_para_dashboard)
        
        # Lo guardamos en la raíz de tu proyecto para que Streamlit lo encuentre fácil
        df.to_csv("datos_dashboard_sisben.csv", index=False, encoding='utf-8')
        
        self.stdout.write(self.style.SUCCESS(f"🎉 ¡Éxito! Archivo 'datos_dashboard_sisben.csv' generado con {len(df)} registros."))
