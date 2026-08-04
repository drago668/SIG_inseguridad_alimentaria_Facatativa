
const sidebar = document.querySelector('#sidebar');
const colapse = document.querySelector('#colapse');
const arrowIcon = document.getElementById('arrow');

// aqui se oculta la barra lateral para diseño responsivo en moviles
window.addEventListener('resize', (e) =>{
    const esPantallaGrande = window.innerWidth >= 768;

    if (esPantallaGrande) {
        console.log("El usuario está en una PC o tablet grande");
        arrowIcon.classList.remove('hidden');
        // Aquí pones el código para acomodar tu barra lateral en PC
    } else {
        console.log("El usuario está en un celular");
        sidebar.classList.add('hidden');
        arrowIcon.classList.add('hidden');5
    }
});


colapse.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');

    setTimeout(() => {
        if (typeof map !== 'undefined') {
            map.invalidateSize();
        }
    }, 300); 
    
});


const map = L.map('map').setView([4.813, -74.354], 13);

const openStreetMap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '&copy; OpenStreetMap contributors | DANE Colombia',
maxZoom: 19
});
const cartoPositron = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
subdomains: 'abcd',
maxZoom: 20
});


const cartoDark = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
subdomains: 'abcd',
maxZoom: 20
});
const cartoVoyager = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager_labels_under/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
subdomains: 'abcd',
maxZoom: 20
});


cartoPositron.addTo(map);


const baseMaps = {
"CartoDB Positron": cartoPositron,
"OpenStreetMap":openStreetMap,
"CartoDB Dark Matter": cartoDark,
"CartoDB Voyager": cartoVoyager,
};

L.control.layers(baseMaps).addTo(map);

const estiloFacatativa = {
color: "#059669",      
weight: 3,             
opacity: 0.7,
fillColor: "#10b981",  
fillOpacity: 0.1      
};

function estiloSegunVia(feature) {
    const fclass = feature.properties.fclass;
        switch (fclass) {
            case 'motorway':
                return {color: '#D73027', weight:5, opacity:1};
            case 'trunk':
                return { color: '#F46D43', weight: 5, opacity: 1 }; 
            case 'primary':
                return { color: '#FDAE61', weight: 4, opacity: 0.7 };
            case 'secondary':
                return { color: '#A6D96A', weight: 3, opacity: 0.6 };
            case 'tertiary':
                return { color: '#1A9850', weight: 3, opacity: 0.6 }; 
            case 'unclassified':
                return { color: '#66C2A5', weight: 2, opacity: 0.5 }; 
            case 'residential':
                return { color: '#74ADD1', weight: 1, opacity: 0.5 };
            default:
                return { color: '#BDBDBD', weight: 1, opacity: 0.3 };
        }
}

//guardar valores de capas
let capaMunicipios;
let capaVias;
let capaVeredas;

// vias
fetch(urlViasGeoJSON)
    .then(response => {
        if (!response.ok) throw new Error("Error en la respuesta de la API de vías");
        return response.json();
    })
    .then(data => {
        capaVias = L.geoJSON(data, {
            style: estiloSegunVia,
            onEachFeature: function (feature, layer) {
                const props = feature.properties;
                const nombreVia = props.name || "Vía sin nombre";
                const velocidad = props.maxspeed ? `${props.maxspeed} km/h` : "No registrada";
                layer.bindPopup(`
                    <b>Vía:</b> ${nombreVia}<br>
                    <b>Tipo:</b> ${props.fclass}<br>
                    <b>Velocidad Máx:</b> ${velocidad}
                `);
            }
        }).addTo(map);
    })
    .catch(err => console.error("Error al cargar las vías:", err));

// filtrado de vias
const selectedVia = document.querySelector('#vias-slct');

