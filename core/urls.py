from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Protected Vision API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'documents': '/api/documents/',
            'detection': '/api/detection/',
            'docs': '/api/docs/',
        }
    })

schema_view = get_schema_view(
    openapi.Info(
        title="Protected Vision API",
        default_version='v1',
        description="API for Protected Vision document analysis",
        terms_of_service="https://www.protectedvision.com/terms/",
        contact=openapi.Contact(email="contact@protectedvision.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root URL
    path('', api_root, name='api-root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/auth/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/detection/', include('detection.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 