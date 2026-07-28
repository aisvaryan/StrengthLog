import pytest
import pandas as pd
from src.analytics import AnalyticsEngine

def test_calculate_volume():
    engine = AnalyticsEngine([])
    assert engine.calculate_volume(225, 5) == 1125

def test_get_personal_record():
    history = [
        {"date": "2026-07-20", "exercise": "Bench Press", "weight": 185, "reps": 5},
        {"date": "2026-07-22", "exercise": "Bench Press", "weight": 195, "reps": 5},
        {"date": "2026-07-24", "exercise": "Bench Press", "weight": 205, "reps": 5},
    ]
    engine = AnalyticsEngine(history)
    assert engine.get_personal_record("Bench Press") == 205
    assert engine.get_personal_record("Squat") == 0

def test_detect_plateau_true():
    history = [
        {"date": "2026-07-20", "exercise": "Bench Press", "weight": 185, "reps": 5},
        {"date": "2026-07-22", "exercise": "Bench Press", "weight": 190, "reps": 5},
        {"date": "2026-07-24", "exercise": "Bench Press", "weight": 190, "reps": 5},
        {"date": "2026-07-26", "exercise": "Bench Press", "weight": 190, "reps": 5},
    ]
    engine = AnalyticsEngine(history)
    result = engine.detect_plateau("Bench Press")
    assert result["is_plateau"] is True
    assert result["suggested_weight"] == 171.0

def test_detect_plateau_false():
    history = [
        {"date": "2026-07-20", "exercise": "Bench Press", "weight": 185, "reps": 5},
        {"date": "2026-07-22", "exercise": "Bench Press", "weight": 195, "reps": 5},
        {"date": "2026-07-24", "exercise": "Bench Press", "weight": 205, "reps": 5},
    ]
    engine = AnalyticsEngine(history)
    result = engine.detect_plateau("Bench Press")
    assert result["is_plateau"] is False
