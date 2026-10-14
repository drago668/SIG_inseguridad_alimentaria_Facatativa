import { ES_ADMINISTRADOR } from '../config.js';
import { activarModoMedicion, limpiarTodasLasMediciones } from '../mapBase.js';

if (ES_ADMINISTRADOR) {
    const btnMenu = document.getElementById('btn-medir-menu');
    const dropdown = document.getElementById('dropdown-medicion');
    const btnCerrar = document.getElementById('btn-cerrar-menu');
    const btnNueva = document.getElementById('btn-nueva-medicion');
    const btnLimpiar = document.getElementById('btn-limpiar-todo');

    btnMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    btnCerrar.addEventListener('click', () => {
        dropdown.classList.add('hidden');
    });

    btnNueva.addEventListener('click', () => {
        activarModoMedicion();
        dropdown.classList.add('hidden');
    });

    btnLimpiar.addEventListener('click', () => {
        limpiarTodasLasMediciones();
    });
}