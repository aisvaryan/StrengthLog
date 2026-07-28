import pandas as pd

class AnalyticsEngine:
    def __init__(self, history):
        """
        history is expected to be a list of workout dictionaries
        or a pandas DataFrame.
        """
        self.history = history
        if isinstance(history, list):
            self.df = pd.DataFrame(history)
        elif isinstance(history, pd.DataFrame):
            self.df = history
        else:
            self.df = pd.DataFrame()
        
        if not self.df.empty and 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df = self.df.sort_values(by='date')

    def get_personal_record(self, exercise: str):
        if self.df.empty:
            return 0
        ex_df = self.df[self.df['exercise'].str.lower() == exercise.lower()]
        if ex_df.empty:
            return 0
        return float(ex_df['weight'].max())

    def calculate_volume(self, weight: float, reps: int):
        return weight * reps

    def get_strength_progression(self, exercise: str):
        """
        Returns a DataFrame with date and max weight for the given exercise per day.
        """
        if self.df.empty:
            return pd.DataFrame()
        ex_df = self.df[self.df['exercise'].str.lower() == exercise.lower()]
        if ex_df.empty:
            return pd.DataFrame()
        
        # Max weight per date
        progression = ex_df.groupby(ex_df['date'].dt.date)['weight'].max().reset_index()
        progression.columns = ['date', 'weight']
        return progression

    def get_volume_progression(self, exercise: str):
        """
        Returns a DataFrame with date and total volume per day.
        """
        if self.df.empty:
            return pd.DataFrame()
        ex_df = self.df[self.df['exercise'].str.lower() == exercise.lower()]
        if ex_df.empty:
            return pd.DataFrame()
        ex_df = ex_df.copy()
        ex_df['volume'] = ex_df['weight'] * ex_df['reps']
        progression = ex_df.groupby(ex_df['date'].dt.date)['volume'].sum().reset_index()
        progression.columns = ['date', 'volume']
        return progression

    def detect_plateau(self, exercise: str):
        """
        Detects if the last 3 workouts for an exercise had the same max weight.
        Returns a dict:
        {"is_plateau": bool, "recommendation": str, "suggested_weight": float}
        """
        if self.df.empty:
            return {"is_plateau": False, "recommendation": "", "suggested_weight": None}
            
        ex_df = self.df[self.df['exercise'].str.lower() == exercise.lower()]
        if ex_df.empty:
            return {"is_plateau": False, "recommendation": "", "suggested_weight": None}
            
        # Group by date to get max weight per session
        daily_max = ex_df.groupby(ex_df['date'].dt.date)['weight'].max().reset_index()
        daily_max = daily_max.sort_values(by='date')
        
        if len(daily_max) < 3:
            return {"is_plateau": False, "recommendation": "", "suggested_weight": None}
            
        last_3 = daily_max['weight'].tail(3).tolist()
        
        # If the max weight of the last 3 sessions is identical, we have a plateau.
        if len(set(last_3)) == 1:
            current_weight = last_3[0]
            suggested_weight = round(current_weight * 0.9, 1)
            return {
                "is_plateau": True, 
                "recommendation": "Reduce training weight by 10%.", 
                "suggested_weight": suggested_weight
            }
        
        return {"is_plateau": False, "recommendation": "", "suggested_weight": None}