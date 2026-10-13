import { map } from "./mapBase.js";
import { toggleLoading } from './utils/dom.js';
import { AUTOR_REPORTE } from './config.js';


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
        const jsPDF = window.jspdf ? window.jspdf.jsPDF : window.jsPDF;

        if (!jsPDF) {
            alert('Error: La librería jsPDF no está cargada en la página.');
            toggleLoading(false);
            return;
        }

        const mapaNodo = document.getElementById('map');
        if (!mapaNodo) throw new Error('No se encontró el mapa.');

        // 1. Captura limpia del mapa (filtrando los controles Zoom/Layers de Leaflet)
        const mapDataUrl = await domtoimage.toPng(mapaNodo, {
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
        const fechaActual = new Date().toLocaleDateString('es-CO', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        // Formatear área con separadores de miles
        const areaFormateada = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 1 }).format(stats.areaHa);

        const reporteContenedor = document.createElement('div');
        reporteContenedor.id = 'reporte-pdf-temp';
        
        reporteContenedor.style.cssText = `
            position: absolute;
            top: 0;
            left: -9999px;
            width: 794px;
            height: 1123px;
            background: #ffffff;
            color: #0f172a;
            font-family: Arial, Helvetica, sans-serif;
            padding: 35px 40px;
            box-sizing: border-box;
        `;

        // CORRECCIÓN 2: Badges usando inline-block con márgenes estrictos
        const veredasHTML = stats.veredas.length > 0 
            ? stats.veredas.map(v => `<span style="display: inline-block; background: #f1f5f9; border: 1px solid #cbd5e1; padding: 4px 7px; border-radius: 4px; font-size: 9px; color: #334155; font-weight: bold; margin: 0 5px 6px 0;">${v}</span>`).join('')
            : '<span style="color: #94a3b8; font-style: italic;">No hay veredas seleccionadas</span>';

        const zonasHTML = stats.centrosPoblados.length > 0 
            ? stats.centrosPoblados.map(z => `<span style="display: inline-block; background: #fdf4ff; border: 1px solid #f5d0fe; padding: 4px 7px; border-radius: 4px; font-size: 9px; color: #701a75; font-weight: bold; margin: 0 5px 6px 0;">${z}</span>`).join('')
            : '<span style="color: #94a3b8; font-style: italic;">Zona urbana general</span>';

        // CORRECCIÓN 3: Estructura basada 100% en Tablas para evitar solapamientos
        reporteContenedor.innerHTML = `
            <!-- Encabezado Institucional -->
            <table style="width: 100%; border-bottom: 2px solid #0f766e; padding-bottom: 10px; margin-bottom: 15px; border-collapse: collapse;">
                <tr>
                    <td style="vertical-align: top; width: 60%;">
                        <h1 style="font-size: 19px; font-weight: bold; color: #0f766e; margin: 0 0 4px 0; line-height: 1.2; padding: 0;">SIG FACATATIVÁ — CUNDINAMARCA</h1>
                        <p style="font-size: 11px; color: #475569; margin: 0; padding: 0; line-height: 1.2;">Reporte Cartográfico y Diagnóstico Territorial</p>
                    </td>
                    <td style="vertical-align: top; text-align: right; width: 40%; font-size: 10px; color: #475569; line-height: 1.5;">
                        <strong>Fuente:</strong> DANE / IGAC<br>
                        <strong>Fecha:</strong> ${fechaActual}<br>
                        <strong>Autor:</strong> ${typeof AUTOR_REPORTE !== 'undefined' ? AUTOR_REPORTE : 'Ciudadano'}
                    </td>
                </tr>
            </table>

            <!-- Banner Municipio -->
            <table style="width: 100%; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; margin-bottom: 15px; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px 14px; font-size: 12px; font-weight: bold; color: #166534; vertical-align: middle;">MUNICIPIO: FACATATIVÁ</td>
                    <td style="padding: 10px 14px; text-align: right; vertical-align: middle;">
                        <span style="font-size: 9px; color: #15803d; font-weight: bold; background: #dcfce7; padding: 3px 8px; border-radius: 10px;">Vista Activa</span>
                    </td>
                </tr>
            </table>

            <!-- Contenedor del Mapa -->
            <div style="border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 15px; background: #f8fafc; overflow: hidden;">
                <img src="${mapDataUrl}" style="width: 100%; height: 380px; object-fit: cover; display: block; border: none; outline: none;" />
                <div style="background: #f1f5f9; padding: 6px 12px; font-size: 9px; color: #64748b; text-align: right; border-top: 1px solid #cbd5e1;">
                    Mapa Base: OpenStreetMap / Positron — EPSG:4326 (WGS84)
                </div>
            </div>

            <!-- Leyenda y Resumen (Tabla para forzar las 2 columnas) -->
            <table style="width: 100%; margin-bottom: 15px; border-collapse: separate; border-spacing: 12px 0; margin-left: -12px;">
                <tr>
                    <!-- Convenciones -->
                    <td style="width: 50%; vertical-align: top; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; background: #ffffff;">
                        <h3 style="font-size: 11px; font-weight: bold; color: #0f766e; margin: 0 0 10px 0; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">LEYENDA DE CONVENCIONES</h3>
                        <table style="width: 100%; font-size: 10px; color: #334155; line-height: 2;">
                            <tr>
                                <td style="width: 50%;"><span style="display:inline-block; width:12px; height:12px; background:#10b981; border:1px solid #059669; margin-right:6px; vertical-align:middle;"></span>Límite Municipal</td>
                                <td style="width: 50%;"><span style="display:inline-block; width:12px; height:12px; background:#601e0a; border:1px solid #8a2b0e; margin-right:6px; vertical-align:middle;"></span>Límite Veredal</td>
                            </tr>
                            <tr>
                                <td><span style="display:inline-block; width:12px; height:12px; background:#63427e; border:1px solid #c988ff; margin-right:6px; vertical-align:middle;"></span>Zona Urbana</td>
                                <td><span style="display:inline-block; width:12px; height:12px; background:#a05656; border:1px solid #ff8888; margin-right:6px; vertical-align:middle;"></span>Zona Rural</td>
                            </tr>
                            <tr>
                                <td colspan="2"><span style="display:inline-block; width:12px; height:3px; background:#D73027; margin-right:6px; vertical-align:middle;"></span>Red Vial Principal</td>
                            </tr>
                        </table>
                    </td>

                    <!-- Resumen Geográfico -->
                    <td style="width: 50%; vertical-align: top; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; background: #ffffff;">
                        <h3 style="font-size: 11px; font-weight: bold; color: #0f766e; margin: 0 0 10px 0; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">RESUMEN GEOGRÁFICO</h3>
                        <table style="width: 100%; font-size: 10px; color: #334155; line-height: 2;">
                            <tr>
                                <td>Área Calculada:</td>
                                <td style="text-align:right;"><strong>${stats.areaHa > 0 ? areaFormateada + ' ha' : 'N/A'}</strong></td>
                            </tr>
                            <tr>
                                <td>Veredas Visibles:</td>
                                <td style="text-align:right;"><strong>${stats.totalVeredas}</strong></td>
                            </tr>
                            <tr>
                                <td>Centros Poblados / Zonas:</td>
                                <td style="text-align:right;"><strong>${stats.totalCentrosPoblados}</strong></td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>

            <!-- Listados -->
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; background: #ffffff; margin-bottom: 15px;">
                <div style="margin-bottom: 12px;">
                    <h4 style="font-size: 10px; font-weight: bold; color: #1e293b; margin: 0 0 8px 0;">VEREDAS IDENTIFICADAS (${stats.totalVeredas})</h4>
                    <div style="line-height: 1.6;">
                        ${veredasHTML}
                    </div>
                </div>
                <div>
                    <h4 style="font-size: 10px; font-weight: bold; color: #1e293b; margin: 0 0 8px 0;">SECTORES / ZONAS URBANAS (${stats.totalCentrosPoblados})</h4>
                    <div style="line-height: 1.6;">
                        ${zonasHTML}
                    </div>
                </div>
            </div>

            <!-- Pie de Página -->
            <div style="border-top: 1px solid #cbd5e1; padding-top: 12px; font-size: 9px; color: #64748b; text-align: center; line-height: 1.5; margin-top: auto;">
                Este documento es un reporte automático generado por el Sistema de Información Geográfica de Facatativá (SIG Facatativá).<br>Información referencial basada en datos cartográficos oficiales del DANE y el IGAC.
            </div>
        `;

        document.body.appendChild(reporteContenedor);

        // 3. Captura en alta calidad del HTML maquetado
        const reporteDataUrl = await domtoimage.toPng(reporteContenedor, {
            quality: 0.98,
            bgcolor: '#ffffff'
        });

        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();

        pdf.addImage(reporteDataUrl, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(`Reporte_SIG_Facatativa_${Date.now()}.pdf`);

        document.body.removeChild(reporteContenedor);

    } catch (error) {
        console.error('Error al generar el reporte PDF:', error);
        alert('Ocurrió un error al generar el reporte en PDF.');
    } finally {
        toggleLoading(false);
    }
}