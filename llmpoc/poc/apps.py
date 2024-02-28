from django.apps import AppConfig
from django.conf import settings
from accelerate import Accelerator
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoModel, AutoConfig

import torch

class PocConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "poc"

if settings.DEBUG:
    model_directory = "/home/ubuntu/mixtral/models--mistralai--Mixtral-8x7B-Instruct-v0.1/snapshots/5c79a376139be989ef1838f360bf4f1f256d7aec/"
else:
    model_directory = "/app/models/snapshots/5c79a376139be989ef1838f360bf4f1f256d7aec/"
    
config = AutoConfig.from_pretrained(model_directory)

model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

print("loading tokenizer")
if settings.LOAD_LLM:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    print("Loading Tokenizer Finished")

    print("Loading LLM to CPU Memory")
    model = AutoModelForCausalLM.from_pretrained(model_directory, config=config, torch_dtype=torch.float16, device_map="auto")
    print("Loading LLM to CPU Memory Finished")
    
    print("Loading LLM to GPU Cluster")
    accelerator = Accelerator()
    model = accelerator.prepare(model)
    print("Model Loaded into the application")
else:
    tokenizer = None
    model = None
latest_file = None
