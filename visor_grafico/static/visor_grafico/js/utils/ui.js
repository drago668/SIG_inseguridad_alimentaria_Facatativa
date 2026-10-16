const modal = document.getElementById('modal-aviso');
const btnCerrar = document.getElementById('modal-aviso-cerrar');
const elTitulo = document.getElementById('modal-aviso-titulo');
const elMensaje = document.getElementById('modal-aviso-mensaje');

export function cerrarExito() {
    if (modal) modal.classList.add('hidden');
}

if (modal && btnCerrar) {
    btnCerrar.addEventListener('click', cerrarExito);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) cerrarExito();
    });
}

export function mostrarExito(titulo, mensaje) {
    if (!modal) return;
    elTitulo.textContent = titulo;
    elMensaje.textContent = mensaje;
    modal.classList.remove('hidden');
}