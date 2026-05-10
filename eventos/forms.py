from django import forms
from .models import SituacaoEvento, Situacao

class SituacaoEventoForm(forms.ModelForm):
    class Meta:
        model = SituacaoEvento
        fields = ['situacao', 'tipo_evento', 'confianca', 'justificativa']
        widgets = {
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'tipo_evento': forms.TextInput(attrs={'class': 'form-control'}),
            'confianca': forms.Select(attrs={'class': 'form-select'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }