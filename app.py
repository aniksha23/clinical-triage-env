import streamlit as st
import time

# 1. Setup the Page (Must be wide for 3 columns)
st.set_page_config(layout="wide", page_title="Clinical Triage AI", page_icon="🏥")

# Custom CSS for the Terminal look
st.markdown("""
<style>
    .terminal {
        background-color: #0e1117;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border-radius: 5px;
        height: 500px;
        overflow-y: auto;
        border: 1px solid #333;
    }
    .metric-card {
        background-color: #1e1e2e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 Clinical Triage AI: Live Evaluation")

# 2. Session State Initialization (Holds our data between clicks)
if "logs" not in st.session_state:
    st.session_state.logs = ["> Environment Initialized. Agent Online."]
if "current_reward" not in st.session_state:
    st.session_state.current_reward = 0.0

# Mock Patient Data (Replace with your env.reset() data later)
patients = [
    {"id": "P1", "desc": "58M, 'Chest heaviness'", "wait": "10 mins", "hidden": "Anterior MI (ST Elev)"},
    {"id": "P2", "desc": "24F, 'Feeling down'", "wait": "45 mins", "hidden": "Active suicidal ideation"},
    {"id": "P3", "desc": "25M, 'Ankle hurts'", "wait": "120 mins", "hidden": "Simple Sprain (Level 5)"}
]

# 3. Build the 3-Column Layout
col1, col2, col3 = st.columns([1, 1.5, 1]) # Make terminal slightly wider

# ==========================================
# COLUMN 1: The Waiting Room (State)
# ==========================================
with col1:
    st.subheader("👥 The Waiting Room")
    st.caption("What the agent sees")
    
    for p in patients:
        with st.container(border=True):
            st.markdown(f"**Patient {p['id']}** | Wait: {p['wait']}")
            st.markdown(f"*{p['desc']}*")

# ==========================================
# COLUMN 2: The Live Terminal (Agent Brain)
# ==========================================
with col2:
    st.subheader("💻 Live Terminal")
    st.caption("Agent action stream")
    
    # Render the logs inside our custom CSS div
    log_text = "<br>".join(st.session_state.logs)
    st.markdown(f'<div class="terminal">{log_text}</div>', unsafe_allow_html=True)

    # The Engine: Connect to your inference here!
    if st.button("⚡ Run Next Agent Action", type="primary", use_container_width=True):
        
        # --- REPLACE THIS BLOCK WITH YOUR ACTUAL INFERENCE ---
        # e.g., response = requests.post("your-hf-space-url/step", json={"obs": current_obs})
        # action = response.json()
        
        # Simulating an API call/inference delay
        with st.spinner("Agent is reasoning..."):
            time.sleep(0.8)
        
        # Mocking an action for the UI
        new_log = "> Agent asks: check_ecg(patient='P1')"
        env_response = "> Env returns: ST Elevation detected. Reward: +0.30"
        
        # Update State
        st.session_state.logs.append(new_log)
        st.session_state.logs.append(env_response)
        st.session_state.current_reward += 0.30
        
        # Force a UI refresh
        st.rerun()

# ==========================================
# COLUMN 3: The Judge's View (Hidden Truth)
# ==========================================
with col3:
    st.subheader("👁️ The Judge's View")
    st.caption("Ground truth & Evaluation")
    
    # Big Reward Metric
    st.markdown(f"""
        <div class="metric-card">
            <h3>Episode Reward</h3>
            <h1 style="color: {'#00ff00' if st.session_state.current_reward > 0 else '#ff4b4b'};">
                {st.session_state.current_reward:+.2f}
            </h1>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    # Cheat Sheet
    st.markdown("**🔍 Ground Truth (Cheat Sheet)**")
    for p in patients:
        with st.expander(f"Reveal Patient {p['id']}"):
            st.error(f"**Hidden Risk:** {p['hidden']}")
            st.caption("If the agent misses this, it receives a severe penalty.")