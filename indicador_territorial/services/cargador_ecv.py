"""
Servicio único de carga de hogares ECV desde un ABT (CSV separado por ';').
Usado por: management command `cargar_hogares_ecv` y (futuro) vista admin.

Convenciones:
    - Booleanos Sí/No del DANE:  1→True, 2→False, otro→None
    - FIES (ya binario en ABT):  1→True, 0→False, otro→None
    - FK catálogos: solo se aceptan códigos existentes; otro→None
    - Municipio: se valida contra municipios.mpio_cdpmp; si no existe → se omite el hogar
    - Idempotente: re-correr no duplica (unique_together + ignore_conflicts)
"""
import pandas as pd
from django.db import transaction

from visor_grafico.models import Municipios
from indicador_territorial.models import (
    Corte, HogarECV,
    DimViviendaServicios, DimTrabajoIngresos, DimEducacion, DimDemografia,
    DimSaludDiscapacidad, DimDesastres, DimFIES,
    TipoVivienda, MaterialVivienda, CatMaterialPisos, FuenteObtencionAgua,
    TratamientoAguaConsumo, CombustibleParaCocinar, CatNivelEducativo,
    ActividadUltimoMes, CatCotizaPension, CatTamanoEmpresa, Sexo, Regimen,
    CatRazonNoAfiliacion, CatNivelDificultad,
)

MAP_SI_NO   = {1: True, 2: False}
MAP_BINARIO = {1: True, 0: False}


