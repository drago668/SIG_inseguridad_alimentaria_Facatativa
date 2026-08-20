import { crearCapaVias, crearCapaMunicipios, crearCapaVeredas, crearCapaZonaRural, crearCapaZonaUrbana } from "./layerTemplate.js";
import { map, layerControl } from "./mapBase.js";
//import { toggleMedicion } from './mapBase.js';

const slctMunicipio = document.querySelector('#municipios-slct');
const slctVereda = document.querySelector('#veredas-slct');
const slctVia = document.querySelector('#vias-slct');

const checkMunicipio = document.querySelector('#chk-municipio');
const checkVeredas = document.querySelector('#chk-veredas');
const checkVias = document.querySelector('#chk-vias');
const checkUrbano = document.querySelector('#chk-urbano');
const checkRural = document.querySelector('#chk-rural');
const btnPdf = document.querySelector('#descargar_pdf')
const btnPng = document.querySelector('#descargar_png')

export let capaMunicipios;
export let capaVeredas;
export let capaVias;
export let capaZonaRural;
export let capaZonaUrbana;

// main.js
import { 
    activarModoMedicion, 
    limpiarTodasLasMediciones 
} from './mapBase.js';

// Elementos DOM
const btnMenu = document.getElementById('btn-medir-menu');
const dropdown = document.getElementById('dropdown-medicion');
const btnCerrar = document.getElementById('btn-cerrar-menu');
const btnNueva = document.getElementById('btn-nueva-medicion');
const btnLimpiar = document.getElementById('btn-limpiar-todo');

// Abrir / Cerrar Menú
btnMenu.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('hidden');
});

btnCerrar.addEventListener('click', () => {
    dropdown.classList.add('hidden');
});

// Acción: Iniciar Nueva Medición
btnNueva.addEventListener('click', () => {
    activarModoMedicion();
    dropdown.classList.add('hidden');
});

// Acción: Borrar Todo
btnLimpiar.addEventListener('click', () => {
    limpiarTodasLasMediciones();
});

// renderizar capa vias
fetch(urlViasGeoJSON)
    .then(response => {
        if (!response.ok) throw new Error("Error en la respuesta de la API de Vías");
        return response.json();
    })
    .then(data => {
        if (capaVias) {
            map.removeLayer(capaVias);
        }
        capaVias = crearCapaVias(data);
        capaVias.addTo(map);
        layerControl.addOverlay(capaVias, "Vías Principales");
    })
    .catch(err => console.error("Error al cargar la(s) Vias: ", err));



// renderizar capa veredas
fetch(urlVeredasGeoJSON)
    .then(response => {
        if (!response.ok) throw new Error("Error en la respuesta de la API de Veredas");
        return response.json();
    })
    .then(data => {
        if (capaVeredas) {
            map.removeLayer(capaVeredas);
        }
        capaVeredas = crearCapaVeredas(data);
        capaVeredas.addTo(map);
        map.fitBounds(capaVeredas.getBounds());
        layerControl.addOverlay(capaVeredas, "Veredas");
    })
    .catch(err => console.error("Error al cargar la(s) veredas: ", err));


// renderizar capa municipios
fetch(urlMunicipioGeoJSON)
    .then(response =>{
        if(!response.ok) throw new Error("Error en la respuesta de la API de Municipios");
        return response.json();
    })
    .then(data => {
        if (capaMunicipios){
            map.removeLayer(capaMunicipios);
        }
        capaMunicipios = crearCapaMunicipios(data);
        capaMunicipios.addTo(map);
        map.fitBounds(capaMunicipios.getBounds());
        layerControl.addOverlay(capaMunicipios, "Municipio");
    })
    .catch(err => console.error("Error al cargar lo(s) Municipios: ", err));

//filtrar capas con base en los select#################################################################

