from django.shortcuts import render
from django.contrib import admin
# views.py
from matplotlib import pyplot as plt
from rest_framework import viewsets
from .models import Usuario, Categoria, NotificacionMovil, ReservaDeMesa, Plato, PromocionDePlato, ComentarioCalificacion, Cliente, RegistroDeVenta, Bebida, Entrada, Contacto, GananciaMes
from .serializers import UsuarioSerializer, CategoriaSerializer, NotificacionMovilSerializer, ReservaDeMesaSerializer, PlatoSerializer, PromocionDePlatoSerializer, ComentarioCalificacionSerializer, ClienteSerializer, RegistroDeVentaSerializer, BebidaSerializer, EntradaSerializer, ContactoSerializer, GananciaMesSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class NotificacionMovilViewSet(viewsets.ModelViewSet):
    queryset = NotificacionMovil.objects.all()
    serializer_class = NotificacionMovilSerializer

class ReservaDeMesaViewSet(viewsets.ModelViewSet):
    queryset = ReservaDeMesa.objects.all()
    serializer_class = ReservaDeMesaSerializer

class PlatoViewSet(viewsets.ModelViewSet):
    queryset = Plato.objects.all()
    serializer_class = PlatoSerializer

class PromocionDePlatoViewSet(viewsets.ModelViewSet):
    queryset = PromocionDePlato.objects.all()
    serializer_class = PromocionDePlatoSerializer


class ComentarioCalificacionViewSet(viewsets.ModelViewSet):
    queryset = ComentarioCalificacion.objects.all().order_by('-fecha')
    serializer_class = ComentarioCalificacionSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class RegistroDeVentaViewSet(viewsets.ModelViewSet):
    queryset = RegistroDeVenta.objects.all()
    serializer_class = RegistroDeVentaSerializer

class BebidaViewSet(viewsets.ModelViewSet):
    queryset = Bebida.objects.all()
    serializer_class = BebidaSerializer

class EntradaViewSet(viewsets.ModelViewSet):
    queryset = Entrada.objects.all()
    serializer_class = EntradaSerializer

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.all()
    serializer_class = ContactoSerializer

class GananciaMesViewSet(viewsets.ModelViewSet):
    queryset = GananciaMes.objects.all()
    serializer_class = GananciaMesSerializer




## CODIGO PARA LOS DATOS DEL PDF

from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib
matplotlib.use('Agg')
import io
from PIL import Image as PILImage

class GananciaMesAdmin(admin.ModelAdmin):
    list_display = ['mes', 'total_reservas', 'total_registros_venta', 'ganancia_reservas', 'ganancia_registros_venta', 'ganancia_total', 'acciones']

    def acciones(self, obj):
        return format_html('<a class="button" href="{}">Descargar PDF</a>', reverse('admin:descargar_reporte_pdf', args=[obj.pk]))
    acciones.short_description = 'Acciones'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('descargar-reporte-pdf/<int:pk>/', self.admin_site.admin_view(descargar_reporte_pdf), name='descargar_reporte_pdf'),
        ]
        return custom_urls + urls

def descargar_reporte_pdf(request, pk):
    ganancia_mes = get_object_or_404(GananciaMes, pk=pk)
    ganancia_mes.actualizar_ganancias()
    buffer = generar_pdf(ganancia_mes)
    return FileResponse(buffer, as_attachment=True, filename=f'Ganancias_{ganancia_mes.mes.strftime("%B_%Y")}.pdf')

def generar_pdf(ganancia_mes):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()


    # Generar la imagen de la gráfica
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(ganancia_mes.fechas))
    width = 0.10
    ax.bar([i - width/1 for i in x], ganancia_mes.ganancias_reservas, width, label='Reservas')
    ax.bar([i + width/1 for i in x], ganancia_mes.ganancias_ventas, width, label='Ventas')
    ax.set_xlabel('Dias del mes')
    ax.set_ylabel('Ganancia Monto')
    ax.set_title(f'Ganancias de {ganancia_mes.mes.strftime("%B %Y")}')
    ax.set_xticks(x)
    ax.set_xticklabels(ganancia_mes.fechas, rotation=45, ha='right')
    ax.legend()
    plt.tight_layout()
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=300)
    img_buffer.seek(0)

    # Ajustar el tamaño de la imagen
    img = PILImage.open(img_buffer)
    max_width = 600
    img_width, img_height = img.size
    aspect_ratio = img_height / img_width
    if img_width > max_width:
        new_width = max_width
        new_height = int(new_width * aspect_ratio)
        img = img.resize((new_width, new_height), PILImage.LANCZOS)
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    image = Image(img_buffer, width=7.5*inch, height=3.75*inch)
    elements.append(image)
    elements.append(Spacer(1, 0.25*inch))

    # Crear la tabla de datos
    data = [['Día', 'Reservas', 'Ventas', 'Total']]
    for fecha, reserva, venta in zip(ganancia_mes.fechas, ganancia_mes.ganancias_reservas, ganancia_mes.ganancias_ventas):
        total = reserva + venta
        data.append([fecha, f"s/ {reserva:.2f}", f"s/ {venta:.2f}", f"s/ {total:.2f}"])
    
    # Añadir fila de totales
    total_reservas = sum(ganancia_mes.ganancias_reservas)
    total_ventas = sum(ganancia_mes.ganancias_ventas)
    total_general = total_reservas + total_ventas
    data.append(['Total', f"s/ {total_reservas:.2f}", f"s/ {total_ventas:.2f}", f"s/ {total_general:.2f}"])

    table = Table(data, colWidths=[1*inch, 2*inch, 2*inch, 2*inch])
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-2), colors.beige),
        ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
    ])
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer