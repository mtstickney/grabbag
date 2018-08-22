"""grabbag URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path, include
from django.views.decorators.http import require_safe, require_http_methods, require_POST
from link_save import views

v1_api_app = views.make_default_app()

urlpatterns = [
    path('api/v1/', include([
        path('tokens/', require_safe(v1_api_app.get_tokens)),
        path('tokens/new/', require_POST(v1_api_app.create_admin_token)),
        path('users/', require_safe(v1_api_app.get_users)),
        path('users/<int:id>/', require_safe(v1_api_app.get_users)),
        path('users/new/', require_POST(v1_api_app.create_user))
    ]))
]
