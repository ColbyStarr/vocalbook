from pathlib import Path

from pydub import AudioSegment

from services.utils import natural_sort_key


def stitch(job_directory: Path, batch_num: int):
    processed = job_directory / "post_processing"
    output_file = job_directory / "audio.mp3"
    pattern = f"{batch_num}*"
    files = sorted(processed.glob(pattern), key=natural_sort_key)

    print(f"Found {len(files)} files to stitch.")
    stitch_wavs(files, output_file)


def stitch_wavs(input_files: list[Path], output_file: Path):
    """
    Combine WAV files and export as an MP3.
    If output MP3 exists, append the new audio to the end.
    """
    if not input_files:
        print("No files found to stitch.")
        return

    # Load and combine all input WAVs
    stitched = AudioSegment.empty()
    for input_file in input_files:
        stitched += AudioSegment.from_wav(input_file)

    # If the MP3 already exists, load it and append
    if output_file.exists():
        existing = AudioSegment.from_mp3(output_file)
        stitched = existing + stitched

    # Export to MP3
    stitched.export(output_file, format="mp3")
    print(f"Appended {len(input_files)} WAV files to {output_file}")
