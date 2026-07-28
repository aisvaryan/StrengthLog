import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from src.engine import TrackerEngine
from src.analytics import AnalyticsEngine

# Configure the Streamlit page layout and title
st.set_page_config(
    page_title="StrengthLog Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_engine():
    return TrackerEngine()

engine = get_engine()

def main():
    # Sidebar
    with st.sidebar:
        st.title("🏋️ StrengthLog")
        st.write("Professional Gym Progression Tracker & Training Analytics.")
        st.divider()
        st.caption("© 2026 StrengthLog Analytics")

    # Tabs
    tab_dashboard, tab_log, tab_history, tab_about = st.tabs([
        "📊 Dashboard & Analytics", 
        "📝 Log Workout", 
        "📋 Workout History", 
        "ℹ️ About StrengthLog"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: DASHBOARD & ANALYTICS
    # ---------------------------------------------------------
    with tab_dashboard:
        history = engine.get_history()
        
        if history:
            analytics = AnalyticsEngine(history)
            df = pd.DataFrame(history)
            df['date'] = pd.to_datetime(df['date'])
            
            # --- Global Dashboard Summary Cards ---
            st.header("Training Overview")
            col1, col2, col3 = st.columns(3)
            
            # 1. Max Weight Lifted (Global PR)
            global_pr = df['weight'].max() if not df.empty else 0
            col1.metric("Max Weight Lifted (Overall)", f"{global_pr:g} lbs")
            
            # 2. Workouts This Month
            current_month = datetime.date.today().month
            current_year = datetime.date.today().year
            workouts_this_month = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]['date'].nunique()
            col2.metric("Workouts This Month", f"{workouts_this_month}")
            
            # 3. Total Training Volume (Global)
            total_global_volume = (df['weight'] * df['reps']).sum()
            col3.metric("Total Training Volume", f"{total_global_volume:g} lbs")
            
            st.divider()
            
            # --- Exercise-Specific Analytics ---
            st.header("Exercise Analytics")
            unique_exercises = sorted(df['exercise'].unique().tolist())
            selected_exercise = st.selectbox("Select Exercise to Analyze:", unique_exercises, key='analytics_exercise')
            
            # Show specific PR
            pr = analytics.get_personal_record(selected_exercise)
            st.metric(f"Current {selected_exercise} Personal Record", f"{pr:g} lbs")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Strength Progression")
                st.caption("Maximum weight lifted over time.")
                strength_df = analytics.get_strength_progression(selected_exercise)
                if not strength_df.empty:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(strength_df['date'], strength_df['weight'], marker='o', color='#1f77b4', linewidth=2)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Max Weight (lbs)")
                    ax.grid(True, linestyle='--', alpha=0.6)
                    st.pyplot(fig)
                else:
                    st.info("Not enough data to display progression.")
                    
            with col_chart2:
                st.subheader("Volume Progression")
                st.caption("Total volume (weight × reps) over time.")
                volume_df = analytics.get_volume_progression(selected_exercise) 
                if not volume_df.empty:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(volume_df['date'], volume_df['volume'], marker='o', color='#2ca02c', linewidth=2)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Total Volume (lbs)")
                    ax.grid(True, linestyle='--', alpha=0.6)
                    st.pyplot(fig)
                else:
                    st.info("Not enough data to display progression.")
            
            st.divider()
            
            # Plateau Detection
            st.subheader("Plateau Detection")
            st.caption("Analyzes recent sessions to detect stalled progress.")
            plateau_info = analytics.detect_plateau(selected_exercise)
            if plateau_info.get("is_plateau"):
                st.warning("⚠️ **Plateau Detected**")
                st.write(f"**Recommendation:** {plateau_info['recommendation']}")
                st.write(f"- **Current max:** {pr:g} lbs")
                st.write(f"- **Suggested deload weight:** {plateau_info['suggested_weight']:g} lbs")
            else:
                st.success("✅ **No plateau detected.** Keep progressing!")
                
        else:
            st.info("No workouts logged yet. Go to the 'Log Workout' tab to get started!")

    # ---------------------------------------------------------
    # TAB 2: LOG WORKOUT
    # ---------------------------------------------------------
    with tab_log:
        st.header("Log a Workout")
        
        with st.form("workout_form", clear_on_submit=True):
            date_input = st.date_input("Date", value=datetime.date.today())
            exercise = st.text_input("Exercise", placeholder="e.g. Bench Press")
            weight = st.number_input("Weight (lbs)", min_value=0.0, step=5.0, format="%.1f")
            reps = st.number_input("Reps", min_value=1, step=1)
            
            submitted = st.form_submit_button("Save Workout")
            
            if submitted:
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

    # ---------------------------------------------------------
    # TAB 3: WORKOUT HISTORY
    # ---------------------------------------------------------
    with tab_history:
        st.header("Workout History")
        
        history = engine.get_history()
        
        if history:
            df = pd.DataFrame(history)
            df = df.sort_values(by='date', ascending=False)
            
            unique_exercises = sorted(df['exercise'].unique().tolist())
            options = ["All Exercises"] + unique_exercises
            selected_exercise = st.selectbox("Filter by Exercise", options)
            
            if selected_exercise != "All Exercises":
                df = df[df['exercise'] == selected_exercise]
            
            display_df = df[['date', 'exercise', 'weight', 'reps']]
            display_df = display_df.rename(columns={
                'date': 'Date',
                'exercise': 'Exercise',
                'weight': 'Weight (lbs)',
                'reps': 'Reps'
            })
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No workouts logged yet. Start tracking your progress!")

    # ---------------------------------------------------------
    # TAB 4: ABOUT
    # ---------------------------------------------------------
    with tab_about:
        st.header("About StrengthLog")
        st.write("StrengthLog is a professional application designed to track training performance and systematically analyze progression trends. It helps athletes avoid guesswork by providing data-driven insights into volume, strength, and plateaus.")
        
        st.subheader("Technologies Used")
        st.markdown("""
        - **Python**: Core application logic and analytics.
        - **Streamlit**: Interactive and responsive web interface.
        - **SQLite**: Lightweight, persistent, and local data storage.
        - **Pandas**: Advanced data manipulation and aggregation.
        - **Matplotlib**: Data visualization and progression charting.
        """)

if __name__ == "__main__":
    main()