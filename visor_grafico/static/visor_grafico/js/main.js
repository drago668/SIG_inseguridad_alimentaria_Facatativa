import { crearCapaVias, crearCapaMunicipios, crearCapaVeredas, crearCapaZonaRural, crearCapaZonaUrbana } from "./layerTemplate.js";
import { map, layerControl } from "./mapBase.js";
import { URLS, ES_ADMINISTRADOR } from './config.js';
import './export/imagen.js';  
import './exportar_pdf.js';
import './capas/capa.js';


const slctMunicipio = document.querySelector('#municipios-slct');
const slctVereda = document.querySelector('#veredas-slct');
const slctVia = document.querySelector('#vias-slct');

const checkMunicipio = document.querySelector('#chk-municipio');
const checkVeredas = document.querySelector('#chk-veredas');
const checkVias = document.querySelector('#chk-vias');
const checkUrbano = document.querySelector('#chk-urbano');
const checkRural = document.querySelector('#chk-rural');


// main.js
import { 
    activarModoMedicion, 
    limpiarTodasLasMediciones 
} from './mapBase.js';

// Elementos DOM
if (ES_ADMINISTRADOR){
    const btnMenu = document.getElementById('btn-medir-menu');
    const dropdown = document.getElementById('dropdown-medicion');
    const btnCerrar = document.getElementById('btn-cerrar-menu');
    const btnNueva = document.getElementById('btn-nueva-medicion');
    const btnLimpiar = document.getElementById('btn-limpiar-todo');

    // Abrir / Cerrar Menú
    btnMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    btnCerrar.addEventListener('click', () => {
        dropdown.classList.add('hidden');
    });

    // Acción: Iniciar Nueva Medición
    btnNueva.addEventListener('click', () => {
        activarModoMedicion();
        dropdown.classList.add('hidden');
    });

    // Acción: Borrar Todo
    btnLimpiar.addEventListener('click', () => {
        limpiarTodasLasMediciones();
    });
}


//filtrar capas con base en los select#################################################################

// filtrar capa municipios con base en los select
slctMunicipio.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Municipio seleccionado:", slcted);
    const urlFiltradaMpios= `${URLS.municipio}?mpio=${slcted}`;
    const urlFiltradaVias= `${URLS.vias}?mpio=${slcted}`;
    const urlFiltradaVdas= `${URLS.veredas}?mpio=${slcted}`;
    const urlFilterVdas= `${URLS.veredasPorMunicipio}?mpio=${slcted}`;

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

    fetch(`${URLS.zonaUrbana}?mpio=${slcted}`)
        .then(r => r.json())
        .then(data => {
            if (capaZonaUrbana) map.removeLayer(capaZonaUrbana);
            capaZonaUrbana = crearCapaZonaUrbana(data);
            if (checkUrbano.checked) capaZonaUrbana.addTo(map);
        });

    fetch(`${URLS.zonaRural}?mpio=${slcted}`)
        .then(r => r.json())
        .then(data => {
            if (capaZonaRural) map.removeLayer(capaZonaRural);
            capaZonaRural = crearCapaZonaRural(data);
            if (checkRural.checked) capaZonaRural.addTo(map);
        });
});

// filtrar con base en los select #####################################################################################
// filtrar capa veredas con base en los select
slctVereda.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Vereda seleccionada:", slcted);
    const urlFiltrada= `${URLS.veredas}?vda=${slcted}`;

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
    const urlFiltrada= `${URLS.vias}?tipo=${slcted}`;

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



//Modal de cargar capas###########################################################################################################################
if (ES_ADMINISTRADOR){
    const modal = document.getElementById('modal-cargar-capa');
    const btnAbrirModal = document.getElementById('abrir-modal');
    const btnAbrir = document.getElementById('btn-abrir-modal');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCancelar = document.getElementById('btn-cancelar-modal');

    btnAbrirModal.addEventListener('click', () => {
        modal.classList.remove('hidden');
        console.log('se presiono el boton')
    });

    const cerrarModal = () => {
        modal.classList.add('hidden');
    };

    btnCerrarModal.addEventListener('click', cerrarModal);
    btnCancelar.addEventListener('click', cerrarModal);
}


// #########################################################################################################################################

// Variable global para almacenar el mapa de dimensiones por DIVIPOLA
let mapaDimensiones = new Map();
let capaCoropletas = null;
let municipioSeleccionadoActual = null;

// 1. Función para consumir el nuevo endpoint de dimensiones
export async function cargarDimensionesMunicipales() {
    try {
        const res = await fetch(URLS.dimensionesMunicipales);
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        const json = await res.json();
        if (json.status === 'success') {
            console.log(json.data);
            return json.data;
        }
        throw new Error(json.message || "Error al cargar dimensiones");
    } catch (e) {
        console.error("Error al obtener dimensiones municipales:", e);
        return [];
    }
}

