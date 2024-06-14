from rest_framework import serializers
from .models import Usuario, Categoria, NotificacionMovil, ReservaDeMesa, Plato, PromocionDePlato, ComentarioCalificacion, Cliente, RegistroDeVenta, Bebida, Entrada, Contacto, GananciaMes

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class NotificacionMovilSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionMovil
        fields = '__all__'

class ReservaDeMesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaDeMesa
        fields = '__all__'

class PlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plato
        fields = '__all__'

class PromocionDePlatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromocionDePlato
        fields = '__all__'

class ComentarioCalificacionSerializer(serializers.ModelSerializer):
    nombre_usuario = serializers.CharField(source='usuario.nombre_usuario', read_only=True)

    class Meta:
        model = ComentarioCalificacion
        fields = ['nombre_cliente', 'fecha', 'calificacion', 'comentario', 'nombre_usuario']


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class RegistroDeVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroDeVenta
        fields = '__all__'

class BebidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bebida
        fields = '__all__'

class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = '__all__'

class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = '__all__'

class GananciaMesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GananciaMes
        fields = '__all__'
