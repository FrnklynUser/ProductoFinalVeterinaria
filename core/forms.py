from django import forms
from .models import Mascota, Propietario, HistorialClinico, Cita, Factura
from .models import HistorialClinico

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'fecha_nacimiento', 'propietario']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['usuario', 'direccion', 'telefono']

class HistorialClinicoForm(forms.ModelForm):
    class Meta:
        model = HistorialClinico
        fields = ['mascota', 'motivo_consulta', 'diagnostico', 'tratamiento', 'observaciones']
        widgets = {
            'mascota': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Seleccione una mascota'
            }),
            'motivo_consulta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el motivo de la consulta'
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ingrese el diagnóstico'
            }),
            'tratamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ingrese el tratamiento'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese observaciones adicionales'
            })
        }

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['mascota', 'fecha_hora', 'motivo', 'estado', 'notas']
        widgets = {
            'mascota': forms.Select(attrs={
                'class': 'form-select',
                'placeholder': 'Seleccione una mascota'
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el motivo de la cita'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre la cita'
            })
        }

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['numero', 'propietario', 'subtotal', 'iva', 'total']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'propietario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'subtotal': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'iva': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'total': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Generate next invoice number
            last_invoice = Factura.objects.order_by('-numero').first()
            if last_invoice:
                next_number = int(last_invoice.numero) + 1
            else:
                next_number = 1
            self.initial['numero'] = f"{next_number:08d}"