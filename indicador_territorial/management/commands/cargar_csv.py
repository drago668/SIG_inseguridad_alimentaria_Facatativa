from django.core.management.base import BaseCommand, CommandError
import os
import csv
from indicador_territorial.models import Vivienda, TipoVivienda, Corte, MaterialVivienda

class Command(BaseCommand):
    help = "Comando definitivo para cargar el archivo completo de Viviendas del Sisbén"

    def add_arguments(self, parser):
        parser.add_argument("archivos_csv", nargs="+", type=str, help="Ruta del o los archivos CSV a leer")

    def handle(self, *args, **options):
        lista_archivos = options["archivos_csv"]

        for ruta_archivo in lista_archivos:
            self.stdout.write(self.style.WARNING(f"\nIniciando el procesamiento masivo de: {ruta_archivo}"))

            if not os.path.exists(ruta_archivo):
                self.stdout.write(self.style.ERROR(f"El archivo '{ruta_archivo}' no existe. Saltando..."))
                continue

            try:
                with open(ruta_archivo, mode='r', encoding="utf-8") as file:
                    lector_csv = csv.DictReader(file)
                    columnas = lector_csv.fieldnames

                    if not columnas:
                        self.stdout.write(self.style.ERROR(f"El archivo '{ruta_archivo}' está vacío o no tiene cabeceras."))
                        continue

                    # Mapeo dinámico de mayúsculas y minúsculas del CSV

                    col_material = "VIV002" if "VIV002" in columnas else "viv002"
                    col_alcantarillado = "VIV005" if "VIV005" in columnas else "viv005"
                    col_acueducto = "VIV008" if "VIV008" in columnas else "viv008"
                    col_corte = "CORTE" if "CORTE" in columnas else "corte"
                    col_llave = "LLAVE" if "LLAVE" in columnas else "llave"

                    contador_nuevos = 0
                    contador_existentes = 0

                    for numero_fila, fila in enumerate(lector_csv, start=1):
                        try:
                            # 1. BUSCAR O CREAR EL CORTE
                            corte_obj, _ = Corte.objects.get_or_create(
                                nombre_corte=fila[col_corte]
                            )

                            # 2. BUSCAR EN TABLAS CATEGÓRICAS ESTÁTICAS
                            codigo_material = int(fila[col_material])

                            try:
                                material_obj = MaterialVivienda.objects.get(id_material=codigo_material)
                            except MaterialVivienda.DoesNotExist:
                                # Omitir fila silenciosamente en cargas masivas para no inundar la consola, o dejar aviso breve
                                continue
                            except TipoVivienda.DoesNotExist:
                                continue

                            # 3. EXTRAER EL VALOR DE LA LLAVE DEL CSV
                            valor_llave = fila[col_llave]

                            # 4. GUARDAR O BUSCAR LA VIVIENDA USANDO EL PUENTE 'LLAVE'
                            vivienda, creada = Vivienda.objects.get_or_create(
                                llave=valor_llave, # Criterio único de búsqueda para evitar duplicados
                                defaults={
                                    "material_vivienda": material_obj,
                                    "alcantarillado": True if fila[col_alcantarillado] == '1' else False,
                                    "acueducto": True if fila[col_acueducto] == '1' else False,
                                    "corte": corte_obj
                                }
                            )

                            if creada:
                                contador_nuevos += 1
                                # Imprimir un mensaje cada 1000 filas para saber que el script sigue vivo sin saturar la pantalla
                                if contador_nuevos % 1000 == 0:
                                    self.stdout.write(self.style.SUCCESS(f"-> {contador_nuevos} nuevas viviendas importadas..."))
                            else:
                                contador_existentes += 1

                        except Exception as error_fila:
                            self.stdout.write(self.style.ERROR(f"Error en fila {numero_fila}: {error_fila}"))

                    self.stdout.write(self.style.SUCCESS(
                        f"\n¡Procesamiento finalizado con éxito para '{os.path.basename(ruta_archivo)}'!"
                        f"\n- Nuevas viviendas guardadas: {contador_nuevos}"
                        f"\n- Viviendas omitidas por ya existir: {contador_existentes}"
                    ))

            except Exception as e:
                raise CommandError(f"Error crítico abriendo el archivo {ruta_archivo}: {e}")
