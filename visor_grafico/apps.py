from django.apps import AppConfig
import joblib
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

class VisorGraficoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visor_grafico'

    # Atributos de clase para acceso global en el proyecto
    ml_model = None
    ml_columns = None
    cache_fies_2025 = None  # <-- Aquí guardaremos el resultado agregado en memoria

    def ready(self):
        modelo_path = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets', 'xgb_model_fies.joblib')
        columnas_path = os.path.join(settings.BASE_DIR, 'visor_grafico', 'ml_assets', 'columnas_entrenamiento.joblib')

        # Protegemos la carga para que comandos como 'migrate' no fallen
        try:
            if os.path.exists(modelo_path) and os.path.exists(columnas_path):
                VisorGraficoConfig.ml_model = joblib.load(modelo_path)
                VisorGraficoConfig.ml_columns = joblib.load(columnas_path)
                logger.info("Modelo XGBoost FIES y columnas de entrenamiento cargados exitosamente.")
            else:
                logger.warning("Archivos .joblib del modelo no encontrados en visor_grafico/ml_assets/")
        except Exception as e:
            logger.error(f"Error cargando assets de ML: {e}")