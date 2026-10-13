import { map, layerControl } from '../mapBase.js';
import { URLS } from '../config.js';
import {
    crearCapaVias, crearCapaMunicipios, crearCapaVeredas,
    crearCapaZonaUrbana, crearCapaZonaRural
} from '../layerTemplate.js';

let vias, veredas, municipios, zonaUrbana, zonaRural;

async function pedir(url, mensajeError) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(mensajeError);
    return response.json();
}

function reemplazar(capaPrevia, capaNueva, { encajar, etiqueta, visible }) {
    if (capaPrevia) map.removeLayer(capaPrevia);
    if (visible) capaNueva.addTo(map);
    if (encajar) map.fitBounds(capaNueva.getBounds());
    if (etiqueta) layerControl.addOverlay(capaNueva, etiqueta);
    return capaNueva;
}

function alternarVisibilidad(capa, visible) {
    if (!capa) return;
    if (visible) {
        capa.addTo(map);
    } else {
        map.removeLayer(capa);
    }
}

export function cargarVias(mpio = null, opciones = {}) {
    const { encajar = false, etiqueta = null, visible = true } = opciones;
    const url = mpio ? `${URLS.vias}?mpio=${mpio}` : URLS.vias;
    return pedir(url, 'Error en la API de vías').then(data => {
        vias = reemplazar(vias, crearCapaVias(data), { encajar, etiqueta, visible });
    });
}

export function cargarVeredas(mpio = null, opciones = {}) {
    const { encajar = false, etiqueta = null, visible = true } = opciones;
    const url = mpio ? `${URLS.veredas}?mpio=${mpio}` : URLS.veredas;
    return pedir(url, 'Error en la API de veredas').then(data => {
        veredas = reemplazar(veredas, crearCapaVeredas(data), { encajar, etiqueta, visible });
    });
}

export function cargarMunicipios(mpio = null, opciones = {}) {
    const { encajar = true, etiqueta = null, visible = true } = opciones;
    const url = mpio ? `${URLS.municipio}?mpio=${mpio}` : URLS.municipio;
    return pedir(url, 'Error en la API de municipios').then(data => {
        municipios = reemplazar(municipios, crearCapaMunicipios(data), { encajar, etiqueta, visible });
    });
}

export function cargarZonaUrbana(mpio = null, opciones = {}) {
    const { encajar = false, etiqueta = null, visible = true } = opciones;
    const url = mpio ? `${URLS.zonaUrbana}?mpio=${mpio}` : URLS.zonaUrbana;
    return pedir(url, 'Error en la API de zona urbana').then(data => {
        zonaUrbana = reemplazar(zonaUrbana, crearCapaZonaUrbana(data), { encajar, etiqueta, visible });
    });
}

export function cargarZonaRural(mpio = null, opciones = {}) {
    const { encajar = false, etiqueta = null, visible = true } = opciones;
    const url = mpio ? `${URLS.zonaRural}?mpio=${mpio}` : URLS.zonaRural;
    return pedir(url, 'Error en la API de zona rural').then(data => {
        zonaRural = reemplazar(zonaRural, crearCapaZonaRural(data), { encajar, etiqueta, visible });
    });
}

export function cargarVeredasConFiltro(vda) {
    return pedir(`${URLS.veredas}?vda=${vda}`, 'Error en la API de veredas').then(data => {
        veredas = reemplazar(veredas, crearCapaVeredas(data), { encajar: false, etiqueta: null, visible: true });
    });
}

export function cargarViasConFiltro(tipo) {
    return pedir(`${URLS.vias}?tipo=${tipo}`, 'Error en la API de vías').then(data => {
        vias = reemplazar(vias, crearCapaVias(data), { encajar: false, etiqueta: null, visible: true });
    });
}

export function cambiarVisibilidadMunicipio(visible) { alternarVisibilidad(municipios, visible); }
export function cambiarVisibilidadVeredas(visible) { alternarVisibilidad(veredas, visible); }
export function cambiarVisibilidadVias(visible) { alternarVisibilidad(vias, visible); }
export function cambiarVisibilidadZonaUrbana(visible) { alternarVisibilidad(zonaUrbana, visible); }
export function cambiarVisibilidadZonaRural(visible) { alternarVisibilidad(zonaRural, visible); }

cargarVias(null, { etiqueta: 'Vías Principales' });
cargarVeredas(null, { encajar: true, etiqueta: 'Veredas' });
cargarMunicipios(null, { etiqueta: 'Municipio' });
cargarZonaUrbana();
cargarZonaRural();
