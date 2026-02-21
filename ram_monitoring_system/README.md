# RAM Monitoring System
A multi-agent system that monitors RAM usage in real-time and escalates alerts automatically.

---

## Project Structure
```
ram_monitoring_system/
├── core/
│   ├── __init__.py
│   ├── base_agent.py       # Abstract base class for all agents
│   ├── message.py          # Message dataclass
│   └── message_bus.py      # Central message broker
├── agents/
│   ├── __init__.py
│   ├── monitor_agent.py    # Monitors RAM every 10 seconds
│   ├── alert_agent.py      # Shows popup + plays sound
│   ├── email_agent.py      # Sends email alert
│   ├── logger_agent.py     # Logs events to CSV
│   ├── dashboard_agent.py  # Real-time web dashboard
│   └── recovery_agent.py   # Restarts system if RAM stays critical
├── main.py                 # Orchestrator — runs all agents
├── .env                    # Email credentials (not committed)
├── ram_log.csv             # Generated log file
└── README.md
```

---

## How It Works

Each agent runs in its own thread and communicates only through a shared **Message Bus**. No agent talks to another directly — they publish and subscribe to events.

**Escalation Flow:**
```
RAM goes high
    │
    ▼ immediately
AlertAgent  →  popup + sound
    │
    ▼ after 70 seconds
EmailAgent  →  sends email
    │
    ▼ after 110 seconds
RestartAgent → restarts system
    │
    (all events logged by LoggerAgent)
    (all events visible on Dashboard)
```

---

## Requirements

- Python 3.10+
- Windows (for system tray icon and sound)

---

## Installation

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd ram_monitoring_system
```

**2. Install dependencies**
```bash
pip install psutil pystray pillow flask python-dotenv
```

**3. Setup email credentials**

Create a `.env` file in the root folder:
```
SMTP_PORT=587
SENDER_EMAIL=yourgmail@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@gmail.com
```

> **Note:** For Gmail you need an App Password, not your regular password.
> Get one at: `myaccount.google.com/apppasswords`

---

## Running the System

```bash
python main.py
```

This will:
- Start all 6 agents in separate threads
- Show a colored circle in your system tray (green/yellow/orange/red)
- Open a web dashboard at `http://localhost:5000`
- Begin monitoring RAM every 10 seconds

**Stop the system:**
```bash
Ctrl+C
```

---

## Running a Single Agent (Standalone)

Each agent can be tested independently:
```bash
python agents/monitor_agent.py
python agents/alert_agent.py
python agents/email_agent.py
python agents/logger_agent.py
python agents/dashboard_agent.py
python agents/recovery_agent.py
```

---

## Agents

| Agent | Trigger | Action |
|---|---|---|
| MonitorAgent | Every 10 seconds | Reads RAM, updates tray icon, publishes data |
| AlertAgent | RAM > threshold | Shows popup warning + plays sound |
| EmailAgent | RAM high for 70s | Sends email alert |
| LoggerAgent | Any event | Writes to `ram_log.csv` |
| DashboardAgent | Always | Serves web dashboard at port 5000 |
| RestartAgent | RAM high for 110s | Restarts the system |

---

## Configuration

In `monitor_agent.py`:
```python
CHECK_INTERVAL = 10   # How often to check RAM (seconds)
RAM_THRESHOLD = 50    # Alert threshold (%)
```

In `main.py`:
```python
if ram >= 50:         # Threshold for escalation
    ...
if duration >= 70:    # Seconds before email
    ...
if duration >= 110:   # Seconds before restart
    ...
```

---

## Logs

Events are saved to `ram_log.csv` automatically:

| Timestamp | Event | RAM% | Details |
|---|---|---|---|
| 2024-01-01 10:00:10 | RAM_HIGH | 55% | Threshold breached |
| 2024-01-01 10:01:00 | EMAIL_SENT | 58% | Alert email sent |
| 2024-01-01 10:03:00 | RESTART | 65% | System restart triggered |
| 2024-01-01 10:03:10 | RAM_NORMAL | 42% | RAM back to normal |
| 2024-01-01 12:00:00 | SNAPSHOT | 48% | Scheduled 6-hour report |

---

## Dashboard

Open `http://localhost:5000` in your browser after running `main.py`.

Features:
- Live RAM gauge with color indicators
- Top 3 RAM-consuming processes
- RAM history chart (last 20 readings)
- Agent status cards

---

## Team

| Name | Responsibility |
|---|---|
| [Your Name] | System architecture, message bus, main orchestrator |
| [Teammate 1] | MonitorAgent |
| [Teammate 2] | AlertAgent |
| [Teammate 3] | EmailAgent |
| [Teammate 4] | LoggerAgent |
| [Teammate 5] | RecoveryAgent |
