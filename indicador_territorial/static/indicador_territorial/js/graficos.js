import { datosMunicipioActual } from './datos.js';
import { DESCRIPCIONES_VARIABLES } from './descripciones_variables.js';

let chartRadarUrbano = null;
let chartRadarRural = null;
let chartBarrasImpacto = null;
let chartValidacion = null;

const LABELS_DIMENSIONES = ['Salud', 'Vivienda', 'Trabajo', 'Educación', 'Demografía', 'Desastres'];

let chartRadarVariables = null;
let zonaDesgloseActiva = 'Urbana';

export function fijarZonaDesglose(zona) {
    zonaDesgloseActiva = zona === 'Rural' ? 'Rural' : 'Urbana';
    const sel = document.getElementById('selector-zona-desglose');
    if (sel) sel.value = zonaDesgloseActiva;
}

function num(v) { const n = Number(v); return isFinite(n) ? n : 0; }
function absNum(v) { return Math.abs(num(v)); }

function datosDesglose() {
    const urb = datosMunicipioActual.urbano;
    const rur = datosMunicipioActual.rural;
    return zonaDesgloseActiva === 'Rural' ? (rur || urb) : (urb || rur);
}

function construirVariablesPorDimension(reg) {
    if (!reg) return {
        "Vivienda y Servicios": { labels: ["Agua y saneamiento", "Nevera", "Peso dimensión"], data: [0,0,0] },
        "Trabajo e Ingresos": { labels: ["Desempleo", "Peso dimensión", "Aporte Trabajo (pts)"], data: [0,0,0] },
        "Salud y Discapacidad": { labels: ["Afiliación a salud", "Peso dimensión", "Aporte Salud (pts)"], data: [0,0,0] },
        "Educación": { labels: ["Subsidio escolar (PAE)", "Peso dimensión", "Aporte Educación (pts)"], data: [0,0,0] },
        "Demografía": { labels: ["Jefatura femenina", "Hogar hacinado", "Peso dimensión"], data: [0,0,0] },
        "Desastres": { labels: ["Aporte Desastres (pts)", "Peso dimensión"], data: [0,0] },
    };
    return {
        "Vivienda y Servicios": {
            labels: ["Nevera (P1077S2)", "Paredes (P4005)", "Pisos (P4015)", "Tipo vivienda (P1070)", "Agua (P8520)", "Obtención agua (P8530)", "Tratamiento agua (P5069)", "Combustible (P8536)"],
            data: [num(reg.var_P1077S2), num(reg.var_P4005), num(reg.var_P4015), num(reg.var_P1070), num(reg.var_P8520), num(reg.var_P8530), num(reg.var_P5069), num(reg.var_P8536)]
        },
        "Trabajo e Ingresos": {
            labels: ["Actividad (P6240)", "Horario (P8624)", "Ingreso (P7250)", "Cotización (P6920)", "Formación (P6990)", "Tamaño empresa (P8632)"],
            data: [num(reg.var_P6240), num(reg.var_P8624), num(reg.var_P7250), num(reg.var_P6920), num(reg.var_P6990), num(reg.var_P8632)]
        },
        "Salud y Discapacidad": {
            labels: ["Régimen (P6100)", "Dificultades (P1906)", "Afiliación (P6090)", "Razón no afiliación (P768)"],
            data: [num(reg.var_P6100), num(reg.var_P1906), num(reg.var_P6090), num(reg.var_P768)]
        },
        "Educación": {
            labels: ["Alfabetismo (P6160)", "Asistencia (P8586)", "Nivel (P8587)", "Subsidio (P8612)"],
            data: [num(reg.var_P6160), num(reg.var_P8586), num(reg.var_P8587), num(reg.var_P8612)]
        },
        "Demografía": {
            labels: ["Tamaño hogar", "Sexo (P6020)", "Edad", "Etnia (P3039)"],
            data: [num(reg.var_CANT_PERSONAS_HOGAR), num(reg.var_P6020), num(reg.var_P6040), num(reg.var_P3039)]
        },
        "Desastres": {
            labels: ["Evento (P3173)", "Efectos (P3174)", "Pérdidas (P4065)"],
            data: [num(reg.var_P3173), num(reg.var_P3174), num(reg.var_P4065)]
        },
    };
}

