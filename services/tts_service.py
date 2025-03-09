import sys
import asyncio
import edge_tts
import os
import re



def auto_speech_setting(sentance:str):
    """
    Enhance logic here when possible
    """
    rate = -12
    pitch = "-5Hz"
    rates = f"+{rate}%" if rate >= 0 else f"{rate}%"
    return rates, pitch

async def sample_text_audio_generate(voice:str):
    sentence = "The quick brown fox jumps over the lazy dog."
    rates, pitch = auto_speech_setting(sentence)
    output_file = f'segment_store/sample_wav_store/tts_{voice}_sample.wav'
    await speak(text=sentence, voice=voice, rates=rates, pitch=pitch, output_file=output_file)


async def text_audio_generate(sentences: list[str], voice:str):
    for idx, sentence in enumerate(sentences, start=1):
        rates, pitch = auto_speech_setting(sentence)
        output_file = f'segment_store/tts_wav_store/tts_{idx:03}.wav'
        await speak(text=sentence, voice=voice, rates=rates, pitch=pitch, output_file=output_file)



async def speak(text:str, voice:str, rates:str, pitch:str, output_file:str):
    await edge_tts.Communicate(text, voice, rate=rates, pitch=pitch).save(output_file)
    print(f"TTS with {voice} completed. Output TTS file: '{output_file}' ")


if __name__ == "__main__":
    asyncio.run(text_audio_generate())

