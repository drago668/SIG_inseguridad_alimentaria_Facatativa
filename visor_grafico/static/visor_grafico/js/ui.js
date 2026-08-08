import { map } from "./mapBase.js";

const sidebar = document.querySelector('#sidebar');
const colapse = document.querySelector('#colapse');
const arrowIcon = document.getElementById('arrow');

const checkMunicipio = document.querySelector('#chk-municipio');
const checkVeredas = document.querySelector('#chk-veredas');
const checkVias = document.querySelector('#chk-vias');

// aqui se oculta la barra lateral para diseño responsivo en moviles
window.addEventListener('resize', (e) =>{
    const esPantallaGrande = window.innerWidth >= 768;

    if (esPantallaGrande) {
        console.log("El usuario está en una PC o tablet grande");
        arrowIcon.classList.remove('hidden');
        // Aquí pones el código para acomodar tu barra lateral en PC
    } else {
        console.log("El usuario está en un celular");
        sidebar.classList.add('hidden');
        arrowIcon.classList.add('hidden');5
    }
});


colapse.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');

    setTimeout(() => {
        if (typeof map !== 'undefined') {
            map.invalidateSize();
        }
    }, 300); 
});


// activar o desactivar capas
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


