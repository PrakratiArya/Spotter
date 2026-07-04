# AGENT SKILL: jumping jacks form analysis
from core.base_exercise import BaseExercise

class JumpingJacksDetector(BaseExercise):
    MIN_VISIBILITY = 0.7

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None
        self.rep_issue = None

    def process(self, landmarks) -> dict:
        l_wrist_y = landmarks[self.LEFT_WRIST].y
        r_wrist_y = landmarks[self.RIGHT_WRIST].y
        l_shoulder_y = landmarks[self.LEFT_SHOULDER].y
        r_shoulder_y = landmarks[self.RIGHT_SHOULDER].y
        
        l_ankle_x = landmarks[self.LEFT_ANKLE].x
        r_ankle_x = landmarks[self.RIGHT_ANKLE].x
        l_hip_x = landmarks[self.LEFT_HIP].x
        r_hip_x = landmarks[self.RIGHT_HIP].x

        # Calculate leg spread relative to hip width
        hip_width = abs(l_hip_x - r_hip_x)
        ankle_spread = abs(l_ankle_x - r_ankle_x)
        
        # Consider arms "up" if wrists are above shoulders (y is inverted, so wrist_y < shoulder_y)
        arms_up = (l_wrist_y < l_shoulder_y) and (r_wrist_y < r_shoulder_y)
        # Consider legs "out" if ankle spread is > 2x hip width (rough heuristic)
        legs_out = ankle_spread > (hip_width * 1.5)

        key_landmarks_visible = (
            landmarks[self.LEFT_WRIST].visibility > self.MIN_VISIBILITY and
            landmarks[self.RIGHT_WRIST].visibility > self.MIN_VISIBILITY and
            landmarks[self.LEFT_ANKLE].visibility > self.MIN_VISIBILITY and
            landmarks[self.RIGHT_ANKLE].visibility > self.MIN_VISIBILITY
        )

        if key_landmarks_visible:
            # Entering the "open" stage of the jack
            if arms_up and legs_out and self.stage != "open":
                self.stage = "open"
                self.rep_issue = None
            
            # Returning to "closed" stage completes a rep
            elif not arms_up and not legs_out and self.stage == "open":
                self.stage = "closed"
                self.reps += 1

            # Track form issues during the movement
            # If they move arms but not legs, or legs but not arms, we can flag it
            if self.stage == "open":
                if arms_up and not legs_out:
                    self.rep_issue = "LEGS NOT WIDE"
                elif legs_out and not arms_up:
                    self.rep_issue = "ARMS NOT HIGH"

        return {
            "reps": self.reps,
            "rep_issue": getattr(self, "rep_issue", None)
        }
