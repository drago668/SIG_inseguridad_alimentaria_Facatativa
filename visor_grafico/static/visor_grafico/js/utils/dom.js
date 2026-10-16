
export function toggleLoading(show) {
    const overlay = document.getElementById('loading_overlay');
    if (!overlay) return;
    
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}