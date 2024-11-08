"""
URL configuration for dgpf1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
import globus_portal_framework.urls

#from django.views.debug import technical_500_response

urlpatterns = [
    path('<index:index>/about/', views.search_about, name='search-about'),
    path('<index:index>/download/', views.download_as_html, name='download-as-html'),
    path('api/provider/', include('provider.urls')),
    path('admin/', admin.site.urls),
    # Provides the basic search portal
    path('', include('globus_portal_framework.urls')),
    # Provides Login urls for Globus Auth
    path('', include('social_django.urls', namespace='social')),
    path('favicon.ico', views.favicon),
    path('dump.html', views.Debug_Details, name='debug-details'),
]
