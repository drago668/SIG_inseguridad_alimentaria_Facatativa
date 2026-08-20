import { capaMunicipios,  capaVeredas, capaVias } from "./main.js";

export const map = L.map('map', {preferCanvas: true}).setView([4.813, -74.354], 13);

const openStreetMap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '&copy; OpenStreetMap contributors | DANE Colombia',
crossOrigin: true,
maxZoom: 19,
});

const cartoPositron = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
crossOrigin: true,
subdomains: 'abcd',
maxZoom: 20
});

const cartoDark = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
crossOrigin: true,
subdomains: 'abcd',
maxZoom: 20
});

const cartoVoyager = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager_labels_under/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
crossOrigin: true,
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

export const layerControl = L.control.layers(baseMaps).addTo(map);

// Grupo para almacenar todas las capas de medición en el mapa
const capaMediciones = L.featureGroup().addTo(map);

let modoMedicion = false;
let puntoInicio = null;
let marcadorInicio = null;
let contadorMediciones = 0;

// Arreglo para guardar el registro de datos
export let historialMediciones = [];

export function activarModoMedicion() {
    modoMedicion = true;
    puntoInicio = null;
    map.getContainer().style.cursor = 'crosshair';
}

export function deshabilitarModoMedicion() {
    modoMedicion = false;
    puntoInicio = null;
    map.getContainer().style.cursor = '';
    if (marcadorInicio) {
        map.removeLayer(marcadorInicio);
        marcadorInicio = null;
    }
}

// Borrar una línea específica por su ID
export function eliminarMedicionPorId(id) {
    // Eliminar del mapa
    capaMediciones.eachLayer((layer) => {
        if (layer.options && layer.options.idMedicion === id) {
            capaMediciones.removeLayer(layer);
        }
    });

    // Eliminar del historial
    historialMediciones = historialMediciones.filter(m => m.id !== id);
    actualizarUIHistorial();
}

// Borrar absolutamente todo el mapa e historial
export function limpiarTodasLasMediciones() {
    deshabilitarModoMedicion();
    capaMediciones.clearLayers();
    historialMediciones = [];
    actualizarUIHistorial();
}

// Evento de Clic en el Mapa
map.on('click', function(e) {
    if (!modoMedicion) return;

    if (!puntoInicio) {
        // Primer Clic: Inicio
        puntoInicio = e.latlng;
        marcadorInicio = L.circleMarker(puntoInicio, {
            color: '#0f766e',
            fillColor: '#0f766e',
            fillOpacity: 1,
            radius: 5
        }).addTo(map);

    } else {
        // Segundo Clic: Fin y Dibujo
        const puntoFin = e.latlng;
        const distanciaMetros = puntoInicio.distanceTo(puntoFin);
        
        const textoDistancia = distanciaMetros >= 1000 
            ? `${(distanciaMetros / 1000).toFixed(2)} km` 
            : `${distanciaMetros.toFixed(1)} m`;

        contadorMediciones++;
        const idActual = `med_${Date.now()}`;

        // Crear elementos con ID asociado
        const marcadorOrigen = L.circleMarker(puntoInicio, { color: '#0f766e', radius: 4, idMedicion: idActual });
        const marcadorDestino = L.circleMarker(puntoFin, { color: '#0f766e', radius: 4, idMedicion: idActual });
        
        const linea = L.polyline([puntoInicio, puntoFin], {
            color: '#0d9488',
            weight: 3,
            dashArray: '6, 8',
            idMedicion: idActual
        });

        const popup = L.popup({ idMedicion: idActual })
            .setLatLng(puntoFin)
            .setContent(`<b>Medición #${contadorMediciones}:</b> ${textoDistancia}`);

        // Agrupar en la capa
        capaMediciones.addLayer(marcadorOrigen);
        capaMediciones.addLayer(marcadorDestino);
        capaMediciones.addLayer(linea);
        linea.bindPopup(popup);

        // Guardar en el registro
        historialMediciones.push({
            id: idActual,
            num: contadorMediciones,
            distancia: textoDistancia
        });

        // Limpieza de estado temporal
        if (marcadorInicio) map.removeLayer(marcadorInicio);
        deshabilitarModoMedicion();
        actualizarUIHistorial();
    }
});

// Renderizar la lista en el menú HTML
function actualizarUIHistorial() {
    const lista = document.getElementById('lista-mediciones');
    if (!lista) return;

    lista.innerHTML = '';

    if (historialMediciones.length === 0) {
        lista.innerHTML = `<li class="text-slate-500 italic text-center py-2">Sin mediciones aún</li>`;
        return;
    }

    historialMediciones.forEach((item) => {
        const li = document.createElement('li');
        li.className = 'flex items-center justify-between bg-teal-50/60 hover:bg-teal-50 px-2.5 py-1.5 rounded-lg border border-teal-100 transition-colors text-slate-700';
        li.innerHTML = `
            <span><strong class="text-teal-800">#${item.num}:</strong> ${item.distancia}</span>
            <button class="btn-del-item text-slate-400 hover:text-rose-600 font-bold px-1 text-sm transition-colors" data-id="${item.id}" title="Eliminar trazo">
                &times;
            </button>
        `;
        lista.appendChild(li);
    });

    // Eventos para eliminar ítems individuales
    document.querySelectorAll('.btn-del-item').forEach(btn => {
        btn.onclick = (e) => {
            const id = e.target.getAttribute('data-id');
            eliminarMedicionPorId(id);
        };
    });
}