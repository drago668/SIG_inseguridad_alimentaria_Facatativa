import { map } from "./mapBase.js"; 

// Municipio
const estiloMunicipio = {
    color: "#059669",      
    weight: 3,             
    opacity: 0.7,
    fillColor: "#10b981",  
    fillOpacity: 0.1      
};

// veredas
const estiloVereda = {
color: "#8a2b0e",      
weight: 3,             
opacity: 0.9,
fillColor:  "#601e0a",  
fillOpacity: 0.6      
};

// vias
function estiloSegunVia(feature) {
    const fclass = feature.properties.fclass;
        switch (fclass) {
            case 'motorway':
                return {color: '#D73027', weight:5, opacity:1};
            case 'trunk':
                return { color: '#F46D43', weight: 5, opacity: 1 }; 
            case 'primary':
                return { color: '#FDAE61', weight: 4, opacity: 0.7 };
            case 'secondary':
                return { color: '#A6D96A', weight: 3, opacity: 0.6 };
            case 'tertiary':
                return { color: '#1A9850', weight: 3, opacity: 0.6 }; 
            case 'unclassified':
                return { color: '#66C2A5', weight: 2, opacity: 0.5 }; 
            case 'residential':
                return { color: '#74ADD1', weight: 1, opacity: 0.5 };
            default:
                return { color: '#BDBDBD', weight: 1, opacity: 0.3 };
        }
}

// zona rural
const estiloRural = {
color: "#ff8888",      
weight: 3,             
opacity: 0.9,
fillColor:  "#a05656",  
fillOpacity: 0.9      
};

// zona urbana
const estiloUrbano = {
color: "#c988ff",      
weight: 3,             
opacity: 0.9,
fillColor:  "#63427e",  
fillOpacity: 0.9      
};

// urls de consulta
urlViasGeoJSON 
urlFacatativaGeoJSON 
urlMunicipioGeoJSON
urlVeredasGeoJSON 

export function crearCapaVias(data) {
    const viaApartada = L.geoJSON(data, {
        style: estiloSegunVia,
        onEachFeature: function (feature, layer){
            const props = feature.properties;
            const nombreVia = props.name || "Vía sin nombre";
            const velocidad = props.maxspeed ? `${props.maxspeed} km/h` : "No registrada";
            layer.bindPopup(`
                <b>Vía:</b> ${nombreVia}<br>
                <b>Tipo:</b> ${props.fclass}<br>
                <b>Velocidad Máx:</b> ${velocidad}`
            );
        }
    })
    return viaApartada;
}


export function crearCapaMunicipios(data) {
    const municipioApartado = L.geoJSON(data, {
        style: estiloMunicipio,
        onEachFeature: function (feature, layer){
            const props = feature.properties;
            layer.bindPopup(`
                <div style="text-align: center;">
                    <h3 style="margin:0; color:#059669;">${props.mpio_cnmbr}</h3>
                    <p style="margin: 5px 0;"><b>Código DANE:</b> ${props.mpio_cdpmp}</p>
                    <p style="margin: 0;"><b>Departamento:</b> Cundinamarca (${props.dpto_ccdgo})</p>
                </div>
            `);
        }
    })
    return municipioApartado;
}


export function crearCapaVeredas(data) {
    const veredaApartada =L.geoJSON(data, {
        style: estiloVereda,
        onEachFeature: function (feature, layer){
            const props = feature.properties;
            layer.bindPopup(`
                <b>Vereda:</b> ${props.nombre_ver || "Vereda sin nombre"}<br>
                <b>Departamento:</b> ${props.nom_dep ? `${props.nom_dep} (${props.cod_dpto})` : "Departamento no disponible"}<br>
                <b>Municipio:</b> ${props.nom_mpio}<br>
                <b>Area:</b> ${props.area_ha ? `${props.area_ha} h`:"No existe informacion"}<br> de informalidad:</b> ${props.tasa_informalidad || "No existe informacion"}<br>
            `);
        }
    })
    return  veredaApartada;
}


export function crearCapaZonaRural(data) {
    const rural = L.geoJSON(data, {
        style: estiloRural,
        onEachFeature: function(feature, layer){
            const props = feature.properties;
            layer.bindPopup(`
                <div style="font-family: sans-serif; padding: 0.25rem;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1e293b;">${props.nombre_zona}</h4>
                    <p style="margin: 4px 0;"><strong>Área Territorial:</strong> ${props.tipo_zona}</p>
                    <p style="margin: 4px 0; color: #b91c1c ;"><strong>Índice Promedio:</strong> ${props.promedio_indice} pts</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 8px 0;">
                    <p style="margin: 4px 0; font-size: 0.85rem;">🏠 Hogares Registrados: ${props.total_hogares}</p>
                    <p style="margin: 4px 0; font-size: 0.85rem;">👶 Carga Infantil Promedio: ${props.promedio_ninos}</p>
                    <p style="margin: 4px 0; font-size: 0.85rem;">💼 Tasa Informalidad: ${props.tasa_informalidad}%</p>
                </div>
            `);
        }
    })
    return rural
}


export function crearCapaZonaUrbana(data) {
    const urbano = L.geoJSON(data, {
        style: estiloUrbano,
        onEachFeature: function(feature, layer){
            const props = feature.properties;
            layer.bindPopup(`
                <div style="font-family: sans-serif; padding: 0.25rem;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1e293b;">${props.nombre_zona}</h4>
                    <p style="margin: 4px 0;"><strong>Área Territorial:</strong> ${props.tipo_zona}</p>
                    <p style="margin: 4px 0; color: #2cb91c;"><strong>Índice Promedio:</strong> ${props.promedio_indice} pts</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 8px 0;">
                    <p style="margin: 4px 0; font-size: 0.85rem;">🏠 Hogares Registrados: ${props.total_hogares}</p>
                    <p style="margin: 4px 0; font-size: 0.85rem;">👶 Carga Infantil Promedio: ${props.promedio_ninos}</p>
                    <p style="margin: 4px 0; font-size: 0.85rem;">💼 Tasa Informalidad: ${props.tasa_informalidad}%</p>
                </div>
            `)
        }
    })
    return urbano
}