// filtrar capa municipios con base en los select
slctMunicipio.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Municipio seleccionado:", slcted);
    const urlFiltradaMpios= `${urlMunicipioGeoJSON}?mpio=${slcted}`;
    const urlFiltradaVias= `${urlViasGeoJSON}?mpio=${slcted}`;
    const urlFiltradaVdas= `${urlVeredasGeoJSON}?mpio=${slcted}`;
    const urlFilterVdas= `${urlVeredasMpio}?mpio=${slcted}`;

    fetch(urlFiltradaMpios)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de municipios");
            return response.json();
        })
        .then(data => {
            if (capaMunicipios) map.removeLayer(capaMunicipios);
            console.log("funciono:", data);

            capaMunicipios = crearCapaMunicipios(data);
            capaMunicipios.addTo(map);
            map.fitBounds(capaMunicipios.getBounds());
        })
        .catch(err => console.error("Error al filtrar los muncipios: ", err));
    fetch(urlFiltradaVias)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de vias");
            return response.json();
        })
        .then(data =>{
            if(capaVias) map.removeLayer(capaVias);
            capaVias =crearCapaVias(data);
            capaVias.addTo(map);
        })
        .catch(err => console.error("Error al filtrar las vias: ", err));
    fetch(urlFiltradaVdas)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de vias");
            return response.json();
        })
        .then(data =>{
            if(capaVeredas) map.removeLayer(capaVeredas);
            capaVeredas = crearCapaVeredas(data);
            capaVeredas.addTo(map);
        })
        .catch(err => console.error("Error al filtrar los muncipios: ", err));
    
    fetch(urlFilterVdas)
        .then(response => response.json())
        .then(data => {
            console.log("veredas encontradas: ", data);
            const selectVereda = document.getElementById('select-veredas');
            if (slctVereda) {
                slctVereda.innerHTML = '<option value="">Seleccione una vereda</option>';
                data.forEach(vereda => {
                    const option = document.createElement('option');
                    option.value = vereda.codigo_ver;
                    option.textContent = vereda.nombre_ver;
                    slctVereda.appendChild(option);
                });
            }
        }).catch(error => console.error('Error cargando veredas:', error));
});

// filtrar con base en los select #####################################################################################
// filtrar capa veredas con base en los select
slctVereda.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Vereda seleccionada:", slcted);
    const urlFiltrada= `${urlVeredasGeoJSON}?vda=${slcted}`;

    fetch(urlFiltrada)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de Veredas: ");
            return response.json();
        })
        .then(data => {

            if (capaVeredas) map.removeLayer(capaVeredas);

            capaVeredas = crearCapaVeredas(data);
            capaVeredas.addTo(map);
        })
        .catch(err => console.error("Error al filtrar las veredas:", err));
});

// filtrar capa vias con base en los select
slctVia.addEventListener('change', (e) => {
    const slcted = e.target.value;
    console.log("Via seleccionada:", slcted);
    const urlFiltrada= `${urlViasGeoJSON}?tipo=${slcted}`;

    fetch(urlFiltrada)
        .then(response => {
            if (!response.ok) throw new Error("Error en la API de Veredas: ");
            return response.json();
        })
        .then(data => {

            if (capaVias) map.removeLayer(capaVias);

            capaVias = crearCapaVias(data);
            capaVias.addTo(map);
        })
        .catch(err => console.error("Error al filtrar las vias:", err));
});


// activar o desactivar capas#########################################################################
checkMunicipio.addEventListener('change', (e)=>{
    const ocultarMostrar = e.target.checked;
    console.log('esta marcado: el municipio',ocultarMostrar);

    if (capaMunicipios){
        if(ocultarMostrar){
            capaMunicipios.addTo(map);
        } else {
            map.removeLayer(capaMunicipios);
        }
    }
});


checkVeredas.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la vereda: ', ocultarMostrar);

    if(capaVeredas){
        if(ocultarMostrar){
            capaVeredas.addTo(map);
        } else {
            map.removeLayer(capaVeredas);
        }
    }
});


checkVias.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la via: ',ocultarMostrar);

    if(capaVias){
        if(ocultarMostrar){
            capaVias.addTo(map);
        } else {
            map.removeLayer(capaVias);
        }
    }
});


checkUrbano.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la urbana: ',ocultarMostrar);

    if(capaZonaUrbana){
        if(ocultarMostrar){
            capaZonaUrbana.addTo(map);
        } else {
            map.removeLayer(capaZonaUrbana);
        }
    }
});


