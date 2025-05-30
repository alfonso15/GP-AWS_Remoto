"""
    great plains URL CONFIGURATION
"""
import json
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView, TemplateView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets.urls import TICKETS_ROUTER
from users.urls import USERS_ROUTER
from users.serializers import CompanySerializer
from django.urls import include

API_V1_ROUTER = DefaultRouter()

API_V1_ROUTER.registry.extend(TICKETS_ROUTER.registry)
API_V1_ROUTER.registry.extend(USERS_ROUTER.registry)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        serializer = CompanySerializer(self.request.user.staff_companies.all(), many=True)
        context['companies'] = json.dumps(serializer.data)
        return context





urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', IndexView.as_view()),
    path('register/', TemplateView.as_view(template_name='register.html')),
    path('login/', TemplateView.as_view(template_name='login.html')),
    path('admin/', admin.site.urls),
    path('api/v2/', include('tickets.apiv2_urls', namespace='api2')),
    path('api/v1/', include([
        path('', include(API_V1_ROUTER.urls)),
    ])),
]

if settings.DEBUG:
    # urlpatterns.append(path('cov/', RedirectView.as_view(url='cov/index.html')))
    #
    # urlpatterns += static('cov', document_root='htmlcov')

    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
