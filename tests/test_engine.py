import pytest
import os
from src.engine import TrackerEngine

# We use a pytest fixture to handle setup and teardown automatically
@pytest.fixture
def engine():
    test_db_path = 'data/test_engine.db'
    
    # Setup: Initialize TrackerEngine with a test database
    eng = TrackerEngine(db_path=test_db_path)
    
    # Yield pauses the fixture, allowing the test to run and access the 'eng' object
    yield eng
    
    # Teardown: Cleanup the test database after the test finishes
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_log_workout(engine):
    # Attempt to log a single workout
    result = engine.log_workout("2026-07-28", "Bench Press", 135, 5)
    
    # Assertions to verify it worked
    assert result['status'] == "success"
    assert 'workout_id' in result


def test_get_history(engine):
    # Log multiple workouts
    engine.log_workout("2026-07-26", "Bench Press", 135, 5)
    engine.log_workout("2026-07-27", "Bench Press", 185, 5)
    engine.log_workout("2026-07-28", "Bench Press", 225, 5)
    
    # Retrieve the history
    history = engine.get_history()
    
    # Assertions to verify retrieval
    assert len(history) == 3
    assert history[0]['exercise'] == "Bench Press"


def test_personal_record(engine):
    # Log workouts with varying weights
    engine.log_workout("2026-07-26", "Bench Press", 135, 5)
    engine.log_workout("2026-07-27", "Bench Press", 185, 5)
    engine.log_workout("2026-07-28", "Bench Press", 225, 5)
    
    # Get the personal record
    pr = engine.get_personal_record("Bench Press")
    
    # Assert PR is the maximum weight
    assert pr == 225


def test_calculate_volume(engine):
    # Calculate volume based on math
    volume = engine.calculate_volume(225, 5)
    
    # Assert math is correct
    assert volume == 1125

def test_log_workout_manual_date(engine):
    # Test that the date provided by the user is the one stored
    engine.log_workout("2026-07-20", "Squat", 315, 3)
    history = engine.get_history()
    
    # Find the Squat workout
    squat_workout = next(w for w in history if w['exercise'] == "Squat")
    assert squat_workout['date'] == "2026-07-20"