import time
from services.config.workout_config import PROMPT

MODELS_TO_TRY = ["gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
_working_model_name = None

def get_working_model_name():
    return _working_model_name

def set_working_model_name(name):
    global _working_model_name
    _working_model_name = name


class LLMCoach:
    def __init__(self, genai_module):
        self.genai = genai_module
        self.system_prompt = PROMPT
        self.history = []

    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        if issue:
            prompt += f" Form Issue: {issue}"

        models_to_test = [get_working_model_name()] if get_working_model_name() else MODELS_TO_TRY

        for model_name in models_to_test:
            if not model_name:
                continue
                
            try:
                print(f"[DEBUG] llm.py: Trying model '{model_name}'...")
                model = self.genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=self.system_prompt
                )
                
                # Start a chat with the current history (last 10 messages)
                chat = model.start_chat(history=self.history[-10:])
                
                response = chat.send_message(prompt)
                text = response.text.strip()
                print(f"[DEBUG] llm.py: Successfully used '{model_name}'. Response: '{text}'")
                
                if get_working_model_name() != model_name:
                    set_working_model_name(model_name)
                    print(f"[DEBUG] Cached working model name: {model_name}")
                
                # Gemini uses "user" and "model" for roles, and "parts" for content
                self.history.append({"role": "user", "parts": [prompt]})
                self.history.append({"role": "model", "parts": [text]})
                
                return text
                
            except Exception as e:
                error_str = str(e)
                print(f"[DEBUG] Gemini API Error with {model_name}: {error_str}")
                
                if "404" in error_str:
                    print(f"[DEBUG] Model {model_name} not found, trying next...")
                    continue
                elif "429" in error_str:
                    print(f"[DEBUG] Rate limited on {model_name} — waiting 3s before retry...")
                    time.sleep(3)
                    try:
                        response = chat.send_message(prompt)
                        text = response.text.strip()
                        self.history.append({"role": "user", "parts": [prompt]})
                        self.history.append({"role": "model", "parts": [text]})
                        return text
                    except Exception as retry_e:
                        print(f"[DEBUG] Retry failed: {retry_e}")
                        pass
                        
        return "Keep going!"