# AI Speech Coach 🎙️

A comprehensive audio analysis tool and web application designed to help users master their speech. It evaluates clarity, fluency, expression, and pacing using advanced AI models.

## 🌟 Features

*   **Dual Interface:**
    *   **Web App:** Premium "Glassmorphism" UI for easy recording and feedback.
    *   **CLI:** Command-line tool for batch processing.
*   **Audio Recording & Upload:** Record directly in-browser or upload `.mp3`/`.wav` files.
*   **Multi-Model Intelligence:**
    *   **Transcription:** OpenAI Whisper (Base, Medium, Large models).
    *   **Qualitative Analysis:** Groq (Llama 3) or Google Gemini.
    *   **Acoustic Metrics:** Pitch tracking, pause analysis, and speech rate via `librosa`.
*   **Text-to-Speech Feedback:** Listen to AI-generated improvement tips via `edge-tts`.
*   **Language Support:** Optimized for English, Hindi, and Marathi.

## 🛠️ Installation

### Prerequisites
1.  **Python 3.8+** installed.
2.  **FFmpeg** installed and added to your system PATH (required for audio processing).

### Setup
1.  **Clone/Download** this repository.
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🔑 Configuration

You need API keys for the LLM analysis.
*   **Groq API Key** (Recommended for speed via Llama 3)
*   **Gemini API Key** (Optional alternative)

Set them in your environment variables (or pass them when running):
```powershell
$env:GROQ_API_KEY = "your_groq_key_here"
```

## 🚀 Usage

### 1. Web Application (Recommended)
Launch the interactive web interface:

```powershell
# Set Key (PowerShell)
$env:GROQ_API_KEY='your_key_here'

# Run Server
py src/web/app.py
```

*   Open your browser to: `http://127.0.0.1:5000`
*   Select your language and accuracy level.
*   Record your speech or upload a file to get instant feedback.

### 2. Command Line Interface (CLI)
Run analysis on a specific file without the UI:

```powershell
py src/main.py "path/to/audio.mp3" --groq_api_key "your_key" --language mr --model medium
```

**Options:**
*   `--provider`: `groq` or `gemini`
*   `--language`: `en`, `hi`, `mr` (or `auto`)
*   `--model`: `base`, `medium`, `large`

## 📂 Project Structure

*   `src/web/`: Web application (Flask + HTML/CSS/JS).
*   `src/main.py`: Entry point for CLI.
*   `src/analyzer.py`: Acoustic and text metric logic.
*   `src/transcriber.py`: Whisper integration.
*   `src/reporter.py`: LLM interaction (Groq/Gemini).
*   `output/`: Generated reports and PDFs.
