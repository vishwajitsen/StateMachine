# pi_mission_tracker.py

import streamlit as st
from transitions import Machine
import uuid
import pandas as pd

# ----------------------------
# Define all mission states
# ----------------------------
states = [
    'Created', 'Assigned', 'In Progress', 'On Hold',
    'Under Review', 'Completed', 'Closed'
]

# ----------------------------
# Define transitions between states
# ----------------------------
transitions = [
    {'trigger': 'assign', 'source': 'Created', 'dest': 'Assigned'},
    {'trigger': 'start', 'source': 'Assigned', 'dest': 'In Progress'},
    {'trigger': 'pause', 'source': 'In Progress', 'dest': 'On Hold'},
    {'trigger': 'resume', 'source': 'On Hold', 'dest': 'In Progress'},
    {'trigger': 'submit_review', 'source': 'In Progress', 'dest': 'Under Review'},
    {'trigger': 'approve', 'source': 'Under Review', 'dest': 'Completed'},
    {'trigger': 'close', 'source': 'Completed', 'dest': 'Closed'}
]

# ----------------------------
# Mission class with FSM
# ----------------------------
class Mission:
    def __init__(self, title, description):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.state = 'Created'
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='Created')

# ----------------------------
# Initialize session state
# ----------------------------
if 'missions' not in st.session_state:
    st.session_state.missions = {}

st.set_page_config(page_title="PI Mission Tracker", layout="wide")
st.title("🔎 PI Mission Tracker – State Machine Workflow")

# ----------------------------
# Display state transition diagram
# ----------------------------
with st.expander("📌 Mission Workflow Diagram"):
    st.graphviz_chart("""
        digraph {
            Created -> Assigned
            Assigned -> "In Progress"
            "In Progress" -> "On Hold"
            "On Hold" -> "In Progress" [label="Resume"]
            "In Progress" -> "Under Review"
            "Under Review" -> Completed
            Completed -> Closed
        }
    """)

# ----------------------------
# Add a new mission form
# ----------------------------
st.markdown("### ➕ Add a New Mission")

with st.form("add_mission"):
    title = st.text_input("Mission Title")
    description = st.text_area("Mission Description")
    create = st.form_submit_button("Create Mission")
    if create and title.strip():
        new_mission = Mission(title.strip(), description.strip())
        st.session_state.missions[new_mission.id] = new_mission
        st.success(f"✅ Mission '{title}' created successfully!")

# ----------------------------
# Manage existing missions
# ----------------------------
st.markdown("---")
st.markdown("### 📋 Manage Missions")

if not st.session_state.missions:
    st.info("No missions created yet.")
else:
    selected_id = st.selectbox(
        "Select Mission to Manage:",
        options=list(st.session_state.missions.keys()),
        format_func=lambda x: f"{st.session_state.missions[x].title} ({x})"
    )

    mission = st.session_state.missions[selected_id]

    st.subheader(f"🎯 {mission.title}")
    st.markdown(f"**Description:** {mission.description}")
    st.markdown(f"**Current State:** `{mission.state}`")

    st.markdown("#### 🔄 Available Transitions")

    col1, col2, col3, col4 = st.columns(4)
    triggered = False

    # Column 1
    with col1:
        if st.button("Assign", key=f"assign_{mission.id}", disabled=mission.state != 'Created'):
            mission.assign()
            triggered = True

        if st.button("Start", key=f"start_{mission.id}", disabled=mission.state != 'Assigned'):
            mission.start()
            triggered = True

    # Column 2
    with col2:
        if st.button("Pause", key=f"pause_{mission.id}", disabled=mission.state != 'In Progress'):
            mission.pause()
            triggered = True

        if st.button("Resume", key=f"resume_{mission.id}", disabled=mission.state != 'On Hold'):
            mission.resume()
            triggered = True

    # Column 3
    with col3:
        if st.button("Submit for Review", key=f"review_{mission.id}", disabled=mission.state != 'In Progress'):
            mission.submit_review()
            triggered = True

        if st.button("Approve Review", key=f"approve_{mission.id}", disabled=mission.state != 'Under Review'):
            mission.approve()
            triggered = True

    # Column 4
    with col4:
        if st.button("Close Mission", key=f"close_{mission.id}", disabled=mission.state != 'Completed'):
            mission.close()
            triggered = True

    if triggered:
        st.success(f"🔁 Mission '{mission.title}' transitioned to `{mission.state}`.")

# ----------------------------
# Show all missions table
# ----------------------------
st.markdown("---")
st.markdown("### 📊 All Missions Summary")

if st.session_state.missions:
    df = pd.DataFrame([
        {
            "ID": m.id,
            "Title": m.title,
            "Description": m.description,
            "Current State": m.state
        }
        for m in st.session_state.missions.values()
    ])
    st.dataframe(df, use_container_width=True)
