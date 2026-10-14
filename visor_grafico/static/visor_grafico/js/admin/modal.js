import { ES_ADMINISTRADOR } from '../config.js';

if (ES_ADMINISTRADOR) {
    const modal = document.getElementById('modal-cargar-capa');
    const btnAbrir = document.getElementById('abrir-modal');
    const btnCerrar = document.getElementById('btn-cerrar-modal');
    const btnCancelar = document.getElementById('btn-cancelar-modal');

    const abrir = () => modal.classList.remove('hidden');
    const cerrar = () => modal.classList.add('hidden');

    if (btnAbrir) btnAbrir.addEventListener('click', abrir);
    if (btnCerrar) btnCerrar.addEventListener('click', cerrar);
    if (btnCancelar) btnCancelar.addEventListener('click', cerrar);
}