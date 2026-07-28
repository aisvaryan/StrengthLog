from src.database import DatabaseManager

class TrackerEngine:
    def __init__(self, db_path: str = "data/strengthlog.db"):
        """
        Initialize the Engine layer. 
        It creates an instance of DatabaseManager, ensuring the database is initialized.
        """
        self.db = DatabaseManager(db_path)

    def log_workout(self, date: str, exercise: str, weight: float, reps: int):
        """
        Record a workout through the database layer.
        This is where business validation (e.g. weight > 0) would typically go.
        """
        if weight < 0 or reps < 0:
            raise ValueError("Weight and reps cannot be negative.")
            
        workout_id = self.db.add_workout(date, exercise, weight, reps)
        return {
            "status": "success",
            "workout_id": workout_id,
            "message": f"Successfully logged {reps} reps of {exercise} at {weight} lbs."
        }

    def get_history(self):
        """
        Retrieve workout history by querying the database layer.
        """
        return self.db.get_workouts()

    def get_personal_record(self, exercise: str):
        """
        Find the highest weight achieved for a specific exercise.
        We do this in python by filtering the history, keeping SQL out of this layer.
        """
        history = self.get_history()
        
        # Filter workouts to only the requested exercise (case-insensitive)
        exercise_workouts = [
            w for w in history 
            if w['exercise'].lower() == exercise.lower()
        ]
        
        if not exercise_workouts:
            return 0
            
        # Find the maximum weight from the filtered list
        max_weight = max(w['weight'] for w in exercise_workouts)
        return max_weight

    def calculate_volume(self, weight: float, reps: int):
        """
        Calculate training volume (weight * reps).
        This is purely business logic/math and doesn't involve the database.
        """
        return weight * reps