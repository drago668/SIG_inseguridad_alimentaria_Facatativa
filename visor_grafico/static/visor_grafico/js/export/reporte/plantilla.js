import { FUENTE_ENCV } from './dimensiones.js';

export function construirDocumento({ datos, stats, mapaDataUrl, autor }) {

    // ── Utilidades internas ──────────────────────────────────
    const fmt = (n) => Number(n || 0).toLocaleString('es-CO');
    const pct = (n) => (n === null || n === undefined ? 'N/A' : `${n.toFixed(1)}%`);

    const nivelRiesgo = (p) => {
        if (p === null || p === undefined) return { texto: 'Sin datos', color: '#94a3b8' };
        if (p > 40) return { texto: 'Crítico / Severo', color: '#990000' };
        if (p > 25) return { texto: 'Moderado-Alto', color: '#ec7014' };
        if (p > 15) return { texto: 'Moderado-Bajo', color: '#fe9929' };
        return { texto: 'Bajo', color: '#10b981' };
    };

    const fecha = new Date().toLocaleDateString('es-CO', {
        year: 'numeric', month: 'long', day: 'numeric'
    });

    const municipioTitulo = datos ? datos.nombre : 'Cundinamarca';

    // ── Sección analítica: solo si hay municipio ───────────
    let seccionAnalitica = '';
    if (datos) {
        const nivel = nivelRiesgo(datos.prevalencia);
        const maximo = Math.max(...datos.aportes.map(a => a.valor));
        const barras = datos.aportes.map(a => {
            const anchoBarra = (a.valor / maximo) * 100;
            return `
                <div style="margin-bottom:7px;">
                    <div style="display:flex; justify-content:space-between; gap:10px; font-size:9px; color:#334155; margin-bottom:2px;">
                        <span style="white-space:nowrap;">${a.etiqueta}</span>
                        <span style="font-weight:bold; color:#0f766e; white-space:nowrap;">${a.valor.toFixed(2)}</span>
                    </div>
                    <div style="background:#e2e8f0; border-radius:3px; height:7px;">
                        <div style="background:#0d9488; border-radius:3px; height:7px; width:${anchoBarra.toFixed(1)}%;"></div>
                    </div>
                </div>`;
        }).join('');

        seccionAnalitica = `
            <div style="background:#f0fdfa; border-radius:10px; padding:14px 16px; margin-bottom:4px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:12px; font-weight:bold; color:#0f766e;">INSEGURIDAD ALIMENTARIA</span>
                    <span style="background:${nivel.color}; color:#ffffff; font-size:9px; font-weight:bold; padding:3px 10px; border-radius:10px;">${nivel.texto}</span>
                </div>
                <div style="display:flex; gap:22px; align-items:flex-end;">
                    <div>
                        <div style="font-size:8px; color:#64748b; text-transform:uppercase;">Prevalencia FIES</div>
                        <div style="font-size:28px; font-weight:bold; color:#0f172a; line-height:1;">
                            ${datos.prevalencia.toFixed(1)}<span style="font-size:13px; color:#64748b;">%</span>
                        </div>
                    </div>
                    <div style="font-size:9px; color:#475569; line-height:1.8;">
                        <strong style="color:#0f172a;">${municipioTitulo}</strong> · DIVIPOLA ${datos.divipola}<br>
                        Hogares proyectados: ${fmt(datos.totalHogares)}<br>
                        Jefatura femenina: ${pct(datos.pctJefatura)} · Hacinamiento: ${pct(datos.pctHacinado)}
                    </div>
                </div>
            </div>

            <div style="background:#f8fafc; border-radius:10px; padding:14px 16px; margin-bottom:12px;">
                <div style="font-size:11px; font-weight:bold; color:#0f766e; margin-bottom:10px;">
                    APORTE DE CADA DIMENSIÓN
                </div>
                ${barras}
                <div style="font-size:8px; color:#64748b; line-height:1.6; margin-top:10px; border-top:1px solid #e2e8f0; padding-top:8px;">
                    Cada barra muestra el aporte de la dimensión a la prevalencia estimada del municipio, en puntos
                    porcentuales. La suma de los seis aportes corresponde a la prevalencia estimada por el modelo; la cifra
                    del encabezado proviene de la base de datos calibrada y puede diferir por la calibración de Platt.
                </div>
            </div>
        `;
    }

    // ── Bloques que ya existían, sin cuadrícula ────────────
    const veredasHTML = stats.veredas.length > 0
        ? stats.veredas.map(v => `<span style="display:inline-block; background:#f1f5f9; color:#334155; font-size:9px; font-weight:bold; padding:4px 7px; border-radius:4px; margin:0 4px 5px 0;">${v}</span>`).join('')
        : '<span style="color:#94a3b8; font-style:italic;">No hay veredas seleccionadas</span>';

    const zonasHTML = stats.centrosPoblados.length > 0
        ? stats.centrosPoblados.map(z => `<span style="display:inline-block; background:#fdf4ff; color:#701a75; font-size:9px; font-weight:bold; padding:4px 7px; border-radius:4px; margin:0 4px 5px 0;">${z}</span>`).join('')
        : '<span style="color:#94a3b8; font-style:italic;">Zona urbana general</span>';

    
    
    // ── Documento completo ─────────────────────────────────
    return `
        <div style="padding:34px 38px; background:#ffffff; color:#0f172a; font-family:Arial, Helvetica, sans-serif;">
            <!-- Encabezado -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start;
                        border-bottom:3px solid #0f766e; padding-bottom:12px; margin-bottom:14px;">
                <div>
                    <div style="font-size:20px; font-weight:bold; color:#0f766e; line-height:26px; padding-bottom:2px;">
                        SIG CUNDINAMARCA
                    </div>
                    <div style="font-size:11px; color:#475569; margin-top:6px;">
                        ${datos ? `Municipio de ${municipioTitulo}` : 'Reporte Cartográfico y Diagnóstico Territorial'}
                    </div>
                </div>
                <div style="font-size:9px; color:#475569; line-height:1.7; text-align:right;">
                    <strong>Fuente:</strong> DANE / IGAC<br>
                    <strong>Fecha:</strong> ${fecha}<br>
                    <strong>Autor:</strong> ${autor}
                </div>
            </div>

            <!-- Mapa -->
            <div style="border-radius:10px; overflow:hidden; margin-bottom:6px; background:#f1f5f9;">
                <img src="${mapaDataUrl}" style="width:50%; height:300px; object-fit:cover; display:block;" />
                <div style="background:#f8fafc; color:#64748b; font-size:8px; text-align:right; padding:5px 10px;">
                    Mapa Base: OpenStreetMap / Positron — EPSG:4326 (WGS84)
                </div>
            </div>

            ${seccionAnalitica}

            <!-- Leyenda y resumen -->
            <div style="display:flex; gap:12px; margin-bottom:12px;">
                <div style="flex:1; background:#ffffff; border-radius:10px; padding:9px;">
                    <div style="font-size:10px; font-weight:bold; color:#0f766e; margin-bottom:9px;">
                        LEYENDA DE CONVENCIONES
                    </div>
                    <div style="font-size:9px; color:#334155; line-height:1.6;">
                        <div><span style="display:inline-block; width:11px; height:11px; background:#10b981; border-radius:2px; margin-right:6px;"></span>Límite Municipal</div>
                        <div><span style="display:inline-block; width:11px; height:11px; background:#601e0a; border-radius:2px; margin-right:6px;"></span>Límite Veredal</div>
                        <div><span style="display:inline-block; width:11px; height:11px; background:#63427e; border-radius:2px; margin-right:6px;"></span>Zona Urbana</div>
                        <div><span style="display:inline-block; width:11px; height:11px; background:#a05656; border-radius:2px; margin-right:6px;"></span>Zona Rural</div>
                        <div><span style="display:inline-block; width:11px; height:3px; background:#D73027; margin-right:6px;"></span>Red Vial Principal</div>
                        <div><span style="display:inline-block; width:11px; height:11px; background:#a1d99b; border-radius:2px; margin-right:6px;"></span>Prevalencia baja</div>
                        <div><span style="display:inline-block; width:11px; height:11px; background:#ec7014; border-radius:2px; margin-right:6px;"></span>Prevalencia alta</div>
                    </div>
                </div>

                <div style="flex:1.15; background:#ffffff; border-radius:10px; padding:9px;">
                    <div style="font-size:10px; font-weight:bold; color:#0f766e; margin-bottom:9px;">
                        RESUMEN GEOGRÁFICO
                    </div>
                    <div style="font-size:10px; color:#334155; line-height:1.9;">
                        <div style="display:flex; justify-content:space-between; gap:10px;">
                            <span style="white-space:nowrap;">Área calculada:</span>
                            <strong style="white-space:nowrap;">${stats.areaHa > 0 ? fmt(stats.areaHa) + ' ha' : 'N/A'}</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; gap:10px;">
                            <span style="white-space:nowrap;">Veredas visibles:</span>
                            <strong style="white-space:nowrap;">${stats.totalVeredas}</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; gap:10px;">
                            <span style="white-space:nowrap;">Sectores / zonas:</span>
                            <strong style="white-space:nowrap;">${stats.totalCentrosPoblados}</strong>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Listados -->
            <div style="background:#ffffff; border-radius:10px; padding:9px; margin-bottom:12px;">
                <div style="margin-bottom:11px;">
                    <div style="font-size:10px; font-weight:bold; color:#1e293b; margin-bottom:7px;">
                        VEREDAS IDENTIFICADAS (${stats.totalVeredas})
                    </div>
                    <div>${veredasHTML}</div>
                </div>
                <div>
                    <div style="font-size:10px; font-weight:bold; color:#1e293b; margin-bottom:7px;">
                        SECTORES / ZONAS URBANAS (${stats.totalCentrosPoblados})
                    </div>
                    <div>${zonasHTML}</div>
                </div>
            </div>

            <!-- Pie -->
            <div style="border-top:1px solid #e2e8f0; padding-top:10px;
                        font-size:8px; color:#64748b; text-align:center; line-height:1.6;">
                Documento generado automáticamente por el Sistema de Información Geográfica de Cundinamarca.<br>
                Información referencial basada en datos cartográficos oficiales del DANE y el IGAC.
                Prevalencias estimadas con modelo XGBoost calibrado sobre microdatos de la ECV 2025.
            </div>
        </div>
    `;
}
export function construirAnexo({ datos, autor }) {
    if (!datos || !datos.dimensiones) return '';

    const fecha = new Date().toLocaleDateString('es-CO', {
        year: 'numeric', month: 'long', day: 'numeric'
    });

    const tarjeta = (d) => {
        const ficha = d.ficha || {};
        return `
            <div style="width:354px; box-sizing:border-box; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; background:#ffffff; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                    <span style="font-size:12px; font-weight:bold; color:#0f766e;">${d.etiqueta}</span>
                    <span style="font-size:9px; font-weight:bold; color:#0f172a; white-space:nowrap; margin-left:8px;">
                        ${d.valor.toFixed(2)} pts · puesto ${d.puesto}
                    </span>
                </div>
                <div style="font-size:9.5px; color:#475569; line-height:1.65;">
                    <strong style="color:#0f172a;">Qué mide.</strong> ${ficha.queMide || ''}
                </div>
                <div style="font-size:9.5px; color:#475569; line-height:1.65; margin-top:5px;">
                    <strong style="color:#0f172a;">Por qué afecta.</strong> ${ficha.porQue || ''}
                </div>
                ${ficha.evidencia ? `
                <div style="font-size:8.5px; color:#0f766e; line-height:1.6; margin-top:6px; border-top:1px solid #e2e8f0; padding-top:5px;">
                    <strong>DANE 2024.</strong> ${ficha.evidencia}
                </div>` : ''}
            </div>`;
    };

    const filas = [];
    for (let i = 0; i < datos.dimensiones.length; i += 2) {
        const par = datos.dimensiones.slice(i, i + 2);
        filas.push(`
            <div style="display:flex; align-items:stretch; margin-bottom:14px;">
                <div style="margin-right:10px;">${tarjeta(par[0])}</div>
                ${par[1] ? tarjeta(par[1]) : ''}
            </div>`);
    }

    return `
        <div style="width:794px; min-height:1123px; padding:34px 38px; background:#ffffff; color:#0f172a; font-family:Arial, Helvetica, sans-serif; box-sizing:border-box; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:3px solid #0f766e; padding-bottom:12px; margin-bottom:16px;">
                <div>
                    <div style="font-size:20px; font-weight:bold; color:#0f766e; line-height:26px;">SIG CUNDINAMARCA</div>
                    <div style="font-size:11px; color:#475569; margin-top:6px;">
                        ${datos.nombre} · DIVIPOLA ${datos.divipola}
                    </div>
                </div>
                <div style="font-size:9px; color:#475569; line-height:1.7; text-align:right;">
                    <strong>Fecha:</strong> ${fecha}<br>
                    <strong>Autor:</strong> ${autor}
                </div>
            </div>

            <div style="font-size:16px; font-weight:bold; color:#0f172a; margin-bottom:8px;">
                ¿Cómo aporta cada dimensión a la inseguridad alimentaria?
            </div>

            <div style="font-size:9.5px; color:#475569; line-height:1.75; margin-bottom:16px;">
                La inseguridad alimentaria no depende solo de la comida disponible: depende de las condiciones en que el
                hogar vive, de lo que puede comprar, de su estado de salud, de su nivel educativo, de su composición y de
                los choques que enfrenta. El modelo estima una probabilidad por hogar y SHAP reparte esa probabilidad entre
                seis dimensiones. Los valores de cada ficha corresponden a este municipio y se expresan en puntos de prevalencia.
            </div>

            <div style="display:flex; flex-direction:column;">
                ${filas.join('')}
            </div>

            <div style="margin-top:14px; background:#f0fdfa; border-left:3px solid #0f766e; border-radius:6px; padding:12px 14px; font-size:9px; color:#334155; line-height:1.65;">
                <strong style="color:#0f766e;">Cómo leer esta página.</strong> Los puntos indican cuánto aporta cada
                dimensión a la prevalencia estimada del municipio; el puesto 1 es la dimensión que más contribuye. Las
                cifras DANE corresponden al total nacional de 2024 y sirven como referencia: no son el valor del municipio.
            </div>

            <div style="margin-top:auto; border-top:1px solid #e2e8f0; padding-top:8px; font-size:7.5px; color:#64748b; line-height:1.6;">
                <strong>Fuente:</strong> ${FUENTE_ENCV.texto}<br>
                <span style="color:#0f766e;">${FUENTE_ENCV.url}</span><br>
                Las cifras describen asociaciones poblacionales; no prueban relaciones causales.
            </div>
        </div>
    `;
}
