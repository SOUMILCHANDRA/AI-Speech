import whisper
import torch

class Transcriber:
    def __init__(self, model_size="base"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model '{model_size}' on {device}...")
        self.model = whisper.load_model(model_size, device=device)

    def transcribe(self, audio_path, language=None):
        """
        Transcribes the audio file.
        Returns a dictionary with text and segments.
        """
        print(f"Transcribing audio (Language: {language if language else 'Auto-detect'})...")
        options = {}
        if language:
            options["language"] = language
            
        result = self.model.transcribe(audio_path, **options)
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"]
        }
