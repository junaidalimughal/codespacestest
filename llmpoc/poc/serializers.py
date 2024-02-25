from rest_framework import serializers

from .models import UploadedFile
class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ["file", "uploaded_at"]

    def validate_file(self, value):
        # Assuming `name` is a property/method on your model that extracts the file name
        file_name = value.name  # Or however you determine the file's name
        print("file name from serializer is -=> ", file_name)
        if UploadedFile.objects.filter(file__endswith=file_name).exists():
            # You can customize this message as needed
            raise serializers.ValidationError("A file with this name already exists.")
        
        return value

