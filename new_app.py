import gradio as gr
import json
import os
import asyncio
import shutil
from services.tts_service import sample_text_audio_generate
from services.rvc_service import run_sample_infer_script_default
from main import run_all

SAMPLE_WAV_STORE = "segment_store/sample_wav_store"
INPUTS_FOLDER = "input"

# Ensure inputs folder exists
os.makedirs(INPUTS_FOLDER, exist_ok=True)
os.makedirs(SAMPLE_WAV_STORE, exist_ok=True)



class UserInterface:
    def __init__(self):
        self.rvc_model = None
        self.tts_model = None
        self.tts_pitch = 0
        self.selected_document = None


    def get_edge_tts_models(self):
        # Load available TTS models from JSON file
        with open("tts_model_info.json", "r") as f:
            available_tts_models = json.load(f)
            tts_name_list = [model["ShortName"] for model in available_tts_models]
        return tts_name_list
    
    def get_rvc_models(self):
        available_rvc_models = [
            name for name in os.listdir("models")
            if os.path.isdir(os.path.join("models", name))
        ]
        return available_rvc_models

    def get_documents(self):
        documents = [
            name for name in os.listdir("input")
            if os.path.isfile(os.path.join("input", name))
        ]
        return documents
    
    def update_rvc_model(self):
        pass

    def update_tts_model(self):
        pass

    def update_tts_pitch(self):
        pass

    def update_document(self):
        pass