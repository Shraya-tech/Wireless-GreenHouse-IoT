# Decentralized Wireless IoT Greenhouse Ecosystem

**Developer:** Shraya Rajkarnikar | UNC Pembroke — IT / Data Analytics  
**Timeline:** January 2026 – April 2026  
**Stack:** Python · Streamlit · PySerial · C++ (Arduino/ESP32) · ESP-NOW · FreeCAD 1.0

---

## Overview

A full-stack IoT irrigation and environmental monitoring system built for a university greenhouse. The system progressed from a wired Arduino prototype to a fully decentralized wireless network using **ESP-NOW peer-to-peer communication** and **Deep Sleep power management** — feeding real-time soil moisture telemetry into a live Python analytics dashboard.

**Core pipeline:** Sense → Transmit (ESP-NOW) → Receive → Clean → Visualize

---

## System Architecture

```
┌─────────────────────────────┐     ESP-NOW 2.4GHz     ┌──────────────────────────────┐
│   REMOTE NODE (Sender)      │ ──────────────────────▶ │   GATEWAY (Receiver)         │
│                             │                         │                              │
│  ESP32 + 20-gauge probes    │                         │  ESP32 connected to laptop   │
│  Reads soil moisture (ADC)  │                         │  Forwards data via Serial    │
│  Transmits via ESP-NOW      │                         │  to Python dashboard         │
│  Deep Sleeps 10 min         │                         │                              │
└─────────────────────────────┘                         └──────────────┬───────────────┘
                                                                       │ PySerial (115200 baud)
                                                                       ▼
                                                        ┌──────────────────────────────┐
                                                        │   STREAMLIT DASHBOARD        │
                                                        │  Live moisture metric        │
                                                        │  Rolling 50-point chart      │
                                                        │  Dry/OK status alerts        │
                                                        └──────────────────────────────┘
```

---

## Repo Structure

```
/
├── firmware/
│   ├── Test_10sec.ino          # Remote node: sense, send, deep sleep (10s demo)
│   ├── sketch_jan28a.ino       # Gateway: ESP-NOW receiver, forwards to Serial
│   ├── sketch_feb9a.ino        # Wired ESP32 prototype (9600 baud)
│   └── switch.ino              # Original Arduino Uno wired proof-of-concept
├── dashboard/
│   ├── send_recv_wireless.py   # Wireless dashboard (115200 baud, ESP-NOW pipeline)
│   └── app.py                  # Wired prototype dashboard (9600 baud)
├── cad/
│   ├── funnel.FCStd            # Water delivery funnel
│   ├── funnel_base.FCStd       # Funnel mounting base
│   ├── funnelbaselid.FCStd     # Funnel base lid
│   ├── jar.FCStd               # ESP32 + battery waterproof enclosure
│   ├── jar_lid.FCStd           # Enclosure lid
│   └── laser.FCStd             # Laser tripwire security bracket
└── README.md
```

---

## Hardware Components

| Component | Role |
|---|---|
| ESP32 Dev Module (×2) | Sender node + Gateway receiver |
| 20-gauge copper wire probes | Soil conductivity sensing via ADC (GPIO 34) |
| Buck Converter | Voltage regulation — 3.3V/5V from battery source |
| LED (GPIO 2) | Visual dry-soil alert indicator |
| FreeCAD-designed enclosures | Moisture-resistant housing for outdoor deployment |

---

## Firmware

### 1. Remote Node — Sender with Deep Sleep (`Test_10sec.ino`)

The field node follows a **Sense → Send → Sleep** cycle for months of autonomous battery operation.

```cpp
void setup() {
    int sensorValue = analogRead(34);   // Read soil moisture via ADC
    Serial.print("DATA:");
    Serial.println(sensorValue);

    if (sensorValue > 800) {           // Dry soil alert
        digitalWrite(ledPin, HIGH);
        delay(3000);
        digitalWrite(ledPin, LOW);
    }

    // Deep Sleep — wake after 10 minutes (10s for demo)
    esp_sleep_enable_timer_wakeup(600 * uS_TO_S_FACTOR);
    esp_deep_sleep_start();
}
```

---

### 2. Gateway Receiver — ESP-NOW (`sketch_jan28a.ino`)

Stays connected to the laptop, catches ESP-NOW packets from the field node, pipes data to Python via Serial.

