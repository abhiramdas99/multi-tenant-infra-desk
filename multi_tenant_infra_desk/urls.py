"""
URL configuration for multi_tenant_infra_desk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.views.generic import TemplateView
from core import views as core_views
from django.urls import path

urlpatterns = [
    # Home → shows your custom home.html
    path(
        "",
        TemplateView.as_view(template_name="home.html"),
        name="home",
    ),

    # Global Search (must be before admin/)
    path(
        "admin/global-search/",
        core_views.global_search,
        name="global_search"
    ),

    # Admin panel
    path("admin/", admin.site.urls),
    
        # 🔹 Export Infra Data
    path(
        "export-infra-data/",
        core_views.export_infra_data,   # <-- call from core_views
        name="export_infra_data",
    ),
]