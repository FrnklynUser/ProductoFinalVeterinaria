from django import forms
from .models import Mascota, Propietario, HistorialClinico, Cita, Factura
from django.contrib.auth.models import User
from django.utils import timezone

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'propietario', 'fecha_nacimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la mascota'}),
            'especie': forms.Select(),
            'raza': forms.TextInput(attrs={'placeholder': 'Raza'}),
            'propietario': forms.Select(),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }

class PropietarioForm(forms.ModelForm):
    class Meta:
        model = Propietario
        fields = ['usuario', 'direccion', 'telefono']
        widgets = {
            'usuario': forms.Select(),
            'direccion': forms.TextInput(attrs={'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono'})
        }

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
        fields = ['mascota', 'fecha_hora', 'motivo', 'notas']
        widgets = {
            'mascota': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Motivo de la cita',
                'required': True
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            })
        }

    def clean_fecha_hora(self):
        fecha_hora = self.cleaned_data.get('fecha_hora')
        if fecha_hora and fecha_hora < timezone.now():
            raise forms.ValidationError('La fecha y hora debe ser futura')
        return fecha_hora

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cita', 'subtotal', 'iva', 'total', 'observaciones']
        widgets = {
            'cita': forms.Select(attrs={'class': 'form-select'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'readonly': True}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'readonly': True}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserProfileEditForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and new_password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data