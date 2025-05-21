from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Propietario, Mascota, HistorialClinico, Cita, Factura
from .forms import MascotaForm, PropietarioForm, HistorialClinicoForm, CitaForm, FacturaForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
import json

# Create your views here.
#def inicio(request):
 #   return HttpResponse("Hola, esta es la vista de inicio de la veterinaria.")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Usuario o contraseña incorrectos'})
    
    return render(request, 'core/login.html')

@login_required
def dashboard(request):
    hoy = timezone.now().date()
    
    # Conteos básicos
    context = {
        'mascotas_count': Mascota.objects.count(),
        'propietarios_count': Propietario.objects.count(),
        'citas_hoy': Cita.objects.filter(fecha_hora__date=hoy).count(),
        'ingresos_hoy': Factura.objects.filter(
            fecha=hoy, 
            estado='PAGADA'
        ).aggregate(total=Sum('total'))['total'] or 0,
    }
    
    # Próximas citas
    context['proximas_citas'] = Cita.objects.filter(
        fecha_hora__gte=timezone.now()
    ).order_by('fecha_hora')[:5]
    
    # Actividades recientes
    actividades = []
    # Últimas facturas
    for factura in Factura.objects.order_by('-fecha')[:3]:
        actividades.append({
            'fecha': factura.fecha,
            'descripcion': f'Nueva factura #{factura.numero} - ${factura.total}',
            'icono': 'fa-file-invoice-dollar'
        })
    # Últimas citas
    for cita in Cita.objects.order_by('-fecha_hora')[:3]:
        actividades.append({
            'fecha': cita.fecha_hora,
            'descripcion': f'Cita para {cita.mascota.nombre}',
            'icono': 'fa-calendar-check'
        })
    context['actividades_recientes'] = sorted(
        actividades, 
        key=lambda x: x['fecha'], 
        reverse=True
    )[:5]
    
    # Datos para gráficos
    # Ingresos mensuales
    ultimos_6_meses = []
    ingresos_mensuales = []
    for i in range(5, -1, -1):
        mes = timezone.now() - timedelta(days=30*i)
        ultimos_6_meses.append(mes.strftime('%B'))
        ingreso = Factura.objects.filter(
            fecha__month=mes.month,
            fecha__year=mes.year,
            estado='PAGADA'
        ).aggregate(total=Sum('total'))['total'] or 0
        ingresos_mensuales.append(float(ingreso))
    
    # Distribución de especies
    especies_data = Mascota.objects.values('especie').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context.update({
        'meses': json.dumps(ultimos_6_meses),
        'ingresos_mensuales': json.dumps(ingresos_mensuales),
        'especies_labels': json.dumps([x['especie'] for x in especies_data]),
        'especies_datos': json.dumps([x['total'] for x in especies_data]),
    })
    
    return render(request, 'core/dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def mascota_list(request):
    mascotas = Mascota.objects.all()
    return render(request, 'core/mascota/list.html', {
        'mascotas': mascotas,
        'page_title': 'Mascotas'
    })

@login_required
def mascota_create(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota creada exitosamente.')
            return redirect('core:mascota_list')
    else:
        form = MascotaForm()
    
    return render(request, 'core/mascota/form.html', {
        'form': form,
        'page_title': 'Nueva Mascota'
    })

@login_required
def mascota_edit(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    
    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota actualizada exitosamente.')
            return redirect('core:mascota_list')
    else:
        form = MascotaForm(instance=mascota)
    
    return render(request, 'core/mascota/form.html', {
        'form': form,
        'mascota': mascota,
        'page_title': 'Editar Mascota'
    })

@login_required
def mascota_delete(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        mascota.delete()
        messages.success(request, 'Mascota eliminada exitosamente.')
        return redirect('core:mascota_list')
    
    return render(request, 'core/mascota/delete.html', {
        'mascota': mascota,
        'page_title': 'Eliminar Mascota'
    })

@login_required
def propietario_list(request):
    propietarios = Propietario.objects.all()
    return render(request, 'core/propietario/list.html', {
        'propietarios': propietarios,
        'page_title': 'Propietarios'
    })

@login_required
def propietario_create(request):
    if request.method == 'POST':
        form = PropietarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propietario creado exitosamente.')
            return redirect('core:propietario_list')
    else:
        form = PropietarioForm()
    
    return render(request, 'core/propietario/form.html', {
        'form': form,
        'page_title': 'Nuevo Propietario'
    })

@login_required
def propietario_edit(request, pk):
    propietario = get_object_or_404(Propietario, pk=pk)
    
    if request.method == 'POST':
        form = PropietarioForm(request.POST, instance=propietario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propietario actualizado exitosamente.')
            return redirect('core:propietario_list')
    else:
        form = PropietarioForm(instance=propietario)
    
    return render(request, 'core/propietario/form.html', {
        'form': form,
        'propietario': propietario,
        'page_title': 'Editar Propietario'
    })

@login_required
def propietario_delete(request, pk):
    propietario = get_object_or_404(Propietario, pk=pk)
    if request.method == 'POST':
        propietario.delete()
        messages.success(request, 'Propietario eliminado exitosamente.')
        return redirect('core:propietario_list')
    
    return render(request, 'core/propietario/delete.html', {
        'propietario': propietario,
        'page_title': 'Eliminar Propietario'
    })

# Historial Clínico views
@login_required
def historial_list(request):
    historiales = HistorialClinico.objects.select_related('mascota').all()
    return render(request, 'core/historial/list.html', {
        'historiales': historiales,
        'page_title': 'Historial Clínico'
    })

@login_required
def historial_create(request):
    if request.method == 'POST':
        form = HistorialClinicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro creado exitosamente.')
            return redirect('core:historial_list')
    else:
        form = HistorialClinicoForm()
    
    return render(request, 'core/historial/form.html', {
        'form': form,
        'page_title': 'Nuevo Registro'
    })

@login_required
def historial_edit(request, pk):
    historial = get_object_or_404(HistorialClinico, pk=pk)
    if request.method == 'POST':
        form = HistorialClinicoForm(request.POST, instance=historial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro actualizado exitosamente.')
            return redirect('core:historial_list')
    else:
        form = HistorialClinicoForm(instance=historial)
    
    return render(request, 'core/historial/form.html', {
        'form': form,
        'historial': historial,
        'page_title': 'Editar Registro'
    })

@login_required
def historial_delete(request, pk):
    historial = get_object_or_404(HistorialClinico, pk=pk)
    if request.method == 'POST':
        historial.delete()
        messages.success(request, 'Registro eliminado exitosamente.')
        return redirect('core:historial_list')
    
    return render(request, 'core/historial/delete.html', {
        'historial': historial,
        'page_title': 'Eliminar Registro'
    })

# Citas views
@login_required
def cita_list(request):
    citas = Cita.objects.select_related('mascota').all()
    return render(request, 'core/cita/list.html', {
        'citas': citas,
        'page_title': 'Citas'
    })

@login_required
def cita_create(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita creada exitosamente.')
            return redirect('core:cita_list')
    else:
        form = CitaForm()
    
    return render(request, 'core/cita/form.html', {
        'form': form,
        'page_title': 'Nueva Cita'
    })

@login_required
def cita_edit(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada exitosamente.')
            return redirect('core:cita_detail', pk=cita.pk)
    else:
        form = CitaForm(instance=cita)
    
    return render(request, 'core/cita/edit.html', {
        'form': form,
        'cita': cita,
        'page_title': f'Actualizar Cita #{cita.id}'
    })

@login_required
def cita_delete(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada exitosamente.')
        return redirect('core:cita_list')
    
    return render(request, 'core/cita/delete.html', {
        'cita': cita,
        'page_title': 'Eliminar Cita'
    })

@login_required
def cita_detail(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    historial_reciente = cita.mascota.historiales.order_by('-fecha').first()
    
    return render(request, 'core/cita/detail.html', {
        'cita': cita,
        'historial_reciente': historial_reciente,
        'page_title': f'Cita #{cita.id}'
    })

# Factura views
@login_required
def factura_list(request):
    facturas = Factura.objects.select_related('propietario')
    return render(request, 'core/factura/list.html', {
        'facturas': facturas,
        'page_title': 'Facturas'
    })

@login_required
def factura_create(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura creada exitosamente.')
            return redirect('core:factura_list')
    else:
        form = FacturaForm()
    
    return render(request, 'core/factura/form.html', {
        'form': form,
        'page_title': 'Nueva Factura'
    })

@login_required
def factura_edit(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura actualizada exitosamente.')
            return redirect('core:factura_list')
    else:
        form = FacturaForm(instance=factura)
    
    return render(request, 'core/factura/form.html', {
        'form': form,
        'factura': factura,
        'page_title': 'Editar Factura'
    })

@login_required
def factura_delete(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        factura.delete()
        messages.success(request, 'Factura eliminada exitosamente.')
        return redirect('core:factura_list')
    
    return render(request, 'core/factura/delete.html', {
        'factura': factura,
        'page_title': 'Eliminar Factura'
    })

@login_required
def factura_detail(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    detalles = factura.detalles.select_related('servicio').all()
    
    return render(request, 'core/factura/detail.html', {
        'factura': factura,
        'detalles': detalles,
        'page_title': f'Factura #{factura.numero}'
    })

@login_required
def factura_anular(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == 'POST':
        factura.estado = 'ANULADA'
        factura.save()
        messages.success(request, 'Factura anulada exitosamente.')
        return redirect('core:factura_list')
    
    return render(request, 'core/factura/anular.html', {
        'factura': factura,
        'page_title': 'Anular Factura'
    })

@login_required
def reporte_dashboard(request):
    return render(request, 'core/reporte/dashboard.html', {
        'page_title': 'Dashboard de Reportes'
    })

@login_required
def reporte_ventas(request):
    return render(request, 'core/reporte/ventas.html', {
        'page_title': 'Reporte de Ventas'
    })

@login_required
def reporte_citas(request):
    return render(request, 'core/reporte/citas.html', {
        'page_title': 'Reporte de Citas'
    })