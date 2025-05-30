from rest_framework.routers import SimpleRouter
from .views import UserViewSet


USERS_ROUTER = SimpleRouter()

USERS_ROUTER.register('users', UserViewSet, basename='users')
