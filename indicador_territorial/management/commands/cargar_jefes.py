from django.core.management.base import BaseCommand, CommandError
import os
import csv
from indicador_territorial.models import JefeHogar, Sexo, Corte, CatNivelEducativo, ActividadUltimoMes

class Command(BaseCommand):
    help = "Comando independiente para cargar los Jefes de Hogar desde el CSV de personas"

    def add_arguments(self, parser):
        parser.add_argument("archivo_personas", type=str, help="Ruta del CSV de Personas/Miembros del Sisbén")

    def handle(self, *args, **options):
        archivo = options["archivo_personas"]

        if not os.path.exists(archivo):
            raise CommandError(f"No se encuentra el archivo en la ruta: {archivo}")

        with open(archivo, mode='r', encoding="utf-8") as file:
            lector_csv = csv.DictReader(file)
            columnas = lector_csv.fieldnames
            self.stdout.write(self.style.SUCCESS(f"-> sexo: {columnas}"))

            if not columnas:
                raise CommandError("El archivo está vacío o no tiene cabeceras.")

            # Identificación de columnas (Mapeo de mayúsculas/minúsculas del Sisbén)
            col_llave = "LLAVE" if "LLAVE" in columnas else "llave"
            col_hogar = "HOGAR" if "HOGAR" in columnas else "hogar"
            col_orden = "ORDEN" if "ORDEN" in columnas else "orden"
            col_corte = "CORTE" if "CORTE" in columnas else "corte"
            
            # Filtro del Jefe que me indicaste
            col_filtro_jefe = "PER003" if "PER003" in columnas else "per003"
            
            # Tus catálogos mapeados según tu DDL original
            col_sexo = "PER001" if "PER001" in columnas else "per001"
            col_grupo_sisben = "GRUPO" if "GRUPO" in columnas else "Grupo"
            col_nivel = "NIVEL" if "NIVEL" in columnas else 'Nivel'
            col_i7 = "I7" if "I7" in columnas else "i7"
            col_i8 = "I8" if "I8" in columnas else "i8"
            col_per017 = "PER017" if "PER017" in columnas else "per017" # codigo de nivel educativo
            col_per019 = "PER019" if "PER019" in columnas else "per019"

            contador_jefes = 0

            for numero_fila, fila in enumerate(lector_csv, start=1):
                # -----------------------------------------------------------------
                # TU REGLA DE VALIDACIÓN: Si per003 NO es '1', se omite la fila
                # -----------------------------------------------------------------
                self.stdout.write(self.style.SUCCESS(f"-> sexo: {fila[col_sexo]}"))
                if fila[col_filtro_jefe] != '1':
                    continue

                try:
                    # 1. BUSCAR O CREAR EL CORTE
                    corte_obj, _ = Corte.objects.get_or_create(
                        nombre_corte=fila[col_corte]
                    )


                    # 2. BUSCAR EL SEXO EN TU TABLA ESTÁTICA
                    # (Convertimos a entero. Si tu CSV trae texto como 'M'/'F', ajusta el get)
                    codigo_sexo = int(fila[col_sexo])
                    codigo_nivel_educativo = int(fila[col_per017])
                    codigo_actividad = int(fila[col_per019])
                    try:
                        sexo_obj = Sexo.objects.get(id_sexo=codigo_sexo)
                    except Sexo.DoesNotExist:
                        # Si el código de sexo no está registrado en tu catálogo estático, saltamos la fila
                        continue
                    try :
                        nivel_educativo = CatNivelEducativo.objects.get(id_nivel_educativo=codigo_nivel_educativo)
                    except CatNivelEducativo.DoesNotExist:
                        continue
                    try:
                        act_princ = ActividadUltimoMes.objects.get(id_actividad=codigo_actividad)
                    except ActividadUltimoMes.DoesNotExist:
                        continue
                    # 3. CAPTURA SEGURA DE I7 E I8 EVITANDO ERRORES POR VALORES VACÍOS
                    valor_i7 = fila.get(col_i7, '0')
                    valor_i8 = fila.get(col_i8, '0')

                    desempleo = True if valor_i7 == '1' else False
                    informal = True if (valor_i8 and valor_i8.isdigit() and int(valor_i8) == 1) else False

                    # 3. GUARDAR EL JEFE DE HOGAR CON ID AUTOMÁTICO DE POSTGRESQL
                    # Usamos get_or_create con la combinación (llave + hogar + corte) para que si 
                    # vuelves a correr el script, no te duplique los jefes de hogar en la BD.
                    jefe, creado = JefeHogar.objects.get_or_create(
                        llave=fila[col_llave],
                        hogar=fila[col_hogar],
                        corte=corte_obj,
                        defaults={
                            "orden": fila[col_orden],
                            "id_sexo": sexo_obj,
                            "grupo_sisben" : fila[col_grupo_sisben],
                            "nivel_sisben": fila[col_nivel],
                            "nivel_educativo": nivel_educativo,
                            "actividad":act_princ,
                            "desempleo_larga_duracion": desempleo, # Valores base por defecto
                            "trabajo_informal": informal,
                        }
                    )

                    if creado:
                        contador_jefes += 1
                        # Aviso en consola cada 1000 registros para saber que avanza rápido y en silencio
                        if contador_jefes % 1000 == 0:
                            self.stdout.write(self.style.SUCCESS(f"-> {contador_jefes} Jefes de Hogar guardados con éxito..."))

                except Exception as error_fila:
                    self.stdout.write(self.style.ERROR(f"Error en fila {numero_fila}: {error_fila}"))
                    #pass

            self.stdout.write(self.style.SUCCESS(
                f"\n¡Carga de Jefes finalizada con éxito!"
                f"\n- Total de Jefes de Hogar nuevos registrados: {contador_jefes}"
            ))
