import time
from services.persistence.exercise_repository import get_users_exercises
from services.coaching.llm import LLMCoach, MODELS_TO_TRY, get_working_model_name, set_working_model_name

class ProgramAgent:
    """
    Google ADK LoopAgent pattern implementation.
    This agent retrieves historical workout data, loops through the exercises, and uses the 
    LLMCoach to generate a suggested program adjustment for the following week.
    
    Design Choice: The LoopAgent pattern separates retrospective analysis from real-time coaching. 
    By pulling aggregate history, it can make long-term decisions without cluttering the real-time sequential pipeline.
    """
    def __init__(self, llm_coach: LLMCoach):
        self.llm_coach = llm_coach

    def generate_weekly_review(self, user_id: int) -> str:
        """
        Loops over a user's exercise history and creates a rule-based weekly report without API calls.
        """
        history_rows = get_users_exercises(user_id)
        if not history_rows:
            return "No workout history found. Get started with a new workout!"

        total_reps = 0
        total_sets = 0
        total_time = 0
        exercises_done = {}
        
        for row in history_rows:
            ex_name = row['exercise_name']
            reps = row['reps']
            sets = row['sets']
            time_spent = row['time']
            
            total_reps += reps
            total_sets += sets
            total_time += time_spent
            
            if ex_name not in exercises_done:
                exercises_done[ex_name] = {"reps": 0, "sets": 0, "time": 0}
            
            exercises_done[ex_name]["reps"] += reps
            exercises_done[ex_name]["sets"] += sets
            exercises_done[ex_name]["time"] += time_spent

        if not exercises_done:
            return "No workout data to report on yet."

        exercise_count = len(exercises_done)
        
        # Find most practiced exercise by total reps
        top_exercise = max(exercises_done.keys(), key=lambda ex: exercises_done[ex]["reps"])
                
        time_str = f"{int(total_time // 60)}m {int(total_time % 60)}s" if total_time > 0 else "N/A"
        
        report = (
            f"This week you completed {total_sets} sets across {exercise_count} exercises, "
            f"totaling {total_reps} reps. Your most practiced exercise was {top_exercise}. "
            f"Total time spent: {time_str}. Keep up the consistency!\n\n"
            "Detailed Breakdown:\n"
        )
        
        for ex, stats in exercises_done.items():
            ex_time_str = f"{int(stats['time'] // 60)}m {int(stats['time'] % 60)}s" if stats['time'] > 0 else "0s"
            report += f"- {ex}: {stats['sets']} sets, {stats['reps']} reps ({ex_time_str})\n"
            
        return report
