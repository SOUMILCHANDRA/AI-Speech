from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import json
import uuid
from werkzeug.utils import secure_filename
import subprocess
import asyncio
import edge_tts

# Add parent directory to path to import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio_processor import AudioProcessor
from transcriber import Transcriber
from analyzer import AcousticAnalyzer, TextAnalyzer
from reporter import Reporter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize components (lazily or globally)
# Note: For production, better to handle API keys securely. 
# Here we expect them in env vars or passed via args (but args are for CLI)
# We will use env vars for the web app.

# Global model cache
LOADED_TRANSCRIBER = None
CURRENT_MODEL_SIZE = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    global LOADED_TRANSCRIBER, CURRENT_MODEL_SIZE

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(f"{uuid.uuid4()}.wav")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # 1. Pipeline Execution
            audio_processor = AudioProcessor()
            
            # Model Caching Logic
            requested_model = request.form.get('model_size', 'medium') # Default to medium
            
            if LOADED_TRANSCRIBER is None or CURRENT_MODEL_SIZE != requested_model:
                print(f"Switching model from {CURRENT_MODEL_SIZE} to {requested_model}...")
                LOADED_TRANSCRIBER = Transcriber(model_size=requested_model)
                CURRENT_MODEL_SIZE = requested_model
            
            transcriber = LOADED_TRANSCRIBER
            acoustic_analyzer = AcousticAnalyzer()
            text_analyzer = TextAnalyzer()
            
            # Get language preference
            language = request.form.get('language')
            if language == 'auto':
                language = None

            # Use Groq by default for Web App if key is available
            groq_key = os.getenv("GROQ_API_KEY") or request.form.get('api_key')
            reporter = Reporter(api_key=None, provider="groq")
            if groq_key:
                reporter.groq_key = groq_key
                reporter.client = __import__('groq').Groq(api_key=groq_key)
                reporter.model_id = "llama-3.3-70b-versatile"
            
            # Process
            wav_path = audio_processor.convert_to_wav(filepath)
            
            # Load audio for acoustic analysis
            y, sr = audio_processor.load_audio_librosa(wav_path)
            
            transcript_data = transcriber.transcribe(wav_path, language=language)
            acoustic_metrics = acoustic_analyzer.analyze(y, sr)
            text_metrics = text_analyzer.analyze(transcript_data)
            
            report = reporter.generate_report(transcript_data['text'], acoustic_metrics, text_metrics, audio_path=wav_path)
            
            # Clean up temp file
            # os.remove(filepath) 
            
            response_data = {
                "transcript": transcript_data['text'],
                "metrics": {
                    "acoustic": acoustic_metrics,
                    "text": text_metrics
                },
                "report": report
            }
            
            return jsonify(response_data)

        except Exception as e:
            print(f"Error executing pipeline: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'en-IN-NeerjaNeural') # Default to Indian English female
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    output_filename = f"tts_{uuid.uuid4()}.mp3"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    async def generate_speech():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    try:
        asyncio.run(generate_speech())
        return jsonify({'audio_url': f'/output/{output_filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<filename>')
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
