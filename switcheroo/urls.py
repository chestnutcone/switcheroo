"""switcheroo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from . import views
from django.conf.urls import url
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
        path('accounts/',include('django.contrib.auth.urls')),
        path('main/', include('project_specific.urls')),
        path('', views.mainView, name='home'),
        path('users/', include('user.urls')),
        path('users/', include('django.contrib.auth.urls')),
        url(r'^login/$', views.loginView, name='login'),
        ]

import project_specific
handler500 = project_specific.views.handler500