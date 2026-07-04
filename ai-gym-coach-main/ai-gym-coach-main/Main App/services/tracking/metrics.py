import streamlit as st
import time
from services.config.workout_config import METRICS_FIELDS
from services.persistence.exercise_repository import add_exercise

# Lazy singleton for the coordinator — built on first use.
_coordinator = None


def _get_coordinator():
    """Returns a cached WorkoutCoordinator bound to the current session's voice_pipeline."""
    global _coordinator
    vp = st.session_state.get("voice_pipeline")
    if vp is None:
        print("[DEBUG] _get_coordinator: voice_pipeline is None in session state!")
        return None

    from agents.coordinator import WorkoutCoordinator

    if _coordinator is None or _coordinator.voice_pipeline is not vp:
        _coordinator = WorkoutCoordinator(vp)
        print("[DEBUG] _get_coordinator: Created new WorkoutCoordinator")

    return _coordinator


def _apply_feedback(result):
    """Unpacks coordinator result into session state for main.py's UI to display."""
    print(f"[DEBUG] _apply_feedback called. result={result}")
    if result and result.get("status") == "SUCCESS":
        feedback = result.get("feedback")
        if feedback:
            audio, text = feedback
            st.session_state.audio_to_play = audio
            st.session_state.coach_feedback = text
            print(f"[DEBUG] _apply_feedback: SESSION STATE UPDATED — text='{text}', audio={len(audio) if audio else 0} bytes")
        else:
            print("[DEBUG] _apply_feedback: feedback tuple was None")
    else:
        print(f"[DEBUG] _apply_feedback: skipped — status={result.get('status') if result else 'None'}")


def sync_metrics_update(context):
    if not context or not hasattr(context, "state") or not context.state.playing:
        return

    processor = getattr(context, "video_processor", None)

    if not processor:
        return

    exercise = st.session_state.get("exercise_type")

    if not exercise:
        return

    processor.set_exercise(exercise)
    latest_metrics = processor.get_latest_metrics()

    if not latest_metrics:
        return

    reps = latest_metrics.get("reps", 0)

    if reps is None:
        reps = 0

    # ── Detect new rep ──────────────────────────────────────────────────────────
    # Compare current rep count to the last known count.
    # If it increased, a new rep was just registered by the skill detector.
    prev_reps = st.session_state.get("reps", 0)
    st.session_state.reps = reps

    fields = METRICS_FIELDS.get(exercise)

    if not fields:
        return

    for key, default in fields.items():
        st.session_state[key] = latest_metrics.get(key, default)

    reps_per_set = st.session_state.get("reps_per_set", 0)
    target_sets = st.session_state.get("target_sets", 0)

    if reps is not None and reps_per_set > 0 and target_sets > 0:
        sets_completed = reps // reps_per_set
        current_set_reps = reps % reps_per_set
        workout_completed = sets_completed >= target_sets
    else:
        sets_completed = 0
        current_set_reps = 0
        workout_completed = False

    st.session_state.sets_completed = sets_completed
    st.session_state.current_set_reps = current_set_reps
    st.session_state.workout_completed = workout_completed

    coordinator = _get_coordinator()
    last_saved_sets = st.session_state.get("last_saved_sets_completed", 0)

    # ── NEW REP DETECTED — always coach ─────────────────────────────────────────
    if reps > prev_reps and coordinator:
        print(f"[DEBUG] *** NEW REP DETECTED *** reps went {prev_reps} -> {reps} (exercise={exercise})")
        print(f"[DEBUG] About to call coordinator.run(event='rep_completed') ...")

        result = coordinator.run(
            exercise_type=exercise,
            metrics=latest_metrics,
            event="rep_completed",
        )

        print(f"[DEBUG] coordinator.run returned: {result}")
        _apply_feedback(result)

    # ── Set completed milestone ─────────────────────────────────────────────────
    if target_sets > 0 and reps_per_set > 0 and sets_completed > last_saved_sets:
        newly_completed = sets_completed - last_saved_sets
        now_ts = time.time()
        started_at = st.session_state.get("set_cycle_started_at", now_ts)
        time_taken = now_ts - started_at
        user_id = st.session_state.get("user_id", 0)

        # Persist via coordinator (Safety -> Coach -> Persist)
        if coordinator:
            result = coordinator.run(
                exercise_type=exercise,
                metrics=latest_metrics,
                event="set_completed",
                user_id=user_id,
                reps=newly_completed * reps_per_set,
                sets=newly_completed,
                duration=time_taken,
            )
            _apply_feedback(result)
        else:
            add_exercise(user_id, exercise, newly_completed * reps_per_set, newly_completed, time_taken)

        st.session_state.set_cycle_started_at = now_ts
        st.session_state.last_saved_sets_completed = sets_completed

    # ── Workout completed milestone ─────────────────────────────────────────────
    if workout_completed and not st.session_state.get("last_notified_workout_complete", False):
        st.session_state.last_notified_workout_complete = True

        if coordinator:
            result = coordinator.run(
                exercise_type=exercise,
                metrics=latest_metrics,
                event="workout_completed",
            )
            _apply_feedback(result)
