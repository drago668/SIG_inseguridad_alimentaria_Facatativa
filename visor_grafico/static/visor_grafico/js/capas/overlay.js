import { map, layerControl } from '../mapBase.js';
import { URLS } from '../config.js';

let mapaDimensiones = new Map();
let capaCoropletas = null;
let municipioSeleccionadoActual = null;

const CAMPOS_DIMENSIONES = [
    { campo: 'aporte_Vivienda_y_Servicios', etiqueta: 'Vivienda y Servicios' },
    { campo: 'aporte_Trabajo_e_Ingresos', etiqueta: 'Trabajo e Ingresos' },
    { campo: 'aporte_Salud_y_Discapacidad', etiqueta: 'Salud y Discapacidad' },
    { campo: 'aporte_Educacion', etiqueta: 'Educación' },
    { campo: 'aporte_Demografia', etiqueta: 'Demografía' },
    { campo: 'aporte_Desastres', etiqueta: 'Desastres' },
];

const CAMPOS_ESPERADOS = CAMPOS_DIMENSIONES.map(d => d.campo);


function dimensionesCompletas() {
    const checks = Array.from(document.querySelectorAll('.chk-dimension'));
    return CAMPOS_ESPERADOS.every(campo => checks.some(chk => chk.value === campo && chk.checked));
}


function getDimensionesActivas() {
    const checks = Array.from(document.querySelectorAll('.chk-dimension'));
    return CAMPOS_DIMENSIONES
        .filter(d => checks.some(chk => chk.value === d.campo && chk.checked))
        .map(d => ({ campo: d.campo, etiqueta: d.etiqueta }));
}


function abrirModalDimensiones() {
    const modal = document.getElementById('modal-dimensiones-shap');
    const contenedor = document.getElementById('modal-dimensiones-contenido');
    if (!modal || !contenedor) return;

    if (!municipioSeleccionadoActual) {
        contenedor.innerHTML = '<p class="text-xs text-slate-400 italic">Seleccione un municipio para ver sus aportes.</p>';
        modal.classList.remove('hidden');
        return;
    }

    const registro = mapaDimensiones.get(String(municipioSeleccionadoActual.divipola).padStart(5, '0')) || null;

    const filas = getDimensionesActivas().map(d => ({
        campo: d.campo,
        etiqueta: d.etiqueta,
        valor: registro && registro[d.campo] !== undefined ? (parseFloat(registro[d.campo]) || 0.0) : 0.0,
    })).sort((a, b) => b.valor - a.valor);

    filas.forEach((f, i) => { f.puesto = i + 1; });

    const total = filas.reduce((suma, f) => suma + f.valor, 0);

    let html = '';
    if (municipioSeleccionadoActual) {
        html += `
            <div class="bg-slate-50 border border-slate-100 rounded-lg p-3 mb-3">
                <p class="text-xs text-slate-600"><span class="font-semibold text-slate-800">Municipio:</span> ${municipioSeleccionadoActual.nombre}</p>
                <p class="text-xs text-slate-600 mt-0.5"><span class="font-semibold text-slate-800">DIVIPOLA:</span> ${municipioSeleccionadoActual.divipola}</p>
                <p class="text-xs text-slate-600 mt-0.5"><span class="font-semibold text-slate-800">Aporte SHAP acumulado (activas):</span> ${total.toFixed(2)} pts</p>
            </div>`;
    }

    if (filas.length === 0) {
        contenedor.innerHTML = '<p class="text-xs text-slate-400 italic">No hay dimensiones activas para este municipio.</p>';
    } else {
        filas.forEach(f => {
            html += `
                <div class="flex items-center justify-between py-2 border-b border-slate-100">
                    <span class="text-sm text-slate-700">${f.etiqueta}</span>
                    <span class="text-xs font-semibold text-teal-800">${f.valor.toFixed(2)} pts SHAP · puesto ${f.puesto}</span>
                </div>`;
        });
    }

    if (filas.length > 0 && !dimensionesCompletas()) {
        html += `
            <div class="mt-3 bg-amber-50 border border-amber-200 rounded-lg p-3">
                <p class="text-[11px] text-amber-700"><strong>Aporte no válido.</strong> Hay dimensiones sin marcar. El valor solo es válido cuando todas las dimensiones están activas.</p>
            </div>`;
    }

    contenedor.innerHTML = html;
    modal.classList.remove('hidden');
}


