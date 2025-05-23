import asyncio
import json
import os
import shutil
from pathlib import Path

import gradio as gr
import TTS

from services.config import get_config, get_configs, write_to_configs
from services.job import Job, write_job_to_file
from services.rvc_service import generate_rvc_sample
from services.tts_service import (
    convert_to_wav,
    generate_coqui_sample,
    generate_edge_sample,
)
from services.utils import list_coqui_samples

INPUTS_FOLDER = Path("input")
JOBS_FOLDER = Path("jobs")
RVC_MODELS = Path("rvc_models")
COQUI_SAMPLE_FOLDER = Path("coqui_samples")
SAMPLE_AUDIO = Path("sample_audio")
JOBS_FILE = Path("jobs.json")

# Ensure inputs folder exists
os.makedirs(INPUTS_FOLDER, exist_ok=True)
os.makedirs(RVC_MODELS, exist_ok=True)
os.makedirs(SAMPLE_AUDIO, exist_ok=True)


class ConfigInterface:
    def __init__(self):
        self.config_name = ""

        self.edge_rate = 0
        self.edge_pitch = 0
        self.edge_text = ""

        self.rvc_model_name = None
        self.edge_tts_voice = None

        self.coqui_text = ""
        self.coqui_sample = None

        self.active_model = "Edge"

    def get_edge_tts_models(self):
        # Load available TTS models from JSON file
        with open("tts_model_info.json", "r") as f:
            available_tts_models = json.load(f)
            tts_name_list = [model["ShortName"] for model in available_tts_models]
        return tts_name_list

    def get_sample_audio(self):
        print("WE GOT HERE")
        documents = [p.name for p in SAMPLE_AUDIO.iterdir() if p.is_file()]
        return documents

    def get_rvc_models(self):
        available_rvc_models = [p.name for p in RVC_MODELS.iterdir() if p.is_dir()]
        return available_rvc_models

    def update_rvc_model(self, model):
        self.rvc_model_name = model
        print("RVC model updated!!!")

    def update_edge_tts_voice(self, shortname):
        self.edge_tts_voice = shortname
        print("EDGE tts model updated!!!")

    def update_edge_pitch(self, pitch):
        self.edge_pitch = pitch
        print("Pitch updated!!!")

    def update_edge_rate(self, rate):
        self.edge_rate = rate
        print("Rate updated!!!")

    def update_coqui_sample(self, sample):
        self.coqui_sample = sample
        return Path("coqui_samples") / sample

    def update_edge_text(self, text: str):
        self.edge_text = text

    def update_config_name_text(self, text: str):
        self.config_name = text

    def update_coqui_text(self, text: str):
        self.coqui_text = text

    def edge_sample_audio(self) -> str:
        if len(self.edge_text) > 0 and self.edge_tts_voice is not None:
            out_file = asyncio.run(
                generate_edge_sample(
                    self.edge_text,
                    voice=self.edge_tts_voice,
                    rate=self.edge_rate,
                    pitch=self.edge_pitch,
                )
            )
        elif self.edge_tts_voice is None:
            gr.Warning("Please select a voice")
            raise Exception("Please select a voice")
        elif len(self.edge_text) == 0:
            gr.Warning("Please input text")
            raise Exception("Please input text")
        return out_file

    def coqui_sample_audio(self) -> str:
        if len(self.coqui_text) > 0 and self.coqui_sample is not None:
            out_file = generate_coqui_sample(
                self.coqui_text,
                self.coqui_sample,
            )
        elif self.coqui_sample is None:
            gr.Warning("Please select an audio sample")
            raise Exception("Please select a voice")
        elif len(self.coqui_text) == 0:
            gr.Warning("Please input text")
            raise Exception("Please input text")
        return out_file

    def rvc_sample_audio(self) -> str:
        tts_model = self.active_model.lower()

        if not Path(SAMPLE_AUDIO / f"{tts_model}_sample.wav").exists():
            raise Exception("You must generate an coqui sample file")
        return generate_rvc_sample(self.rvc_model_name, tts_model)

    def save_uploaded_sample(self, filepath: str):
        if not filepath:
            return list_coqui_samples()

        filepath = Path(filepath)
        if filepath.suffix == ".mp3":
            print("We got here")
            filepath = convert_to_wav(filepath)
            print(filepath)
        dest_path = COQUI_SAMPLE_FOLDER / filepath.name
        shutil.copy(filepath, dest_path)

        if dest_path.exists():
            gr.Info("File uploaded!")
        else:
            gr.Warning("File could not be uploaded")
        return gr.update(choices=list_coqui_samples(), value=filepath.name)

    def on_tab_switch(self, tab):
        print(tab)
        return tab

    def update_selected_model(self, model: str):
        self.active_model = model
        print(f"Switched to: {model}")

    def save_rvc_model(self, name: str, pth_file, index_file):
        name = name.replace(" ", "_")
        if not name or not pth_file or not index_file:
            return self.get_rvc_models()
        model_dir = RVC_MODELS / name
        model_dir.mkdir(exist_ok=True)

        index_path = Path(model_dir / f"{name}.index")
        pth_path = Path(model_dir / f"{name}.pth")

        shutil.move(pth_file.name, pth_path)
        shutil.move(index_file.name, index_path)
        if index_path.exists() and pth_path.exists():
            gr.Info("Model added!")
        else:
            gr.Warning("Model could not be added")
        return gr.update(choices=self.get_rvc_models(), value=name)

    def on_tab_change(self, selected_tab):

        edge_visible = selected_tab == "Edge"
        coqui_visible = selected_tab == "Coqui"
        self.active_model = selected_tab
        print(self.active_model)
        return (
            gr.update(visible=edge_visible),
            gr.update(visible=coqui_visible),
        )

    def save_config(self, name):
        if self.active_model == "Edge":
            if self.edge_tts_voice is None:
                gr.Warning("Please select a tts voice")
                raise Exception("Please select a voice")
            if self.rvc_model_name is None:
                gr.Warning("Please select an rvc model")
                raise Exception("Please select an rvc model")
            data = {
                "tts_model": "edge",
                "tts_voice": self.edge_tts_voice,
                "tts_pitch": self.edge_pitch,
                "tts_rate": self.edge_rate,
                "rvc_model": self.rvc_model_name,
            }
        if self.active_model == "Coqui":
            if self.coqui_sample is None:
                gr.Warning("Please select an audio sample")
                raise Exception("Please select an audio sample")
            if self.rvc_model_name is None:
                gr.Warning("Please select an rvc model")
                raise Exception("Please select an rvc model")
            data = {
                "tts_model": "coqui",
                "tts_sample": self.coqui_sample,
                "rvc_model": self.rvc_model_name,
            }
        gr.Info("Config added")
        write_to_configs(name, config_data=data)