```cpp
void OnDataRecv(const uint8_t *mac, const uint8_t *incoming, int len) {
    memcpy(&myData, incoming, sizeof(myData));
    Serial.print("Received:");
    Serial.println(myData.randomValue);
}

void setup() {
    WiFi.mode(WIFI_STA);
    esp_now_init();
    esp_now_register_recv_cb((esp_now_recv_cb_t)OnDataRecv);
}
```

**Why ESP-NOW over Wi-Fi:** No router dependency, lower latency, significantly lower power draw — critical for battery-powered field nodes.

---

### 3. Wired Prototype (`sketch_feb9a.ino`)

Initial proof-of-concept before wireless migration. ESP32 reads moisture and streams to Python over USB Serial at 9600 baud.

---

## Analytics Dashboard

### Wireless Dashboard (`send_recv_wireless.py`)

Connects to the Gateway via PySerial at 115200 baud, parses the `Received:` prefix, and renders live telemetry.

**Key engineering decisions:**
- `errors='ignore'` in `readline().decode()` — handles garbage bytes during ESP32 wake-up
- `@st.cache_resource` — opens Serial connection once, survives Streamlit rerenders
- Rolling 50-point history window — smooths noise from 20-gauge probe baseline fluctuations
- `try/except` on all Serial reads — handles port flicker without crashing

```python
if "Received:" in line:
    value = int(line.split(":")[1])
    st.session_state.history.append(value)
    if len(st.session_state.history) > 50:
        st.session_state.history.pop(0)
    val_display.metric("Soil Moisture", value)
    if value > 400:
        status_display.error("STATUS: SOIL DRY - PUMPING")
    else:
        status_display.success("STATUS: MOISTURE OK")
    chart_display.line_chart(st.session_state.history)
```

---

## CAD & Mechanical Design (FreeCAD 1.0)

All enclosures designed using parametric **Sketch → Constraint → Pad** workflow for field durability.

| File | Purpose |
|---|---|
| `funnel.FCStd` + `funnel_base.FCStd` | Standardizes water delivery to sensor zone |
| `jar.FCStd` + `jar_lid.FCStd` | Waterproof enclosure for ESP32 + battery |
| `laser.FCStd` | Bracket for laser tripwire physical security monitoring |

---

## Setup & Usage

### Requirements

```bash
pip install streamlit pyserial
```

### Running the Wireless Dashboard

1. Flash `sketch_jan28a.ino` to your Gateway ESP32
2. Flash `Test_10sec.ino` to your Remote Node ESP32
3. Connect Gateway to laptop via USB
4. Update `arduino_port` in `send_recv_wireless.py` to match your COM port
5. Run: `streamlit run send_recv_wireless.py`

> **Note:** Close Arduino IDE Serial Monitor before running — only one process can hold the serial port at a time.

### Moisture Thresholds

| Value | Status | Action |
|---|---|---|
| 0 – 400 | Moisture OK | None |
| 400 – 800 | Getting Dry | Monitor |
| 800+ | Dry | LED alert + pump trigger |

---

## Development Progression

| Phase | Milestone |
|---|---|
| Jan 2026 | Arduino Uno wired prototype — proof of concept |
| Feb 2026 | ESP32 migration, wired Python/Streamlit dashboard |
| Mar 2026 | ESP-NOW wireless — eliminated Wi-Fi/router dependency |
| Mar 2026 | Deep Sleep integration — 10-minute cycles for battery longevity |
| Apr 2026 | FreeCAD enclosures, laser security tripwire, full documentation |

---

## Research Outcomes

- Successfully migrated from wired serial to ESP-NOW peer-to-peer wireless — no router, no cloud dependency
- Identified 260-value ADC baseline from 20-gauge wire probes; rolling window manages signal noise
- Deep Sleep architecture enables months of autonomous field operation on battery
- Investigated Federated Learning feasibility for on-device ESP32 model training
- Designed 6 parametric CAD components for moisture-resistant field deployment

---

## Author

**Shraya Rajkarnikar**  
B.S. Information Technology — UNC Pembroke, Expected May 2026  
[LinkedIn](https://linkedin.com/in/shraya-rajkarnikar-510280214) | [GitHub](https://github.com/Shraya-tech)
