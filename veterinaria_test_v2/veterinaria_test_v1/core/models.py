from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import decimal
import decimal
from django.db import models
from django.core.validators import MinValueValidator

class Propietario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

class Mascota(models.Model):
    ESPECIE_CHOICES = [
        ('PERRO', 'Perro'),
        ('GATO', 'Gato'),
        ('AVE', 'Ave'),
        ('OTRO', 'Otro')
    ]
    
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES)
    raza = models.CharField(max_length=100)
    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()})"

class HistorialClinico(models.Model):
    mascota = models.ForeignKey('Mascota', on_delete=models.CASCADE, related_name='historiales')
    fecha = models.DateTimeField(auto_now_add=True)
    motivo_consulta = models.CharField(max_length=200)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

class Cita(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    mascota = models.ForeignKey('Mascota', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    motivo = models.CharField(max_length=200)
    notas = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Factura(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]
    
    numero = models.AutoField(primary_key=True)
    cita = models.ForeignKey('Cita', on_delete=models.CASCADE, related_name='facturas')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal('0.01'))]
    )
    iva = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True
    )
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='PENDIENTE'
    )
    observaciones = models.TextField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_emision']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f'Factura #{self.numero} - {self.cita.mascota.nombre}'

    def save(self, *args, **kwargs):
        # Calcular IVA si no está definido
        if self.iva is None:
            self.iva = self.subtotal * decimal.Decimal('0.19')
        
        # Calcular total si no está definido
        if self.total is None:
            self.total = self.subtotal + self.iva
        
        super().save(*args, **kwargs)

    def calcular_totales(self):
        """Método para recalcular totales manualmente"""
        self.iva = self.subtotal * decimal.Decimal('0.19')
        self.total = self.subtotal + self.iva
        
    @property
    def puede_anularse(self):
        """Verifica si la factura puede ser anulada"""
        return self.estado in ['PENDIENTE']
    
    def anular(self):
        """Anula la factura si es posible"""
        if self.puede_anularse:
            self.estado = 'ANULADA'
            self.save()
            return True
        return False

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.servicio.nombre} - Factura #{self.factura.numero}"
    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)