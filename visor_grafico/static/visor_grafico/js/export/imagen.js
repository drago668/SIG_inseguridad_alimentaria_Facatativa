import { toggleLoading } from '../utils/dom.js';

function exportarMapaImagen(formato = 'png') {
    toggleLoading(true);

    setTimeout(() => {
        const mapaNodo = document.getElementById('map');

        if (!mapaNodo) {
            alert('No se encontró el contenedor del mapa.');
            toggleLoading(false);
            return;
        }

        const opciones = {
            quality: 0.95,
            bgcolor: '#ffffff',
            filter: (node) => node.tagName !== 'SCRIPT'
        };

        const metodoExportar = formato === 'jpg'
            ? domtoimage.toJpeg(mapaNodo, opciones)
            : domtoimage.toPng(mapaNodo, opciones);

        metodoExportar
            .then((dataUrl) => {
                const link = document.createElement('a');
                link.download = `mapa_facatativa.${formato}`;
                link.href = dataUrl;
                link.click();
                link.remove();
            })
            .catch((error) => {
                console.error('Error al exportar con dom-to-image:', error);
                alert('Ocurrió un error al generar la imagen del mapa.');
            })
            .finally(() => toggleLoading(false));
    }, 200);
}

document.addEventListener('DOMContentLoaded', () => {
    const btnPng = document.getElementById('descargar_png');
    const btnJpg = document.getElementById('descargar_jpg');

    if (btnPng) btnPng.addEventListener('click', () => exportarMapaImagen('png'));
    if (btnJpg) btnJpg.addEventListener('click', () => exportarMapaImagen('jpg'));
});