from django.contrib import admin

# Register your models here.
from .models import UploadedFile, GeneratedFile

class UploadFileAdmin(admin.ModelAdmin):
    pass

class GeneratedFileAdmin(admin.ModelAdmin):
    pass


admin.site.register(UploadedFile, UploadFileAdmin)
admin.site.register(GeneratedFile, GeneratedFileAdmin)