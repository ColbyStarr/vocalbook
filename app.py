import gradio as gr
import json
import os
import asyncio
import shutil
from services.tts_service import sample_text_audio_generate
from services.rvc_service import run_sample_infer_script_default
from main import run_all


session_storage = {"rvc_model": None, "tts_model": None, "tts_pitch":0, "selected_book":None}


SAMPLE_WAV_STORE = "segment_store/sample_wav_store"
INPUTS_FOLDER = "input"

# Load available TTS models from JSON file
with open("tts_model_info.json", "r") as f:
    available_tts_models = json.load(f)
    tts_name_list = [model["ShortName"] for model in available_tts_models]

available_rvc_models = [
    name for name in os.listdir("models")
    if os.path.isdir(os.path.join("models", name))
]

books = [
    name for name in os.listdir("input")
    if os.path.isfile(os.path.join("input", name))
]


def update_rvc(model):
    session_storage["rvc_model"] = model
    print(session_storage)

def update_tts(model):
    session_storage["tts_model"] = model
    print(session_storage)

def update_pitch(pitch):
    session_storage["tts_pitch"] = pitch
    print(session_storage)

def update_book(book):
    session_storage["selected_book"] = book
    print(session_storage)


def app_run():
    tts_model = session_storage["tts_model"]
    rvc_model = session_storage["rvc_model"]
    book = f"input/{session_storage['selected_book']}"
    run_all(tts_model, rvc_model, book)
    return "output/book.wav"

# Ensure inputs folder exists
os.makedirs(INPUTS_FOLDER, exist_ok=True)

def save_uploaded_file(file):
    print("We got here")
    if file is None:
        return "No file uploaded!"
    
    destination = os.path.join(INPUTS_FOLDER, os.path.basename(file.name))
    shutil.copy(file.name, destination)

    print(f"Uploaded file saved to: {destination}")
    return f"File saved to inputs folder: {destination}"



def generate_tts_sample():
    if not session_storage["tts_model"]:
        return None, "No TTS model selected!"
    
    sample_path = os.path.join(SAMPLE_WAV_STORE, f"tts_{session_storage['tts_model']}_sample.wav")
    print(f"Generating TTS sample at: {sample_path}")

    asyncio.run(sample_text_audio_generate(session_storage["tts_model"]))

    return sample_path

# Same idea for RVC samples
def generate_rvc_sample():
    if not session_storage["rvc_model"]:
        return None, "No RVC model selected!"
    tts_sample_path = os.path.join(SAMPLE_WAV_STORE, f"tts_{session_storage['tts_model']}_sample.wav")
    sample_path = os.path.join(SAMPLE_WAV_STORE, f"{session_storage['rvc_model']}_sample.wav")
    print(f"Generating RVC sample at: {sample_path}")

    asyncio.run(sample_text_audio_generate(session_storage["tts_model"]))
    run_sample_infer_script_default(session_storage["rvc_model"], tts_sample_path)
    return sample_path


# Session storage (you might want to persist this later
with gr.Blocks() as demo:
    gr.Markdown("# Vocalbook")

    with gr.Row():
        with gr.Column(variant='panel' ):
            gr.Markdown("### TTS Models")
            tts_dropdown = gr.Dropdown(label="Select TTS Model", choices=tts_name_list, type="value")
            tts_dropdown.change(
                update_tts,
                inputs=tts_dropdown,
            )
            gr.Markdown("### RVC Models")
            rvc_dropdown = gr.Dropdown(label="Select RVC Model", choices=available_rvc_models, type="value")
            rvc_dropdown.change(
                update_rvc,
                inputs=rvc_dropdown,
            )
            # This audio component will hold the RVC sample and let the user play it
            audio_player = gr.Audio(label="Audio Sample", interactive=False, type="filepath")
            with gr.Row():
                gr.Markdown("### Generate TTS Sample")
                tts_sample_gen = gr.Button()
                tts_sample_gen.click(
                    generate_tts_sample,
                    inputs=None,
                    outputs=[audio_player]
                )

                gr.Markdown("### Generate RVC Sample")
                rvc_sample_gen = gr.Button()
                rvc_sample_gen.click(
                    generate_rvc_sample,
                    inputs=None,
                    outputs=[audio_player]
                )
        with gr.Column(variant='panel'):
            # 1. Drag & Drop Text File
            text_file_upload = gr.File(label="Upload Book (TXT)", file_types=[".txt"])
            text_file_upload.change(
                save_uploaded_file,
                inputs=text_file_upload
            )
            gr.Markdown("### Books")
            text_input = gr.Dropdown(label="Select Book", choices=books, type="value")
            text_input.change(
                update_book,
                inputs=text_input,
            )

            final_audio_player = gr.Audio(label="Generated Audiobook", interactive=False, type="filepath")
            start_job_btn = gr.Button("Start Processing")
            start_job_btn.click(
                app_run,
                inputs=None,
                outputs=[final_audio_player]
            )


            # 4. Status Message
            status_box = gr.Textbox(label="Status", interactive=False)


demo.launch()