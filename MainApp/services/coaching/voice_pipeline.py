import streamlit as st


class VoicePipeline:
    """
    Simplified coaching pipeline — fires on EVERY call, no cooldown, no filtering.
    The caller (metrics.py) decides WHEN to call this; this class just executes.
    """

    def __init__(self, llm, tts):
        self.llm = llm
        self.tts = tts

    def _find_form_issue(self, exercise, metrics):
        """Checks metrics for known form problems. Returns issue string or None."""
        if "issue" in metrics:
            return metrics["issue"]
            
        # First check the cached rep_issue that was tracked during the rep's active phase
        rep_issue = metrics.get("rep_issue")
        
        if rep_issue:
            if rep_issue == "TOO HIGH":
                return "The user's squat is not deep enough — knees are not bending sufficiently."
            elif rep_issue == "Poor Form":
                return "The user's body is not straight during the push-up."
            elif rep_issue == "SAGGING":
                return "The user's hips are sagging down during the push-up."
            elif rep_issue == "PIKED UP":
                return "The user's hips are too high — lower them to form a straight line."
            elif rep_issue == "SWINGING":
                return "The user is swinging their torso during the curl — keep the body still."
            elif rep_issue == "ELBOW DRIFTING":
                return "The user's elbow is drifting away from their side during the curl."
            elif rep_issue == "Excessive Arch":
                return "The user is arching their lower back excessively during the press."
            elif rep_issue == "Slight Arch":
                return "Slight back arch detected — encourage the user to brace their core."
            elif rep_issue == "OFF BALANCE":
                return "The user is losing balance during the lunge — feet should be hip-width apart."
            elif rep_issue == "LEGS NOT WIDE":
                return "The user is not spreading their legs wide enough during the jumping jack."
            elif rep_issue == "ARMS NOT HIGH":
                return "The user's arms are not going high enough during the jumping jack."

        # Fallback to current live metrics (e.g. for ongoing back angle checks)
        if exercise == "Squats":
            back_angle = metrics.get("back_angle", 180)
            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return "The user is leaning too far forward during the squat."

        return None

    def process_event(self, event, exercise, metrics):
        """
        ALWAYS calls the LLM and TTS. No cooldown. No conditional skipping.
        Returns (audio_bytes, text_str) every single time.
        """
        issue = self._find_form_issue(exercise, metrics)

        # Always call the LLM — good form gets hype, bad form gets correction.
        text = self.llm.give_feedback(event, issue)
        voice = self.tts.speak(text)
        print(f"[DEBUG] voice_pipeline: tts.speak returned audio of length {len(voice) if voice else 0} bytes")

        return voice, text


def autoplay_audio(audio_bytes):
    if not audio_bytes:
        print("[DEBUG] voice_pipeline autoplay_audio: audio_bytes is empty, skipping.")
        return
    
    st.markdown("<style>[data-testid='stAudio'] {display: none;}</style>", unsafe_allow_html=True)
    
    print(f"[DEBUG] voice_pipeline autoplay_audio: playing audio of length {len(audio_bytes)} bytes")
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