def _int(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or pd.isna(x):
        return None
    try:
        return int(float(x))
    except (ValueError, TypeError):
        return None


def _float(x):
    v = _int(x) if not isinstance(x, float) else x
    if v is None or pd.isna(v):
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _bool(row, col, mapa):
    return mapa.get(_int(row.get(col)))


def _fk(row, col, validos):
    v = _int(row.get(col))
    return v if v in validos else None


def cargar_desde_csv(ruta_csv, anio, chunk_size=5000, out=print):
    # ── 1. Leer ABT y filtrar año ────────────────────────────────
    df = pd.read_csv(ruta_csv, sep=';', low_memory=False)
    if 'ANIO' in df.columns:
        df = df[df['ANIO'] == anio].copy()
    df['DIVIPOLA'] = (df['DIVIPOLA'].astype(str)
                    .str.replace(r'\.0$', '', regex=True).str.zfill(5))
    out(f"Filas del ABT para el año {anio}: {len(df):,}")

    # ── 2. Corte + referencias válidas ───────────────────────────
    corte, creado = Corte.objects.get_or_create(
        id_corte=anio, defaults={'nombre_corte': f'ECV {anio}'})
    out(f"Corte: {corte.nombre_corte} ({'nuevo' if creado else 'existente'})")

    muni_validos = set(Municipios.objects.values_list('mpio_cdpmp', flat=True))
    CAT = {
        'p1070': set(TipoVivienda.objects.values_list('id_tipo_vivienda', flat=True)),
        'p4005': set(MaterialVivienda.objects.values_list('id_material', flat=True)),
        'p4015': set(CatMaterialPisos.objects.values_list('id_material_pisos', flat=True)),
        'p8530': set(FuenteObtencionAgua.objects.values_list('id_fuente', flat=True)),
        'p5069': set(TratamientoAguaConsumo.objects.values_list('id_tratamiento_agua', flat=True)),
        'p8536': set(CombustibleParaCocinar.objects.values_list('id_combustible', flat=True)),
        'p8587': set(CatNivelEducativo.objects.values_list('id_nivel_educativo', flat=True)),
        'p6240': set(ActividadUltimoMes.objects.values_list('id_actividad', flat=True)),
        'p6920': set(CatCotizaPension.objects.values_list('id_cotiza_pension', flat=True)),
        'p8632': set(CatTamanoEmpresa.objects.values_list('id_tamano_empresa', flat=True)),
        'p6020': set(Sexo.objects.values_list('id_sexo', flat=True)),
        'p6100': set(Regimen.objects.values_list('id_regimen', flat=True)),
        'p768':  set(CatRazonNoAfiliacion.objects.values_list('id_razon_no_afiliacion', flat=True)),
        'dif':   set(CatNivelDificultad.objects.values_list('id_nivel_dificultad', flat=True)),
    }

    # ── 3. Procesar por chunks ───────────────────────────────────
    n_ok, n_omitidos = 0, 0
    registros = df.to_dict('records')

    for ini in range(0, len(registros), chunk_size):
        bloque = registros[ini:ini + chunk_size]
        hogares, claves = [], []

        for r in bloque:
            divipola = str(r.get('DIVIPOLA', ''))
            if divipola not in muni_validos:
                n_omitidos += 1
                continue
            directorio = _int(r.get('DIRECTORIO'))
            secuencia = _int(r.get('SECUENCIA_P'))
            if directorio is None or secuencia is None:
                n_omitidos += 1
                continue
            hogares.append(HogarECV(
                directorio=directorio,
                secuencia_p=secuencia,
                corte=corte,
                municipio_id=divipola,
                clase=_int(r.get('CLASE')),
                fex_c=_float(r.get('FEX_C_num')) or 0.0,
            ))
            claves.append((directorio, secuencia, r))

        with transaction.atomic():
            HogarECV.objects.bulk_create(hogares, ignore_conflicts=True)
            dirs = [c[0] for c in claves]
            mapa_id = {(h['directorio'], h['secuencia_p']): h['id']
                for h in HogarECV.objects
                .filter(corte=corte, directorio__in=dirs)
                .values('id', 'directorio', 'secuencia_p')}

            vivienda, trabajo, educacion, demografia = [], [], [], []
            salud, desastres, fies = [], [], []

            for directorio, secuencia, r in claves:
                hid = mapa_id.get((directorio, secuencia))
                if hid is None:
                    continue
                n_ok += 1

                vivienda.append(DimViviendaServicios(
                    hogar_id=hid,
                    p1070_id=_fk(r, 'P1070', CAT['p1070']),
                    p4005_id=_fk(r, 'P4005', CAT['p4005']),
                    p4015_id=_fk(r, 'P4015', CAT['p4015']),
                    p8530_id=_fk(r, 'P8530', CAT['p8530']),
                    p5069_id=_fk(r, 'P5069', CAT['p5069']),
                    p8536_id=_fk(r, 'P8536', CAT['p8536']),
                    p1077S2=_bool(r, 'P1077S2', MAP_SI_NO),
                    p8520S3=_bool(r, 'P8520S3', MAP_SI_NO),
                    p8520S5=_bool(r, 'P8520S5', MAP_SI_NO),
                    p5047=_bool(r, 'P5047', MAP_SI_NO),
                    p1698=_bool(r, 'P1698', MAP_SI_NO),
                ))
                trabajo.append(DimTrabajoIngresos(
                    hogar_id=hid,
                    p6240_id=_fk(r, 'P6240', CAT['p6240']),
                    p6920_id=_fk(r, 'P6920', CAT['p6920']),
                    p8632_id=_fk(r, 'P8632', CAT['p8632']),
                    p6990=_bool(r, 'P6990', MAP_SI_NO),
                    p8624=_float(r.get('P8624')),
                    p7250=_float(r.get('P7250')),
                    p416=_float(r.get('P416')),
                ))
                educacion.append(DimEducacion(
                    hogar_id=hid,
                    p6160=_bool(r, 'P6160', MAP_SI_NO),
                    p8586=_bool(r, 'P8586', MAP_SI_NO),
                    p8612=_bool(r, 'P8612', MAP_SI_NO),
                    p8587_id=_fk(r, 'P8587', CAT['p8587']),
                ))
                demografia.append(DimDemografia(
                    hogar_id=hid,
                    cant_personas_hogar=_int(r.get('CANT_PERSONAS_HOGAR')),
                    p6020_id=_fk(r, 'P6020', CAT['p6020']),
                    p6040=_int(r.get('P6040')),
                ))
                salud.append(DimSaludDiscapacidad(
                    hogar_id=hid,
                    p6090=_bool(r, 'P6090', MAP_SI_NO),
                    p6100_id=_fk(r, 'P6100', CAT['p6100']),
                    p768_id=_fk(r, 'P768', CAT['p768']),
                    p1906S4_id=_fk(r, 'P1906S4', CAT['dif']),
                    p1906S5_id=_fk(r, 'P1906S5', CAT['dif']),
                    p1906S6_id=_fk(r, 'P1906S6', CAT['dif']),
                    p1906S7_id=_fk(r, 'P1906S7', CAT['dif']),
                    p1906S8_id=_fk(r, 'P1906S8', CAT['dif']),
                ))
                desastres.append(DimDesastres(
                    hogar_id=hid,
                    **{f'p{c}': _bool(r, f'P{c}', MAP_SI_NO) for c in
                        ['3173', '3174S1', '3174S2', '3174S3', '3174S4', '3174S5',
                        '4065S1', '4065S2', '4065S3', '4065S4', '4065S5']}
                ))
                fies.append(DimFIES(
                    hogar_id=hid,
                    **{f'p3516s{i}': _bool(r, f'P3516S{i}', MAP_BINARIO)
                        for i in range(1, 9)},
                    puntaje_fies=_int(r.get('puntaje_fies')),
                    inseguridad_mod_grave=bool(_int(r.get('puntaje_inseguridad_mod_grave')) or 0),
                ))

            DimViviendaServicios.objects.bulk_create(vivienda, ignore_conflicts=True)
            DimTrabajoIngresos.objects.bulk_create(trabajo, ignore_conflicts=True)
            DimEducacion.objects.bulk_create(educacion, ignore_conflicts=True)
            DimDemografia.objects.bulk_create(demografia, ignore_conflicts=True)
            DimSaludDiscapacidad.objects.bulk_create(salud, ignore_conflicts=True)
            DimDesastres.objects.bulk_create(desastres, ignore_conflicts=True)
            DimFIES.objects.bulk_create(fies, ignore_conflicts=True)

        out(f"  Chunk {ini // chunk_size + 1}: {len(hogares)} hogares procesados "
            f"(acumulado: {n_ok:,})")

    out(f"\n[LISTO] Hogares cargados: {n_ok:,} | Omitidos (municipio/llave inválida): {n_omitidos:,}")
    return {'cargados': n_ok, 'omitidos': n_omitidos, 'corte': anio}