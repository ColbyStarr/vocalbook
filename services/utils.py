import json
import os
import re
import shutil
import zipfile
from io import BytesIO
from pathlib import Path

import requests

INPUT_FOLDER = Path("input")
MODEL_FOLDER = Path("rvc_models")
SAMPLE_FOLDER = Path("coqui_samples")


def unpack_model_from_link(
    url: str, model_name: str, output_folder: str = "voice_models"
):
    """
    Downloads a ZIP file from the given URL and extracts its contents into the specified folder.
    The extracted .pth and .index files are renamed to match the given model_name.
    """
    model_path = os.path.join(output_folder, model_name)
    os.makedirs(model_path, exist_ok=True)

    print(f"Downloading model from {url}...")
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            extract_path = os.path.join(output_folder, f"{model_name}_temp")
            os.makedirs(extract_path, exist_ok=True)
            zip_ref.extractall(extract_path)

        # Search for .pth and .index files inside extracted contents
        for root, _, files in os.walk(extract_path):
            for file in files:
                if file.endswith(".pth"):
                    os.rename(
                        os.path.join(root, file),
                        os.path.join(model_path, f"{model_name}.pth"),
                    )
                elif file.endswith(".index"):
                    os.rename(
                        os.path.join(root, file),
                        os.path.join(model_path, f"{model_name}.index"),
                    )

        # Clean up temp extraction folder
        shutil.rmtree(extract_path, ignore_errors=True)

        print(f"Model extracted successfully to '{model_path}'")
    else:
        print(f"Failed to download model. HTTP Status: {response.status_code}")


def get_model_file_paths(model_name: str) -> tuple[str, str]:
    folder_path = MODEL_FOLDER / model_name
    pth_path = None
    index_path = None

    for file in folder_path.iterdir():
        if file.suffix == ".pth":
            pth_path = file
        elif file.suffix == ".index":
            index_path = file

    if not pth_path or not index_path:
        raise FileNotFoundError(f"Missing .pth or .index file in {folder_path}")

    return str(pth_path), str(index_path)


def list_rvc_models():
    model_names = []
    for folder in MODEL_FOLDER.iterdir():
        if folder.is_dir():
            model_names.append(folder.name)
    return model_names


def prompt_with_choices(prompt: str, choices: list[str]):
    """
    Prompts the user to select from a list of choices.
    If more than 3 choices, prints each one on its own line.
    """
    choices = [str(choice) for choice in choices]  # Ensure all strings

    while True:
        print(prompt)

        if len(choices) > 3:
            for c in choices:
                print(f" - {c}")
        else:
            print(f" ({'  /  '.join(choices)})")

        user_input = input("> ").strip()

        if user_input.lower() in [c.lower() for c in choices]:
            return user_input
        else:
            print("Invalid option.")


def prompt_until_valid(prompt, validator, error_message="Invalid input."):
    while True:
        user_input = input(prompt).strip()
        result = validator(user_input)
        if result:
            return user_input
        else:
            print(f"{error_message}")


def list_input_files():
    files = [f.name for f in INPUT_FOLDER.iterdir() if f.is_file()]
    return files


def list_coqui_samples():
    files = [f.name for f in SAMPLE_FOLDER.iterdir() if f.is_file()]
    return files


def natural_sort_key(path):
    """
    Extracts numeric parts from a filename for natural sorting.
    Example: '2_10.wav' ➜ [2, 10]
    """
    parts = re.findall(r"\d+", path.stem)
    return [int(p) for p in parts]


def list_edge_model_shortnames():
    # Load available TTS models from JSON file
    with open("edge_model_info.json", "r") as f:
        available_tts_models = json.load(f)
        tts_name_list = [model["ShortName"] for model in available_tts_models]
    return tts_name_list


def wipe_folder(folder_path):
    if folder_path is None:
        return
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Deletes file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Deletes folder and its contents
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
