# VocalBook

<p align="center">
  <img src="images/icon.png" alt="Vocalbook Icon" width="150">
</p>

**VocalBook** is a text-to-audio generator that uses a **Text-to-Speech (TTS) → RVC** pipeline. The pipeline works by first generating audio with a TTS model, and then passing it through an RVC model. This app is designed to run on hardware that would normally be considered less than optimal for heavy-duty machine learning tasks.

---

### Text to Speech

For text-to-speech, this app uses **Edge TTS** and **Coqui TTS**:

- **Edge TTS** is a Microsoft project with over 300 voices. It includes both male and female voices for nearly every country and language. Edge is a great tool for **fast audio conversion**.

- **Coqui TTS** is an open-source project with several high-quality models. In this app, we specifically use **XTTS**. It performs something called **voice cloning**: when given a short (15–30 second) audio clip, it will try to synthesize future speech in that voice. Coqui is excellent for voice mimicking, but it is **slow**, occasionally mispronounces words, and can struggle with long chunks of text.

---

### RVC

**RVC** stands for _Retrieval-Based Voice Conversion_. Whereas TTS generates audio from text, RVC transforms one audio input into another — it’s **audio-to-audio**. It's commonly used in voice changers and has become a popular tool for:

- Enhancing audio quality
- Mimicking specific voices
- Voice style transfer

There’s a lot of community support for RVC:

- https://voice-models.com/
- https://www.weights.com/
- https://rvc-models.com/

To find a particular voice — whether it’s a celebrity, politician, or fictional character — check out those sites. _(Please use responsibly.)_

---

## How to Use VocalBook

This app revolves around two key abstractions: **configs** and **jobs**.

- A **config** is a set of instructions you build to tell VocalBook **how** to generate the voice you want. If you use the frontend interface, it gives you a great way to experiment and find the perfect voice.

- A **job** consists of a config, a document, and all the audio generated during a run. Keeping configs and jobs as separate concepts means you can reuse a config across many different documents.
