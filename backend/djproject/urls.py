"""Root URL configuration for the Django project.

We include the `accounts` app at root for templates and again under `/api/` for API endpoints.
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from accounts import views
from django.views.static import serve
from django.urls import path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Mount accounts app (templates + APIs) at root using a namespace
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),
    # Redirect legacy static 'index.html' links to the root home view
    path('index.html', RedirectView.as_view(url='/', permanent=False)),
    # API routes mounted under /api/ for client JS convenience
    re_path(r'^(?P<path>.*\.html)$', views.dynamic_html, name='dynamic_html'),
]

if settings.DEBUG:
    # Serve static files during development
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'accounts', 'static'))
    # Serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Explicitly add /assets/ URL mapping
urlpatterns += [
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

