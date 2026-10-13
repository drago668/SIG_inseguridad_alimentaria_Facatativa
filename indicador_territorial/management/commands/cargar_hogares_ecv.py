"""
Carga hogares ECV desde un ABT del pipeline ML.
Uso:  python manage.py cargar_hogares_ecv --ruta /tmp/abt_test_2025.csv --anio 2025
"""
from django.core.management.base import BaseCommand
from indicador_territorial.services.cargador_ecv import cargar_desde_csv


class Command(BaseCommand):
    help = 'Carga hogares ECV (y sus 7 dimensiones) desde un archivo ABT'

    def add_arguments(self, parser):
        parser.add_argument('--ruta', required=True,
                            help='Ruta del CSV ABT (dentro del contenedor)')
        parser.add_argument('--anio', type=int, required=True,
                            help='Año del corte a cargar (ej: 2025)')
        parser.add_argument('--chunk', type=int, default=5000,
                            help='Tamaño de chunk para bulk_create (default: 5000)')

    def handle(self, *args, **options):
        cargar_desde_csv(
            ruta_csv=options['ruta'],
            anio=options['anio'],
            chunk_size=options['chunk'],
            out=self.stdout.write,
        )
        self.stdout.write(self.style.SUCCESS('Carga finalizada con éxito.'))