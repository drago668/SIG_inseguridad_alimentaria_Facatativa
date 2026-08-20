# app_capas/forms.py
from django import forms
from .models import CapaEspacial

class CapaEspacialForm(forms.ModelForm):
    class Meta:
        model = CapaEspacial
        fields = ['nombre', 'descripcion', 'formato', 'archivo', 'url_wfs', 'capa_wfs_layer']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500'}),
            'formato': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500'}),
            'archivo': forms.FileInput(attrs={'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100'}),
            'url_wfs': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500', 'placeholder': 'https://ejemplo.com/geoserver/wfs'}),
            'capa_wfs_layer': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500', 'placeholder': 'workspace:nombre_capa'}),
        }