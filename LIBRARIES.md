# 📚 Project Libraries & Dependencies

This document provides a detailed list of the Python libraries used in the **AI Speech Coach** project and their specific roles.

## 🧠 Core AI & Analysis
*   **`openai-whisper`**:  
    Used for **Speech-to-Text (ASR)**. It handles the transcription of audio files into text, supporting multiple languages (English, Hindi, Marathi) and different model sizes (base, medium, large).
*   **`groq`**:  
    The primary client for accessing the **Llama 3** model. It provides the qualitative analysis (clarity, tone, grammar) of the unified transcript.
*   **`google-genai`** (Optional):  
    Client for **Google Gemini 2.0**. Serves as an alternative analysis backend if Groq is not used.

## 🌐 Web Application
*   **`flask`**:  
    The micro-framework powering the web server. It handles routing, API endpoints (`/analyze`, `/tts`), and serving the HTML frontend.

## 🔊 Audio Processing
*   **`librosa`**:  
    A powerful library for music and audio analysis. Used here to extract acoustic metrics like:
    *   Pitch (Fundamental Frequency)
    *   Pause Rate
    *   Speech Durations
*   **`edge-tts`**:  
    Provides **Text-to-Speech** functionality. It generates the MP3 feedback audio using Microsoft Edge's neural voices (e.g., `en-IN-NeerjaNeural`).
*   **`pydub`**:  
    Used for high-level audio manipulation, such as converting varying audio formats into the standard WAV format required by the analysis pipeline.
*   **`soundfile`**:  
    A dependency for reading and writing audio files, used internally by librosa and for buffer management.
*   **`gTTS`** (Legacy/Fallback):  
    Google Text-to-Speech library, kept as a backup for TTS generation.

## 🧮 Utilities
*   **`numpy`**:  
    Fundamental package for scientific computing. Used for handling audio data arrays and performing calculations (mean pitch, standard deviation).
*   **`scipy`**:  
    Used for signal processing tasks within the acoustic analysis pipeline.
*   **`torch`**:  
    PyTorch deep learning framework, required to run the local Whisper models.