selectedVia.addEventListener('change', (e) => {
    const tipoSeleccionado = e.target.value;
    const urlEnvio = `${urlViasGeoJSON}?tipo=${tipoSeleccionado}`;

    if (capaVias) {
        map.removeLayer(capaVias);
    }

    fetch(urlEnvio)
        .then(response => response.json())
        .then(data => {
            capaVias = L.geoJSON(data, { 
                style: estiloSegunVia,
                onEachFeature: function (feature, layer) {
                    const props = feature.properties;
                    const nombreVia = props.name || "Vía sin nombre";
                    const velocidad = props.maxspeed ? `${props.maxspeed} km/h` : "No registrada";
                    layer.bindPopup(`
                        <b>Vía:</b> ${nombreVia}<br>
                        <b>Tipo:</b> ${props.fclass}<br>
                        <b>Velocidad Máx:</b> ${velocidad}
                    `);
            }
            }).addTo(map);
        })
        .catch(err => console.error("Error al filtrar las vías:", err));
});

const slctMunicipio =document.querySelector('#municipios-slct');

function dibujarMunicipio(data) {
    // 1. Si ya había una capa en el mapa, la borramos primero
    if (capaMunicipios) {
        map.removeLayer(capaMunicipios);
    }

    // 2. Creamos la capa con el GeoJSON que nos llegue
    capaMunicipios = L.geoJSON(data, { style: estiloFacatativa });

    // 3. Le aplicamos los popups (Tu código limpio)
    capaMunicipios.eachLayer(function (layer) {
        const props = layer.feature.properties;
        layer.bindPopup(`
            <div style="text-align: center;">
                <h3 style="margin:0; color:#059669;">${props.mpio_cnmbr}</h3>
                <p style="margin: 5px 0;"><b>Código DANE:</b> ${props.mpio_cdpmp}</p>
                <p style="margin: 0;"><b>Departamento:</b> Cundinamarca (${props.dpto_ccdgo})</p>
            </div>
        `);
    });

    // 4. La subimos al mapa y encuadrarnos la cámara
    capaMunicipios.addTo(map);
    map.fitBounds(capaMunicipios.getBounds());
}

fetch(urlFacatativaGeoJSON)
    .then(response => {
        if (!response.ok) throw new Error("Error en la API del municipio");
        return response.json();
    })
    .then(data => {
        // Ejecutamos nuestra función con los datos completos
        dibujarMunicipio(data);
    })
    .catch(error => console.error("Error cargando la capa espacial inicial:", error));


slctMunicipio.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Municipio seleccionado:", slcted);

    // Si el usuario vuelve a seleccionar la opción vacía, recargamos la capa completa original
    if (slcted === "") {
        fetch(urlFacatativaGeoJSON)
            .then(res => res.json())
            .then(data => dibujarMunicipio(data));
        return;
    }

    // Si elige un municipio real, armamos la URL con filtro hacia Django
    const urlEnvioMunicipio = `${urlFacatativaGeoJSON}?mpio=${slcted}`;
    const urlViasFiltradas = `${urlViasGeoJSON}?mpio=${slcted}`;

    fetch(urlEnvioMunicipio)
        .then(response => response.json())
        .then(data => {
            dibujarMunicipio(data);
        })
        .catch(err => console.error("Error al filtrar los municipios:", err));
        
    fetch(urlViasFiltradas)
        .then(response => response.json())
        .then(data => {
            // Borramos las vías anteriores si existen en el mapa
            if (capaVias) {
                map.removeLayer(capaVias);
            }
            // Dibujamos las nuevas vías que intersectan al municipio elegido
            capaVias = L.geoJSON(data, { 
                style: estiloSegunVia,
                onEachFeature: function (feature, layer) {
                    const props = feature.properties;
                    const nombreVia = props.name || "Vía sin nombre";
                    const velocidad = props.maxspeed ? `${props.maxspeed} km/h` : "No registrada";
                    layer.bindPopup(`
                        <b>Vía:</b> ${nombreVia}<br>
                        <b>Tipo:</b> ${props.fclass}<br>
                        <b>Velocidad Máx:</b> ${velocidad}
                    `);
                }
            });
            capaVias.addTo(map);
        })
        .catch(err => console.error("Error al actualizar las vías del municipio:", err));
});

// activar o desactivar capas #########################################################################################
const checkMunicipio = document.querySelector('#chk-municipio');

