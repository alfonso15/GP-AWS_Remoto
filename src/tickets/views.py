from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from app.db_handler import FailureCatalogueHandler, SerialNumbersHandler
from users.models import Token
from .models import Ticket
from .serializers import TicketSerializer, TicketUpdateSerializer


class TokenPermission(BasePermission):
    """Permission class for token auth"""
    def has_permission(self, request, view):
        token = request.data.pop('token', None)
        if token is None:
            return False
        try:
            Token.objects.get(uuid=token)
            return True
        except Token.DoesNotExist:
            return False


class TicketViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, UpdateModelMixin):
    serializer_class = TicketSerializer
    filterset_fields = ['serial_number', 'failure_id']
    permission_classes = [IsAuthenticated]
    lookup_field = 'report_id'

    def get_permissions(self):
        if self.action == 'partial_update':
            return [TokenPermission()]
        return super(TicketViewSet, self).get_permissions()

    def get_queryset(self):
        if self.action == 'partial_update':
            return Ticket.objects.all()
        return Ticket.objects.filter(company=self.request.user.company)

    def update(self, request, *args, **kwargs):
        self.serializer_class = TicketUpdateSerializer
        return super(TicketViewSet, self).update(request, *args, **kwargs)

    @action(detail=False, methods=['GET'])
    def serials(self, request, *args, **kwargs):
        data = SerialNumbersHandler().get_serial_numbers(self.request.user.company)
        return Response(data)

    @action(detail=False, methods=['GET'])
    def failures(self, request, *args, **kwargs):
        data = FailureCatalogueHandler().get_failures_catalogue()
        return Response(data)
