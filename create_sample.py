from gtts import gTTS
import os

def create_sample_audio():
    text = """
    Hello everyone. Today I would like to talk about the importance of artificial intelligence in our daily lives.
    AI is transforming how we work, learn, and communicate. However, we must be mindful of the ethical implications.
    Thank you for listening to my short speech.
    """
    
    tts = gTTS(text=text, lang='en')
    output_path = "sample_speech.mp3"
    tts.save(output_path)
    print(f"Sample audio saved to {output_path}")

if __name__ == "__main__":
    create_sample_audio()
