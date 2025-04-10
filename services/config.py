import json
import os
from pathlib import Path

from services.utils import (
    list_coqui_samples,
    list_rvc_models,
    prompt_until_valid,
    prompt_with_choices,
)

COQUI_SAMPLES = "coqui_samples"

CONFIGS_FILE = "configs.json"
EDGE_MODELS = "edge_model_info.json"


def config_does_not_exist(name: str) -> bool:
    with open(CONFIGS_FILE, "r", encoding="utf-8") as f:
        configs = json.loads(f.read().strip())
    return not name in configs


def run_interactive_config_builder():
    config = {}
    print("Creating a new Vocalbook config...")
    name = prompt_until_valid(
        "Config name -> ", config_does_not_exist, "Config already exists"
    )
    tts_model = prompt_with_choices("Select a tts model -> ", ["edge", "coqui"])

    config["tts_model"] = tts_model

    if tts_model == "edge":
        tts_voice = prompt_until_valid(
            "Select edge tts voice -> ", shortname_exists, "Model does not exist"
        )
        config["tts_voice"] = tts_voice
    elif tts_model == "coqui":
        sample = prompt_with_choices("Select an audio sample -> ", list_coqui_samples())
        config["tts_sample"] = sample

    rvc_model = prompt_with_choices("Select an rvc model -> ", list_rvc_models())
    config["rvc_model"] = rvc_model

    write_to_configs(name, config)


def write_to_configs(config_name: str, config_data: dict):

    with open(CONFIGS_FILE, "r", encoding="utf-8") as f:
        configs = json.load(f)
    updated = False
    if config_name in configs:
        updated = True

    configs[config_name] = config_data

    with open(CONFIGS_FILE, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=4)

    if updated:
        print(f"Updated config '{config_name}' in configs.json")
    else:
        print(f"Added new config '{config_name}' to configs.json")


def shortname_exists(shortname, model_info_path="edge_model_info.json"):
    with open(model_info_path, "r", encoding="utf-8") as f:
        models = json.load(f)

    return any(
        model.get("ShortName", "").lower() == shortname.lower() for model in models
    )


def load_config(config_name: str) -> dict:
    # Sanitize and build path
    filename = config_name.strip().lower().replace(" ", "_") + ".json"
    path = os.path.join("configs", filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config '{config_name}' not found")
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


def delete_config(name: str):
    with open(CONFIGS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            raise ValueError("configs.json is empty.")
        configs = json.loads(content)

    new_configs = [cfg for cfg in configs if cfg.get("name") != name]

    if len(new_configs) == len(configs):
        print(f"{name} not found in configs")

    with open(CONFIGS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_configs, f, indent=4)
    print(f"Deleted config '{name}' from configs.json")


def get_configs() -> dict:
    with open(CONFIGS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []

        configs = json.loads(content)
    return configs


def get_config(name: str):
    configs = get_configs()
    if name in configs:
        return configs[name]
    return None


def list_edge_model_shortnames():
    pass
