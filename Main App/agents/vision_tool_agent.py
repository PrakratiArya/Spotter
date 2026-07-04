import json
from skills.squat import SquatDetector
from skills.pushup import PushUpDetector
from skills.biceps_curl import BicepsCurlDetector
from skills.shoulder_press import ShoulderPressDetector
from skills.lunges import LungesDetector
from skills.plank import PlankDetector
from skills.jumping_jacks import JumpingJacksDetector

class VisionToolAgent:
    """
    Google ADK Custom Tool pattern implementation.
    This agent takes pose landmark data, calls the correct skill file based on the selected exercise,
    and returns a structured JSON (angles, rep count, form status) deterministically without LLM.
    """
    def __init__(self):
        # Instantiate all detectors as deterministic skills
        self._skills = {
            "squat": SquatDetector(),
            "pushup": PushUpDetector(),
            "biceps_curl": BicepsCurlDetector(),
            "shoulder_press": ShoulderPressDetector(),
            "lunges": LungesDetector(),
            "plank": PlankDetector(),
            "jumping_jacks": JumpingJacksDetector()
        }

    def process_frame(self, exercise_type: str, landmarks):
        """
        Processes a single frame's landmarks deterministically using the selected exercise skill.
        Returns a structured dictionary (JSON-like).
        """
        skill = self._skills.get(exercise_type)
        if not skill:
            return {"error": f"Unknown exercise type: {exercise_type}"}
        
        # Delegate to the appropriate deterministic skill
        result = skill.process(landmarks)
        
        return result