// 2. Función matemática de Overlay: Calcula la suma de dimensiones activas
function calcularValorOverlay(divipola) {
    const registro = mapaDimensiones.get(divipola);
    if (!registro) return null;

    // Obtener los checkboxes de dimensiones que estén marcados
    const checkboxesActivos = Array.from(document.querySelectorAll('.chk-dimension:checked'));
    
    // Si no hay ninguna dimensión activa, el valor es 0
    if (checkboxesActivos.length === 0) return 0.0;

    let sumaAportes = 0.0;
    checkboxesActivos.forEach(chk => {
        const campo = chk.value;
        if (registro[campo] !== undefined) {
            sumaAportes += parseFloat(registro[campo]) || 0.0;
        }
    });

    return Number(sumaAportes.toFixed(2));
}

// 3. Escala oficial de colores DANE
function getColorFIES(prevalencia) {
    if (prevalencia === undefined || prevalencia === null) return '#cccccc'; // Sin datos
    return prevalencia > 40.0 ? '#990000' :
        prevalencia > 25.0 ? '#ec7014' :
        prevalencia > 15.0 ? '#fe9929' :
                                '#a1d99b';
}

// 4. Actualizar el panel lateral de Tailwind
function actualizarPanelDetalle(nombre, divipola, valor) {
    document.getElementById('det-municipio-nombre').textContent = nombre;
    document.getElementById('det-municipio-divipola').textContent = `DIVIPOLA: ${divipola}`;
    
    const textoValor = (valor !== null && valor !== undefined) ? `${valor.toFixed(1)}%` : 'Sin datos';
    document.getElementById('det-prevalencia-valor').textContent = textoValor;

    const badge = document.getElementById('badge-nivel-riesgo');
    if (valor === null || valor === undefined) {
        badge.textContent = "Sin datos de encuesta";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600";
    } else if (valor > 40.0) {
        badge.textContent = "Crítico / Severo";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-700";
    } else if (valor > 25.0) {
        badge.textContent = "Moderado-Alto";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-orange-100 text-orange-700";
    } else if (valor > 15.0) {
        badge.textContent = "Moderado-Bajo";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700";
    } else {
        badge.textContent = "Bajo";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700";
    }
}

// 5. Inicialización: Carga paralela de GeoJSON y Dimensiones SHAP
Promise.all([
    fetch(URLS.municipio).then(res => res.json()),
    cargarDimensionesMunicipales()
]).then(([geojsonData, listaDimensiones]) => {
    
    // Indexar datos por DIVIPOLA a 5 dígitos
    mapaDimensiones.clear();
    listaDimensiones.forEach(item => {
        const divipolaNormalizado = String(item.DIVIPOLA_SIG).padStart(5, '0');
        mapaDimensiones.set(divipolaNormalizado, item);
    });

    // Crear capa GeoJSON
    capaCoropletas = L.geoJSON(geojsonData, {
        style: function (feature) {
            const divipola = feature.properties.mpio_cdpmp;
            const valor = calcularValorOverlay(divipola);
            return {
                fillColor: getColorFIES(valor),
                weight: 1.5,
                opacity: 1,
                color: '#ffffff',
                dashArray: '2',
                fillOpacity: 0.75
            };
        },
        onEachFeature: function (feature, layer) {
            const divipola = feature.properties.mpio_cdpmp;
            const nombre = feature.properties.mpio_cnmbr;

            // Hover interactions
            layer.on({
                mouseover: function (e) {
                    const l = e.target;
                    l.setStyle({ weight: 3, color: '#0f766e', dashArray: '', fillOpacity: 0.9 });
                    l.bringToFront();
                },
                mouseout: function (e) {
                    capaCoropletas.resetStyle(e.target);
                },
                click: function () {
                    municipioSeleccionadoActual = { nombre, divipola };
                    const valor = calcularValorOverlay(divipola);
                    actualizarPanelDetalle(nombre, divipola, valor);
                }
            });

            // Tooltip dinámico
            layer.bindTooltip(() => {
                const valor = calcularValorOverlay(divipola);
                const txt = valor !== null ? `${valor.toFixed(1)}%` : 'Sin datos';
                return `<strong>${nombre}</strong><br>Aporte acumulado: ${txt}`;
            });
        }
    });

    capaCoropletas.addTo(map);
    layerControl.addOverlay(capaCoropletas, "Vulnerabilidad FIES (SHAP)");

    // 6. EVENTO DINÁMICO: Escuchar cambios en los checkboxes de dimensiones
    const checkboxes = document.querySelectorAll('.chk-dimension');
    checkboxes.forEach(chk => {
        chk.addEventListener('change', () => {
            // Repintar todos los polígonos instantáneamente sin recargar la página
            if (capaCoropletas) {
                capaCoropletas.eachLayer(layer => {
                    if (layer.feature) {
                        const divipola = layer.feature.properties.mpio_cdpmp;
                        const nuevoValor = calcularValorOverlay(divipola);
                        layer.setStyle({
                            fillColor: getColorFIES(nuevoValor)
                        });
                    }
                });
            }

            // Si hay un municipio activo en el panel, actualizar su valor en pantalla
            if (municipioSeleccionadoActual) {
                const nuevoValor = calcularValorOverlay(municipioSeleccionadoActual.divipola);
                actualizarPanelDetalle(
                    municipioSeleccionadoActual.nombre,
                    municipioSeleccionadoActual.divipola,
                    nuevoValor
                );
            }
        });
    });
});

