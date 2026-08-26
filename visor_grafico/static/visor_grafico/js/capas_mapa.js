import { map, layerControl } from "./mapBase.js";
// Objeto global para almacenar las capas de Leaflet activas por su ID
const capasActivas = {};

// 1. Obtener la lista de capas creadas desde el backend Django
async function cargarListaCapas() {
    const container = document.getElementById('lista-capas-container');
    
    // Verificación defensiva si el contenedor no existe en el DOM
    if (!container) return;

    try {
        const response = await fetch('/capas/api/listar/');
        
        if (!response.ok) {
            throw new Error(`Error servidor: ${response.status}`);
        }

        const data = await response.json();

        if (!data.capas || data.capas.length === 0) {
            container.innerHTML = `<p class="text-slate-400 text-center py-3">No hay capas procesadas aún.</p>`;
            return;
        }

        container.innerHTML = '';
        data.capas.forEach(capa => {
            const itemHTML = `
                <div class="flex items-center justify-between p-2.5 bg-slate-50 hover:bg-slate-100/80 rounded-xl border border-slate-200/60 transition-all">
                    <div class="flex items-center gap-2.5 overflow-hidden">
                        <input type="checkbox" 
                            id="capa-chk-${capa.id}" 
                            data-capa-id="${capa.id}"
                            data-capa-nombre="${capa.nombre}"
                            class="chk-capa-espacial w-4 h-4 text-teal-600 rounded border-slate-300 focus:ring-teal-500 cursor-pointer">
                        <div class="truncate">
                            <label for="capa-chk-${capa.id}" class="font-medium text-slate-700 cursor-pointer truncate block" title="${capa.nombre}">
                                ${capa.nombre}
                            </label>
                            <span class="text-[10px] text-slate-400 font-mono">${capa.formato} • ${capa.num_registros} ent.</span>
                        </div>
                    </div>
                    <!-- Botón de Borrado -->
                    <button type="button" 
                            data-eliminar-id="${capa.id}" 
                            data-eliminar-nombre="${capa.nombre}"
                            class="btn-eliminar-capa p-1 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors ml-1" 
                            title="Eliminar capa">
                        <svg class="w-3.5 h-3.5 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                    </button>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', itemHTML);
        });

    } catch (error) {
        console.error("Error al obtener la lista de capas:", error);
        container.innerHTML = `<p class="text-rose-500 text-center py-3">Error al cargar capas.</p>`;
    }
}

// 2. Alternar entre renderizar y remover la capa en Leaflet
async function alternarCapa(capaId, nombreCapa, visible) {
    if (visible) {
        if (!capasActivas[capaId]) {
            try {
                // Petición a la vista que genera el GeoJSON desde PostGIS
                const response = await fetch(`/capas/api/geojson/${capaId}/`);
                const geojsonData = await response.json();

                // Crear capa GeoJSON en Leaflet
                const layerLeaflet = L.geoJSON(geojsonData, {
                    style: function(feature) {
                        return {
                            color: '#0f766e',
                            weight: 2,
                            fillColor: '#14b8a6',
                            fillOpacity: 0.35
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        // Crear emergente dinámico con atributos
                        if (feature.properties) {
                            let popupContent = `<div class="p-1 max-h-48 overflow-y-auto text-xs">`;
                            popupContent += `<strong class="text-teal-700">${nombreCapa}</strong><hr class="my-1"/>`;
                            for (const [clave, valor] of Object.entries(feature.properties)) {
                                popupContent += `<b>${clave}:</b> ${valor}<br/>`;
                            }
                            popupContent += `</div>`;
                            layer.bindPopup(popupContent);
                        }
                    }
                });

                // Guardar referencia y añadir al mapa
                capasActivas[capaId] = layerLeaflet;
                capasActivas[capaId].addTo(map);

                // Auto-enfocar el mapa a los límites de la nueva capa
                if (layerLeaflet.getBounds().isValid()) {
                    map.fitBounds(layerLeaflet.getBounds());
                }

            } catch (error) {
                console.error(`Error al cargar el GeoJSON de la capa ${capaId}:`, error);
                const chk = document.getElementById(`capa-chk-${capaId}`);
                if (chk) chk.checked = false;
            }
        } else {
            capasActivas[capaId].addTo(map);
        }
    } else {
        // Remover del mapa si el usuario desmarca la casilla
        if (capasActivas[capaId]) {
            map.removeLayer(capasActivas[capaId]);
        }
    }
}

// Exponer la función al scope global de window por compatibilidad con módulos
window.alternarCapa = alternarCapa;

// 3. Event Listeners e Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Cargar la lista inicial de capas
    cargarListaCapas();

    // Delegación de eventos centralizada para los checkboxes
    const container = document.getElementById('lista-capas-container');
    if (container) {
        container.addEventListener('change', (event) => {
            if (event.target && event.target.classList.contains('chk-capa-espacial')) {
                const checkbox = event.target;
                const capaId = checkbox.getAttribute('data-capa-id');
                const nombreCapa = checkbox.getAttribute('data-capa-nombre');
                
                alternarCapa(capaId, nombreCapa, checkbox.checked);
            }
        });
    }
});



// 2. Función para solicitar la eliminación y limpiar el mapa
async function eliminarCapa(capaId, nombreCapa) {
    if (!confirm(`¿Estás seguro de que deseas eliminar la capa "${nombreCapa}" y todas sus geometrías asociadas?`)) {
        return;
    }

    try {
        const mapaInstancia = window.map || map;

        // Si la capa está renderizada en el mapa, la removemos primero
        if (capasActivas[capaId]) {
            if (mapaInstancia && typeof mapaInstancia.removeLayer === 'function') {
                mapaInstancia.removeLayer(capasActivas[capaId]);
            }
            delete capasActivas[capaId];
        }

        // Obtener el Token CSRF de las cookies de Django
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        const response = await fetch(`/capas/api/eliminar/${capaId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (response.ok && result.status === 'ok') {
            // Remover el elemento directamente del DOM
            const itemDOM = document.getElementById(`capa-item-${capaId}`);
            if (itemDOM) itemDOM.remove();

            // Si no quedan más capas, mostrar el mensaje vacío
            const container = document.getElementById('lista-capas-container');
            if (container && container.children.length === 0) {
                container.innerHTML = `<p class="text-slate-400 text-center py-3">No hay capas procesadas aún.</p>`;
            }
        } else {
            alert(`Error al eliminar: ${result.message}`);
        }

    } catch (error) {
        console.error("Error al eliminar la capa:", error);
        alert("Ocurrió un error al intentar eliminar la capa.");
    }
}

// 3. Capturar el click sobre el botón de eliminar usando delegación de eventos
document.addEventListener('DOMContentLoaded', () => {
    // ... tus eventos existentes ...

    const container = document.getElementById('lista-capas-container');
    if (container) {
        container.addEventListener('click', (event) => {
            const btnEliminar = event.target.closest('.btn-eliminar-capa');
            if (btnEliminar) {
                const capaId = btnEliminar.getAttribute('data-eliminar-id');
                const nombreCapa = btnEliminar.getAttribute('data-eliminar-nombre');
                eliminarCapa(capaId, nombreCapa);
            }
        });
    }
});