import './admin/modal.js';
import './capas/filtros.js';
import './capas/overlay.js';
import './core/medicion.js';
import './export/imagen.js';
import './exportar_pdf.js';
import './export/datos.js';
import { crearCapaPoliticasAlimentaria } from './politicas.js';  // Cambiado

let capaPoliticasAlimentaria = null;

// Función para obtener map de forma segura
function getMap() {
    // mapBase.js debería haber asignado map a window.map
    return window.map || (typeof map !== 'undefined' ? map : null);
}

async function inicializarPoliticas() {
    try {
        const capa = await crearCapaPoliticasAlimentaria();
        if (capa) {
            // GUARDAR REFERENCIA GLOBAL (no añadir al mapa aún)
            window.capaPoliticasAlimentaria = capa;
            console.log('[Visor] Capa de políticas cargada, lista para activar');
        }
    } catch (e) {
        console.error('[Visor] Error inicializando políticas:', e);
    }
}

export function toggleCapaPoliticas(checked) {
    const m = getMap();
    if (!m) {
        console.error('[Visor] Map no disponible aún');
        return;
    }
    
    const capa = window.capaPoliticasAlimentaria;
    if (!capa) {
        console.warn('[Visor] Capa no cargada aún');
        return;
    }
    
    if (checked) {
        capa.addTo(m);
        console.log('[Visor] Capa políticas ACTIVADA');
    } else {
        m.removeLayer(capa);
        console.log('[Visor] Capa políticas DESACTIVADA');
    }
}

// Inicializar cuando el DOM esté listo Y map exista
function waitForMap() {
    return new Promise((resolve) => {
        const check = () => {
            const m = getMap();
            if (m && m._container) { // Verificar que Leaflet ya inicializó
                resolve(m);
            } else {
                setTimeout(check, 50);
            }
        };
        check();
    })
}

document.addEventListener('DOMContentLoaded', async () => {
    // Esperar a que mapBase.js haya inicializado el mapa
    await waitForMap();
    
    await inicializarPoliticas();
    
    // Event listener para checkbox
    const chk = document.getElementById('chk-capa-politicas-visor');
    if (chk) {
        chk.addEventListener('change', (e) => {
            toggleCapaPoliticas(e.target.checked);
        });
    }
});