const PROMPT_IA_RADAR = `Sos un asistente que explica visualizaciones de un Sistema de Información Geográfica (SIG) de inseguridad alimentaria.

El usuario te envió la captura de un radar (gráfico de ejes radiales) del dashboard del SIG Facatativá (Cundinamarca).

Contexto técnico:
- El radar desglosa, para una dimensión elegida, el peso de cada variable que la compone.
- Los datos provienen de la Encuesta Nacional de Calidad de Vida (ECV) del DANE, Anexo FIES 2024.
- Los valores son aportes SHAP (Shapley Additive Explanations) calculados con un modelo XGBoost, calibrados con ajuste Platt.
- El área ideal es toda la escala en cero: ningún factor de riesgo.

Explicá, en lenguaje sencillo y paso a paso:
1. Cómo leer el radar (ejes, variables, valores).
2. Qué significa que una variable esté en un valor alto o bajo.
3. Cómo interpretar el área ideal (ceros).
4. Qué significa todo esto para la inseguridad alimentaria en el municipio.`;


export function inicializarGraficos() {
    inicializarRadares();
    inicializarRadarVariables();
    inicializarGraficoImpacto();
    inicializarValidacion();
}

export function obtenerGraficoImpacto() {
    return chartBarrasImpacto;
}

function inicializarRadares() {
    const opciones = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            r: {
                min: 0,
                suggestedMax: 12,
                ticks: { backdropColor: 'transparent', font: { size: 9 }, color: '#64748b' },
                grid: { color: '#e2e8f0' },
                angleLines: { color: '#cbd5e1' },
                pointLabels: { font: { size: 11, weight: 'bold' }, color: '#334155' }
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const raw = ctx.raw;
                        const val = (typeof raw === 'number' && isFinite(raw)) ? raw : 0;
                        return ` Aporte SHAP: ${val.toFixed(2)}% al riesgo`;
                    }
                }
            }
        }
    };

    chartRadarUrbano = new Chart(
        document.getElementById('radarUrbano').getContext('2d'),
        {
            type: 'radar',
            data: {
                labels: LABELS_DIMENSIONES,
                datasets: [{
                    label: 'Zona Urbana',
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(59, 130, 246, 0.25)',
                    borderColor: '#2563eb',
                    pointBackgroundColor: '#1d4ed8',
                    pointBorderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: opciones
        }
    );

    chartRadarRural = new Chart(
        document.getElementById('radarRural').getContext('2d'),
        {
            type: 'radar',
            data: {
                labels: LABELS_DIMENSIONES,
                datasets: [{
                    label: 'Zona Rural',
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(16, 185, 129, 0.25)',
                    borderColor: '#059669',
                    pointBackgroundColor: '#047857',
                    pointBorderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: opciones
        }
    );
}

function inicializarGraficoImpacto() {
    chartBarrasImpacto = new Chart(
        document.getElementById('barrasImpacto').getContext('2d'),
        {
            type: 'bar',
            data: {
                labels: [
                    'Desempleo / Trabajo',
                    'Vivienda Inadecuada',
                    'Desastres naturales',
                    'Nevera',
                    'Subsidio Escolar (PAE)',
                    'Acceso a Acueducto',
                    'Empleo Formal Juvenil',
                    'Afiliación a Salud',
                ],
                datasets: [{
                    label: 'Puntos SHAP',
                    data: [5.75, 9.25, 0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(244, 63, 94, 0.8)',
                        'rgba(244, 63, 94, 0.8)',
                        'rgba(244, 63, 94, 0.8)',
                        'rgba(244, 63, 94, 0.8)',
                        'rgba(244, 63, 94, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {
                    x: {
                        grid: { color: '#f1f5f9' },
                        ticks: { callback: (v) => `${v > 0 ? '+' : ''}${v} pts` }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { font: { weight: 'bold', size: 11 } }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const raw = ctx.raw;
                                // Asegurar que val sea un número válido
                                const val = (typeof raw === 'number' && isFinite(raw)) ? raw : 0;
                                
                                return val < 0
                                    ? ` Mitigación de Política: ${val.toFixed(2)} pts de hambre reducidos`
                                    : ` Riesgo Adicional: +${val.toFixed(2)} pts al FIES`;
                            }
                        }
                    }
                }
            }
        }
    );
}

function inicializarValidacion() {
    const ctx = document.getElementById('barrasValidacion');
    if (!ctx) return;

    chartValidacion = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Zona Urbana', 'Zona Rural'],
            datasets: [
                { label: 'Real (ECV)', data: [0, 0], backgroundColor: '#10b981', borderRadius: 8 },
                { label: 'Modelo XGBoost', data: [0, 0], backgroundColor: '#3b82f6', borderRadius: 8 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${c.parsed.y}%` } }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: '% inseguridad alimentaria' }, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

export function actualizarRadares(regUrb, regRur) {
    if (chartRadarUrbano) {
        if (regUrb) {
            chartRadarUrbano.data.datasets[0].data = aportes(regUrb);
        } else {
            chartRadarUrbano.data.datasets[0].data = [0, 0, 0, 0, 0, 0]; // LIMPIAR
        }
        chartRadarUrbano.update();
    }
    
    // Rural
    if (chartRadarRural) {
        if (regRur) {
            chartRadarRural.data.datasets[0].data = aportes(regRur);
        } else {
            chartRadarRural.data.datasets[0].data = [0, 0, 0, 0, 0, 0]; // LIMPIAR
        }
        chartRadarRural.update();
    }
}

function aportes(reg) {
    return [
        reg.aporte_Salud_y_Discapacidad || 0,
        reg.aporte_Vivienda_y_Servicios || 0,
        reg.aporte_Trabajo_e_Ingresos || 0,
        reg.aporte_Educacion || 0,
        reg.aporte_Demografia || 0,
        reg.aporte_Desastres || 0,
    ];
}

export function actualizarGraficoImpacto(datos) {
    if (!chartBarrasImpacto) return;
    
    // datos = { valDesempleo, valViviendaBarra, valDesastre, valNevera, 
    //           valSubsidio, valAcueducto, valEmpleo, valSalud }
    const data = [
        datos.valDesempleo ?? 0,
        datos.valViviendaBarra ?? 0,
        datos.valDesastre ?? 0,
        datos.valNevera ?? 0,
        datos.valSubsidio ?? 0,
        datos.valAcueducto ?? 0,
        datos.valEmpleo ?? 0,
        datos.valSalud ?? 0,
    ];
    
    chartBarrasImpacto.data.datasets[0].data = data;
    chartBarrasImpacto.data.datasets[0].backgroundColor = data.map(v => 
        v < 0 ? 'rgba(16, 185, 129, 0.85)' : 'rgba(244, 63, 94, 0.85)'
    );
    chartBarrasImpacto.update();
}


export function actualizarValidacion() {
    if (!chartValidacion) return;
    const u = datosMunicipioActual.urbano;
    const r = datosMunicipioActual.rural;

    chartValidacion.data.datasets[0].data = [u?.prevalencia_real ?? 0, r?.prevalencia_real ?? 0];
    chartValidacion.data.datasets[1].data = [u?.prevalencia_zona ?? 0, r?.prevalencia_zona ?? 0];
    chartValidacion.update();

    const titulo = document.getElementById('titulo-validacion');
    if (titulo) titulo.textContent = `Realidad vs Modelo — ${datosMunicipioActual.nombreMunicipio}`;
}

function inicializarRadarVariables() {
    const canvas = document.getElementById('radarVariables');
    if (!canvas) return;

    const dimension = document.getElementById('selector-dimension-desglose')?.value || "Vivienda y Servicios";
    const vars = construirVariablesPorDimension(datosDesglose());
    const selectorZona = document.getElementById('selector-zona-desglose');
    if (selectorZona) {
        zonaDesgloseActiva = selectorZona.value === 'Rural' ? 'Rural' : 'Urbana';
        selectorZona.addEventListener('change', () => {
            zonaDesgloseActiva = selectorZona.value === 'Rural' ? 'Rural' : 'Urbana';
            actualizarRadarVariables(datosMunicipioActual.urbano, datosMunicipioActual.rural);
        });
    }

    chartRadarVariables = new Chart(canvas.getContext('2d'), {
        type: 'radar',
        data: {
            labels: vars[dimension]?.labels || [],
            datasets: [{
                label: dimension,
                data: vars[dimension]?.data || [],
                backgroundColor: 'rgba(20, 184, 166, 0.25)',
                borderColor: '#0d9488',
                pointBackgroundColor: '#0f766e',
                pointBorderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    suggestedMax: 10,
                    ticks: { backdropColor: 'transparent', font: { size: 9 }, color: '#64748b' },
                    grid: { color: '#e2e8f0' },
                    angleLines: { color: '#cbd5e1' },
                    pointLabels: { font: { size: 11, weight: 'bold' }, color: '#334155' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const val = (typeof ctx.raw === 'number' && isFinite(ctx.raw)) ? ctx.raw : 0;
                            const match = ctx.label.match(/\(([^)]+)\)/);
                            const codigo = match ? match[1] : ctx.label;
                            const desc = DESCRIPCIONES_VARIABLES[codigo];
                            return desc
                                ? ` ${desc.nombre}: ${val.toFixed(2)} - ${desc.descripcion}`
                                : ` ${ctx.label}: ${val.toFixed(2)}`;
                        }
                    }
                }
            }
        }
    });

    const btnToggle = document.getElementById('btn-toggle-desglose');
    const panel = document.getElementById('panel-desglose-dimension');
    if (btnToggle && panel) {
        btnToggle.addEventListener('click', () => {
            panel.classList.toggle('hidden');
            btnToggle.textContent = panel.classList.contains('hidden')
                ? 'Ver composición de la dimensión'
                : 'Ocultar composición de la dimensión';

            if (!panel.classList.contains('hidden') && chartRadarVariables) {
                actualizarRadarVariables(datosMunicipioActual.urbano, datosMunicipioActual.rural);
                chartRadarVariables.resize();
            }
        });
    }

    const selector = document.getElementById('selector-dimension-desglose');
    if (selector) {
        selector.addEventListener('change', () => {
            const dim = selector.value;
            const vars2 = construirVariablesPorDimension(datosDesglose());
            chartRadarVariables.data.labels = vars2[dim]?.labels || [];
            chartRadarVariables.data.datasets[0].label = dim;
            chartRadarVariables.data.datasets[0].data = vars2[dim]?.data || [];
            chartRadarVariables.update();
        });
    }

    const btnCopiar = document.getElementById('btn-copiar-prompt-ia');
    const mensaje = document.getElementById('mensaje-prompt-ia');
    if (btnCopiar) {
        btnCopiar.addEventListener('click', async () => {
            await navigator.clipboard.writeText(PROMPT_IA_RADAR);
            if (mensaje) {
                mensaje.classList.remove('hidden');
                setTimeout(() => mensaje.classList.add('hidden'), 3000);
            }
        });
    }

    const btnExplicar = document.getElementById('btn-explicar-ia');
    if (btnExplicar) {
        btnExplicar.addEventListener('click', async () => {
            const contenedor = document.getElementById('contenedor-captura-radar');
            const dim = document.getElementById('selector-dimension-desglose')?.value || 'dimension';
            if (contenedor && window.html2canvas) {
                const canvasImg = await html2canvas(contenedor, { scale: 2, backgroundColor: '#ffffff' });
                const link = document.createElement('a');
                link.download = `radar_${dim.replaceAll(' ', '_')}.png`;
                link.href = canvasImg.toDataURL('image/png');
                link.click();
            }
            await navigator.clipboard.writeText(PROMPT_IA_RADAR);
            if (mensaje) {
                mensaje.classList.remove('hidden');
                setTimeout(() => mensaje.classList.add('hidden'), 3000);
            }
        });
    }
}

export function actualizarRadarVariables(regUrb, regRur) {
    if (!chartRadarVariables) return;
    const dim = document.getElementById('selector-dimension-desglose')?.value || "Vivienda y Servicios";
    const reg = zonaDesgloseActiva === 'Rural' ? (regRur || regUrb) : (regUrb || regRur);
    const vars = construirVariablesPorDimension(reg);
    chartRadarVariables.data.labels = vars[dim]?.labels || [];
    chartRadarVariables.data.datasets[0].label = dim + ' (' + zonaDesgloseActiva + ')';
    chartRadarVariables.data.datasets[0].data = vars[dim]?.data || [];
    chartRadarVariables.update();
}