import { capaMunicipios,  capaVeredas, capaVias } from "./main.js";

export const map = L.map('map').setView([4.813, -74.354], 13);

const openStreetMap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '&copy; OpenStreetMap contributors | DANE Colombia',
maxZoom: 19
});

const cartoPositron = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
subdomains: 'abcd',
maxZoom: 20
});

const cartoDark = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
subdomains: 'abcd',
maxZoom: 20
});

const cartoVoyager = L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager_labels_under/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors &copy; <a href="https://carto.com">CARTO</a>',
subdomains: 'abcd',
maxZoom: 20
});


cartoPositron.addTo(map);


const baseMaps = {
"CartoDB Positron": cartoPositron,
"OpenStreetMap":openStreetMap,
"CartoDB Dark Matter": cartoDark,
"CartoDB Voyager": cartoVoyager,
};

export const layerControl = L.control.layers(baseMaps).addTo(map);

