"""
Calibra las probabilidades crudas del modelo XGBoost con Platt scaling
(regresión logística 1D, ponderada por FEX_C) por DEPARTAMENTO,
con fallback al calibrador global si el depto tiene pocos hogares.

Uso:  python manage.py calibrar_probabilidades_fies --ruta-abt /tmp/abt_test_2025.csv
"""
import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from indicador_territorial.models import Corte, HogarECV, DimFIES

MIN_N_DEPT = 500  # mínimo de hogares para calibrador propio por depto


class Command(BaseCommand):
    help = 'Calibra (Platt) las probabilidades del modelo y guarda prob_calibrada'

    def add_arguments(self, parser):
        parser.add_argument('--ruta-abt', required=True)
        parser.add_argument('--anio', type=int, default=2025)
        parser.add_argument('--chunk', type=int, default=5000)

    def handle(self, *args, **opts):
        anio = opts['anio']
        ml = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets')

        self.stdout.write('Cargando modelo y datos...')
        X = pd.read_csv(os.path.join(ml, 'X_test_2025.csv'))
        modelo = joblib.load(os.path.join(ml, 'xgb_model_fies.joblib'))
        cols = joblib.load(os.path.join(ml, 'columnas_entrenamiento.joblib'))
        abt = pd.read_csv(opts['ruta-abt'] if False else opts['ruta_abt'], sep=';',
                usecols=['DIRECTORIO', 'DIVIPOLA', 'FEX_C_num',
                        'puntaje_inseguridad_mod_grave'])

        norm = lambda s: s.astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(5)
        if len(X) != len(abt):
            self.stderr.write('ABORTADO: X_test y ABT no tienen las mismas filas')
            return
        if (norm(X['DIVIPOLA']).values != norm(abt['DIVIPOLA']).values).mean() > 0.001:
            self.stderr.write('ABORTADO: desalineación X_test vs ABT')
            return

        self.stdout.write('Prediciendo probabilidades crudas...')
        prob = modelo.predict_proba(X.reindex(columns=cols, fill_value=0))[:, 1]
        abt['prob'] = prob
        abt['depto'] = norm(abt['DIVIPOLA']).str[:2]
        y = abt['puntaje_inseguridad_mod_grave'].values.astype(int)
        w = pd.to_numeric(abt['FEX_C_num'], errors='coerce').fillna(1.0).values
        abt['fex'] = w

        from sklearn.linear_model import LogisticRegression

        self.stdout.write('Ajustando calibrador GLOBAL (Platt, ponderado por FEX_C)...')
        platt_global = LogisticRegression(max_iter=1000)
        platt_global.fit(prob.reshape(-1, 1), y, sample_weight=w)
        abt['prob_cal'] = platt_global.predict_proba(prob.reshape(-1, 1))[:, 1]

        # ── Calibradores por departamento ──
        n_propios = 0
        for dep, idx in abt.groupby('depto').indices.items():
            idx = np.asarray(idx)
            if len(idx) < MIN_N_DEPT:
                continue
            lr = LogisticRegression(max_iter=1000)
            lr.fit(prob[idx].reshape(-1, 1), y[idx], sample_weight=w[idx])
            abt.iloc[idx, abt.columns.get_loc('prob_cal')] = \
                lr.predict_proba(prob[idx].reshape(-1, 1))[:, 1]
            n_propios += 1
        self.stdout.write(f'Deptos con calibrador propio: {n_propios} (resto usa global)')

        # ── Reporte antes/después ──
        wprev = lambda df, c: np.average(df[c], weights=df['fex']) * 100
        self.stdout.write('\n=== CONTRASTE (ponderado FEX) ===')
        for nombre, sub in [('Nacional', abt),
                            ('Cundinamarca', abt[abt['depto'] == '25']),
                            ('Facatativá', abt[norm(abt['DIVIPOLA']) == '25269'])]:
            self.stdout.write(
                f"{nombre:14s} real {wprev(sub, 'puntaje_inseguridad_mod_grave'):5.2f}% | "
                f"cruda {wprev(sub, 'prob'):5.2f}% | calibrada {wprev(sub, 'prob_cal'):5.2f}%")

        joblib.dump({'platt_global': platt_global},
                    os.path.join(ml, 'calibrador_platt.joblib'))

        # ── Guardar en BD ──
        corte = Corte.objects.get(id_corte=anio)
        hogares = {h['directorio']: h['id'] for h in
                HogarECV.objects.filter(corte=corte).values('directorio', 'id')}
        fies_ids = {f['hogar_id']: f['id'] for f in
                    DimFIES.objects.filter(hogar__corte=corte).values('hogar_id', 'id')}

        registros = abt.to_dict('records')
        actualizados, sin_match = 0, 0
        for ini in range(0, len(registros), opts['chunk']):
            objs = []
            for r in registros[ini:ini + opts['chunk']]:
                fid = fies_ids.get(hogares.get(int(r['DIRECTORIO'])))
                if fid is None:
                    sin_match += 1
                    continue
                objs.append(DimFIES(id=fid, prob_calibrada=float(r['prob_cal'])))
            with transaction.atomic():
                DimFIES.objects.bulk_update(objs, ['prob_calibrada'])
            actualizados += len(objs)
            self.stdout.write(f'  actualizados: {actualizados:,}')

        self.stdout.write(self.style.SUCCESS(
            f'\n[LISTO] prob_calibrada: {actualizados:,} | sin match: {sin_match:,}'))