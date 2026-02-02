import argparse
import os
import json
from audio_processor import AudioProcessor
from transcriber import Transcriber
from analyzer import AcousticAnalyzer, TextAnalyzer
from reporter import Reporter
from groq import Groq

def main():
    # Add FFmpeg to PATH for the current session
    ffmpeg_path = r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] += os.pathsep + ffmpeg_path
    
    parser = argparse.ArgumentParser(description="Audio Analysis and Rating System")
    parser.add_argument("input_file", help="Path to the input audio/video file")
    parser.add_argument("--api_key", help="Gemini API Key (optional, can be set via env var GEMINI_API_KEY)", default=None)
    parser.add_argument("--groq_api_key", help="Groq API Key (optional, can be set via env var GROQ_API_KEY)", default=None)
    parser.add_argument("--provider", help="LLM Provider: 'auto', 'gemini', 'groq'", default="auto")
    parser.add_argument("--language", help="Language code (e.g., 'en', 'mr', 'hi'). If not set, auto-detects.", default=None)
    parser.add_argument("--model", help="Whisper model size (tiny, base, small, medium, large)", default="base")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return

    print(f"Processing file: {input_path}")
    
    # 1. Preprocessing
    processor = AudioProcessor()
    try:
        wav_path = processor.convert_to_wav(input_path)
    except Exception as e:
        print(f"Error converting audio: {e}")
        return

    # 2. Transcription
    transcriber = Transcriber(model_size=args.model)
    transcript_data = transcriber.transcribe(wav_path, language=args.language)
    print(f"Detected Language: {transcript_data['language']}")
    print(f"Transcript start: {transcript_data['text'][:100]}...")

    # 3. Analysis
    # Acoustic
    print("Running acoustic analysis...")
    y, sr = processor.load_audio_librosa(wav_path)
    acoustic_analyzer = AcousticAnalyzer()
    acoustic_metrics = acoustic_analyzer.analyze(y, sr)
    
    # Text
    print("Running text analysis...")
    text_analyzer = TextAnalyzer()
    text_metrics = text_analyzer.analyze(transcript_data)

    # 4. Reporting
    # 4. Reporting
    print("Generating report...")
    # Initialize reporter with keys and provider preference
    # Note: We pass api_key as 'api_key' which Reporter uses for Gemini, and groq_key explicitly if needed
    # Ideally Reporter constructor handles the logic of which key to use based on provider
    
    # We pass the gemini key to api_key param for backward compat, and handle groq logic inside
    reporter = Reporter(api_key=args.api_key, provider=args.provider)
    if args.groq_api_key:
        reporter.groq_key = args.groq_api_key
        # Re-evaluate provider logic if key was just set (or better, modify Reporter __init__ to accept kwargs, but let's just set it)
        if reporter.provider == "auto" or reporter.provider == "groq":
             if reporter.groq_key and reporter.groq_key.startswith("gsk_"):
                reporter.provider = "groq"
                reporter.client = Groq(api_key=reporter.groq_key)
                reporter.model_id = "llama-3.3-70b-versatile"
                print("Using Provider: Groq (Llama 3) via explicit key")

    # Pass wav_path for native audio analysis if available
    report = reporter.generate_report(transcript_data['text'], acoustic_metrics, text_metrics, audio_path=wav_path)
    
    # Output
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.json")
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"Report saved to {output_path}")
    
    # Save transcript
    transcript_path = os.path.join(output_dir, "transcript.json")
    with open(transcript_path, "w") as f:
        json.dump(transcript_data, f, indent=4)
    print(f"Transcript saved to {transcript_path}")
    
    # Print summary to console
    print("\n--- Analysis Summary ---")
    if "overall_summary" in report:
        print(report["overall_summary"])
    print("\n--- Ratings ---")
    if "ratings" in report:
        for category, data in report["ratings"].items():
            print(f"{category}: {data['score']}/10 - {data['reason']}")

    # Cleanup
    if os.path.exists(wav_path) and wav_path != input_path:
        os.remove(wav_path)

if __name__ == "__main__":
    main()
