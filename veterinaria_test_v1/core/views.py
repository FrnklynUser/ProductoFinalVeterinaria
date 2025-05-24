from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import HistorialClinico, Mascota, Cita, Factura, Propietario
from .forms import MascotaForm, PropietarioForm, HistorialClinicoForm, CitaForm, FacturaForm, UserProfileEditForm
import io
from datetime import timedelta
from django.db.models import Count, Sum
import json
from openpyxl import Workbook
from django.urls import reverse
from django.db import connection
from django.core.paginator import Paginator
from django.db.models import Q



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('core:dashboard')  
        else:
            messages.error(request, 'Usuario o contraseña incorrectos') 

    return render(request, 'accounts/login.html')
@login_required
def dashboard(request):
    total_mascotas = Mascota.objects.count()
    total_citas = Cita.objects.count()
    total_facturas = Factura.objects.count()
    
    try:
        citas_recientes = Cita.objects.select_related('mascota').order_by('-fecha_hora')[:5]
    except Exception:
        citas_recientes = []
    
    try:
        facturas_recientes = Factura.objects.select_related(
            'cita', 'cita__mascota'
        ).order_by('-fecha_emision')[:5]
    except Exception:
        facturas_recientes = []
    
    try:
        now = timezone.now()
        primer_dia_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ingresos_mes = Factura.objects.filter(
            fecha_emision__gte=primer_dia_mes,
            estado='PAGADA'
        ).aggregate(
            total=Sum('total')
        )['total'] or 0
    except Exception:
        ingresos_mes = 0
    
    return render(request, 'core/dashboard.html', {
        'total_mascotas': total_mascotas,
        'total_citas': total_citas,
        'total_facturas': total_facturas,
        'citas_recientes': citas_recientes,
        'facturas_recientes': facturas_recientes,
        'ingresos_mes': ingresos_mes,
        'page_title': 'Dashboard'
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:login')

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
            mascota = form.save()
            messages.success(request, 'Mascota creada exitosamente.')
            return redirect('core:mascota_list')
    else:
        form = MascotaForm()

    return render(request, 'core/mascota/form.html', {
        'form': form,
        'page_title': 'Nueva Mascota',
        'cancel_url': reverse('core:mascota_list'),
        'icon': 'plus'
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
        'page_title': f'Editar Mascota: {mascota.nombre}',
        'cancel_url': reverse('core:mascota_list'),
        'icon': 'edit'
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

@login_required
def historial_detail(request, pk):
    historial = get_object_or_404(HistorialClinico, pk=pk)
    return render(request, 'core/historial/detail.html', {
        'historial': historial,
        'page_title': f'Historial #{historial.id}'
    })


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
            cita = form.save(commit=False)
            cita.estado = 'PENDIENTE'
            cita.save()
            messages.success(request, 'Cita creada exitosamente.')
            return redirect('core:cita_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = CitaForm()

    return render(request, 'core/cita/form.html', {
        'form': form,
        'page_title': 'Nueva Cita',
        'cancel_url': reverse('core:cita_list'),
        'icon': 'plus'
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


@login_required
def factura_list(request):
    facturas = Factura.objects.select_related(
        'cita',
        'cita__mascota',
        'cita__mascota__propietario'
    ).all()
    
    # Búsqueda
    q = request.GET.get('q')
    if q:
        facturas = facturas.filter(
            Q(numero__icontains=q) |
            Q(cita__mascota__nombre__icontains=q) |
            Q(cita__mascota__propietario__usuario__first_name__icontains=q)
        )
    
    # Paginación
    paginator = Paginator(facturas, 10)
    page = request.GET.get('page')
    facturas = paginator.get_page(page)
    
    return render(request, 'core/factura/list.html', {'facturas': facturas})

@login_required
def factura_create(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.estado = 'PENDIENTE'
            factura.save()
            messages.success(request, 'Factura creada exitosamente.')
            return redirect('core:factura_detail', pk=factura.numero)
    else:
        # Preseleccionar cita si viene como parámetro
        initial = {}
        cita_id = request.GET.get('cita')
        if cita_id:
            try:
                cita = Cita.objects.get(id=cita_id)
                initial['cita'] = cita
            except Cita.DoesNotExist:
                pass
        form = FacturaForm(initial=initial)
    
    return render(request, 'core/factura/create.html', {
        'form': form,
        'titulo': 'Nueva Factura'
    })

@login_required
def factura_edit(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    
    if request.method == 'POST':
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            messages.success(request, 'Factura actualizada exitosamente.')
            return redirect('core:factura_detail', pk=factura.pk)
    else:
        form = FacturaForm(instance=factura)

    return render(request, 'core/factura/form.html', {
        'form': form,
        'factura': factura,
        'page_title': f'Editar Factura #{factura.id}'
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
    return render(request, 'core/reporte/dashboard_1.html', {
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

@login_required
def profile_view(request):
    return render(request, 'core/profile.html', {
        'user': request.user,
        'page_title': 'Mi Perfil'
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('core:profile')
    else:
        form = UserProfileEditForm(instance=request.user)
    
    return render(request, 'core/profile_edit.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:login')

@login_required
def estadisticas_clinicas(request):
    return render(request, 'core/reporte/estadisticas.html', {
        'page_title': 'Estadísticas Clínicas'
    })
def exportar_estadisticas_clinicas_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Estadísticas"

    ws.append(["Paciente", "Tratamiento", "Fecha"])
    # ejemplo(["Juan Pérez", "Carilla", "2025-05-01"])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=estadisticas_clinicas.xlsx'

    wb.save(response)
    return response