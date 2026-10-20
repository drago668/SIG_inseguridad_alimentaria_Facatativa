import { URLS, RUTAS_CSV } from './config.js';
import { actualizarRadares, actualizarValidacion } from './graficos.js';

// Estado del tablero
export let datosZonalesCompletos = [];
export let zonaSimulacionActiva = 'Urbana';

export const datosMunicipioActual = {
    urbano: null,
    rural: null,
    totalHogares: 0,
    prevalenciaPonderada: 0,
    nombreMunicipio: 'Facatativá'
};

const NOMBRES_MPIOS = {
    '25269': 'Facatativá', '25040': 'Anolaima', '25053': 'Arbeláez',
    '25095': 'Bituima', '25126': 'Cajicá', '25175': 'Chía',
    '25183': 'Chocontá', '25200': 'Cogua', '25214': 'Cota',
    '25286': 'Funza', '25290': 'Fusagasugá', '25295': 'Gachancipá',
    '25307': 'Girardot', '25317': 'Guachetá', '25320': 'Guaduas',
    '25322': 'Guasca', '25339': 'Gutiérrez', '25377': 'La Calera',
    '25386': 'La Mesa', '25430': 'Madrid', '25436': 'Manta',
    '25473': 'Mosquera', '25488': 'Nilo', '25513': 'Pacho',
    '25530': 'Paratebueno', '25612': 'Ricaurte', '25658': 'San Francisco',
    '25740': 'Sibaté', '25754': 'Soacha', '25758': 'Sopó',
    '25769': 'Subachoque', '25793': 'Tena', '25797': 'Tenjo',
    '25805': 'Tibacuy', '25839': 'Une', '25873': 'Villapinzón',
    '25875': 'Villeta', '25899': 'Zipaquirá'
};

export function nombreMunicipio(codigo) {
    return NOMBRES_MPIOS[codigo] || `Municipio (${codigo})`;
}

export function fijarZonaSimulacion(zona) {
    zonaSimulacionActiva = zona;
}

export function fijarNombreMunicipio(codigo) {
    datosMunicipioActual.nombreMunicipio = nombreMunicipio(codigo);
}

export async function cargarDatosZonales() {
    try {
        const res = await fetch(URLS.dimensionesZonales);
        if (res.ok) {
            const json = await res.json();
            if (json.status === 'success' && json.data.length > 0) {
                return json.data;
            }
        }
    } catch (e) {
        console.warn('API de dimensiones no disponible, se intenta el CSV');
    }

    for (const ruta of RUTAS_CSV) {
        try {
            const response = await fetch(ruta);
            if (response.ok) {
                const csvText = await response.text();
                return new Promise((resolve) => {
                    Papa.parse(csvText, {
                        header: true,
                        dynamicTyping: true,
                        skipEmptyLines: true,
                        complete: (results) => resolve(results.data)
                    });
                });
            }
        } catch (err) {
            console.warn(`No se pudo leer desde ${ruta}`);
        }
    }

    return DATOS_CONTINGENCIA;
}

export async function fusionarConBD(registros, corte = 2025) {
    try {
        const res = await fetch(`${URLS.prevalenciaZonales}?corte=${corte}`);
        const json = await res.json();
        if (json.status !== 'success' || !json.data.length) return registros;

        const mapaBD = {};
        json.data.forEach(r => {
            mapaBD[`${String(r.DIVIPOLA_SIG).padStart(5, '0')}-${r.Zona}`] = r;
        });

        let fusionados = 0;
        const salida = registros.map(r => {
            const bd = mapaBD[`${String(r.DIVIPOLA_SIG).padStart(5, '0')}-${r.Zona}`];
            if (!bd) return r;
            fusionados++;
            return {
                ...r,
                total_hogares_zona: bd.total_hogares_zona,
                prevalencia_zona: bd.prevalencia_zona,
                prevalencia_real: bd.prevalencia_real,
                hogares_predichos_pct: bd.hogares_predichos_pct,
                pct_jefatura_femenina: bd.pct_jefatura_femenina,
                pct_hogar_hacinado: bd.pct_hogar_hacinado,
            };
        });
        console.log(`Fusión BD: ${fusionados}/${registros.length} registros actualizados`);
        return salida;
    } catch (e) {
        console.warn('BD no disponible, se usan solo los datos del CSV:', e);
        return registros;
    }
}

