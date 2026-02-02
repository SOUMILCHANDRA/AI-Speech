import os
from google import genai
from google.genai import types
from groq import Groq
import json

class Reporter:
    def __init__(self, api_key=None, provider="auto"):
        self.provider = provider
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        self.groq_key = api_key or os.getenv("GROQ_API_KEY") # Check same arg for simplicity or separate env var
        
        self.client = None
        self.model_id = None
        
        # Determine provider
        if (self.provider == "auto" or self.provider == "groq") and self.groq_key and self.groq_key.startswith("gsk_"):
            self.provider = "groq"
            print("Using Provider: Groq (Llama 3)")
            self.client = Groq(api_key=self.groq_key)
            self.model_id = "llama-3.3-70b-versatile" 
        elif (self.provider == "auto" or self.provider == "gemini") and self.gemini_key:
            self.provider = "gemini"
            print("Using Provider: Google Gemini")
            self.client = genai.Client(api_key=self.gemini_key)
            self.model_id = "gemini-2.0-flash"
        else:
            print("Warning: No valid API Key found (Gemini or Groq). Qualitative analysis will be limited.")
            self.client = None

    def generate_report(self, transcript_text, acoustic_metrics, text_metrics, audio_path=None):
        """
        Generates the final report using LLM for qualitative parts and hard metrics for others.
        If audio_path is provided, it uploads the audio to Gemini for native multimodal analysis.
        """
        
        # Base prompt structure
        prompt_text = f"""
        You are an expert communication coach. Analyze the speech and provided metrics to generate a detailed performance report.
        
        **Speech Transcript:**
        "{transcript_text}"
        
        **Quantitative Metrics:**
        - Duration: {acoustic_metrics.get('duration_sec', 0):.2f} seconds
        - Speaking Rate: {text_metrics.get('wpm', 0):.2f} Words Per Minute
        - Pause Fraction: {acoustic_metrics.get('pause_fraction', 0):.2%} of time is silence
        - Pitch Variation (Std Dev): {acoustic_metrics.get('pitch_std_hz', 0):.2f} Hz (Higher means more expressive tone)
        - Average Sentence Length: {text_metrics.get('avg_sentence_length', 0):.2f} words
        
        **Task:**
        Rate the speaker on a scale of 1-10 for the following categories and provide a brief justification for each.
        
        1. Clarity and Voice (Consider pitch metrics and transcript clarity)
        2. Expression and Tone (Consider pitch variability)
        3. Fluency (Consider WPM and pauses)
        4. Length (Is it too short or too long? Context: General speech)
        5. Pauses and Punctuation Awareness (Consider pause fraction)
        6. Relevance and Creativity (Judge based on content)
        7. Sentence Size (Consider avg sentence length)
        8. Spelling and Punctuation (Judge based on transcript structure)
        9. Story Structure (Beginning, Middle, End?)
        10. Word Usage (Vocabulary richness)
        
        **Output Format:**
        Provide the output strictly as a JSON object with the following structure:
        {{
            "ratings": {{
                "Clarity and Voice": {{ "score": int, "reason": "string" }},
                "Expression and Tone": {{ "score": int, "reason": "string" }},
                "Fluency": {{ "score": int, "reason": "string" }},
                "Length": {{ "score": int, "reason": "string" }},
                "Pauses and Punctuation Awareness": {{ "score": int, "reason": "string" }},
                "Relevance and Creativity": {{ "score": int, "reason": "string" }},
                "Sentence Size": {{ "score": int, "reason": "string" }},
                "Spelling and Punctuation": {{ "score": int, "reason": "string" }},
                "Story Structure": {{ "score": int, "reason": "string" }},
                "Word Usage": {{ "score": int, "reason": "string" }}
            }},
            "overall_summary": "string",
            "improvement_recommendations": ["string", "string", ...]
        }}
        """

        if self.client:
            try:
                # GROQ IMPLEMENTATION
                if self.provider == "groq":
                    # For Groq, we just use the text prompt since it's Llama 3 (audio upload not native in this context)
                    # We append a specific JSON instruction for Llama to ensure strict parsing
                    prompt_text += "\nIMPORTANT: Valid JSON output only."
                    
                    chat_completion = self.client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that outputs strictly in JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt_text,
                            }
                        ],
                        model=self.model_id,
                        response_format={"type": "json_object"}, 
                    )
                    return json.loads(chat_completion.choices[0].message.content)

                # GEMINI IMPLEMENTATION
                elif self.provider == "gemini":
                    contents = []
                    
                    # If audio is available, upload and include it
                    if audio_path and os.path.exists(audio_path):
                        print(f"Uploading audio to Gemini: {audio_path}")
                        audio_file = self.client.files.upload(file=audio_path)
                        contents.append(audio_file)
                        prompt_text = "Listen to the attached audio and analyze the speech based on the transcript and metrics below.\n" + prompt_text
                    
                    contents.append(prompt_text)

                    response = self.client.models.generate_content(
                        model=self.model_id,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                    
                    return json.loads(response.text)

            except Exception as e:
                print(f"Error calling LLM ({self.provider}): {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return self._fallback_report(acoustic_metrics, text_metrics)
        else:
            print("Skipping LLM analysis (No valid API Key).")
            return self._fallback_report(acoustic_metrics, text_metrics)

    def _fallback_report(self, acoustic_metrics, text_metrics):
        """
        Fallback if no LLM is available.
        """
        return {
            "ratings": {
                "Clarity and Voice": {"score": 5, "reason": "LLM unavailable. Neutral score."},
                # ... fill others with defaults or simple heuristic logic
            },
            "overall_summary": "Report generated without LLM analysis. Only quantitative metrics are accurate.",
            "improvement_recommendations": ["Check API key configuration."]
        }
