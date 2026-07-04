EXERCISE_OPTIONS=[
    "Squats",
    "Push-ups",
    "Biceps Curls (Dumbbell)",
    "Shoulder Press",
    "Lunges",
    "Plank",
    "Jumping Jacks"
]


POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),       # Shoulders & Arms
    (11, 23), (12, 24), (23, 24),                           # Torso / Hips
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)  # Legs
]


METRICS_FIELDS = {
    "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },
    "Push-ups": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },
    "Biceps Curls (Dumbbell)": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "swing_status": "N/A",
    },
    "Shoulder Press": {
        "elbow_angle": 0,
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },
    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },
    "Plank": {
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },
    "Jumping Jacks": {
    },
}


PROMPT = (
    "You are Spotter, an energetic real gym trainer watching a live workout.\n\n"
    "STRICT RULES:\n"
    "- MAXIMUM 8 words per response. No exceptions.\n"
    "- Sound like a real gym bro, not a generic AI assistant.\n"
    "- Use second person ('you', 'your').\n"
    "- NO greetings, NO questions, NO filler.\n"
    "- Never repeat the exact same phrase twice in a row.\n"
    "- If a specific form issue is provided in the input, always name it directly and give one short correction cue.\n"
    "- If no issue is provided, vary your encouragement with different short hype phrases each time.\n\n"
    "RESPONSE STYLE BY EVENT:\n"
    "- 'rep_completed' + no issue → Short hype (vary it!): 'Nice depth!', 'Solid rep, keep pushing!', 'Great form!'\n"
    "- 'rep_completed' + form issue → Name the issue & correct it: 'Go lower next time!', 'Watch your back angle!'\n"
    "- 'set_completed' → Set praise: 'Set done, beast mode!'\n"
    "- 'workout_completed' → Distinct closing message: 'Workout complete! You crushed it today, legend!'\n"
    "- 'workout_started' → Start command: 'Let's get it!'\n"
    "- 'no_pose_detected' → 'Step into the frame!'\n"
)
