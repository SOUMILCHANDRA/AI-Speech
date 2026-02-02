import os
from pydub import AudioSegment
import librosa
import soundfile as sf
import numpy as np

class AudioProcessor:
    def __init__(self):
        pass

    def convert_to_wav(self, input_path):
        """
        Converts input audio/video to WAV format suitable for processing.
        Returns path to the temporary WAV file.
        """
        file_ext = os.path.splitext(input_path)[1].lower()
        output_path = "temp_audio.wav"
        
        try:
            if file_ext == ".wav":
                # Just copy or return original if it's already wav
                # But to be safe and consistent with sampling rate, we might want to reload
                audio = AudioSegment.from_file(input_path)
            else:
                audio = AudioSegment.from_file(input_path)
            
            # Export as wav, mono, 16kHz (good for Whisper)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(output_path, format="wav")
            return output_path
        except FileNotFoundError:
            raise RuntimeError("FFmpeg is not installed or not found in PATH. Please install FFmpeg to process audio files.")
        except Exception as e:
            raise RuntimeError(f"Error processing audio file: {str(e)}")

    def load_audio_librosa(self, file_path):
        """
        Loads audio using librosa for acoustic analysis.
        """
        y, sr = librosa.load(file_path, sr=None)
        return y, sr
