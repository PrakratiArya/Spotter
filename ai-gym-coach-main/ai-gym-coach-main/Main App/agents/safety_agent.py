import os

class SafetyAgent:
    """
    Google ADK human-in-the-loop confirmation pattern.
    Receives Vision Tool Agent output. Pauses if form angle crosses dangerous threshold,
    or if user input contains "pain", "hurt", "injury".
    """
    def __init__(self):
        # Ensure no hardcoded API keys exist, read from environment
        self.api_key = os.getenv("API_KEY") 
        
        # Defining dangerous thresholds per exercise.
        # Rationale:
        # - Squat: knee angle < 45 might put excessive load on patellar tendon. back angle > 60 might indicate dangerous forward lean.
        # - Pushup: elbow angle > 190 means hyperextension, < 45 means too deep causing shoulder strain.
        # - Biceps Curl: elbow angle < 20 means excessive joint compression.
        # - Shoulder Press: elbow angle < 30 means excessive strain on shoulders at the bottom.
        # - Lunges: knee angle < 60 means excessive knee travel forward or deep lunge stressing the joint.
        self.thresholds = {
            "squat": {"min_knee": 45, "max_back": 60},
            "pushup": {"max_elbow": 190, "min_elbow": 45},
            "biceps_curl": {"min_elbow": 20},
            "shoulder_press": {"min_elbow": 30},
            "lunges": {"min_knee": 60}
        }
        
        self.danger_keywords = ["pain", "hurt", "injury"]

    def check_safety(self, exercise_type: str, vision_output: dict, user_text: str = "") -> bool:
        """
        Evaluates vision output and user text.
        Returns True if the execution should pause for human-in-the-loop confirmation.
        """
        # Check user text for pain keywords
        text_lower = user_text.lower()
        for word in self.danger_keywords:
            if word in text_lower:
                return True
                
        if "error" in vision_output:
            return False
            
        # Check form thresholds
        thresholds = self.thresholds.get(exercise_type)
        if not thresholds:
            return False
            
        if exercise_type == "squat":
            knee = vision_output.get("knee_angle", 180)
            back = vision_output.get("back_angle", 0)
            if knee < thresholds["min_knee"] or back > thresholds["max_back"]:
                return True
        elif exercise_type == "pushup":
            elbow = vision_output.get("elbow_angle", 180)
            if elbow > thresholds["max_elbow"] or elbow < thresholds["min_elbow"]:
                return True
        elif exercise_type in ["biceps_curl", "shoulder_press"]:
            elbow = vision_output.get("elbow_angle", 180)
            if elbow < thresholds["min_elbow"]:
                return True
        elif exercise_type == "lunges":
            knee = vision_output.get("knee_angle", 180)
            if knee < thresholds["min_knee"]:
                return True
                
        return False
        
    def prompt_human_confirmation(self):
        """
        Pauses execution using ADK's human-in-the-loop confirmation pattern.
        Waits for explicit user confirmation before continuing.
        """
        print("\n[SAFETY AGENT WARN] Dangerous form or pain detected!")
        while True:
            response = input("Do you wish to continue? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                print("Continuing execution...")
                return True
            elif response in ['no', 'n']:
                print("Execution paused for safety. Please rest.")
                return False
            else:
                print("Please answer yes or no.")