class CreateJobInterface:
    def __init__(self):
        self.new_job_name = ""

        self.config_name = None
        self.document = None
        self.input_text = None
        self.batch_size = 5

    def get_documents(self):
        print("WE GOT HERE")
        documents = [p.name for p in INPUTS_FOLDER.iterdir() if p.is_file()]
        return documents

    def update_config(self, name):
        self.config_name = name
        self.config = get_config(name)
        print("Updating config!!!")

    def update_document(self, document):
        self.document = document
        print("Updating config!!!")

    def update_batch_size(self, size: int):
        self.batch_size = size
        print("Updating batch size")

    def update_new_job_name(self, name):
        self.new_job_name = name
        print("Updating new job name")

    def get_all_jobs(self) -> dict:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
        return jobs

    def get_final_audio_path(job_name: str):
        output_path = Path("jobs") / job_name / "book.wav"  # or .mp3
        if output_path.exists():
            return str(output_path)
        return None

    def upload_file(self, file) -> list[str]:
        if file is None:
            return "No file provided."

        file_path = Path(file.name)
        ext = file_path.suffix.lower()

        if ext not in [".txt", ".pdf"]:
            gr.Warning("Unsupported file type. Please upload a .txt or .pdf.")
            return "Unsupported file type. Please upload a .txt or .pdf."

        destination = INPUTS_FOLDER / file_path.name
        shutil.move(file.name, destination)

        if destination.exists():
            gr.Info("File uploaded")
        else:
            gr.Warning("File could not be uploaded")
        return self.get_documents()

    def write_job(self) -> list[str]:
        if len(self.new_job_name) == 0:
            gr.Warning("Please enter a name for the job")
            raise Exception("Please enter a name for the job")
        if self.config_name is None:
            gr.Warning("Please select a config")
            raise Exception("Please select a config")
        if self.document is None:
            gr.Warning("Please select a document")
            raise Exception("Please select a document")

        input_path = self.document
        write_job_to_file(
            self.new_job_name, self.config_name, input_path, self.batch_size
        )
        gr.Info("Job created!")
        return gr.update(
            choices=list(
                self.get_all_jobs().keys()
            ),  # make sure this returns updated job list
            value=self.new_job_name,  # auto-select the newly created job
        )


