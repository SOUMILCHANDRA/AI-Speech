import librosa
import numpy as np

class AcousticAnalyzer:
    def __init__(self):
        pass

    def analyze(self, y, sr):
        """
        Extracts acoustic features: pitch variability, pause rate, speech rate (approx).
        """
        duration = librosa.get_duration(y=y, sr=sr)
        
        # 1. Pauses (Silence detection)
        # Split at silence (default top_db=60)
        non_silent_intervals = librosa.effects.split(y, top_db=20)
        non_silent_time = sum([ (end - start) / sr for start, end in non_silent_intervals ])
        pause_time = duration - non_silent_time
        pause_fraction = pause_time / duration if duration > 0 else 0
        
        # 2. Pitch (Fundamental Frequency)
        # Use piptrack or pyin
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        # Filter out NaNs
        f0_clean = f0[~np.isnan(f0)]
        if len(f0_clean) > 0:
            pitch_mean = np.mean(f0_clean)
            pitch_std = np.std(f0_clean)
        else:
            pitch_mean = 0
            pitch_std = 0

        return {
            "duration_sec": duration,
            "pause_time_sec": pause_time,
            "pause_fraction": pause_fraction,
            "pitch_mean_hz": pitch_mean,
            "pitch_std_hz": pitch_std
        }

class TextAnalyzer:
    def __init__(self):
        pass

    def analyze(self, transcript_data):
        """
        Analyzes text features: word count, sentence count, average sentence length.
        """
        text = transcript_data["text"]
        segments = transcript_data["segments"]
        
        words = text.split()
        word_count = len(words)
        
        # Simple sentence splitting by punctuation
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        sentence_count = len(sentences)
        
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Estimate WPM based on transcript timestamps if available, or just total duration
        # Segments usually have start/end
        if segments:
            start_time = segments[0]['start']
            end_time = segments[-1]['end']
            speech_duration = end_time - start_time
            wpm = (word_count / (speech_duration / 60)) if speech_duration > 0 else 0
        else:
            wpm = 0

        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "wpm": wpm
        }
