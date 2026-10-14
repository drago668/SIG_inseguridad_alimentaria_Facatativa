import { URLS } from '../config.js';
import {
    cargarMunicipios, cargarVias, cargarVeredas,
    cargarZonaUrbana, cargarZonaRural,
    cargarVeredasConFiltro, cargarViasConFiltro,
    cambiarVisibilidadMunicipio, cambiarVisibilidadVeredas,
    cambiarVisibilidadVias, cambiarVisibilidadZonaUrbana,
    cambiarVisibilidadZonaRural
} from './capa.js';

const slctMunicipio = document.querySelector('#municipios-slct');
const slctVereda = document.querySelector('#veredas-slct');
const slctVia = document.querySelector('#vias-slct');

const checkMunicipio = document.querySelector('#chk-municipio');
const checkVeredas = document.querySelector('#chk-veredas');
const checkVias = document.querySelector('#chk-vias');
const checkUrbano = document.querySelector('#chk-urbano');
const checkRural = document.querySelector('#chk-rural');

const veredaSeleccionada = document.getElementById('select-veredas');

slctMunicipio.addEventListener('change', (e) => {
    const mpio = e.target.value;

    cargarMunicipios(mpio);
    cargarVias(mpio);
    cargarVeredas(mpio);
    cargarZonaUrbana(mpio, { visible: checkUrbano.checked });
    cargarZonaRural(mpio, { visible: checkRural.checked });

    fetch(`${URLS.veredasPorMunicipio}?mpio=${mpio}`)
        .then(r => r.json())
        .then(data => {
            veredaSeleccionada.innerHTML = '<option value="">Seleccione una vereda</option>';
            data.forEach(v => {
                const opcion = document.createElement('option');
                opcion.value = v.codigo_ver;
                opcion.textContent = v.nombre_ver;
                veredaSeleccionada.appendChild(opcion);
            });
        })
        .catch(err => console.error('Error cargando veredas:', err));
});


slctVereda.addEventListener('change', (e) => cargarVeredasConFiltro(e.target.value));
slctVia.addEventListener('change', (e) => cargarViasConFiltro(e.target.value));

checkMunicipio.addEventListener('change', (e) => cambiarVisibilidadMunicipio(e.target.checked));
checkVeredas.addEventListener('change', (e) => cambiarVisibilidadVeredas(e.target.checked));
checkVias.addEventListener('change', (e) => cambiarVisibilidadVias(e.target.checked));
checkUrbano.addEventListener('change', (e) => cambiarVisibilidadZonaUrbana(e.target.checked));
checkRural.addEventListener('change', (e) => cambiarVisibilidadZonaRural(e.target.checked));