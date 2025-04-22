import json
import multiprocessing
import os
import shutil
from pathlib import Path

from services.audio_stitcher import stitch
from services.config import get_config, get_configs
from services.rvc_service import rvc_audio_generate
from services.text_processing import count_text_chunks, read_and_chunk_text
from services.tts_service import text_audio_generate
from services.utils import (
    list_input_files,
    prompt_until_valid,
    prompt_with_choices,
    wipe_folder,
)

JOBS_FILE = Path("jobs.json")
JOBS_FOLDER = Path("jobs")
INPUT_FOLDER = Path("input")


class Job:
    def __init__(self, name: str):
        self.name = name
        data = self.get_job()

        self.stop_process = False

        self.job_dir = JOBS_FOLDER / name
        self.processing_folder = self.job_dir / "processing"
        self.post_processing_folder = self.job_dir / "post_processing"

        self.input_path = INPUT_FOLDER / data["input_file"]
        self.batch_size = data["batch_size"]
        self.total_chunks = data["total_batches"]
        self.completed_batches = data["completed_batches"]

        self.config_name = data["config"]
        self.config = get_config(self.config_name)
        self.tts_model = self.config["tts_model"]

    def __exit__(self):
        # Handler if the process quits unexpectedly
        print("exiting job")
        self.update_job_progress(self.name, self.completed_batches)

    def delete_job(self):
        if job_does_not_exist(self.name):
            print("That job doesn't exist")
            return None
        job_folder = JOBS_FOLDER / self.name
        if job_folder.exists():
            shutil.rmtree(job_folder)
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("jobs.json is empty.")

            jobs = json.loads(content)
        if self.name not in jobs:
            raise KeyError(f"Job '{self.name}' not found in jobs.json.")
        del jobs[self.name]
        with open(JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=4)
        print(f"Deleted job '{self.name}' from jobs.json")

    def get_job(self) -> dict:
        if not JOBS_FILE.exists():
            return None

        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            jobs = json.load(f)
        return jobs[self.name]

    def update_job_progress(self):
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                jobs = json.loads(content)

        job = jobs[self.name]
        previous = job.get("completed_batches", 0)

        if self.completed_batches > previous:
            job["completed_batches"] = self.completed_batches

        with open(JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=4)

        print(
            f"Job '{self.name}' updated: completed_batches =  {self.completed_batches}"
        )

    def get_job_progress(self):
        percent = self.completed_batches / self.total_chunks
        return round(percent * 100)

    # Starts/resumes the job
    def run_job(self):
        try:
            full_text = read_and_chunk_text(self.input_path, self.batch_size)
            for index, batch in full_text.items():
                if index < self.completed_batches:
                    continue
                self.check_stop()
                text_audio_generate(
                    self.config,
                    self.processing_folder,
                    index,
                    batch,
                    self.post_processing_folder,
                )
                self.check_stop()
                rvc_audio_generate(
                    config=self.config,
                    input_folder=self.processing_folder,
                    output_folder=self.post_processing_folder,
                )
                self.check_stop()
                # stitch chunks to output
                stitch(self.job_dir, index)
                self.completed_batches += 1
                self.update_job_progress()
        finally:
            wipe_folder(self.processing_folder)
            wipe_folder(self.post_processing_folder)

    def check_stop(self):
        if self.stop_process:
            raise Exception("Stopping")


# Makes a new job and initializes metadata
def write_job_to_file(
    job_name: str, config_name: str, input_file: Path, batch_size: int
):
    file_path = INPUT_FOLDER / input_file

    job_name = job_name.strip().replace(" ", "_").lower()

    total_chunks = count_text_chunks(file_path, batch_size=batch_size)
    completed_batches = 0
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content:
            jobs = json.loads(content)
    job = {
        "input_file": input_file,
        "total_batches": total_chunks,
        "completed_batches": completed_batches,
        "batch_size": batch_size,
        "config": config_name,
    }
    jobs[job_name] = job
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4)
    print("Saved job")
    # Make the job folder
    os.makedirs(JOBS_FOLDER / job_name, exist_ok=True)
    # Make the processing folder for our job
    os.makedirs(JOBS_FOLDER / job_name / "processing", exist_ok=True)
    # Make the chunk storage folder
    os.makedirs(JOBS_FOLDER / job_name / "post_processing", exist_ok=True)


def job_does_not_exist(name: str) -> bool:
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        configs = json.loads(f.read().strip())
    return not name in configs


def run_interactive_job_builder():
    # Ask for a name
    print("Creating a new Vocalbook job...")
    name = prompt_until_valid("Job name -> ", job_does_not_exist, "Job already exists")
    # Ask for an input file
    book = prompt_with_choices("Select a book -> ", list_input_files())

    # Ask for a config
    config = prompt_with_choices("Select a configuration -> ", get_configs())

    batch_size = int(
        prompt_until_valid(
            "Batch size [1 - 100] -> ",
            between,
            "Please pick a number between 1 and 100",
        )
    )

    write_job_to_file(name, config, book, batch_size)


def between(number: str, low: int = 1, high: int = 100) -> bool:
    try:
        value = int(number)
        return low <= value <= high
    except (ValueError, TypeError):
        return False
