"""
Siembra los catálogos DANE ECV (una sola ejecución).
Uso:  python manage.py sembrar_catalogos
Es idempotente: se puede correr varias veces sin duplicar (usa update_or_create).
"""
from django.core.management.base import BaseCommand
from indicador_territorial.models import (
    ActividadUltimoMes, CatNivelEducativo, CombustibleParaCocinar,
    FuenteObtencionAgua, MaterialVivienda, Regimen, Sexo, TipoVivienda,
    TratamientoAguaConsumo, CatMaterialPisos, CatCotizaPension,
    CatTamanoEmpresa, CatRazonNoAfiliacion, CatNivelDificultad,
)

# (codigo, nombre) según el Diccionario de datos ECV2025 del DANE
CATALOGOS = [
    # (Modelo, campo_pk, campo_nombre, [(codigo, etiqueta), ...])

    (TipoVivienda, 'id_tipo_vivienda', 'nombre_tipo_vivienda', [
        (1, 'Casa'),
        (2, 'Apartamento'),
        (3, 'Cuarto(s)'),
        (4, 'Vivienda tradicional indígena'),
        (5, 'Otro (carpa, contenedor, vagón, embarcación, cueva, refugio natural, etc.)'),
    ]),

    (MaterialVivienda, 'id_material', 'nombre_material', [  # P4005 paredes
        (1, 'Bloque, ladrillo, piedra, madera pulida'),
        (2, 'Tapia pisada, adobe'),
        (3, 'Bahareque revocado'),
        (4, 'Bahareque sin revocar'),
        (5, 'Madera burda, tabla, tablón'),
        (6, 'Material prefabricado'),
        (7, 'Guadua'),
        (8, 'Caña, esterilla, otro vegetal'),
        (9, 'Zinc, tela, lona, cartón, latas, desechos, plástico'),
        (10, 'Sin paredes'),
    ]),

    (CatMaterialPisos, 'id_material_pisos', 'nombre_material_pisos', [  # P4015
        (1, 'Alfombra o tapete de pared a pared'),
        (2, 'Madera pulida y lacada, parqué'),
        (3, 'Mármol'),
        (4, 'Baldosa, vinilo, tableta, ladrillo, laminado'),
        (5, 'Madera burda, tabla o tablón, otro vegetal'),
        (6, 'Cemento, gravilla'),
        (7, 'Tierra, arena o barro'),
    ]),

    (FuenteObtencionAgua, 'id_fuente', 'nombre_fuente', [  # P8530
        (1, 'Acueducto público'),
        (2, 'Acueducto comunal o veredal'),
        (3, 'Pozo con bomba'),
        (4, 'Pozo sin bomba, aljibe, jagüey o barreno'),
        (5, 'Agua lluvia'),
        (6, 'Río, quebrada, manantial o nacimiento'),
        (7, 'Pila pública'),
        (8, 'Carro tanque'),
        (9, 'Aguatero'),
        (10, 'Agua embotellada o en bolsa'),
    ]),

    (TratamientoAguaConsumo, 'id_tratamiento_agua', 'nombre_tratamiento', [  # P5069
        (1, 'La usan tal como la obtienen'),
        (2, 'La hierven'),
        (3, 'Le echan cloro'),
        (4, 'Utilizan filtros'),
        (5, 'La decantan o usan filtros naturales'),
        (6, 'Compran agua embotellada o en bolsa'),
    ]),

    (CombustibleParaCocinar, 'id_combustible', 'nombre_combustible', [  # P8536
        (1, 'Electricidad'),
        (2, 'Gas natural conectado a red pública'),
        (3, 'Petróleo, gasolina, kerosene, alcohol'),
        (4, 'Gas propano / GLP (en cilindro o pipeta)'),
        (5, 'Carbón mineral'),
        (6, 'Leña, madera'),
        (7, 'Carbón de leña'),
        (8, 'Material de desecho'),
    ]),

    (CatNivelEducativo, 'id_nivel_educativo', 'nombre_nivel', [  # P8587
        (1, 'Ninguno'),
        (2, 'Preescolar'),
        (3, 'Básica Primaria (1º - 5º)'),
        (4, 'Básica secundaria (6º - 9º)'),
        (5, 'Media (10º - 13º)'),
        (6, 'Técnico sin título'),
        (7, 'Técnico con título'),
        (8, 'Tecnológico sin título'),
        (9, 'Tecnológico con título'),
        (10, 'Universitario sin título'),
        (11, 'Universitario con título'),
        (12, 'Postgrado sin título'),
        (13, 'Postgrado con título'),
    ]),

    (ActividadUltimoMes, 'id_actividad', 'nombre_actividad', [  # P6240
        (1, 'Trabajando'),
        (2, 'Buscando trabajo'),
        (3, 'Estudiando'),
        (4, 'Oficios del hogar'),
        (5, 'Incapacitado permanente para trabajar'),
        (6, 'Otra actividad'),
    ]),

    (CatCotizaPension, 'id_cotiza_pension', 'nombre_cotiza_pension', [  # P6920
        (1, 'Sí'),
        (2, 'No'),
        (3, 'Ya es pensionado'),
    ]),

    (CatTamanoEmpresa, 'id_tamano_empresa', 'nombre_tamano_empresa', [  # P8632
        (1, 'Trabaja solo/a'),
        (2, '2 a 3 personas'),
        (3, '4 a 5 personas'),
        (4, '6 a 10 personas'),
        (5, '11 a 19 personas'),
        (6, '20 a 30 personas'),
        (7, '31 a 50 personas'),
        (8, '51 a 100 personas'),
        (9, '101 o más personas'),
    ]),

    (Sexo, 'id_sexo', 'nombre_sexo', [  # P6020
        (1, 'Hombre'),
        (2, 'Mujer'),
    ]),

    (Regimen, 'id_regimen', 'nombre_regimen', [  # P6100
        (1, 'Contributivo (EPS)'),
        (2, 'Especial (Fuerzas Armadas, Ecopetrol, universidades públicas, magisterio)'),
        (3, 'Subsidiado (EPS-S)'),
    ]),

    (CatRazonNoAfiliacion, 'id_razon_no_afiliacion', 'nombre_razon', [  # P768
        (1, 'Por falta de dinero'),
        (2, 'Muchos trámites'),
        (3, 'No le interesa o descuido'),
        (4, 'No sabe que debe afiliarse'),
        (5, 'No está vinculado/a laboralmente a una empresa o entidad'),
        (6, 'Está en trámite de afiliación'),
        (7, 'Problemas con el Sisbén'),
        (8, 'Falta de documentación'),
        (9, 'Otra razón'),
    ]),

    (CatNivelDificultad, 'id_nivel_dificultad', 'nombre_nivel_dificultad', [  # P1906S4-S8
        (1, 'No puede hacerlo'),
        (2, 'Sí, con mucha dificultad'),
        (3, 'Sí, con alguna dificultad'),
        (4, 'Sin dificultad'),
    ]),
]


class Command(BaseCommand):
    help = 'Siembra los catálogos DANE ECV (idempotente)'

    def handle(self, *args, **options):
        total_creados, total_actualizados = 0, 0

        for modelo, campo_pk, campo_nombre, valores in CATALOGOS:
            creados = 0
            for codigo, nombre in valores:
                _, creado = modelo.objects.update_or_create(
                    **{campo_pk: codigo},
                    defaults={campo_nombre: nombre},
                )
                if creado:
                    creados += 1
            total_creados += creados
            total_actualizados += len(valores) - creados
            self.stdout.write(f"  {modelo.__name__:25s} → {len(valores)} códigos "
                                f"({creados} nuevos)")

        self.stdout.write(self.style.SUCCESS(
            f"\n[LISTO] Catálogos sembrados: {total_creados} insertados, "
            f"{total_actualizados} ya existían."
        ))