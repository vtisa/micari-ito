import os
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

# Define a custom storage location for uploaded images
image_storage = FileSystemStorage(
    location=settings.MEDIA_ROOT,
)

# Function to generate upload path based on model name
def get_upload_path(instance, filename):
    model_name = instance.__class__.__name__.lower()
    return os.path.join('images', model_name, filename)


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)
    nombre_usuario = models.CharField(max_length=50, unique=True)
    contraseña = models.CharField(max_length=128)

    def save(self, *args, **kwargs):

        if not self.pk or not check_password(self.contraseña, Usuario.objects.get(pk=self.pk).contraseña):
            self.contraseña = make_password(self.contraseña)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class NotificacionMovil(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.usuario.nombre_usuario}'

    @classmethod
    def enviar_a_todos(cls, titulo, mensaje):
        usuarios = Usuario.objects.all()
        for usuario in usuarios:
            cls.objects.create(usuario=usuario, titulo=titulo, mensaje=mensaje)

class Plato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    imagen = models.ImageField(upload_to=get_upload_path, storage=image_storage, blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class PromocionDePlato(models.Model):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    enunciado = models.TextField(null=True)
    precio_descuento = models.DecimalField(max_digits=6, decimal_places=2)
    imagen = models.ImageField(upload_to=get_upload_path, storage=image_storage, blank=True, null=True)

    def __str__(self):
        return f'{self.plato.nombre}'


class ComentarioCalificacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    calificacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField(max_length=200, blank=False, null=False)

    def _str_(self):
        if self.usuario:
            return f'{self.usuario.nombre_usuario} - {self.calificacion}'
        elif self.nombre_cliente:
            return f'{self.nombre_cliente} - {self.calificacion}'
        else:
            return f'Anónimo - {self.calificacion}'

    def save(self, *args, **kwargs):
        if self.usuario:
            # Si es un usuario el que escribe, nombre_cliente debe quedar nulo
            self.nombre_cliente = None
        else:
            # Si el campo nombre_cliente está en blanco, asignar 'Anónimo'
            if not self.nombre_cliente:
                self.nombre_cliente = 'Anónimo'
            # Si hay un nombre de cliente, asegurar que usuario es nulo
            else:
                self.usuario = None
        
        # Guardar los cambios
        super().save(*args, **kwargs)

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Bebida(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    imagen = models.ImageField(upload_to=get_upload_path, storage=image_storage, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Entrada(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    imagen = models.ImageField(upload_to=get_upload_path, storage=image_storage, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField()
    mensaje = models.TextField()

    def __str__(self):
        return f'{self.nombre} - {self.correo_electronico}'


class RegistroDeVenta(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    platos = models.ManyToManyField('Plato')
    bebidas = models.ManyToManyField('Bebida', blank=True)
    entradas = models.ManyToManyField('Entrada', blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_venta = models.DateField(auto_now_add=True)

    def __str__(self):
        fecha_formateada = self.fecha_venta.strftime('%Y-%m-%d')
        return f'{self.cliente.nombre} - {fecha_formateada}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        GananciaMes.actualizar_o_crear_ganancia_mes(self.fecha_venta)

class ReservaDeMesa(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    num_personas = models.IntegerField()
    numero_mesa = models.IntegerField()
    fecha = models.DateField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    hora = models.TimeField(null=False)
    nota = models.TextField(blank=True, null=True)
    fecha_reg = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Reserva para {self.usuario.nombre} ({self.fecha} - {self.hora})'

    def save(self, *args, **kwargs):
        if self.hora is None:
            raise ValidationError("La hora no puede ser nula.")
        super().save(*args, **kwargs)
        GananciaMes.actualizar_o_crear_ganancia_mes(self.fecha_reg)



class GananciaMes(models.Model):
    mes = models.DateField(unique=True)
    total_reservas = models.IntegerField(default=0)
    total_registros_venta = models.IntegerField(default=0)
    ganancia_reservas = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ganancia_registros_venta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ganancia_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fechas = []  
    ganancias_reservas = []  
    ganancias_ventas = [] 

    def __str__(self):
        return f'Ganancias de {self.mes.strftime("%B %Y")}'

    @classmethod
    def actualizar_o_crear_ganancia_mes(cls, fecha_reg):
        mes = fecha_reg.replace(day=1)
        ganancia_mes, created = cls.objects.get_or_create(mes=mes)
        ganancia_mes.actualizar_ganancias(fecha_reg)
        return ganancia_mes

    def actualizar_ganancias(self, fecha_reg=None):
        # Actualizamos las reservas
        reservas = ReservaDeMesa.objects.filter(fecha_reg__year=self.mes.year, fecha_reg__month=self.mes.month)
        self.total_reservas = reservas.count()
        self.ganancia_reservas = reservas.aggregate(Sum('precio'))['precio__sum'] or Decimal('0.00')

        # Actualizamos las ventas
        ventas = RegistroDeVenta.objects.filter(fecha_venta__year=self.mes.year, fecha_venta__month=self.mes.month)
        self.total_registros_venta = ventas.count()
        self.ganancia_registros_venta = ventas.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')

        # Actualizamos la ganancia total
        self.ganancia_total = self.ganancia_reservas + self.ganancia_registros_venta

        # Actualizar las listas de fechas y ganancias
        self.fechas = sorted(list(set(
            reservas.values_list('fecha_reg__day', flat=True).distinct()
        ).union(
            ventas.values_list('fecha_venta__day', flat=True).distinct()
        )))

        self.ganancias_reservas = [0] * len(self.fechas)
        self.ganancias_ventas = [0] * len(self.fechas)

        for reserva in reservas:
            if reserva.fecha_reg.day in self.fechas:
                index = self.fechas.index(reserva.fecha_reg.day)
                self.ganancias_reservas[index] += reserva.precio

        for venta in ventas:
            if venta.fecha_venta.day in self.fechas:
                index = self.fechas.index(venta.fecha_venta.day)
                self.ganancias_ventas[index] += venta.total

        self.save()