import streamlit as st
import datetime
import pandas as pd
from utils import get_ai_tip, load_data, save_data

# Set page configuration for a wider, more professional layout
st.set_page_config(page_title="Gym Tracker", layout="wide")
st.title("🏋️ My Gym Tracker")

# Load persistent data from the JSON file
data = load_data()

# Initialize Streamlit session state for the current active workout
if 'current_workout' not in st.session_state:
    st.session_state.current_workout = []

# --- SIDEBAR: INPUT FORM ---
with st.sidebar:
    st.header("Add Exercise")
    selected_date = st.date_input("Workout Date", datetime.date.today())
    
    # Extract exercise names from the routine, and add a fallback option
    routine_names = [ex["name"] for ex in data.get("routine", [])]
    routine_names.append("Other / Custom")
    
    # clear_on_submit=True resets the form automatically after submission
    with st.form("exercise_form", clear_on_submit=True):
        selected_exercise = st.selectbox("Choose Exercise", routine_names)
        
        if selected_exercise == "Other / Custom":
            exercise_name = st.text_input("Custom Exercise Name")
        else:
            exercise_name = selected_exercise
            
        target_reps = st.number_input("Target Reps", min_value=1, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5)
        actual_reps = st.number_input("Actual Reps Done", min_value=0, step=1)
        
        submit_button = st.form_submit_button("➕ Add to Workout", use_container_width=True)
        
    if submit_button:
        if exercise_name:
            st.session_state.current_workout.append({
                "name": exercise_name, "target_reps": int(target_reps),
                "weight": float(weight), "actual_reps": int(actual_reps)
            })
            # Clear any old AI tips to prevent UI confusion when a new workout starts
            if 'last_tip' in st.session_state:
                del st.session_state.last_tip
        else:
            st.error("Please enter an exercise name.")

# --- MAIN PAGE: TABS ---
tab1, tab2, tab3 = st.tabs(["📝 Current Session", "📜 History Grid", "⚙️ My Routine"])

# --- TAB 1: CURRENT SESSION ---
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Today's Session")
        if st.session_state.current_workout:
            # Convert data to a Pandas DataFrame for grid display
            df_current = pd.DataFrame(st.session_state.current_workout)
            
            # Map internal database keys to user-friendly column names
            display_map = {"name": "Exercise", "target_reps": "Target Reps", "weight": "Weight (kg)", "actual_reps": "Actual Reps"}
            df_display = df_current.rename(columns=display_map)
            
            # Render grid (num_rows="fixed" prevents users from adding empty rows)
            edited_df = st.data_editor(df_display, use_container_width=True, hide_index=True, num_rows="fixed")
            
            # Map column names back to internal keys before saving to state
            reverse_map = {v: k for k, v in display_map.items()}
            st.session_state.current_workout = edited_df.rename(columns=reverse_map).to_dict('records')

            # Custom Delete UI
            st.divider()
            with st.form("delete_current_form"):
                # Enumerating options handles cases where the same exercise is added multiple times
                options = {f"{ex['name']}": i for i, ex in enumerate(st.session_state.current_workout)}
                selected_to_delete = st.selectbox("Select exercise to remove from today:", list(options.keys()))
                delete_current_btn = st.form_submit_button("🗑️ Delete from Session")
                
            if delete_current_btn:
                idx_to_remove = options[selected_to_delete]
                st.session_state.current_workout.pop(idx_to_remove)
                st.rerun()

        else:
            st.info("No exercises added yet. Use the sidebar to add exercises.")
            
    with col2:
        st.subheader("Finish Workout")
        if st.button("Finish & Save Workout", type="primary", use_container_width=True):
            if st.session_state.current_workout:
                date_str = selected_date.isoformat()
                
                # MERGER LOGIC: Check if a session for this date already exists
                session_found = False
                for session in data["sessions"]:
                    if session["date"] == date_str:
                        # Append to existing date rather than creating a duplicate entry
                        session["exercises"].extend(st.session_state.current_workout)
                        session_found = True
                        break
                
                # If no session exists for this date, create a new one
                if not session_found:
                    new_session = {"date": date_str, "exercises": st.session_state.current_workout}
                    data["sessions"].append(new_session)
                
                save_data(data)
                
                # Stash data for the AI coach before clearing the active session
                st.session_state.workout_to_analyze = st.session_state.current_workout
                st.session_state.current_workout = []
                st.rerun()
            else:
                st.error("Add at least one exercise first.")

        # --- AI STREAMING FLOW ---
        if 'workout_to_analyze' in st.session_state:
            st.success("✅ Workout saved to history!")
            
            if st.button("🤖 Ask Coach for Tip", use_container_width=True):
                stream_placeholder = st.empty()
                
                # Stream the text visually
                full_response = stream_placeholder.write_stream(
                    get_ai_tip(
                        str(st.session_state.workout_to_analyze), 
                        data["sessions"]
                    )
                )
                
                # Save final response and clear the queue
                st.session_state.last_tip = full_response
                del st.session_state.workout_to_analyze 
                
                # Force rerun to replace the streaming text with the clean final UI box
                st.rerun()

        # Display the finalized AI tip
        if 'last_tip' in st.session_state:
            st.info(f"🤖 **Coach's Tip:** {st.session_state.last_tip}")


