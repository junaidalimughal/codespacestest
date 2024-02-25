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
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from poc import views

urlpatterns = [
    path("api/upload/", views.FileUploadAPIView.as_view(), name="upload-file-api"),
    path("api/processllm/", views.ProcessLLMAPI.as_view(), name="process-mixtral-api"),
    path("processllm/", views.RunLLMView.as_view(), name="precessllm"),
    path("admin/", admin.site.urls),
    path('upload/', views.FileUploadView.as_view(), name='upload_file'),
    path("upload/success/", views.UploadSuccessView.as_view(), name="upload_success"),
    path("runllm", views.ListMediaFilesView.as_view(), name="list_media_files"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

