import { URLS } from '../config.js';
import { obtenerRegistro } from '../capas/overlay.js';

function obtenerNombreDesdeSeleccion(divipola) {
    const slct = document.getElementById('municipios-slct');
    if (!slct) return null;
    const opcion = slct.querySelector(`option[value="${divipola}"]`);
    return opcion ? opcion.textContent.trim() : null;
}

const CAMPOS_DIMENSION = [
    { campo: 'aporte_Salud_y_Discapacidad', etiqueta: 'Salud y Discapacidad' },
    { campo: 'aporte_Vivienda_y_Servicios',   etiqueta: 'Vivienda y Servicios' },
    { campo: 'aporte_Trabajo_e_Ingresos',     etiqueta: 'Trabajo e Ingresos' },
    { campo: 'aporte_Educacion',              etiqueta: 'Educación' },
    { campo: 'aporte_Demografia',             etiqueta: 'Demografía' },
    { campo: 'aporte_Desastres',              etiqueta: 'Desastres' },
];

export async function obtenerDatosReporte(divipola) {
    if (!divipola) return null;

    const registro = obtenerRegistro(divipola);
    if (!registro) return null;

    const respuesta = await fetch(`${URLS.prevalenciaZonales}?corte=2025`);
    const json = await respuesta.json();

    const divipolaTexto = String(divipola).trim().padStart(5, '0');

    const nombreMunicipio = await obtenerNombreDesdeSeleccion(divipolaTexto);

    const filas = json.data.filter(f =>
        String(f.DIVIPOLA_SIG).padStart(5, '0') === divipolaTexto
        || (nombreMunicipio && f.nombre_municipio === nombreMunicipio)
    );

    const totales = filas.reduce((acc, f) => {
        acc.hogares += f.total_hogares_zona || 0;
        acc.sumaPesada += (f.prevalencia_zona || 0) * (f.total_hogares_zona || 0);
        acc.jefatura += (f.pct_jefatura_femenina || 0) * (f.total_hogares_zona || 0);
        acc.hacinado += (f.pct_hogar_hacinado || 0) * (f.total_hogares_zona || 0);
        return acc;
    }, { hogares: 0, sumaPesada: 0, jefatura: 0, hacinado: 0 });

    const prevalencia = totales.hogares > 0 ? totales.sumaPesada / totales.hogares : null;

    const aportes = CAMPOS_DIMENSION
        .map(({ campo, etiqueta }) => ({ etiqueta, valor: registro[campo] ?? 0 }))
        .filter(a => a.valor > 0)
        .sort((a, b) => b.valor - a.valor);

    const sumaAportes = aportes.reduce((t, a) => t + a.valor, 0);

    return {
        divipola,
        nombre: nombreMunicipio || `Municipio ${divipola}`,
        prevalencia,
        totalHogares: Math.round(totales.hogares),
        aportes,
        sumaAportes,
        pctJefatura: totales.hogares > 0 ? totales.jefatura / totales.hogares : null,
        pctHacinado: totales.hogares > 0 ? totales.hacinado / totales.hogares : null,
    };
}