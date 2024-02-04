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
import pandas as pd
from execute_script import read_file

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
    template_name = "poc/runllm.html"

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        
        prompt = request.POST.get("prompt")

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

            local_df = read_file()
            print(local_df)
            file_name = file_name.split("/")[-1]
            dfs_html[f"{file_name}"] = df.head().to_html(classes="table table-striped", index=False)
            print(df.head().to_html(classes="table table-striped", index=False))

        context["dfs_html"] = dfs_html
        return context
    