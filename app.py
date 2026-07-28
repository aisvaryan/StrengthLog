import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from src.engine import TrackerEngine
from src.analytics import AnalyticsEngine

# Configure the Streamlit page layout and title
st.set_page_config(
    page_title="StrengthLog",
    layout="wide"
)

# Initialize the TrackerEngine. 
# We use @st.cache_resource so the engine (and database connection) 
# is created once and reused across different page reloads.
@st.cache_resource
def get_engine():
    return TrackerEngine()

engine = get_engine()

def main():
    # Create Sidebar
    with st.sidebar:
        st.title("StrengthLog")
        st.write("Track workouts, strength progression, and personal records.")

    tab1, tab2, tab3 = st.tabs(["Log Workout", "Workout History", "Analytics"])
    
    with tab1:
        # Main Page Title
        st.header("Log a Workout")
        
        # Create workout input section using a form
        # Forms allow us to batch user input together until the save button is clicked
        with st.form("workout_form", clear_on_submit=True):
            # Date input defaulting to today
            date_input = st.date_input("Date", value=datetime.date.today())
            
            # Exercise input MUST be free text to allow for any exercise to be tracked
            exercise = st.text_input("Exercise", placeholder="e.g. Romanian Deadlift")
            
            # Weight numeric input
            weight = st.number_input("Weight (lbs)", min_value=0.0, step=5.0, format="%.1f")
            
            # Reps numeric input
            reps = st.number_input("Reps", min_value=1, step=1)
            
            # Save Button
            submitted = st.form_submit_button("Save Workout")
            
            if submitted:
                # 1. Input Validation
                is_valid = True
                
                if not exercise or not exercise.strip():
                    st.error("Please enter an exercise name.")
                    is_valid = False
                    
                if weight <= 0:
                    st.error("Weight must be greater than zero.")
                    is_valid = False
                    
                if reps < 1:
                    st.error("Reps must be at least 1.")
                    is_valid = False
                    
                # Only save if all validation passes
                if is_valid:
                    try:
                        engine.log_workout(
                            date=date_input.strftime("%Y-%m-%d"),
                            exercise=exercise.strip(),
                            weight=float(weight),
                            reps=int(reps)
                        )
                        st.success("Workout saved successfully!")
                    except Exception as e:
                        st.error(f"Failed to save workout: {e}")

    with tab2:
        # Display workout history
        st.header("Workout History")
        
        # Retrieve the history strictly through the Engine Layer
        history = engine.get_history()
        
        if history:
            # Convert history dictionary to a pandas DataFrame for a clean table view
            df = pd.DataFrame(history)
            
            # Sort by date descending
            df = df.sort_values(by='date', ascending=False)
            
            # Filter by exercise
            unique_exercises = sorted(df['exercise'].unique().tolist())
            options = ["All Exercises"] + unique_exercises
            selected_exercise = st.selectbox("Filter by Exercise", options)
            
            if selected_exercise != "All Exercises":
                df = df[df['exercise'] == selected_exercise]
            
            # Select the desired columns
            display_df = df[['date', 'exercise', 'weight', 'reps']]
            
            # Rename the columns for display purposes
            display_df = display_df.rename(columns={
                'date': 'Date',
                'exercise': 'Exercise',
                'weight': 'Weight',
                'reps': 'Reps'
            })
            
            # Use Streamlit's dataframe component to render a clean, interactive table
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No workouts logged yet. Start tracking your progress!")

    with tab3:
        st.header("Analytics Dashboard")
        
        history = engine.get_history()
        
        if history:
            analytics = AnalyticsEngine(history)
            
            # Exercise selector for analytics
            df = pd.DataFrame(history)
            unique_exercises = sorted(df['exercise'].unique().tolist())
            selected_exercise = st.selectbox("Select Exercise for Analysis", unique_exercises, key='analytics_exercise')
            
            # Display Metrics
            col1, col2 = st.columns(2)
            pr = analytics.get_personal_record(selected_exercise)
            with col1:
                st.metric("Personal Record", f"{pr} lbs")
                
            # Total volume for the selected exercise
            ex_df = df[df['exercise'] == selected_exercise]
            total_vol = (ex_df['weight'] * ex_df['reps']).sum()
            with col2:
                st.metric("Total Training Volume", f"{total_vol} lbs")
            
            # Strength Progression Chart
            st.subheader("Strength Progression")
            strength_df = analytics.get_strength_progression(selected_exercise)
            if not strength_df.empty:
                fig, ax = plt.subplots()
                ax.plot(strength_df['date'], strength_df['weight'], marker='o')
                ax.set_xlabel("Date")
                ax.set_ylabel("Max Weight (lbs)")
                ax.set_title(f"{selected_exercise} Strength Progression")
                st.pyplot(fig)
            else:
                st.info("Not enough data for strength progression.")
                
            # Volume Progression Chart
            st.subheader("Volume Progression")
            volume_df = analytics.get_volume_progression(selected_exercise) 
            if not volume_df.empty:
                fig, ax = plt.subplots()
                ax.plot(volume_df['date'], volume_df['volume'], marker='o', color='green')
                ax.set_xlabel("Date")
                ax.set_ylabel("Total Volume (lbs)")
                ax.set_title("Overall Volume Progression")
                st.pyplot(fig)
            
            # Plateau Detection
            st.subheader("Plateau Detection")
            plateau_info = analytics.detect_plateau(selected_exercise)
            if plateau_info.get("is_plateau"):
                st.warning("Plateau detected")
                st.write(f"Recommendation: {plateau_info['recommendation']}")
                st.write(f"Current max: {pr} lbs")
                st.write(f"Suggested weight: {plateau_info['suggested_weight']} lbs")
            else:
                st.success("No plateau detected. Keep progressing!")
                
        else:
            st.info("No workouts logged yet. Start tracking to see analytics!")

if __name__ == "__main__":
    main()