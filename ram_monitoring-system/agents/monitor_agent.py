"""
Monitor Agent - Simple Version

Continuously checks RAM usage every 10 seconds.
Easy to understand and explain!
"""

import psutil
import time
from datetime import datetime

# ============ CONFIGURATION ============
CHECK_INTERVAL = 10  # Check every 10 seconds
RAM_THRESHOLD = 80  # Alert if RAM > 80%

# ============ GLOBAL STATE ============
breach_start_time = None  # When high RAM started


def get_ram_percent():
    """Get current RAM percentage"""
    return psutil.virtual_memory().percent


def get_top_processes():
    """Get top 3 processes using most RAM"""
    processes = []

    # Get all running processes
    for proc in psutil.process_iter(['name', 'memory_percent']):
        try:
            processes.append({
                'name': proc.info['name'],
                'memory': round(proc.info['memory_percent'], 2)
            })
        except:
            pass  # Skip if process ended or no permission

    # Sort by memory and get top 3
    processes.sort(key=lambda x: x['memory'], reverse=True)
    return processes[:3]


def print_status(ram_percent, top_processes):
    """Print current RAM status to screen"""
    global breach_start_time

    timestamp = datetime.now().strftime('%H:%M:%S')

    print(f"\n[{timestamp}] RAM: {ram_percent}%")

    # Check if RAM is high
    if ram_percent >= RAM_THRESHOLD:
        if breach_start_time is None:
            breach_start_time = time.time()
            print(f"⚠️  HIGH RAM! Started monitoring...")
        else:
            duration = int(time.time() - breach_start_time)
            print(f"⚠️  HIGH RAM for {duration} seconds!")
    else:
        if breach_start_time is not None:
            print("✓ RAM back to normal")
            breach_start_time = None
        else:
            print("✓ RAM normal")

    # Print top processes
    print(f"Top processes: ", end="")
    for i, proc in enumerate(top_processes):
        if i > 0:
            print(", ", end="")
        print(f"{proc['name']} ({proc['memory']}%)", end="")
    print()


def monitor_loop():
    """
    Main monitoring loop - runs forever

    1. Check RAM
    2. Get top processes
    3. Print status
    4. Sleep 10 seconds
    5. Repeat
    """
    print("=" * 50)
    print("MONITOR AGENT STARTED")
    print(f"Checking RAM every {CHECK_INTERVAL} seconds")
    print(f"Threshold: {RAM_THRESHOLD}%")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        while True:
            # 1. PERCEIVE - Check environment
            ram = get_ram_percent()
            processes = get_top_processes()

            # 2. ACT - Print status
            print_status(ram, processes)

            # 3. SLEEP - Wait before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nMonitor stopped!")


# ============ START HERE ============
if __name__ == "__main__":
    monitor_loop()
