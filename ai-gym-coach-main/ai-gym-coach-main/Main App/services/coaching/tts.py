from io import BytesIO
from gtts import gTTS


class TextToSpeech:
    def speak(self, text, lang="en"):
        cleaned = (text or "").strip()

        if not cleaned:
            return
        
        buffer = BytesIO()

        try:
            gTTS(text=cleaned, lang=lang).write_to_fp(buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            print(f"[DEBUG] tts.py: gTTS failed to generate audio! Error: {e}")
            return None
    