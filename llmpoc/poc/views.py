from django.shortcuts import render

# Create your views here.
# views.py


from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views import View
from .forms import UploadFileForm
from django.conf import settings
import os
from llmpoc.settings import MEDIA_URL
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import pandas as pd

from .apps import latest_file
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import serializers
from rest_framework.views import APIView
from .serializers import UploadedFileSerializer
from .models import GeneratedFile, UploadedFile
from django.core.files.base import ContentFile

from django.http import HttpResponseRedirect
import os

class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        file_serializer = UploadedFileSerializer(data=request.data)
        
        if file_serializer.is_valid():
            file_serializer.save()
            print("file name is -> ", file_serializer.data)
            latest_file = file_serializer.data
            
            return Response({"data": file_serializer.data, "message": "File Uploaded successfully."}, status=201)
        else:
            return Response({"message": "File Uploaded Failed."}, status=500)

class TestAPIView(APIView):
    parser_classes = (JSONParser)

    def post(self, request, *args, **kwargs):
        prompt_value = request.POST.get("prompt")
        print(f"Prompt value is -> {prompt_value}")

        return Response("Prompt reached on the system.")

class ProcessLLMAPI(APIView):

    def post(self, request, *args, **kawrgs):
        print(request)
        print(request.POST.__dict__)
        
        prompt = request.data.get("message")
        fileName = request.data.get("fileName")
        print("File path is -=>", latest_file)

        last_file = UploadedFile.objects.all().last()
        print(last_file.file)
        print(last_file.file.name)

        df = pd.read_csv(f"media/{last_file.file}")
        
        local_namespace = {"df":df}
        response = """
import pandas as pd
import numpy as np

df = pd.read_csv("media/data_df.csv")
print(df.columns)
print(df)
"""
        exec(response, globals(), local_namespace)
        local_df = local_namespace["df"]
        new_file_name = f"generated_{fileName}"

        #local_df.to_csv(f"media/temp_files/{new_file_name}.csv", index=False)
        
        document = GeneratedFile()
        print("Attempting to create the file.")
        document.file.save(new_file_name, ContentFile(local_df.to_csv(index=False)))
        print("File saved.")
        
        document.save()
        print("Document saved.")

        file_url = request.build_absolute_uri(document.file.url)
        return Response(data={"message": f"{file_url}"})
        
class FileUploadView(FormView):
    template_name = 'poc/upload.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('upload_success')  # Adjust as necessary

    def form_valid(self, form):
        self.handle_uploaded_file(self.request.FILES['file'])
        return super().form_valid(form)

    def handle_uploaded_file(self, f):
        os.makedirs(os.path.dirname(settings.MEDIA_ROOT), exist_ok=True)

        with open(os.path.join(settings.MEDIA_ROOT, f.name), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

class UploadSuccessView(TemplateView):
    template_name = "poc/upload_success.html"

class RunLLMView(View):
    template_name = "poc/post_prompt.html"

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        selected_files = request.POST.getlist("files")
        
        prompt = request.POST.get("prompt")
        
        response = """
import pandas as pd
import numpy as np

df = pd.read_csv("media/data_df.csv")
print("dataframe printed from actual script is", df)"""
        print(f"selected File is ->  {selected_files}")
        print(f"And prompt is -> {prompt}")

        
        if os.path.exists("execute_script.py"):
            os.remove("execute_script.py")
        with open("execute_script.py", "w") as script_file_pointer:
            response_lines = response.split("\n")
            for line in response_lines:
                script_file_pointer.write(line)
                script_file_pointer.write("\n")
        
        with open("execute_script.py") as script_file:
            exec(script_file.read())

        return HttpResponseRedirect(reverse("upload_file"))

class ListMediaFilesView(TemplateView):
    template_name = "poc/post_prompt.html"

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        media_dir = settings.MEDIA_ROOT
        
        files_names = [os.path.join(dp, f) for dp, dn, filenames in os.walk(media_dir) for f in filenames if ".ipynb" not in f]
        
        dfs_html = {}
        for file_name in files_names:
            if file_name.split(".")[-1] == "csv":
                df = pd.read_csv(file_name) 
            else:
                df = pd.read_excel(file_name)

            file_name = file_name.split("/")[-1]
            dfs_html[f"{file_name}"] = df.head().to_html(classes="table table-striped", index=False)
            print(df.head().to_html(classes="table table-striped", index=False))

        context["dfs_html"] = dfs_html
        return context
    