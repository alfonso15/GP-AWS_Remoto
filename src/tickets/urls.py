from rest_framework.routers import SimpleRouter
from .views import TicketViewSet


TICKETS_ROUTER = SimpleRouter()

TICKETS_ROUTER.register('tickets', TicketViewSet, basename='tickets')
