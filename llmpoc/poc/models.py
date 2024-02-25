from django.db import models

# Create your models here.
class UploadedFile(models.Model):
    file = models.FileField(upload_to="media/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class GeneratedFile(models.Model):
    file = models.FileField(upload_to="generated/")
    uplaoded_at = models.DateTimeField(auto_now_add=True)