export function poblarSelectorMunicipios() {
    const selector = document.getElementById('selector-municipio');
    if (!selector) return;

    const codigos = [...new Set(datosZonalesCompletos
        .map(d => String(d.DIVIPOLA_SIG).padStart(5, '0'))
        .filter(cod => NOMBRES_MPIOS[cod])
    )];

    if (codigos.length === 0) return;

    selector.innerHTML = '';
    const ordenados = codigos
        .map(cod => ({ cod, nombre: nombreMunicipio(cod) }))
        .sort((a, b) => a.nombre.localeCompare(b.nombre));

    ordenados.forEach(mpio => {
        const opt = document.createElement('option');
        opt.value = mpio.cod;
        opt.textContent = `${mpio.nombre} (${mpio.cod})`;
        if (mpio.cod === '25269') opt.selected = true;
        selector.appendChild(opt);
    });
}

export function procesarMunicipio(divipolaSeleccionado) {
    const divipolaNorm = String(divipolaSeleccionado).padStart(5, '0');
    const registros = datosZonalesCompletos
        .filter(r => String(r.DIVIPOLA_SIG).padStart(5, '0') === divipolaNorm);

    const regUrb = registros.find(r => String(r.Zona).toLowerCase() === 'urbana') || null;
    const regRur = registros.find(r => String(r.Zona).toLowerCase() === 'rural') || null;

    datosMunicipioActual.urbano = regUrb;
    datosMunicipioActual.rural = regRur;

    actualizarKpis(regUrb, regRur);
    actualizarRadares(regUrb, regRur);
    actualizarValidacion();
}

function actualizarKpis(regUrb, regRur) {
    if (regUrb) {
        document.getElementById('kpi-prev-urbana').textContent = `${Number(regUrb.prevalencia_zona).toFixed(1)}%`;
        document.getElementById('kpi-hogares-urbana').textContent = `Hogares: ${Math.round(regUrb.total_hogares_zona).toLocaleString()}`;
    } else {
        document.getElementById('kpi-prev-urbana').textContent = 'Sin datos';
        document.getElementById('kpi-hogares-urbana').textContent = '--';
    }

    if (regRur) {
        document.getElementById('kpi-prev-rural').textContent = `${Number(regRur.prevalencia_zona).toFixed(1)}%`;
        document.getElementById('kpi-hogares-rural').textContent = `Hogares: ${Math.round(regRur.total_hogares_zona).toLocaleString()}`;
    } else {
        document.getElementById('kpi-prev-rural').textContent = 'Sin datos';
        document.getElementById('kpi-hogares-rural').textContent = '--';
    }

    let sumaPond = 0;
    let totalHogares = 0;
    if (regUrb) {
        sumaPond += (regUrb.prevalencia_zona * regUrb.total_hogares_zona);
        totalHogares += regUrb.total_hogares_zona;
    }
    if (regRur) {
        sumaPond += (regRur.prevalencia_zona * regRur.total_hogares_zona);
        totalHogares += regRur.total_hogares_zona;
    }

    const prevGlobal = totalHogares > 0 ? (sumaPond / totalHogares) : 0;
    datosMunicipioActual.totalHogares = totalHogares;
    datosMunicipioActual.prevalenciaPonderada = prevGlobal;

    document.getElementById('kpi-prev-global').textContent = `${prevGlobal.toFixed(1)}%`;

    const badge = document.getElementById('kpi-badge-riesgo');
    if (prevGlobal > 40) {
        badge.textContent = 'Severo';
        badge.className = 'text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700';
    } else if (prevGlobal > 25) {
        badge.textContent = 'Moderado-Alto';
        badge.className = 'text-[10px] font-bold px-2 py-0.5 rounded-full bg-orange-100 text-orange-700';
    } else {
        badge.textContent = 'Moderado-Bajo';
        badge.className = 'text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700';
    }
}

const DATOS_CONTINGENCIA = [
    {
        DIVIPOLA_SIG: '25269', Zona: 'Urbana',
        total_hogares_zona: 71977.7, prevalencia_zona: 24.38,
        aporte_Salud_y_Discapacidad: 3.03, aporte_Vivienda_y_Servicios: 9.25,
        aporte_Trabajo_e_Ingresos: 5.75, aporte_Educacion: 3.52,
        aporte_Demografia: 2.83, aporte_Desastres: 1.61,
    },
    {
        DIVIPOLA_SIG: '25269', Zona: 'Rural',
        total_hogares_zona: 4754.2, prevalencia_zona: 22.12,
        aporte_Salud_y_Discapacidad: 2.93, aporte_Vivienda_y_Servicios: 7.69,
        aporte_Trabajo_e_Ingresos: 5.43, aporte_Educacion: 3.60,
        aporte_Demografia: 2.47, aporte_Desastres: 0.31,
    }
];