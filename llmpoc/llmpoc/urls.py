"""
URL configuration for llmpoc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from poc import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('upload/', views.FileUploadView.as_view(), name='upload_file'),
    path("upload/success/", views.UploadSuccessView.as_view(), name="upload_success"),
    path("runllm", views.ListMediaFilesView.as_view(), name="list_media_files"),
]

