import asyncio
import json
import os
import shutil
from pathlib import Path

import gradio as gr
from gradio_pdf import PDF

from backend_interface import (
    ConfigInterface,
    CreateJobInterface,
    RunJobInterface,
    ViewJobInterface,
)
from services.config import get_configs
from services.utils import (
    list_coqui_samples,
    list_edge_model_shortnames,
    list_rvc_models,
)

INPUTS_FOLDER = Path("input")
RVC_MODELS = Path("rvc_models")
COQUI_SAMPLE_FOLDER = Path("coqui_samples")
SAMPLE_AUDIO = Path("sample_audio")


# Ensure inputs folder exists
os.makedirs(INPUTS_FOLDER, exist_ok=True)
os.makedirs(RVC_MODELS, exist_ok=True)
os.makedirs(SAMPLE_AUDIO, exist_ok=True)

with open("README.md") as f:
    readme = f.read()


css_styling = """
.book-button {
    height: 120px; /* or however tall you want */
}
"""


def render_progress_bar(percent: int = 70):
    return f"""
    <div style='width: 100%; background: #e0e0e0; border-radius: 8px; overflow: hidden; height: 20px;'>
        <div style='width: {percent}%; background: #4caf50; color: white; text-align: center;
                    height: 100%; line-height: 20px; font-size: 12px;'>
            {percent}%
        </div>
    </div>
    """


def loading_animation():
    return """
    <div style="width: 100%; padding: 10px 0;">
        <div style="
            width: 100%;
            height: 6px;
            background: linear-gradient(90deg, #4caf50 0%, #a5d6a7 50%, #4caf50 100%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite linear;
            border-radius: 4px;
        "></div>

        <style>
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        </style>
    </div>
    """


con_interface = ConfigInterface()
cjob_interface = CreateJobInterface()
rjob_interface = RunJobInterface()
vjob_interface = ViewJobInterface()

