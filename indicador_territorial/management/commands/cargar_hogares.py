from django.core.management.base import BaseCommand, CommandError
import os
import csv
from indicador_territorial.models import (
    Hogar, Vivienda, JefeHogar, Corte, TipoVivienda,
    FuenteObtencionAgua, TratamientoAguaConsumo, CombustibleParaCocinar,
    ZonaGeografica
)

class Command(BaseCommand):
    help = "Paso 3: Cargar hogares unificando Viviendas, Jefes y Catálogos según el diagrama ER"

    def add_arguments(self, parser):
        parser.add_argument("archivo_hogares", type=str, help="Ruta del CSV de Hogares del Sisbén")

    def handle(self, *args, **options):
        archivo = options["archivo_hogares"]

        if not os.path.exists(archivo):
            raise CommandError(f"No se encuentra el archivo en la ruta: {archivo}")

        with open(archivo, mode='r', encoding="utf-8") as file:
            lector_csv = csv.DictReader(file)
            columnas = lector_csv.fieldnames

            if not columnas:
                raise CommandError("El archivo está vacío o no tiene cabeceras.")

            # Mapeo de columnas del archivo CSV (Puentes de texto)
            col_llave = "LLAVE" if "LLAVE" in columnas else "llave"
            col_hogar = "HOGAR" if "HOGAR" in columnas else "hogar"
            col_corte = "CORTE" if "CORTE" in columnas else "corte"
            
            # Columnas de servicios públicos en el CSV
            col_agua_7_dias = "HOG008" if "HOG008" in columnas else "hog008"
            col_cocina = "HOG014" if "HOG014" in columnas else "hog014"
            col_nevera = "HOG018" if "HOG018" in columnas else "hog018"
            col_personas_total = "HOG027" if "HOG027" in columnas else "hog027"
            
            # Columnas de catálogos en el CSV (IDs numéricos)
            col_tipo_viv = "HOG001" if "HOG001" in columnas else "hog01"
            col_fuente_agua = "HOG007" if "HOG007" in columnas else "hog007" # Ajusta según tu CSV
            col_tratamiento = "HOG012" if "HOG012" in columnas else "hog012" # Ajusta según tu CSV
            col_combustible = "HOG017" if "HOG017" in columnas else "hog017" # Ajusta según tu CSV
            col_zona_geografica = "ZONA" if "ZONA" in columnas else "zona"

            col_ninos= "cantidad_ninos" if "cantidad_ninos" in columnas else "COLUMNA_NINOS"
            col_adultos_mayores= "cantidad_adultos_mayores" if "cantidad_adultos_mayores" in columnas else "CANTIDAD_ADULTOS_MAYORES"

            contador_hogares = 0
            contador_omitidos = 0

            for numero_fila, fila in enumerate(lector_csv, start=1):
                
                try:
                    # 1. BUSCAR EL CORTE
                    corte_obj = Corte.objects.get(nombre_corte=fila[col_corte])

                    # 2. SEGUIMIENTO DE LLAVES PUENTE: Buscar las instancias de los papás en Django
                    valor_llave_csv = fila[col_llave]
                    valor_hogar_csv = fila[col_hogar]

                    try:
                        # Buscamos la vivienda usando la llave única que indexamos en el Paso 1
                        vivienda_obj = Vivienda.objects.get(llave=valor_llave_csv)
                        
                        # Buscamos al jefe usando la combinación única indexada en el Paso 2
                        jefe_obj = JefeHogar.objects.get(
                            llave=valor_llave_csv, 
                            hogar=valor_hogar_csv, 
                            corte=corte_obj
                        )
                    except (Vivienda.DoesNotExist, JefeHogar.DoesNotExist):
                        # Si la vivienda o el jefe no existen en la BD, omitimos la fila por integridad relacional
                        contador_omitidos += 1
                        continue

                    # 3. BUSCAR LAS CATEGORÍAS ESTÁTICAS DEL DIAGRAMA
                    try:
                        tipo_viv_obj = TipoVivienda.objects.get(id_tipo_vivienda=int(fila[col_tipo_viv]))
                        fuente_obj = FuenteObtencionAgua.objects.get(id_fuente=int(fila.get(col_fuente_agua, 1)))
                        tratamiento_obj = TratamientoAguaConsumo.objects.get(id_tratamiento_agua=int(fila.get(col_tratamiento, 1)))
                        combustible_obj = CombustibleParaCocinar.objects.get(id_combustible=int(fila.get(col_combustible, 1)))
                        zona_obj = ZonaGeografica.objects.get(id_zona_geografica =int(fila[col_zona_geografica]) )
                    except Exception as e_cat:
                        self.stdout.write(self.style.ERROR(f"[Fila {numero_fila}] Error en categorías estáticas: {e_cat}"))
                        continue

                    # 4. GUARDAR EL HOGAR DEJANDO QUE POSTGRESQL ASIGNE EL ID AUTOMÁTICO (id_hogar)
                    # Como en el modelo Hogar sí guardas 'llave' y 'hogar', los usamos para controlar duplicados
                    hogar_registro, creado = Hogar.objects.get_or_create(
                        llave=valor_llave_csv,
                        hogar=valor_hogar_csv,
                        corte=corte_obj,
                        defaults={
                            "jefe_hogar": jefe_obj,
                            "vivienda": vivienda_obj,
                            "tipo_vivienda": tipo_viv_obj,
                            "fuente_agua": fuente_obj,
                            "tratamiento_agua": tratamiento_obj,
                            "combustible_para_cocinar": combustible_obj,
                            "agua_llega_7_dias": True if fila.get(col_agua_7_dias) == '1' else False,
                            "cantidad_ninos": fila.get(col_ninos),
                            "cantidad_adultos_mayores":fila.get(col_adultos_mayores),
                            "cocina": True if fila.get(col_cocina) == '1' else False,
                            "nevera": True if fila.get(col_nevera) == '1' else False,
                            "total_personas_hogar": int(fila[col_personas_total]) if fila.get(col_personas_total) else 1,
                            "zona_geografica": zona_obj,
                        }
                    )

                    if creado:
                        contador_hogares += 1
                        if contador_hogares % 1000 == 0:
                            self.stdout.write(self.style.SUCCESS(f"-> {contador_hogares} Hogares enlazados..."))

                except Exception as error_fila:
                    # Descomenta esto si necesitas auditar algún tipo de dato corrupto del CSV
                    self.stdout.write(self.style.ERROR(f"Error en fila {numero_fila}: {error_fila}"))
                    #pass

            self.stdout.write(self.style.SUCCESS(
                f"\n¡Procesamiento masivo de Hogares completado!"
                f"\n- Total de Hogares nuevos enlazados: {contador_hogares}"
                f"\n- Registros omitidos por falta de relación previa: {contador_omitidos}"
            ))
