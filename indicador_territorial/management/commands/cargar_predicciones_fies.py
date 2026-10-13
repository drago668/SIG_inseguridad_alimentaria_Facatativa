"""
Calcula las probabilidades de riesgo FIES con el modelo XGBoost (ml_assets)
y las guarda en DimFIES (prob_riesgo_modelo, predicho_mod_grave).

Uso:  python manage.py cargar_predicciones_fies --ruta-abt /tmp/abt_test_2025.csv --anio 2025
"""
import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from indicador_territorial.models import Corte, HogarECV, DimFIES


class Command(BaseCommand):
    help = 'Guarda en DimFIES las predicciones del modelo XGBoost por hogar'

    def add_arguments(self, parser):
        parser.add_argument('--ruta-abt', required=True,
                            help='ABT del año de evaluación (dentro del contenedor)')
        parser.add_argument('--anio', type=int, default=2025)
        parser.add_argument('--chunk', type=int, default=5000)

    def handle(self, *args, **opts):
        anio = opts['anio']
        ml = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets')

        self.stdout.write('Cargando modelo y datos...')
        X = pd.read_csv(os.path.join(ml, 'X_test_2025.csv'))
        modelo = joblib.load(os.path.join(ml, 'xgb_model_fies.joblib'))
        cols = joblib.load(os.path.join(ml, 'columnas_entrenamiento.joblib'))
        abt = pd.read_csv(opts['ruta_abt'], sep=';',
                            usecols=['DIRECTORIO', 'SECUENCIA_P', 'DIVIPOLA',
                                    'puntaje_inseguridad_mod_grave'])

        # ── Verificación de alineación posicional X_test vs ABT ──
        if len(X) != len(abt):
            self.stderr.write(f'ABORTADO: X_test tiene {len(X)} filas y el ABT {len(abt)}')
            return
        norm = lambda s: s.astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(5)
        coinciden = (norm(X['DIVIPOLA']).values == norm(abt['DIVIPOLA']).values).mean()
        self.stdout.write(f'Alineación X_test vs ABT (DIVIPOLA fila a fila): {coinciden:.2%}')
        if coinciden < 0.999:
            self.stderr.write('ABORTADO: desalineación > 0.1%. No se escribió nada.')
            return

        # ── Predicción ──
        self.stdout.write('Prediciendo probabilidades (puede tardar)...')
        prob = modelo.predict_proba(X.reindex(columns=cols, fill_value=0))[:, 1]

        # ── Umbral óptimo F1 (misma búsqueda que modelo_comparativo.py) ──
        from sklearn.metrics import f1_score
        y = abt['puntaje_inseguridad_mod_grave'].values
        mejor_f1, umbral = 0.0, 0.5
        for u in np.arange(0.40, 0.75, 0.05):
            f1 = f1_score(y, (prob >= u).astype(int))
            if f1 > mejor_f1:
                mejor_f1, umbral = f1, u
        self.stdout.write(f'Umbral óptimo: {umbral:.2f} (F1={mejor_f1:.3f})')

        abt['prob'] = prob
        abt['pred'] = (prob >= umbral).astype(bool)

        # ── Mapas ligeros (solo IDs) para actualizar en bloque ──
        corte = Corte.objects.get(id_corte=anio)
        hogares = {h['directorio']: h['id']
            for h in HogarECV.objects.filter(corte=corte)
            .values('directorio', 'id')}  # directorio es único por hogar dentro del corte
        fies_ids = {f['hogar_id']: f['id']
                    for f in DimFIES.objects.filter(hogar__corte=corte)
                    .values('hogar_id', 'id')}

        registros = abt.to_dict('records')
        actualizados, sin_match = 0, 0
        for ini in range(0, len(registros), opts['chunk']):
            objs = []
            for r in registros[ini:ini + opts['chunk']]:
                hid = hogares.get(int(r['DIRECTORIO']))
                fid = fies_ids.get(hid)
                if fid is None:
                    sin_match += 1
                    continue
                objs.append(DimFIES(id=fid,
                                    prob_riesgo_modelo=float(r['prob']),
                                    predicho_mod_grave=bool(r['pred'])))
            with transaction.atomic():
                DimFIES.objects.bulk_update(
                    objs, ['prob_riesgo_modelo', 'predicho_mod_grave'])
            actualizados += len(objs)
            self.stdout.write(f'  actualizados: {actualizados:,}')

        self.stdout.write(self.style.SUCCESS(
            f'[LISTO] DimFIES actualizados: {actualizados:,} | sin match: {sin_match:,}'))