class RunJobInterface:
    def __init__(self):
        self.selected_job = None
        self.selected_job_object = None
        self.job_obj = None
        self.running = False

        self.config_name = None
        self.config = None
        print("running1", self.running)

    def update_selected_job(self, job_name):
        print("running2.5", self.running)
        self.selected_job = job_name
        self.selected_job_object = self.get_all_jobs()[job_name]
        self.config_name = self.selected_job_object["config"]
        self.config = get_config(self.config_name)
        print(self.config)
        print(self.selected_job_object)
        print("running2", self.running)

        print("Updated!!!!")

    def get_percent_completed(self):
        print(self.selected_job_object["completed_batches"])
        print(self.selected_job_object["total_batches"])
        percentage = round(
            (
                self.selected_job_object["completed_batches"]
                / self.selected_job_object["total_batches"]
            )
            * 100
        )
        print(percentage)
        return percentage

    def start_job(self, job_name: str):
        print("running3", self.running)
        if self.selected_job is None:
            gr.Info("Please select a job from the dropdown ")
        if not self.running:
            self.selected_job = job_name
            self.running = True
            self.job_obj = Job(job_name)
            self.job_obj.run_job()
        else:
            gr.Warning("Already a job in progress")
            print(self.selected_job)

    def stop_job(self, job_name: str):
        print("running2", self.running)
        if self.selected_job == job_name:
            if self.job_obj:
                self.job_obj.stop_process = True
                self.job_obj = None
            self.running = False
        elif self.running == False:
            gr.Info("No jobs running")
            print("No jobs running")
        elif self.selected_job != job_name:
            gr.Info("This job is not running")
            print("This job is not running")
        return str(JOBS_FOLDER / job_name / "audio.mp3")

    def get_all_jobs(self) -> dict:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
        return jobs


class ViewJobInterface:
    def __init__(self):
        self.job = None

    # def load_reader_content(self, job_name) -> tuple[Path, Path]:
    #     self.job = job_name
    #     if self.job is None:
    #         raise Exception("Please select a job")
    #     jobs = self.get_all_jobs()
    #     job = jobs[self.job]
    #     input_text = str(INPUTS_FOLDER / job["input_file"])
    #     audio_output = str(JOBS_FOLDER / self.job / "audio.mp3")
    #     return audio_output, input_text

    def get_all_jobs(self) -> dict:
        with open("jobs.json", "r") as f:
            jobs = json.load(f)
        return jobs

    def get_job_audio_path(self, job_name) -> str:
        audio_output = JOBS_FOLDER / job_name / "audio.mp3"
        return audio_output

    def get_job_text_path(self, job_name) -> str:
        jobs = self.get_all_jobs()
        job = jobs[job_name]
        input_text = INPUTS_FOLDER / job["input_file"]
        return input_text
