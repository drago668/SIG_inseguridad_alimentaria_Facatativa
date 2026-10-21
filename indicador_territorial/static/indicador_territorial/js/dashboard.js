import {
    datosZonalesCompletos,
    datosMunicipioActual,
    zonaSimulacionActiva,
    cargarDatosZonales,
    fusionarConBD,
    poblarSelectorMunicipios,
    procesarMunicipio,
    fijarZonaSimulacion,
    fijarNombreMunicipio,
} from './datos.js';
import { inicializarGraficos, obtenerGraficoImpacto, actualizarGraficoImpacto   } from './graficos.js';

// ---------------------------------------------------------
// SIMULACION DSS
// ---------------------------------------------------------
function actualizarSimulacionDSS() {
    const datosZona = zonaSimulacionActiva === 'Urbana'
        ? datosMunicipioActual.urbano
        : datosMunicipioActual.rural;

    const badgeImpacto = document.getElementById('badge-impacto-neto');
    const txtImpacto = document.getElementById('txt-impacto-neto');
    const chartBarrasImpacto = obtenerGraficoImpacto();

    if (!datosZona) {
        document.getElementById('hogares-riesgo').textContent = "--";
        document.getElementById('status-focalizacion').textContent =
            `● Sin datos en muestra ECV para zona ${zonaSimulacionActiva}`;
        badgeImpacto.textContent = "Sin Datos";
        badgeImpacto.className = "text-xs font-extrabold px-3 py-1 rounded-lg bg-slate-200 text-slate-500";
        txtImpacto.textContent =
            `El DANE no reportó muestra representativa en la zona ${zonaSimulacionActiva} de este municipio.`;

        if (chartBarrasImpacto) {
            chartBarrasImpacto.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 0, 0];
            chartBarrasImpacto.update();
        }
        return;
    }

    const totalHogares = datosZona.total_hogares_zona;
    let prevalenciaBase = datosZona.prevalencia_zona;

    const focJefatura = document.getElementById('chk-foc-jefatura').checked;
    const focVivienda = document.getElementById('chk-foc-vivienda').checked;

    const alertaDesempleo = document.getElementById('chk-alerta-desempleo').checked;
    const alertaVivienda = document.getElementById('chk-alerta-vivienda').checked;
    const alertaDesastre = document.getElementById('chk-alerta-desastre').checked;
    const alertaNevera = document.getElementById('chk-alerta-nevera').checked;

    const intSubsidio = document.getElementById('chk-int-subsidio').checked;
    const intAcueducto = document.getElementById('chk-int-acueducto').checked;
    const intEmpleo = document.getElementById('chk-int-empleo').checked;
    const intSalud = document.getElementById('chk-int-salud').checked;

    const baseTrabajo = datosZona.shap_desempleo || 0;
    const baseVivienda = datosZona.aporte_Vivienda_y_Servicios || 0;
    const baseDesastre = datosZona.Desastres || datosZona.aporte_Desastres || 0;
    const baseNevera = datosZona.shap_nevera || 0;

    const valDesempleo = alertaDesempleo ? Math.abs(baseTrabajo) : 0;
    const valViviendaBarra = alertaVivienda ? Math.abs(baseVivienda) : 0;
    const valDesastre = alertaDesastre ? Math.abs(baseDesastre) : 0;
    const valNevera = alertaNevera ? Math.abs(baseNevera) : 0;

    const valSubsidio = intSubsidio ? -Math.abs(datosZona.shap_educacion || 0) : 0;
    const valAcueducto = intAcueducto ? -Math.abs(datosZona.shap_agua_saneamiento || 0) : 0;
    const valEmpleo = intEmpleo ? -Math.abs(datosZona.shap_desempleo || 0) : 0;
    const valSalud = intSalud ? -Math.abs(datosZona.shap_salud || 0) : 0;

    if (chartBarrasImpacto) {
    const datosImpacto = {
        valDesempleo,
        valViviendaBarra,
        valDesastre,
        valNevera,
        valSubsidio,
        valAcueducto,
        valEmpleo,
        valSalud
    };
    
    // Usar la función del módulo graficos (importar arriba)
    actualizarGraficoImpacto(datosImpacto);
}

    const pctJefatura = datosZona.pct_jefatura_femenina || 0;
    const pctHacinado = datosZona.pct_hogar_hacinado || 0;

    let factorFocalizacion = 1.0;
    let labelFocalizacion = "Población General";

    if (focJefatura && focVivienda) {
        factorFocalizacion = (pctJefatura * pctHacinado) * 1.2;
        prevalenciaBase *= 1.45;
        labelFocalizacion = "Foc: Jefatura Fem. + Vivienda Precaria";
    } else if (focJefatura) {
        factorFocalizacion = pctJefatura;
        prevalenciaBase *= 1.25;
        labelFocalizacion = "Focalizado: Jefatura Femenina";
    } else if (focVivienda) {
        factorFocalizacion = pctHacinado;
        prevalenciaBase *= 1.35;
        labelFocalizacion = "Focalizado: Déficit Habitacional";
    }

    const puntosMitigados = Math.abs(valSubsidio) + Math.abs(valAcueducto)
        + Math.abs(valEmpleo) + Math.abs(valSalud);
    const prevalenciaFinal = Math.max(0.0, prevalenciaBase - puntosMitigados);

    const hogaresSubgrupo = totalHogares * factorFocalizacion;
    const hogaresEnRiesgo = Math.round(hogaresSubgrupo * (prevalenciaFinal / 100));

    document.getElementById('hogares-riesgo').textContent = hogaresEnRiesgo.toLocaleString();
    document.getElementById('status-focalizacion').textContent = `● ${labelFocalizacion}`;

    if (puntosMitigados > 0) {
        badgeImpacto.textContent = `-${puntosMitigados.toFixed(1)} pts FIES`;
        badgeImpacto.className = "text-xs font-extrabold px-3 py-1 rounded-lg bg-emerald-100 text-emerald-800 animate-pulse";
        const hogaresProtegidos = Math.round(hogaresSubgrupo * (puntosMitigados / 100));
        txtImpacto.textContent =
            `Se proyecta proteger a ~${hogaresProtegidos.toLocaleString()} hogares de la inseguridad alimentaria en la zona ${zonaSimulacionActiva}.`;
    } else {
        badgeImpacto.textContent = "0.0 pts";
        badgeImpacto.className = "text-xs font-extrabold px-3 py-1 rounded-lg bg-slate-200 text-slate-700";
        txtImpacto.textContent = "Sin intervenciones activas. Active palancas en el panel izquierdo.";
    }
}

