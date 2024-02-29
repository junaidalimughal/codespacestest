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
import re

from .apps import tokenizer, model

print("Printing tokenizers and models from views file")
print(tokenizer)
print(model)

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

        if str(last_file.file).split(".")[-1] == "csv":
            df = pd.read_csv(f"media/{last_file.file}")
            print("File Loaded csv")
        else:
            df = pd.read_excel(f"media/{last_file.file}")
            print("File Loaded excel")
        
        column_names = ','.join(['`' + col + '`' for col in list(df.columns)])
        variable_name = f'{df=}'.split('=')[0]
        
        prompt = f"Write pandas script to calculate {prompt}. Columns are  {column_names}. Make sure to put \\begin at start of code and \\end at the end of code? And data is already loaded in {variable_name}"

        input_tokens = tokenizer(prompt, return_tensors="pt")

        input_ids = input_tokens["input_ids"]
        attention_mask = input_tokens["attention_mask"]

        input_tokens = input_tokens.to(0)
        response = model.generate(**input_tokens, max_length=400, temperature=1.0)
        decoded = tokenizer.decode(response[0])

        prompt_length = len(prompt) + 4
        decoded = decoded[prompt_length: ]

        print(decoded)
        start_pattern = r'\\begin{python}'
        end_pattern = r'\\end{python}'
        
        try:
            try:
                start_index = re.search(start_pattern, decoded)
                end_index = re.search(end_pattern, decoded)
            except:
                start_index = re.search(start_pattern, decoded)
                end_index = re.search(end_pattern, decoded)

                start_index = re.search(start_pattern, decoded)
                end_index = re.search(end_pattern, decoded)

            start_index = start_index.span()[-1]
            end_index = end_index.span()[0]

            generated_query = decoded[start_index:end_index]

            local_namespace = {"df":df}
            
            print("Query Generated is -=>")
            print(generated_query)

            execution_status = "Success"
            exception_message = ""

            exec(generated_query, globals(), local_namespace)
        except Exception as ex:
            exception_message = str(ex)
            execution_status = "Failed"

        local_df = local_namespace["df"].copy()
        other_name_space_elements = [(key, value) for key, value in local_namespace.items() if key != "df"]

        new_file_name = f"generated_{fileName}"
        
        document = GeneratedFile()
        print("Attempting to create the file for df")
        document.file.save(new_file_name, ContentFile(local_df.to_csv(index=False)))
        print("File saved.")
        file_url = request.build_absolute_uri(document.file.url)
        
        document.save()
        
        response_dict = {}

        response_dict["df"] = {"data": local_df.to_json(orient="split"), "datatype":"dataframe", "url":file_url}
        response_dict["generated_query"] = {"data": generated_query, "datatype": "variable", "url": "No URL"}
        response_dict["execution_status"] = {"data": execution_status, "datatype":"variable", "url": "No URL"}

        for key, value in other_name_space_elements:
            if isinstance(value, pd.DataFrame):
                document = GeneratedFile()
                print(f"Attempting to create the file {key}")
                document.file.save(new_file_name, ContentFile(value.to_csv(index=False)))
                file_url = request.build_absolute_uri(document.file.url)
                print("File saved.")
                response_dict[key] = {"data": value.to_json(orient="split"), "datatype": "dataframe", "url": file_url}
            else:
                response_dict[key] = {"data": value, "datatype":"variable", "url": "No URL"}
        
        print("Resposne is -> \n")
        print(response_dict)
        return Response(data=response_dict)

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
    