function cerrarModalDimensiones() {
    const modal = document.getElementById('modal-dimensiones-shap');
    if (modal) {
        modal.classList.add('hidden');
    }
}


export function toggleCapaCoropletas(checked) {
    if (capaCoropletas) {
        if (checked) {
            capaCoropletas.addTo(map);
        } else {
            map.removeLayer(capaCoropletas);
        }
    }
}

export function isCapaCoropletasVisible() {
    return capaCoropletas && map.hasLayer(capaCoropletas);
}


export async function cargarDimensionesMunicipales() {
    try {
        const res = await fetch(URLS.dimensionesMunicipales);
        if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
        const json = await res.json();
        if (json.status === 'success') {
            return json.data;
        }
        throw new Error(json.message || "Error al cargar dimensiones");
    } catch (e) {
        console.error("Error al obtener dimensiones municipales:", e);
        return [];
    }
}


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


function getColorFIES(prevalencia) {
    if (prevalencia === undefined || prevalencia === null) return '#cccccc'; // Sin datos
    return prevalencia > 40.0 ? '#990000' :
        prevalencia > 25.0 ? '#ec7014' :
        prevalencia > 15.0 ? '#fe9929' :
                                '#a1d99b';
}


function actualizarPanelDetalle(nombre, divipola, valor) {
    document.getElementById('det-municipio-nombre').textContent = nombre;
    document.getElementById('det-municipio-divipola').textContent = `DIVIPOLA: ${divipola}`;
    
    const textoValor = (valor !== null && valor !== undefined) ? `${valor.toFixed(1)} pts SHAP`  : 'Sin datos';
    document.getElementById('det-prevalencia-valor').textContent = textoValor;

    const badge = document.getElementById('badge-nivel-riesgo');
    if (valor === null || valor === undefined) {
        badge.textContent = "Sin datos SHAP";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600";
    } else if (!dimensionesCompletas()) {
        badge.textContent = "Aporte no válido";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700";
    } else if (valor > 40.0) {
        badge.textContent = "Crítico (Aporte SHAP > 40)";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-700";
    } else if (valor > 25.0) {
        badge.textContent = "Moderado-Alto (25-40)";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-orange-100 text-orange-700";
    } else if (valor > 15.0) {
        badge.textContent = "Moderado-Bajo (15-25)";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700";
    } else {
        badge.textContent = "Bajo (≤ 15)";
        badge.className = "text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700";
    }
}

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
                const txt = valor !== null ? `${valor.toFixed(1)}pts SHAP`  : 'Sin datos';
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

    // Abrir el modal con los aportes SHAP por dimensión del municipio seleccionado
    const btnVerDimensiones = document.getElementById('btn-ver-dimensiones-shap');
    const modalDimensiones = document.getElementById('modal-dimensiones-shap');
    const btnCerrarDimensiones = document.getElementById('btn-cerrar-modal-dimensiones');
    const btnCerrarDimensionesFooter = document.getElementById('modal-dimensiones-cerrar');

    if (btnVerDimensiones) {
        btnVerDimensiones.addEventListener('click', abrirModalDimensiones);
    }

    if (btnCerrarDimensiones) {
        btnCerrarDimensiones.addEventListener('click', cerrarModalDimensiones);
    }
    if (btnCerrarDimensionesFooter) {
        btnCerrarDimensionesFooter.addEventListener('click', cerrarModalDimensiones);
    }
    if (modalDimensiones) {
        modalDimensiones.addEventListener('click', (e) => {
            if (e.target === modalDimensiones) cerrarModalDimensiones();
        });
    }
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') cerrarModalDimensiones();
    });
});

export function obtenerRegistro(divipola) {
    return mapaDimensiones.get(String(divipola).padStart(5, '0')) || null;
}

export function obtenerMunicipioNombre(divipola) {
    const r = mapaDimensiones.get(String(divipola).padStart(5, '0'));
    return r ? r.nombre_municipio : null;
}

export { map } from '../mapBase.js'; 