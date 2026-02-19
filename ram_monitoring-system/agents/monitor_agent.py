"""
Monitor Agent - Simple Version

Continuously checks RAM usage every 10 seconds.
Easy to understand and explain!
"""

import psutil
import time
import threading
from datetime import datetime
import pystray
from PIL import Image, ImageDraw

# ============ CONFIGURATION ============
CHECK_INTERVAL = 10  # Check every 10 seconds
RAM_THRESHOLD = 80   # Alert if RAM > 80%

# ============ GLOBAL STATE ============
breach_start_time = None
tray_icon = None


def get_ram_percent():
    return psutil.virtual_memory().percent


def get_top_processes():
    processes = []
    for proc in psutil.process_iter(['name', 'memory_percent']):
        try:
            processes.append({
                'name': proc.info['name'],
                'memory': round(proc.info['memory_percent'], 2)
            })
        except:
            pass
    processes.sort(key=lambda x: x['memory'], reverse=True)
    return processes[:3]


def print_status(ram_percent, top_processes):
    global breach_start_time
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{timestamp}] RAM: {ram_percent}%")

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

    print(f"Top processes: ", end="")
    for i, proc in enumerate(top_processes):
        if i > 0:
            print(", ", end="")
        print(f"{proc['name']} ({proc['memory']}%)", end="")
    print()


# ============ TASKBAR ICON ============
def create_icon_image(ram_percent):
    image = Image.new('RGB', (256, 256), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Color based on RAM level
    if ram_percent >= 80:
        color = (255, 0, 0)      # red - critical
    elif ram_percent >= 60:
        color = (255, 165, 0)    # orange - warning
    elif ram_percent >= 40:
        color = (255, 255, 0)    # yellow - moderate
    else:
        color = (0, 255, 0)      # green - normal

    # Draw filled circle
    draw.ellipse((4, 4, 252, 252), fill=color)

    return image


def setup_tray():
    global tray_icon
    image = create_icon_image(0)
    tray_icon = pystray.Icon("RAM Monitor", image, "RAM: 0%")
    threading.Thread(target=tray_icon.run, daemon=True).start()


def monitor_loop():
    print("=" * 50)
    print("MONITOR AGENT STARTED")
    print(f"Checking RAM every {CHECK_INTERVAL} seconds")
    print(f"Threshold: {RAM_THRESHOLD}%")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    setup_tray()

    try:
        while True:
            ram = get_ram_percent()
            processes = get_top_processes()

            tray_icon.icon = create_icon_image(ram)
            tray_icon.title = f"RAM: {ram}%"

            print_status(ram, processes)
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        tray_icon.stop()
        print("\n\nMonitor stopped!")


# ============ START HERE ============
if __name__ == "__main__":
    monitor_loop()