# --- TAB 2: HISTORY GRID ---
with tab2:
    st.subheader("📜 Workout History")
    if data["sessions"]:
        # Remove duplicate dates while preserving chronological order
        all_dates = [session["date"] for session in reversed(data["sessions"])]
        unique_dates = list(dict.fromkeys(all_dates))[:30] # Limit to last 30 unique days for performance
        
        selected_past_date = st.selectbox("Select a date to view:", unique_dates)
        
        # Gather ALL exercises across any sessions matching the selected date
        exercises_for_date = []
        for session in data["sessions"]:
            if session["date"] == selected_past_date:
                exercises_for_date.extend(session["exercises"])
                
        # Render the aggregated history grid
        if exercises_for_date:
            df_history = pd.DataFrame(exercises_for_date)
            display_map = {"name": "Exercise", "target_reps": "Target Reps", "weight": "Weight (kg)", "actual_reps": "Actual Reps"}
            df_history = df_history.rename(columns=display_map)
            st.dataframe(df_history, use_container_width=True, hide_index=True)
    else:
        st.info("No past workouts recorded yet.")

# --- TAB 3: ROUTINE ---
with tab3:
    st.subheader("⚙️ Manage Default Routine")
    col_r1, col_r2 = st.columns([1, 1])
    
    with col_r1:
        st.write("**Your Current Routine**")
        if data.get("routine"):
            df_routine = pd.DataFrame(data["routine"])
            df_routine.columns = ["Exercise", "Target Reps", "Weight (kg)"]
            st.dataframe(df_routine, use_container_width=True, hide_index=True)
            
            # Routine Deletion Logic
            st.divider()
            st.write("**Delete from Routine**")
            routine_names = [ex["name"] for ex in data["routine"]]
            with st.form("delete_routine_form"):
                exercise_to_delete = st.selectbox("Select exercise to remove", routine_names)
                delete_btn = st.form_submit_button("🗑️ Delete Exercise")
                
            if delete_btn:
                # Rebuild the list excluding the deleted exercise
                data["routine"] = [ex for ex in data["routine"] if ex["name"] != exercise_to_delete]
                save_data(data)
                st.success(f"Deleted {exercise_to_delete}!")
                st.rerun()
        else:
            st.info("No routine set yet.")
            
    with col_r2:
        st.write("**Add New to Routine**")
        with st.form("routine_form", clear_on_submit=True):
            new_routine_name = st.text_input("Exercise Name")
            new_routine_target = st.number_input("Default Target Reps", min_value=1, step=1)
            new_routine_weight = st.number_input("Default Weight", min_value=0.0, step=2.5)
            add_routine_btn = st.form_submit_button("Add to Routine")
            
        if add_routine_btn and new_routine_name:
            data["routine"].append({
                "name": new_routine_name, "target_reps": int(new_routine_target), "weight": float(new_routine_weight)
            })
            save_data(data)
            st.rerun()