checkRural.addEventListener('change', (e) =>{
    const ocultarMostrar =e.target.checked;
    console.log('esta marcada la zona rural: ',ocultarMostrar);

    if(capaZonaRural){
        if(ocultarMostrar){
            capaZonaRural.addTo(map);
        } else {
            map.removeLayer(capaZonaRural);
        }
    }
});

// cargar capas de zona geografica (zona urbana, zona rural)#####################################################
fetch(urlZonaUrbana)
    .then(response =>{
        if(!response.ok) throw new Error("Error en la respuesta de la API de zona geografica(urbana)");
        return response.json();
    })
    .then(data => {
        if(capaZonaUrbana){
            map.removeLayer(capaZonaUrbana);
        }
        capaZonaUrbana = crearCapaZonaUrbana(data);
        capaZonaUrbana.addTo(map);
    })
    .catch(err => console.error("Error al cargar la zona urbana: ", err));


fetch(urlZonaRural)
    .then(response =>{
        if(!response.ok) throw new Error("Error en la respuesta de la API de zona geografica(rural)");
        return response.json();
    })
    .then(data => {
        if(capaZonaRural){
            map.removeLayer(capaZonaRural);
        }
        capaZonaRural = crearCapaZonaRural(data);
        capaZonaRural.addTo(map);
    })
    .catch(err => console.error("Error al cargar la zona rural: ", err));

// Función para mostrar / ocultar el spinner de carga
function toggleLoading(show) {
    const overlay = document.getElementById('loading_overlay');
    if (!overlay) return;
    
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

// Exportar a Imagen (PNG / JPG) con leaflet-image
function exportarMapaImagen(formato = 'png') {
    toggleLoading(true); // Mostrar estado de carga

    // Pequeña pausa con setTimeout para asegurar que el DOM dibuje el modal de carga antes de bloquear la CPU
    setTimeout(() => {
        leafletImage(map, function(err, canvas) {
            try {
                if (err) {
                    console.error('Error al generar la imagen:', err);
                    alert('Ocurrió un error al procesar el mapa.');
                    return;
                }

                const mimeType = formato === 'jpg' ? 'image/jpeg' : 'image/png';
                const imageURI = canvas.toDataURL(mimeType, 0.95);

                const link = document.createElement('a');
                link.download = `mapa_exportado.${formato}`;
                link.href = imageURI;
                link.click();
                link.remove();
            } finally {
                toggleLoading(false); // Ocultar estado de carga siempre
            }
        });
    }, 100);
}

// Exportar a PDF con leaflet-image + jsPDF
function exportarMapaPDF() {
    toggleLoading(true);

    setTimeout(() => {
        leafletImage(map, function(err, canvas) {
            try {
                if (err) {
                    console.error('Error al generar el PDF:', err);
                    alert('Ocurrió un error al procesar el PDF.');
                    return;
                }

                const { jsPDF } = window.jspdf;
                const imgData = canvas.toDataURL('image/png');
                
                const orientation = canvas.width > canvas.height ? 'l' : 'p';
                const pdf = new jsPDF(orientation, 'mm', 'a4');

                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = pdf.internal.pageSize.getHeight();

                const ratio = canvas.width / canvas.height;
                let width = pdfWidth - 20;
                let height = width / ratio;

                if (height > pdfHeight - 20) {
                    height = pdfHeight - 20;
                    width = height * ratio;
                }

                pdf.addImage(imgData, 'PNG', 10, 10, width, height);
                pdf.save('mapa_exportado.pdf');
            } finally {
                toggleLoading(false);
            }
        });
    }, 100);
}


document.addEventListener('DOMContentLoaded', () => {
    // Capturar referencias de los botones
    const btnPng = document.getElementById('descargar_png');
    const btnPdf = document.getElementById('descargar_pdf');
    const btnJpg = document.getElementById('descargar_jpg'); // Opcional si agregas botón JPG

    // Asignar el evento 'click' a cada función
    if (btnPng) {
        btnPng.addEventListener('click', () => exportarMapaImagen('png'));
    }

    if (btnJpg) {
        btnJpg.addEventListener('click', () => exportarMapaImagen('jpg'));
    }

    if (btnPdf) {
        btnPdf.addEventListener('click', () => exportarMapaPDF());
    }
});

