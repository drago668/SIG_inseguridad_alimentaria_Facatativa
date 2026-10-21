export async function crearCapaPoliticasAlimentaria() {
    try {
        const res = await fetch('/capas/api/politicas-seguridad-alimentaria/');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        
        if (data.features.length === 0) {
            console.warn('[Visor] No hay políticas de seguridad alimentaria');
            return null;
        }
        
        return L.geoJSON(data, {
            style: (feature) => ({
                color: feature.properties._color_sugerido,
                weight: 2,
                fillColor: feature.properties._color_sugerido,
                fillOpacity: 0.6
            }),
            onEachFeature: (feature, layer) => {
                const p = feature.properties;
                let popup = `<strong>Municipio: ${p.f2 || p.f3 || 'N/A'}</strong><br>`;
                popup += `Política alimentaria: ${p._valor_f22 || 'N/A'}<br>`;
                popup += `Código DANE: ${p.codigo_mun || p.EXCEL_ID || 'N/A'}<br>`;
                layer.bindPopup(popup);
            }
        });
    } catch (e) {
        console.error('[Visor] Error cargando políticas alimentarias:', e);
        return null;
    }
}