// ---------------------------------------------------------
// EXPORTACION
// ---------------------------------------------------------
async function exportarPDF() {
    const elemento = document.getElementById('dashboard-content');
    if (!elemento) return;

    elemento.classList.add('pdf-mode');

    const opciones = {
        margin: [0.3, 0.3, 0.3, 0.3],
        filename: `Reporte_DSS_Inseguridad_Alimentaria_${datosMunicipioActual.nombreMunicipio}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
        pagebreak: { mode: ['avoid-all', 'css'] }
    };

    try {
        await html2pdf().set(opciones).from(elemento).save();
    } catch (err) {
        console.error("Error al exportar PDF:", err);
        alert("Ocurrió un error al generar el PDF.");
    } finally {
        elemento.classList.remove('pdf-mode');
    }
}

function exportarCSV() {
    const regUrb = datosMunicipioActual.urbano;
    const regRur = datosMunicipioActual.rural;

    const encabezados = [
        "Municipio", "Ambito_Territorial", "Prevalencia_FIES_Porcentaje",
        "Hogares_Expandidos", "Aporte_Salud_SHAP", "Aporte_Vivienda_SHAP",
        "Aporte_Trabajo_SHAP", "Aporte_Educacion_SHAP", "Aporte_Demografia_SHAP"
    ];

    const filas = [];
    if (regUrb) {
        filas.push([
            datosMunicipioActual.nombreMunicipio, "Cabecera Urbana",
            regUrb.prevalencia_zona, Math.round(regUrb.total_hogares_zona),
            regUrb.aporte_Salud_y_Discapacidad, regUrb.aporte_Vivienda_y_Servicios,
            regUrb.aporte_Trabajo_e_Ingresos, regUrb.aporte_Educacion,
            regUrb.aporte_Demografia
        ]);
    }
    if (regRur) {
        filas.push([
            datosMunicipioActual.nombreMunicipio, "Zona Rural",
            regRur.prevalencia_zona, Math.round(regRur.total_hogares_zona),
            regRur.aporte_Salud_y_Discapacidad, regRur.aporte_Vivienda_y_Servicios,
            regRur.aporte_Trabajo_e_Ingresos, regRur.aporte_Educacion,
            regRur.aporte_Demografia
        ]);
    }

    let contenido = "\uFEFF" + encabezados.join(",") + "\n";
    filas.forEach(f => { contenido += f.join(",") + "\n"; });

    const blob = new Blob([contenido], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Datos_SHAP_${datosMunicipioActual.nombreMunicipio}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// ---------------------------------------------------------
// EVENTOS
// ---------------------------------------------------------
function suscribirEventos() {
    const btnUrbana = document.getElementById('btn-zona-urbana');
    const btnRural = document.getElementById('btn-zona-rural');

    btnUrbana.addEventListener('click', (e) => {
        fijarZonaSimulacion('Urbana');
        e.target.classList.add('bg-white', 'shadow-sm', 'text-blue-700', 'border-slate-200', 'font-extrabold');
        e.target.classList.remove('text-slate-500', 'font-bold');
        btnRural.classList.remove('bg-white', 'shadow-sm', 'text-emerald-700', 'border-slate-200', 'font-extrabold');
        btnRural.classList.add('text-slate-500', 'font-bold');
        actualizarSimulacionDSS();
    });

    btnRural.addEventListener('click', (e) => {
        fijarZonaSimulacion('Rural');
        e.target.classList.add('bg-white', 'shadow-sm', 'text-emerald-700', 'border-slate-200', 'font-extrabold');
        e.target.classList.remove('text-slate-500', 'font-bold');
        btnUrbana.classList.remove('bg-white', 'shadow-sm', 'text-blue-700', 'border-slate-200', 'font-extrabold');
        btnUrbana.classList.add('text-slate-500', 'font-bold');
        actualizarSimulacionDSS();
    });

    const selector = document.getElementById('selector-municipio');
    selector.addEventListener('change', (e) => {
        fijarNombreMunicipio(e.target.value);
        procesarMunicipio(e.target.value);
        actualizarSimulacionDSS();
    });

    document.querySelectorAll('.chk-focalizacion, .chk-alerta, .chk-intervencion')
        .forEach(chk => chk.addEventListener('change', actualizarSimulacionDSS));

    const btnReset = document.getElementById('btn-reset-simulador');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            document.getElementById('chk-foc-jefatura').checked = false;
            document.getElementById('chk-foc-vivienda').checked = false;
            document.getElementById('chk-alerta-desempleo').checked = true;
            document.getElementById('chk-alerta-vivienda').checked = true;
            document.getElementById('chk-alerta-desastre').checked = false;
            document.getElementById('chk-alerta-nevera').checked = false;
            document.getElementById('chk-int-subsidio').checked = false;
            document.getElementById('chk-int-acueducto').checked = false;
            document.getElementById('chk-int-empleo').checked = false;
            document.getElementById('chk-int-salud').checked = false;
            actualizarSimulacionDSS();
        });
    }

    document.getElementById('btn-exportar-pdf').addEventListener('click', exportarPDF);
    document.getElementById('btn-exportar-csv').addEventListener('click', exportarCSV);
}

// ---------------------------------------------------------
// ARRANQUE
// ---------------------------------------------------------
async function iniciar() {
    inicializarGraficos();

    let registros = await cargarDatosZonales();
    registros = await fusionarConBD(registros, 2025);

    datosZonalesCompletos.length = 0;
    datosZonalesCompletos.push(...registros);

    poblarSelectorMunicipios();
    suscribirEventos();

    const selector = document.getElementById('selector-municipio');
    const codInicial = selector && selector.value ? selector.value : '25269';
    fijarNombreMunicipio(codInicial);
    procesarMunicipio(codInicial);
    actualizarSimulacionDSS();
}

document.addEventListener('DOMContentLoaded', iniciar);