from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializers import UserSerializer, CompanyChangeSerializer


class UserViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(methods=['post'], detail=False)
    def login(self, request):
        user = authenticate(**request.data)
        if user is None:
            raise ValidationError('No se encontró un usuario con el email y la contraseña indicados')
        login(self.request, user)
        return Response()

    @action(methods=["patch"], detail=False)
    def company(self, request, *args, **kwargs):
        serializer = CompanyChangeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(True)
        serializer.save()
        return Response(serializer.data)
