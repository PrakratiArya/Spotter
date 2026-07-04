# AGENT SKILL: plank form analysis
from core.base_exercise import BaseExercise

class PlankDetector(BaseExercise):
    MIN_VISIBILITY = 0.7
    HIP_SAG_TOLERANCE = 0.08

    LEFT_SHOULDER = 11
    LEFT_HIP = 23
    LEFT_ANKLE = 27
    RIGHT_SHOULDER = 12
    RIGHT_HIP = 24
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self.reps = 0
        self.stage = "hold"
        self.rep_issue = None
        self._frames_held = 0

    def process(self, landmarks) -> dict:
        left_vis = landmarks[self.LEFT_HIP].visibility
        right_vis = landmarks[self.RIGHT_HIP].visibility

        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            hip_idx = self.LEFT_HIP
            ankle_idx = self.LEFT_ANKLE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            hip_idx = self.RIGHT_HIP
            ankle_idx = self.RIGHT_ANKLE

        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )

        shoulder_y = landmarks[shoulder_idx].y
        ankle_y = landmarks[ankle_idx].y
        hip_y = landmarks[hip_idx].y

        expected_hip_y = (shoulder_y + ankle_y) / 2
        hip_deviation = hip_y - expected_hip_y

        key_landmarks_visible = landmarks[shoulder_idx].visibility > self.MIN_VISIBILITY and landmarks[hip_idx].visibility > self.MIN_VISIBILITY and landmarks[ankle_idx].visibility > self.MIN_VISIBILITY

        if body_angle > 160:
            body_alignment = "Straight"
        elif body_angle > 140:
            body_alignment = "Slight Bend"
        else:
            body_alignment = "Poor Form"

        if abs(hip_deviation) <= self.HIP_SAG_TOLERANCE:
            hip_status = "LEVEL"
        elif hip_deviation > self.HIP_SAG_TOLERANCE:
            hip_status = "SAGGING"
        else:
            hip_status = "PIKED UP"

        if key_landmarks_visible:
            # For a hold exercise, we might increment reps artificially to trigger feedback,
            # or just track frames. The user requested we follow the exact same pattern:
            self._frames_held += 1
            if self._frames_held > 30: # artificially complete a 'rep' every ~1 second of hold
                self.reps += 1
                self._frames_held = 0
                self.rep_issue = None

            # Track worst issue during this hold block
            if body_alignment == "Poor Form":
                self.rep_issue = "Poor Form"
            elif hip_status in ["SAGGING", "PIKED UP"] and getattr(self, "rep_issue", None) != "Poor Form":
                self.rep_issue = hip_status

        return {
            "reps": self.reps,
            "body_alignment": body_alignment,
            "hip_status": hip_status,
            "rep_issue": getattr(self, "rep_issue", None)
        }
