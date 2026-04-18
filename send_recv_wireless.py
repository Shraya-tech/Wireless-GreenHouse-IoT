import streamlit as st
import serial
import time

# --- DASHBOARD UI ---
st.set_page_config(page_title="Greenhouse Analytics", layout="wide")
st.title("🌱 Wireless Greenhouse Monitor")

# CONFIGURATION
# 1. Double check your Port in Arduino IDE (Tools > Port)
arduino_port = 'COM4' 
# 2. Must match the 115200 in your Receiver C++ code
baud_rate = 115200 

@st.cache_resource
def get_connection():
    try:
        # We use a 0.1s timeout to keep the UI smooth
        return serial.Serial(arduino_port, baud_rate, timeout=0.1)
    except Exception:
        return None

# Initialize Session State for the graph history
if 'history' not in st.session_state:
    st.session_state.history = []

ser = get_connection()

# --- UI CONTAINERS ---
col1, col2 = st.columns(2)
with col1:
    val_display = st.empty()
with col2:
    status_display = st.empty()

chart_display = st.empty()

if ser:
    st.success(f"Receiver Active on {arduino_port} (Listening at 115200 baud)")
    
    while True:
        try:
            if ser.in_waiting > 0:
                # 'errors=ignore' handles the 'garbage bytes' when David's board wakes up
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Matching your Receiver code: Serial.print("Received:");
                if "Received:" in line:
                    try:
                        # Extract the number after the colon
                        raw_val = line.split(":")[1]
                        value = int(raw_val)
                        
                        # Add to history
                        st.session_state.history.append(value)
                        if len(st.session_state.history) > 50:
                            st.session_state.history.pop(0)
                        
                        # Update Displays
                        val_display.metric("Soil Moisture", value)
                        
                        if value > 400:
                            status_display.error("STATUS: SOIL DRY - PUMPING")
                        else:
                            status_display.success("STATUS: MOISTURE OK")
                        
                        chart_display.line_chart(st.session_state.history)
                        
                    except (ValueError, IndexError):
                        continue
        except Exception as e:
            # If the port flickers, just keep trying
            continue
        
        time.sleep(0.01)
else:
    st.error(f"Waiting for Receiver Board... Check {arduino_port} and close Serial Monitor.")