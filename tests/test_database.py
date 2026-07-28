import os
from src.database import DatabaseManager

def main():
    # Use a specific test database file so we don't mess up production data
    db_path = 'data/test_strengthlog.db'
    
    # 1. Create a DatabaseManager instance 
    # 2. Create the SQLite database (happens inside __init__)
    print(f"Creating database at {db_path}...")
    db_manager = DatabaseManager(db_path)
    
    # 3. Add workout
    print("\nAdding workout: Bench Press, 225 lbs, 5 reps...")
    db_manager.add_workout(
        date="2026-07-28",
        exercise="Bench Press",
        weight=225,
        reps=5
    )
    
    # 4. Retrieve the workout
    print("\nRetrieving workouts...")
    workouts = db_manager.get_workouts()
    
    # 5. Print the result
    print("Workout Results:")
    for workout in workouts:
        print(f" - ID: {workout['workout_id']} | Date: {workout['date']} | {workout['exercise']} - {workout['weight']} lbs x {workout['reps']} reps")
        
    # 6. Verify that the data remains after closing and reopening the database connection
    print("\nVerifying data persistence by creating a new database connection...")
    
    # Creating a new instance simulates closing the app and reopening it
    new_db_manager = DatabaseManager(db_path)
    persisted_workouts = new_db_manager.get_workouts()
    
    print("Persisted Workout Results:")
    for workout in persisted_workouts:
        print(f" - ID: {workout['workout_id']} | Date: {workout['date']} | {workout['exercise']} - {workout['weight']} lbs x {workout['reps']} reps")

    if len(workouts) == len(persisted_workouts):
        print("\nSuccess: Data was successfully persisted and retrieved!")
    else:
        print("\nError: Data persistence failed!")
        
    # Clean up the test database so we start fresh next time
    print("\nCleaning up test database...")
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    main()
