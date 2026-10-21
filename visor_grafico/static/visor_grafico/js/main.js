import './admin/modal.js';
import './capas/filtros.js';
import './capas/overlay.js';
import './core/medicion.js';
import './export/imagen.js';
import './exportar_pdf.js';
import './export/datos.js';
import { crearCapaPoliticasAlimentaria } from './politicas.js';  
import { toggleCapaCoropletas, isCapaCoropletasVisible } from './capas/overlay.js'; 

let capaPoliticasAlimentaria = null;

function getMap() {
    return window.map || (typeof map !== 'undefined' ? map : null);
}

async function inicializarPoliticas() {
    try {
        const capa = await crearCapaPoliticasAlimentaria();
        if (capa) {
            window.capaPoliticasAlimentaria = capa;
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
    } else {
        m.removeLayer(capa);
    }
}

function waitForMap() {
    return new Promise((resolve) => {
        const check = () => {
            const m = getMap();
            if (m && m._container) { 
                resolve(m);
            } else {
                setTimeout(check, 50);
            }
        };
        check();
    })
}

document.addEventListener('DOMContentLoaded', async () => {
    await waitForMap();
    await inicializarPoliticas();
    
    const chk = document.getElementById('chk-capa-politicas-visor');
    if (chk) {
        chk.addEventListener('change', (e) => {
            toggleCapaPoliticas(e.target.checked);
        });
    }
});

function toggleCapaCoropletasHandler(checked) {
    import('./capas/overlay.js').then(({ toggleCapaCoropletas }) => {
        toggleCapaCoropletas(checked);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    await waitForMap();
    
    await inicializarPoliticas();
    
    const chkPoliticas = document.getElementById('chk-capa-politicas-visor');
    if (chkPoliticas) {
        chkPoliticas.addEventListener('change', (e) => {
            toggleCapaPoliticas(e.target.checked);
        });
    }
    
    const chkCoropletas = document.getElementById('chk-capa-fies');
    if (chkCoropletas) {
        chkCoropletas.checked = true;
        chkCoropletas.addEventListener('change', (e) => {
            import('./capas/overlay.js').then(({ toggleCapaCoropletas }) => {
                toggleCapaCoropletas(e.target.checked);
            });
        });
    }
});