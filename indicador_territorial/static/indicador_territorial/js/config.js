const CONFIG = JSON.parse(document.getElementById('app-config').textContent);

export const URLS = {
    dimensionesZonales: CONFIG.urlDimensionesZonales,
    prevalenciaZonales: CONFIG.urlPrevalenciaZonales,
    dimensionesMunicipales: CONFIG.urlDimensionesMunicipales,
};

export const RUTAS_CSV = [
    CONFIG.csvDimensionesZonales,
    CONFIG.csvDimensionesZonalesAlterno,
];

export const AUTOR_REPORTE = CONFIG.autorReporte;