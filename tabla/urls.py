from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, CategoriaViewSet, NotificacionMovilViewSet
from .views import ReservaDeMesaViewSet, PlatoViewSet, PromocionDePlatoViewSet
from .views import ComentarioCalificacionViewSet, ClienteViewSet, RegistroDeVentaViewSet
from .views import BebidaViewSet, EntradaViewSet, ContactoViewSet, GananciaMesViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'notificaciones-movil', NotificacionMovilViewSet)
router.register(r'reservas-mesa', ReservaDeMesaViewSet)
router.register(r'platos', PlatoViewSet)
router.register(r'promociones-plato', PromocionDePlatoViewSet)
router.register(r'comentarios-calificacion', ComentarioCalificacionViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'registros-venta', RegistroDeVentaViewSet)
router.register(r'bebidas', BebidaViewSet)
router.register(r'entradas', EntradaViewSet)
router.register(r'contactos', ContactoViewSet)
router.register(r'ganancias-mes', GananciaMesViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    
]
