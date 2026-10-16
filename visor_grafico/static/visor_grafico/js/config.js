const CONFIG = JSON.parse(document.getElementById('app-config').textContent);

export const URLS = {
    vias: CONFIG.urlViasGeoJSON,
    municipio: CONFIG.urlMunicipioGeoJSON,
    veredas: CONFIG.urlVeredasGeoJSON,
    veredasPorMunicipio: CONFIG.urlVeredasMpio,
    zonaRural: CONFIG.urlZonaRural,
    zonaUrbana: CONFIG.urlZonaUrbana,
    datosMapa2025: CONFIG.urlDatosMapa2025,
    dimensionesMunicipales: CONFIG.urlDimensionesMunicipales,
    prevalenciaZonales: CONFIG.urlPrevalenciaZonales,
};

export const AUTOR_REPORTE = CONFIG.autorReporte;
export const ES_ADMINISTRADOR = CONFIG.esAdministrador;