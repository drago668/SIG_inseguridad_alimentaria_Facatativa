import { map } from "./mapBase.js";
import { toggleLoading } from './utils/dom.js';
import { AUTOR_REPORTE } from './config.js';
import { obtenerDatosReporte } from './export/datos.js';
import { construirDocumento, construirAnexo } from './export/reporte/plantilla.js';
import { FUENTE_ENCV } from './export/reporte/dimensiones.js';

function obtenerEstadisticasCapa() {
    const veredasNombres = [];
    let areaTotalHa = 0;
    const centrosPobladosNombres = [];

    map.eachLayer((layer) => {
        if (layer.feature && layer.feature.properties) {
            const props = layer.feature.properties;

            if (props.nombre_ver) {
                if (!veredasNombres.includes(props.nombre_ver)) {
                    veredasNombres.push(props.nombre_ver);
                }
                if (props.area_ha) {
                    areaTotalHa += parseFloat(props.area_ha) || 0;
                }
            }

            if (props.nombre_zona) {
                if (!centrosPobladosNombres.includes(props.nombre_zona)) {
                    centrosPobladosNombres.push(props.nombre_zona);
                }
            }
        }
    });

    return {
        veredas: veredasNombres,
        totalVeredas: veredasNombres.length,
        areaHa: areaTotalHa,
        centrosPoblados: centrosPobladosNombres,
        totalCentrosPoblados: centrosPobladosNombres.length
    };
}

export async function exportarMapaPDF() {
    toggleLoading(true);

    try {
        const slct = document.getElementById('municipios-slct');
        const divipola = slct ? slct.value : '';
        const datos = await obtenerDatosReporte(divipola);
        const jsPDF = window.jspdf ? window.jspdf.jsPDF : window.jsPDF;

        if (!jsPDF) {
            alert('Error: La librería jsPDF no está cargada en la página.');
            toggleLoading(false);
            return;
        }

        const mapaNodo = document.getElementById('map');
        if (!mapaNodo) throw new Error('No se encontró el mapa.');

        // 1. Captura limpia del mapa (filtrando los controles Zoom/Layers de Leaflet)
        const mapaDataUrl = await domtoimage.toPng(mapaNodo, {
            quality: 0.98,
            bgcolor: '#ffffff',
            filter: (node) => {
                // Filtra scripts y controles de interfaz de Leaflet (+ / - y capas)
                const esScript = node.tagName === 'SCRIPT';
                const esControlLeaflet = node.classList && node.classList.contains('leaflet-control-container');
                return !esScript && !esControlLeaflet;
            }
        });

        const stats = obtenerEstadisticasCapa();
        const reporteContenedor = document.createElement('div');
        reporteContenedor.style.cssText =
            'position:absolute; top:0; left:-9999px; width:794px; background:#ffffff;';

        reporteContenedor.innerHTML = construirDocumento({
            datos,
            stats,
            mapaDataUrl,
            autor: AUTOR_REPORTE
        });

        document.body.appendChild(reporteContenedor);

        // 3. Captura en alta calidad del HTML maquetado
        const mapDataUrl = await html2canvas(mapaNodo, {
            backgroundColor: '#ffffff',
            scale: 2,
            logging: false,
            onclone: (doc) => {
                doc.querySelectorAll('.leaflet-control-container')
                    .forEach(el => el.style.display = 'none');
            }
        }).then(c => c.toDataURL('image/png'));

        const reporteDataUrl = await html2canvas(reporteContenedor, {
            backgroundColor: '#ffffff',
            scale: 2,
            logging: false
        }).then(c => c.toDataURL('image/png'));

        const pdf = new jsPDF('p', 'mm', 'a4');
        const anchoPagina = pdf.internal.pageSize.getWidth();
        const altoPagina = pdf.internal.pageSize.getHeight();

        const img = new Image();
        img.src = reporteDataUrl;
        await img.decode();

        const altoReal = anchoPagina * (img.height / img.width);

        if (altoReal <= altoPagina) {
            pdf.addImage(reporteDataUrl, 'PNG', 0, 0, anchoPagina, altoReal);
        } else {
            let y = 0;
            pdf.addImage(reporteDataUrl, 'PNG', 0, 0, anchoPagina, altoReal);
            y += altoPagina;
            while (y < altoReal) {
                pdf.addPage();
                pdf.addImage(reporteDataUrl, 'PNG', 0, -y, anchoPagina, altoReal);
                y += altoPagina;
            }
        }
        
        console.log('ALTO REAL px:', img.height, '| ANCHO px:', img.width,'| ALTO en mm:', Math.round(altoReal), '| PAGINA mm:', Math.round(altoPagina));

        if (datos) {
            const anexoContenedor = document.createElement('div');
            anexoContenedor.style.cssText =
                'position:absolute; top:0; left:-9999px; width:794px; background:#ffffff;';
            anexoContenedor.innerHTML = construirAnexo({ datos, autor: AUTOR_REPORTE });
            document.body.appendChild(anexoContenedor);

            const anexoDataUrl = await html2canvas(anexoContenedor, {
                backgroundColor: '#ffffff',
                scale: 2,
                logging: false
            }).then(c => c.toDataURL('image/png'));

            const imgAnexo = new Image();
            imgAnexo.src = anexoDataUrl;
            await imgAnexo.decode();

            pdf.addPage();

            const escala = Math.min(anchoPagina / imgAnexo.width, altoPagina / imgAnexo.height);
            const anchoAnexo = imgAnexo.width * escala;
            const altoAnexo = imgAnexo.height * escala;
            const xAnexo = (anchoPagina - anchoAnexo) / 2;

            pdf.addImage(anexoDataUrl, 'PNG', xAnexo, 0, anchoAnexo, altoAnexo);
            pdf.link(xAnexo + 5, altoAnexo - 22, anchoAnexo - 10, 18, { url: FUENTE_ENCV.url });

            document.body.removeChild(anexoContenedor);
        }

        pdf.save(`Reporte_${datos ? datos.divipola : 'Cundinamarca'}_${Date.now()}.pdf`);

        document.body.removeChild(reporteContenedor);

    } catch (error) {
        console.error('Error al generar el reporte PDF:', error);
        alert('Ocurrió un error al generar el reporte en PDF.');
    } finally {
        toggleLoading(false);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const btnPdf = document.getElementById('descargar_pdf');
    if (btnPdf) {
        btnPdf.addEventListener('click', () => exportarMapaPDF());
    }
});