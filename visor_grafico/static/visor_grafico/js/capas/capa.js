import { map, layerControl } from '../mapBase.js';
import { URLS } from '../config.js';
import {crearCapaVias, crearCapaMunicipios, crearCapaVeredas,
        crearCapaZonaUrbana, crearCapaZonaRural
} from '../layerTemplate.js';

export let capaMunicipios;
export let capaVeredas;
export let capaVias;
export let capaZonaRural;
export let capaZonaUrbana;


fetch(URLS.vias)
    .then(response => {
        if (!response.ok) throw new Error("Error en la respuesta de la API de Vías");
        return response.json();
    })
    .then(data => {
        if (capaVias) {
            map.removeLayer(capaVias);
        }
        capaVias = crearCapaVias(data);
        capaVias.addTo(map);
        layerControl.addOverlay(capaVias, "Vías Principales");
    })
    .catch(err => console.error("Error al cargar la(s) Vias: ", err));

// renderizar capa veredas
fetch(URLS.veredas)
    .then(response => {
        if (!response.ok) throw new Error("Error en la respuesta de la API de Veredas");
        return response.json();
    })
    .then(data => {
        if (capaVeredas) {
            map.removeLayer(capaVeredas);
        }
        capaVeredas = crearCapaVeredas(data);
        capaVeredas.addTo(map);
        map.fitBounds(capaVeredas.getBounds());
        layerControl.addOverlay(capaVeredas, "Veredas");
    })
    .catch(err => console.error("Error al cargar la(s) veredas: ", err));

// renderizar capa municipios
fetch(URLS.municipio)
    .then(response =>{
        if(!response.ok) throw new Error("Error en la respuesta de la API de Municipios");
        return response.json();
    })
    .then(data => {
        if (capaMunicipios){
            map.removeLayer(capaMunicipios);
        }
        capaMunicipios = crearCapaMunicipios(data);
        capaMunicipios.addTo(map);
        map.fitBounds(capaMunicipios.getBounds());
        layerControl.addOverlay(capaMunicipios, "Municipio");
    })
    .catch(err => console.error("Error al cargar lo(s) Municipios: ", err));

// cargar capas de zona geografica (zona urbana, zona rural)#####################################################
fetch(URLS.zonaUrbana)
    .then(response =>{
        if(!response.ok) throw new Error("Error en la respuesta de la API de zona geografica(urbana)");
        return response.json();
    })
    .then(data => {
        if(capaZonaUrbana){
            map.removeLayer(capaZonaUrbana);
        }
        capaZonaUrbana = crearCapaZonaUrbana(data);
        capaZonaUrbana.addTo(map);
    })
    .catch(err => console.error("Error al cargar la zona urbana: ", err));


fetch(URLS.zonaRural)
    .then(response =>{
        if(!response.ok) throw new Error("Error en la respuesta de la API de zona geografica(rural)");
        return response.json();
    })
    .then(data => {
        if(capaZonaRural){
            map.removeLayer(capaZonaRural);
        }
        capaZonaRural = crearCapaZonaRural(data);
        capaZonaRural.addTo(map);
    })
    .catch(err => console.error("Error al cargar la zona rural: ", err));