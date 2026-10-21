import { datosMunicipioActual } from './datos.js';

let chartRadarUrbano = null;
let chartRadarRural = null;
let chartBarrasImpacto = null;
let chartValidacion = null;

const LABELS_DIMENSIONES = ['Salud', 'Vivienda', 'Trabajo', 'Educación', 'Demografía', 'Desastres'];

export function inicializarGraficos() {
    inicializarRadares();
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