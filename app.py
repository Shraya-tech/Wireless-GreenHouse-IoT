import streamlit as st
import serial
import time

st.set_page_config(page_title="Greenhouse Dashboard", layout="wide")
st.title("🌱 Smart Irrigation Dashboard")

# Ensure this is COM4
arduino_port = 'COM4' 

@st.cache_resource
def get_serial_connection():
    try:
        # Open the connection ONCE and keep it open
        ser = serial.Serial(arduino_port, 9600, timeout=0.1) 
        return ser
    except:
        return None

ser = get_serial_connection()

# Containers for the UI
val_display = st.empty()
status_display = st.empty()
chart_display = st.empty()

if 'history' not in st.session_state:
    st.session_state.history = []

if ser:
    st.success(f"Connected to {arduino_port}")
    while True:
        try:
            if ser.in_waiting > 0:
                # The 'errors=ignore' prevents the glitching/crashing
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if "DATA:" in line:
                    value = int(line.split(":")[1])
                    st.session_state.history.append(value)
                    
                    if len(st.session_state.history) > 30:
                        st.session_state.history.pop(0)
                        
                    val_display.metric("Soil Moisture Level", value)
                    
                    if value > 400:
                        status_display.error("STATUS: SOIL DRY - PUMPING WATER")
                    else:
                        status_display.success("STATUS: SOIL MOISTURE OK")
                        
                    chart_display.line_chart(st.session_state.history)
        except:
            continue
        time.sleep(0.01) # Very small sleep to stay smooth
else:
    st.error(f"Could not open {arduino_port}. Is the Serial Monitor open in Arduino IDE?")