with gr.Blocks(theme=gr.themes.Ocean(), css=css_styling) as demo:
    with gr.Tabs():
        with gr.Tab("Welcome!"):
            with gr.Row():
                gr.Markdown(readme)
        with gr.Tab("Config Builder"):
            with gr.Row():
                with gr.Column():
                    tab_switcher = gr.Radio(
                        choices=["Edge", "Coqui"],
                        label="Select Mode",
                        value="Edge",
                        interactive=True,
                    )
                    edge_tab = gr.Column(visible=True)
                    coqui_tab = gr.Column(visible=False)

                    with edge_tab:
                        tts_dropdown = gr.Dropdown(
                            label="Select Edge TTS voice",
                            choices=list_edge_model_shortnames(),
                            value=None,
                            type="value",
                        )
                        tts_dropdown.change(
                            con_interface.update_edge_tts_voice,
                            inputs=tts_dropdown,
                        )
                        edge_rate = gr.Slider(
                            minimum=-50,
                            maximum=50,
                            step=1,
                            value=0,
                            label="Rate (%)",
                        )
                        edge_rate.change(
                            con_interface.update_edge_rate, inputs=edge_rate
                        )

                        edge_pitch = gr.Slider(
                            minimum=-100,
                            maximum=100,
                            step=1,
                            value=0,
                            label="Pitch (Hz)",
                        )
                        edge_pitch.change(
                            con_interface.update_edge_pitch, inputs=edge_pitch
                        )
                        edge_text_input = gr.Textbox(
                            label="Enter Text (max 100 characters)",
                            max_length=100,
                            lines=2,
                            placeholder="Type here...",
                        )
                        edge_text_input.input(
                            fn=con_interface.update_edge_text,
                            inputs=edge_text_input,
                        )
                        edge_audio_block = gr.Audio(
                            label="Sample",
                            type="filepath",
                            interactive=False,
                        )
                        edge_audio_button = gr.Button("Generate Sample")
                        edge_audio_button.click(
                            fn=con_interface.edge_sample_audio,
                            outputs=edge_audio_block,
                        )

                    with coqui_tab:
                        coqui_input_dropdown = gr.Dropdown(
                            label="Select Coqui Sample",
                            choices=list_coqui_samples(),
                            value=None,
                            type="value",
                        )
                        coqui_input_audio = gr.Audio(
                            label="Upload Custom Sample",
                            type="filepath",
                            sources=["upload", "microphone"],
                        )
                        coqui_input_dropdown.change(
                            con_interface.update_coqui_sample,
                            inputs=coqui_input_dropdown,
                            outputs=coqui_input_audio,
                        )
                        upload_coqui_input = gr.Button("Upload Sample")
                        upload_coqui_input.click(
                            fn=con_interface.save_uploaded_sample,
                            inputs=coqui_input_audio,
                            outputs=coqui_input_dropdown,
                        )
                        coqui_text_input = gr.Textbox(
                            label="Enter Text (max 100 characters)",
                            max_length=100,
                            lines=2,
                            placeholder="Type here...",
                        )
                        coqui_text_input.input(
                            fn=con_interface.update_coqui_text,
                            inputs=coqui_text_input,
                        )
                        coqui_audio_button = gr.Button("Generate Sample")
                        coqui_audio_block = gr.Audio(
                            label="Sample",
                            type="filepath",
                            interactive=False,
                        )
                        coqui_audio_button.click(
                            fn=con_interface.coqui_sample_audio,
                            outputs=coqui_audio_block,
                        )
                    tab_switcher.change(
                        fn=con_interface.on_tab_change,
                        inputs=tab_switcher,
                        outputs=[edge_tab, coqui_tab],
                    )
                with gr.Column():
                    gr.Markdown("### RVC Settings")
                    # Add RVC input fields here
                    with gr.Accordion("Upload a new rvc model", open=False):
                        rvc_name_box = gr.Textbox(label="Model Name (e.g. 'Narrator')")
                        with gr.Row():
                            pth_upload = gr.File(
                                label="Upload .pth File", file_types=[".pth"]
                            )
                            index_upload = gr.File(
                                label="Upload .index File", file_types=[".index"]
                            )
                        upload_rvc_btn = gr.Button("Add RVC Model")

                    rvc_dropdown = gr.Dropdown(
                        label="Select RVC Model",
                        choices=list_rvc_models(),
                        value=None,
                        type="value",
                    )
                    rvc_dropdown.change(
                        con_interface.update_rvc_model,
                        inputs=rvc_dropdown,
                    )
                    rvc_audio_block = gr.Audio(
                        label="Sample",
                        type="filepath",
                        interactive=False,
                    )
                    rvc_audio_button = gr.Button("Generate Sample from RVC")

                    rvc_audio_button.click(
                        fn=con_interface.rvc_sample_audio,
                        outputs=rvc_audio_block,
                    )

                    upload_rvc_btn.click(
                        fn=con_interface.save_rvc_model,
                        inputs=[rvc_name_box, pth_upload, index_upload],
                        outputs=rvc_dropdown,
                    )
                    config_name_input = gr.Textbox(
                        label="Config name",
                        max_length=25,
                        lines=1,
                        placeholder="Type here...",
                    )
                    config_name_input.input(
                        fn=con_interface.update_config_name_text,
                        inputs=config_name_input,
                    )
                    save_config_button = gr.Button("Save current config")
                    save_config_button.click(
                        fn=con_interface.save_config,
                        inputs=config_name_input,
                    )

        with gr.Tab("Jobs"):

            with gr.Row():
                with gr.Column(scale=1):

                    def upload_document(files):
                        print(files)
                        print(type(files))
                        if not files:
                            return gr.update()

                        uploaded_file = Path(files)
                        # Where you want to store documents (adjust if needed)
                        target_dir = Path("input")
                        target_dir.mkdir(exist_ok=True)
                        target_path = target_dir / uploaded_file.name

                        print("TARGET PATH", target_path)

                        shutil.copy(uploaded_file, str(target_path))

                        # Now update the dropdown
                        all_documents = cjob_interface.get_documents()
                        new_doc = uploaded_file.name

                        return gr.update(choices=all_documents, value=new_doc)

                    gr.Markdown("## Add Document")
                    file_upload = gr.File(
                        label="Upload your book", file_types=[".pdf", ".txt"]
                    )
                    gr.Markdown("## Create Job")
                    job_name_box = gr.Textbox(
                        label="Job Name",
                        placeholder="Enter a name for your job...",
                        max_lines=1,
                        lines=1,
                    )
                    job_name_box.change(
                        fn=cjob_interface.update_new_job_name, inputs=job_name_box
                    )
                    configs = gr.Dropdown(
                        label="Select Config",
                        choices=get_configs(),
                        value=None,
                        type="value",
                    )
                    configs.change(fn=cjob_interface.update_config, inputs=configs)

                    documents = gr.Dropdown(
                        label="Select Document",
                        choices=cjob_interface.get_documents(),
                        value=None,
                        type="value",
                    )
                    documents.change(
                        fn=cjob_interface.update_document, inputs=documents
                    )
                    batch_size = gr.Slider(
                        minimum=1,
                        maximum=100,
                        step=1,
                        value=5,
                        label="Batch Size",
                    )
                    batch_size.change(
                        cjob_interface.update_batch_size, inputs=batch_size
                    )
                    file_upload.upload(upload_document, file_upload, outputs=documents)
                    create_job_button = gr.Button("Create Job")

                with gr.Column(scale=5):

                    def show_loading_only():
                        if rjob_interface.selected_job is not None:
                            return gr.update(value=loading_animation(), visible=True)
                        gr.Warning("No job selected")
                        return None

                    def show_progress_bar():
                        percent = rjob_interface.get_percent_completed()
                        return gr.update(
                            value=render_progress_bar(percent), visible=True
                        )

                    def handle_job_selection(job_name):
                        rjob_interface.update_selected_job(
                            job_name
                        )  # update the active job
                        return show_progress_bar()

                    gr.Markdown("# Current Jobs")

                    job_dropdown = gr.Dropdown(
                        label="Select Job",
                        choices=list(rjob_interface.get_all_jobs().keys()),
                        value=None,
                        type="value",
                    )
                    loading_display = gr.HTML(value="", visible=True)
                    job_dropdown.change(
                        fn=handle_job_selection,
                        inputs=job_dropdown,
                        outputs=loading_display,
                    )

                    with gr.Row():

                        # job_dropdown.change(fn=show_progress_bar)

                        start_btn = gr.Button("Start")
                        stop_btn = gr.Button("Stop")

                    create_job_button.click(
                        fn=cjob_interface.write_job, outputs=job_dropdown
                    )
                    audio_box = gr.Audio(
                        label="Audio",
                        interactive=False,
                    )

                    stop_btn.click(
                        fn=rjob_interface.stop_job,
                        inputs=job_dropdown,
                        outputs=audio_box,
                    )  # actual stop logic

                    stop_btn.click(
                        fn=show_progress_bar,
                        outputs=loading_display,
                    )  # stop loader
                    start_btn.click(
                        fn=rjob_interface.start_job, inputs=job_dropdown
                    )  # actual job logic
                    start_btn.click(
                        fn=show_loading_only,
                        outputs=loading_display,
                    )  # loader
                    job_dropdown.change(
                        fn=rjob_interface.stop_job,
                        inputs=job_dropdown,
                        outputs=audio_box,
                    )  # actual stop logic

        with gr.Tab("Reader"):

            def load_reader_content(job_name: str):
                audio_path = vjob_interface.get_job_audio_path(job_name)
                text_path = vjob_interface.get_job_text_path(job_name)

                if text_path.suffix.lower() == ".pdf":
                    return (
                        str(audio_path),
                        gr.update(visible=False),  # hide text
                        gr.update(value=str(text_path), visible=True),  # show PDF
                    )
                else:
                    content = text_path.read_text(encoding="utf-8")
                    return (
                        str(audio_path),
                        gr.update(value=content, visible=True),  # show text
                        gr.update(visible=False),  # hide PDF
                    )

            with gr.Row():
                # LEFT COLUMN — audio & selector
                with gr.Column(scale=1):
                    job_reader_dropdown = gr.Dropdown(
                        label="Select Job",
                        choices=list(rjob_interface.get_all_jobs().keys()),
                        value=None,
                        type="value",
                    )

                    audio_box = gr.Audio(
                        label="Audio",
                        interactive=False,
                    )

                # RIGHT COLUMN — text content
                with gr.Column(scale=5):
                    document_text = gr.Textbox(
                        label="Text Content",
                        lines=30,
                        interactive=False,
                        visible=False,
                        show_copy_button=True,
                    )

                    document_pdf = PDF(label="PDF Viewer", scale=1, visible=False)

                    job_reader_dropdown.change(
                        fn=load_reader_content,
                        inputs=job_reader_dropdown,
                        outputs=[audio_box, document_text, document_pdf],
                    )


demo.launch()
