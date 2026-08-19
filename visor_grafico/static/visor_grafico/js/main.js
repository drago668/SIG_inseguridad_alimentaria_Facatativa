import { crearCapaVias, crearCapaMunicipios, crearCapaVeredas, crearCapaZonaRural, crearCapaZonaUrbana } from "./layerTemplate.js";
import { map, layerControl } from "./mapBase.js";

const slctMunicipio = document.querySelector('#municipios-slct');
const slctVereda = document.querySelector('#veredas-slct');
const slctVia = document.querySelector('#vias-slct');

const checkMunicipio = document.querySelector('#chk-municipio');
const checkVeredas = document.querySelector('#chk-veredas');
const checkVias = document.querySelector('#chk-vias');
const checkUrbano = document.querySelector('#chk-urbano');
const checkRural = document.querySelector('#chk-rural');

export let capaMunicipios;
export let capaVeredas;
export let capaVias;
export let capaZonaRural;
export let capaZonaUrbana;


// renderizar capa vias
fetch(urlViasGeoJSON)
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
fetch(urlVeredasGeoJSON)
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
fetch(urlMunicipioGeoJSON)
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

//filtrar capas con base en los select#################################################################

// filtrar capa municipios con base en los select
slctMunicipio.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Municipio seleccionado:", slcted);
    const urlFiltradaMpios= `${urlMunicipioGeoJSON}?mpio=${slcted}`;
    const urlFiltradaVias= `${urlViasGeoJSON}?mpio=${slcted}`;
    const urlFiltradaVdas= `${urlVeredasGeoJSON}?mpio=${slcted}`;
    const urlFilterVdas= `${urlVeredasMpio}?mpio=${slcted}`;

    fetch(urlFiltradaMpios)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de municipios");
            return response.json();
        })
        .then(data => {
            if (capaMunicipios) map.removeLayer(capaMunicipios);
            console.log("funciono:", data);

            capaMunicipios = crearCapaMunicipios(data);
            capaMunicipios.addTo(map);
            map.fitBounds(capaMunicipios.getBounds());
        })
        .catch(err => console.error("Error al filtrar los muncipios: ", err));
    fetch(urlFiltradaVias)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de vias");
            return response.json();
        })
        .then(data =>{
            if(capaVias) map.removeLayer(capaVias);
            capaVias =crearCapaVias(data);
            capaVias.addTo(map);
        })
        .catch(err => console.error("Error al filtrar las vias: ", err));
    fetch(urlFiltradaVdas)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de vias");
            return response.json();
        })
        .then(data =>{
            if(capaVeredas) map.removeLayer(capaVeredas);
            capaVeredas = crearCapaVeredas(data);
            capaVeredas.addTo(map);
        })
        .catch(err => console.error("Error al filtrar los muncipios: ", err));
    
    fetch(urlFilterVdas)
        .then(response => response.json())
        .then(data => {
            console.log("veredas encontradas: ", data);
            const selectVereda = document.getElementById('select-veredas');
            if (slctVereda) {
                slctVereda.innerHTML = '<option value="">Seleccione una vereda</option>';
                data.forEach(vereda => {
                    const option = document.createElement('option');
                    option.value = vereda.codigo_ver;
                    option.textContent = vereda.nombre_ver;
                    slctVereda.appendChild(option);
                });
            }
        }).catch(error => console.error('Error cargando veredas:', error));
});

// filtrar con base en los select #####################################################################################
// filtrar capa veredas con base en los select
slctVereda.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Vereda seleccionada:", slcted);
    const urlFiltrada= `${urlVeredasGeoJSON}?vda=${slcted}`;

    fetch(urlFiltrada)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de Veredas: ");
            return response.json();
        })
        .then(data => {

            if (capaVeredas) map.removeLayer(capaVeredas);

            capaVeredas = crearCapaVeredas(data);
            capaVeredas.addTo(map);
        })
        .catch(err => console.error("Error al filtrar las veredas:", err));
});

// filtrar capa vias con base en los select
slctVia.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Via seleccionada:", slcted);
    const urlFiltrada= `${urlViasGeoJSON}?tipo=${slcted}`;

    fetch(urlFiltrada)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de Veredas: ");
            return response.json();
        })
        .then(data => {

            if (capaVias) map.removeLayer(capaVias);

            capaVias = crearCapaVias(data);
            capaVias.addTo(map);
        })
        .catch(err => console.error("Error al filtrar las vias:", err));
});


// activar o desactivar capas#########################################################################
checkMunicipio.addEventListener('change', (e)=>{
    const ocultarMostrar = e.target.checked;
    console.log('esta marcado: el municipio',ocultarMostrar);

    if (capaMunicipios){
        if(ocultarMostrar){
            capaMunicipios.addTo(map);
        } else {
            map.removeLayer(capaMunicipios);
        }
    }
});


checkVeredas.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la vereda: ', ocultarMostrar);

    if(capaVeredas){
        if(ocultarMostrar){
            capaVeredas.addTo(map);
        } else {
            map.removeLayer(capaVeredas);
        }
    }
});


checkVias.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la via: ',ocultarMostrar);

    if(capaVias){
        if(ocultarMostrar){
            capaVias.addTo(map);
        } else {
            map.removeLayer(capaVias);
        }
    }
});


checkUrbano.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la urbana: ',ocultarMostrar);

    if(capaZonaUrbana){
        if(ocultarMostrar){
            capaZonaUrbana.addTo(map);
        } else {
            map.removeLayer(capaZonaUrbana);
        }
    }
});


checkRural.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la zona rural: ',ocultarMostrar);

    if(capaZonaRural){
        if(ocultarMostrar){
            capaZonaRural.addTo(map);
        } else {
            map.removeLayer(capaZonaRural);
        }
    }
});

// cargar capas de zona geografica (zona urbana, zona rural)#####################################################
fetch(urlZonaUrbana)
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


fetch(urlZonaRural)
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