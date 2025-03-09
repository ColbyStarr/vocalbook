import os
import re
import wave

def get_sorted_rvc_files(directory):
    """
    Scan the directory for files matching rvc_###.wav and return them sorted by number.
    """
    files = []
    pattern = re.compile(r"rvc_(\d+)\.wav")

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            files.append((int(match.group(1)), filename))

    # Sort by number (the captured group)
    files.sort(key=lambda x: x[0])

    # Return just the file paths
    return [os.path.join(directory, file[1]) for file in files]


def stitch_wavs(input_files, output_file):
    """
    Combine all input WAV files into a single output WAV file.
    """
    if not input_files:
        print("No files found to stitch.")
        return

    with wave.open(output_file, 'wb') as output_wav:
        with wave.open(input_files[0], 'rb') as first_wav:
            output_wav.setparams(first_wav.getparams())

        for input_file in input_files:
            with wave.open(input_file, 'rb') as wav:
                frames = wav.readframes(wav.getnframes())
                output_wav.writeframes(frames)

    print(f"Stitched {len(input_files)} files into {output_file}")

def stitch():
    segment_store = os.path.join('segment_store', 'rvc_wav_store')
    output_file = 'output/book.wav'

    # Scan and sort the files
    rvc_files = get_sorted_rvc_files(segment_store)
    
    if not rvc_files:
        print("No RVC files found in segment_store/rvc_wav_store.")
        return

    print(f"Found {len(rvc_files)} files to stitch.")
    stitch_wavs(rvc_files, output_file)

