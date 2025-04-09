import asyncio
import os
import re
import sys
from pathlib import Path

import edge_tts
import torch
import TTS
from pydub import AudioSegment
from TTS.api import TTS

INPUT_FOLDER = Path("input")
JOBS_FOLDER = Path("jobs")
COQUI_FOLDER = Path("coqui_samples")
AUDIO_SAMPLES = Path("sample_audio")


def text_audio_generate(
    config: dict,
    output_folder: Path,
    batch_num: int,
    batch: list[str],
    post_output_folder: Path = None,
):
    if config["tts_model"] == "edge":
        voice = config["tts_voice"]
        asyncio.run(
            edge_tts_generate(
                voice, output_folder, batch_num, batch, post_output_folder
            )
        )

    elif config["tts_model"] == "coqui":
        sample_path = COQUI_FOLDER / config["tts_sample"]
        coqui_tts_generate(
            output_folder, batch_num, batch, sample_path, post_output_folder
        )


async def edge_tts_generate(
    voice: str,
    output_folder: Path,
    batch_num: int,
    batch: list[str],
    post_output_folder: Path = None,
    rate: int = 0,
    pitch: int = 0,
):
    for idx, sentence in enumerate(batch, start=1):
        output_file = output_folder / f"{batch_num}_{idx}.wav"
        if output_file.exists():
            continue
        if post_output_folder:
            post_output_file = post_output_folder / f"{batch_num}_{idx}.wav"
            if post_output_file.exists():
                continue

        await edge_speak(
            text=sentence,
            voice=voice,
            output_file=output_file,
            rate=rate,
            pitch=pitch,
        )


async def edge_speak(
    text: str, voice: str, output_file: str, rate: int = 0, pitch: int = 0
):
    pitch = f"+{pitch}Hz" if pitch >= 0 else f"-{pitch}Hz"
    rate = f"+{rate}%" if rate >= 0 else f"{rate}%"
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(output_file)
    print(f"TTS with {voice} completed. Output TTS file: '{output_file}' ")


async def generate_edge_sample(
    text: str, voice: str, rate: int = 0, pitch: int = 0
) -> Path:
    output_file = AUDIO_SAMPLES / f"edge_sample.wav"
    pitch = f"+{pitch}Hz" if pitch >= 0 else f"{pitch}Hz"
    rate = f"+{rate}%" if rate >= 0 else f"{rate}%"
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(output_file)
    print(f"TTS with {voice} completed. Output TTS file: '{output_file}' ")
    return output_file


def coqui_tts_generate(
    output_folder: Path,
    batch_num: int,
    batch: list[str],
    sample: Path,
    post_output_folder: Path = None,
):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    for idx, sentence in enumerate(batch, start=1):
        output_file = output_folder / f"{batch_num}_{idx}.wav"
        if output_file.exists():
            continue
        if post_output_folder:
            post_output_file = post_output_folder / f"{batch_num}_{idx}.wav"
            if post_output_file.exists():
                continue
        tts.tts_to_file(
            text=sentence,
            speaker_wav=str(sample),
            language="en",
            file_path=str(output_file),
        )


def generate_coqui_sample(text: str, speaker_wav: Path, language="en"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    output_file = AUDIO_SAMPLES / f"coqui_sample.wav"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(
        text=text,
        speaker_wav=str(COQUI_FOLDER / speaker_wav),
        file_path=str(output_file),
        language=language,
    )
    return output_file


def convert_to_wav(mp3_path) -> Path:
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    wav_path = Path(mp3_path).with_suffix(".wav")
    audio.export(wav_path, format="wav")
    return wav_path
