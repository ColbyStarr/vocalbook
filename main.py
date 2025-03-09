# from vocalize.vocalize import run_infer_script
# input_path="tts_wav_store/tts_4.wav",
# output_path="/Users/colbystarr/Desktop/VocalbookRVC/conversion_store/converted.wav",
# pth_path="voice_models/michael_caine/michael_caine.pth",
# index_path="/Users/colbystarr/Desktop/VocalbookRVC/voice_models/GOTHMOMMY/added_GOTHMOMMY_v2.index",





import argparse
import sys
import asyncio
from services.tts_service import text_audio_generate
from services.text_processing import read_and_chunk_text
from services.rvc_service import run_infer_script_default
from services.audio_stitcher import stitch

import argparse

def parse_args(argv):
    parser = argparse.ArgumentParser(description="Text Processor")
    parser.add_argument('-i', '--input-file', type=str, required=True, help='Path to input text file')
    parser.add_argument('-m', '--mode', choices=['tts', 'rvc'], required=True, help='Choose either text-to-speech (tts) or retrieval-based conversion (rvc)')
    parser.add_argument('-model', '--model-name', type=str, required=True, help='Specify the model name to use (either TTS or RVC)')
    return parser.parse_args(argv)



def run_all(tts_model_name:str, rvc_model_name:str, input_file:str):
    sentances = read_and_chunk_text(input_file)
    asyncio.run(text_audio_generate(sentances, tts_model_name))
    run_infer_script_default(rvc_model_name)
    stitch()


def main(argv):
    my_args = parse_args(argv)
    if my_args.mode == "tts":
        sentances = read_and_chunk_text(my_args.input_file)
        asyncio.run(text_audio_generate(sentances, my_args.model_name))
    elif my_args.mode == "rvc":
        run_infer_script_default(my_args.model_name)
        stitch()
        


if __name__ == "__main__":
    main(sys.argv[1:])

