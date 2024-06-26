"""lunawaelections URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', views.auth, name='auth'),
    path('upload/', views.upload, name='upload'),
    path('get_image/<str:img_name>/', views.get_image, name='get_image'),
    path('counter/<str:android_id>/', views.counter, name='counter'),
    path('delete/<str:android_id>/', views.delete, name='delete'),
    path('stats/', views.stats, name='stats'),
    path('', views.streamlit, name='streamlit'),
]