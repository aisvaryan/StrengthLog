import sqlite3
from pathlib import Path
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/strengthlog.db"):
        """Initialize the DatabaseManager and ensure the database and tables exist."""
        self.db_path = db_path
        # Ensure the directory for the database exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        # Create tables if they don't exist
        self.create_tables()

    def _get_connection(self):
        """Helper method to get a database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        # Enable foreign key support in SQLite (disabled by default)
        conn.execute('PRAGMA foreign_keys = ON;')
        # Set row_factory to sqlite3.Row to get dictionary-like access to rows
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """Create the necessary database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # WORKOUTS table stores the top-level workout session
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS WORKOUTS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL
                )
            ''')
            
            # EXERCISES table stores unique exercises to avoid duplicate text data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS EXERCISES (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            
            # PERFORMANCES table links a workout and an exercise, storing the actual lift data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS PERFORMANCES (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workout_id INTEGER NOT NULL,
                    exercise_id INTEGER NOT NULL,
                    weight REAL NOT NULL,
                    reps INTEGER NOT NULL,
                    FOREIGN KEY (workout_id) REFERENCES WORKOUTS (id) ON DELETE CASCADE,
                    FOREIGN KEY (exercise_id) REFERENCES EXERCISES (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def add_workout(self, date: str, exercise: str, weight: float, reps: int):
        """Add a new workout, creating the exercise if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Handle the Exercise
            # Try to insert the exercise. If it already exists, IGNORE will prevent an error.
            cursor.execute('INSERT OR IGNORE INTO EXERCISES (name) VALUES (?)', (exercise,))
            # Fetch the ID of the exercise (whether it was just created or already existed)
            cursor.execute('SELECT id FROM EXERCISES WHERE name = ?', (exercise,))
            exercise_id = cursor.fetchone()['id']
            
            # 2. Handle the Workout Session
            cursor.execute('INSERT INTO WORKOUTS (date) VALUES (?)', (date,))
            workout_id = cursor.lastrowid # Get the ID of the newly inserted workout
            
            # 3. Handle the Performance
            # Link the workout and exercise with the specific weight and reps
            cursor.execute('''
                INSERT INTO PERFORMANCES (workout_id, exercise_id, weight, reps)
                VALUES (?, ?, ?, ?)
            ''', (workout_id, exercise_id, weight, reps))
            
            conn.commit()
            return workout_id

    def get_workouts(self):
        """Retrieve all workout history by joining tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Join WORKOUTS, PERFORMANCES, and EXERCISES to get a complete view
            cursor.execute('''
                SELECT 
                    w.id as workout_id,
                    w.date, 
                    e.name AS exercise, 
                    p.weight, 
                    p.reps
                FROM WORKOUTS w
                JOIN PERFORMANCES p ON w.id = p.workout_id
                JOIN EXERCISES e ON p.exercise_id = e.id
                ORDER BY w.date DESC
            ''')
            
            # Convert the Row objects to standard Python dictionaries
            return [dict(row) for row in cursor.fetchall()]

    def delete_workout(self, workout_id: int):
        """Safely delete a workout record by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Because we used ON DELETE CASCADE in our foreign keys,
            # deleting the workout here will automatically delete all related
            # records in the PERFORMANCES table as well!
            cursor.execute('DELETE FROM WORKOUTS WHERE id = ?', (workout_id,))
            conn.commit()