checkMunicipio.addEventListener('change', (e)=>{
    const ocultarMostrar = e.target.checked;

    console.log('esta marcado?: ',ocultarMostrar);

    if (capaMunicipios){
        if(ocultarMostrar){
            capaMunicipios.addTo(map);
        } else {
            map.removeLayer(capaMunicipios);
        }
    }
});

const checkVias = document.querySelector('#chk-vias');

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

const checkVeredas = document.querySelector('#chk-veredas');

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


// veredas
const estiloVereda = {
color: "#8a2b0e",      
weight: 3,             
opacity: 0.9,
fillColor:  "#601e0a",  
fillOpacity: 0.6      
};

fetch(urlVeredasGeoJSON)
    .then(response =>{
        if (!response.ok) throw new Error("Error en la respuesta de la API de veredas");
        return response.json();
    })
    .then(data => {
        capaVeredas = L.geoJSON(data,{
            style: estiloVereda,
            onEachFeature: function (feature, layer) {
                const props = feature.properties;
                const nombreVereda= props.nombre_ver || "Vereda sin nombre";
                const nombreMunicipio = props.nom_mpio || "Municipio no disponible";
                const nombreDepartamento= props.nom_dep ? `${props.nom_dep} (${props.cod_dpto})` : "Departamento no disponible";
                const areaHectareas=props.area_ha ? `${props.area_ha} h` : "No existe informacion";
                layer.bindPopup(`
                    <b>Vereda:</b> ${props.nombre_ver || "Vereda sin nombre"}<br>
                    <b>Departamento:</b> ${props.nom_dep ? `${props.nom_dep} (${props.cod_dpto})` : "Departamento no disponible"}<br>
                    <b>Municipio:</b> ${props.nom_mpio}<br>
                    <b>area:</b> ${props.area_ha ? `${props.area_ha} h`:"No existe informacion"}<br>
                `);
            }
        }).addTo(map);
    })
    .catch(err => console.error("Error al cargar las vías:", err));






function dibujarVereda(data) {
    // 1. Si ya había una capa en el mapa, la borramos primero
    if (capaVeredas) {
        map.removeLayer(capaVeredas);
    }

    // 2. Creamos la capa con el GeoJSON que nos llegue
    capaVeredas = L.geoJSON(data, { style: estiloVereda });

    // 3. Le aplicamos los popups (Tu código limpio)
    capaVeredas.eachLayer(function (layer) {
        const props = layer.feature.properties;
        layer.bindPopup(`
            <b>Vereda:</b> ${props.nombre_ver || "Vereda sin nombre"}<br>
            <b>Departamento:</b> ${props.nom_dep ? `${props.nom_dep} (${props.cod_dpto})` : "Departamento no disponible"}<br>
            <b>Municipio:</b> ${props.nom_mpio}<br>
            <b>area:</b> ${props.area_ha ? `${props.area_ha} h`:"No existe informacion"}<br>
        `);
    });

    // 4. La subimos al mapa y encuadrarnos la cámara
    capaVeredas.addTo(map);
    map.fitBounds(capaVeredas.getBounds());
}

const slctVereda = document.querySelector('#veredas-slct');

fetch(urlVeredasGeoJSON)
    .then(response => {
        if (!response.ok) throw new Error("Error en la API de veredas");
        return response.json();
    })
    .then(data => {
        // Ejecutamos nuestra función con los datos completos
        dibujarVereda(data);
    })
    .catch(error => console.error("Error cargando la capa espacial inicial:", error));

const urlEnvioVereda = "";
slctVereda.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Vereda seleccionada:", slcted);
    const urlEnvioVereda = `${urlVeredasGeoJSON}?vda=${slcted}`;
    // Si el usuario vuelve a seleccionar la opción vacía, recargamos la capa completa original
    if (slcted === "") {
        fetch(urlEnvioVereda)
            .then(res => res.json())
            .then(data => dibujarVereda(data));
        return;
    }

// Si elige un municipio real, armamos la URL con filtro hacia Django


fetch(urlEnvioVereda)
    .then(response => response.json())
    .then(data => {
        dibujarVereda(data);
    })
    .catch(err => console.error("Error al filtrar las veredas:", err));

});