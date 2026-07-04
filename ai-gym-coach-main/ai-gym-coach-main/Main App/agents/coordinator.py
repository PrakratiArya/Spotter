import time
from agents.safety_agent import SafetyAgent
from services.coaching.voice_pipeline import VoicePipeline
from services.persistence.exercise_repository import add_exercise

# Design Choice: The WorkoutCoordinator implements the ADK SequentialAgent pattern.
# Its role is to orchestrate the pipeline AFTER vision has already run in the WebRTC thread.
# The VisionToolAgent (skill dispatcher) runs inside VideoProcessorClass.recv() because that
# is the only place where raw MediaPipe landmarks are available in real time. By the time
# sync_metrics_update() fires in the Streamlit main thread, we already have computed metrics
# (angles, rep count, form status). So the coordinator accepts those pre-computed metrics
# and runs: Safety Check → Coaching → Persistence — exactly the sequential steps it should own.
#
# This is intentional: splitting perception (WebRTC thread) from reasoning (main thread)
# avoids blocking the camera pipeline with LLM calls.

class WorkoutCoordinator:
    """
    ADK SequentialAgent — orchestrates Safety → Coaching → Persistence.

    Step 1: SafetyAgent evaluates computed metrics and optional user voice/text input.
            If a dangerous threshold is crossed it requests human confirmation before continuing.
    Step 2: VoicePipeline + LLMCoach generate proactive audio + text feedback.
    Step 3: On milestone events (set_completed, workout_completed), data is persisted to SQLite.
    """

    def __init__(self, voice_pipeline: VoicePipeline):
        # Safety agent is stateless — safe to construct once and reuse across frames.
        self.safety_agent = SafetyAgent()
        self.voice_pipeline = voice_pipeline

    def run(
        self,
        exercise_type: str,
        metrics: dict,
        event: str,
        user_text: str = "",
        user_id: int = None,
        reps: int = 0,
        sets: int = 0,
        duration: float = 0.0,
    ) -> dict:
        """
        Execute the sequential pipeline for a single coaching tick.

        Args:
            exercise_type: e.g. "Squats", "Push-ups"
            metrics:       Pre-computed dict from the skill detector (angles, rep count, form status).
            event:         Coaching trigger — "ongoing_form_check", "set_completed", etc.
            user_text:     Optional voice/text input to check for pain keywords.
            user_id:       Database user ID; required for persistence steps.
            reps/sets/duration: Accumulated values to persist on milestone events.

        Returns:
            {
              "status":   "SUCCESS" | "SAFETY_STOP",
              "feedback": (audio_bytes, text_str) tuple from VoicePipeline, or None,
            }
        """
        # ── Step 1: Safety Agent ────────────────────────────────────────────────
        # Check computed angles against exercise-specific danger thresholds,
        # and scan user_text for pain/injury keywords.
        needs_pause = self.safety_agent.check_safety(exercise_type, metrics, user_text)
        if needs_pause:
            # ADK Human-in-the-loop confirmation: prompt the user before continuing.
            # In the Streamlit context this surfaces as a terminal prompt (or can be
            # replaced with a st.warning + st.button flow in a future iteration).
            confirmed = self.safety_agent.prompt_human_confirmation()
            if not confirmed:
                return {"status": "SAFETY_STOP", "feedback": None}

        # ── Step 2: Coaching Logic ──────────────────────────────────────────────
        # VoicePipeline decides whether to fire the LLM based on event type,
        # cooldown timer (5 s), and whether a form issue was detected.
        # Returns (audio_bytes, text) or None if no feedback warranted.
        feedback = self.voice_pipeline.process_event(event, exercise_type, metrics)

        # ── Step 3: Persistence ─────────────────────────────────────────────────
        # Only write to SQLite on milestone events so we don't spam the DB every frame.
        # Note: metrics.py already handles set_completed persistence; this covers any
        # additional events the coordinator is called with directly (e.g. workout_completed
        # triggered outside the normal metrics loop).
        if event in ("set_completed", "workout_completed") and user_id is not None:
            add_exercise(user_id, exercise_type, reps, sets, int(duration))

        return {"status": "SUCCESS", "feedback": feedback}
