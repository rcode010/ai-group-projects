"""
Alert Agent - Simple Version

Shows popup warning when RAM is high.
Plays sound to get user's attention.

Easy to understand and explain!
"""

import psutil
import time
import tkinter as tk
from tkinter import messagebox
import winsound  # For Windows beep sound (built-in)

CHECK_INTERVAL = 10  # Check every 10 seconds
RAM_THRESHOLD = 30  # Alert if RAM > 80%

alert_shown = False  # Have we already shown alert?


def get_ram_percent():
    """Get current RAM percentage"""
    return psutil.virtual_memory().percent


def get_top_processes(n=3):
    """Get top N processes using most RAM"""
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
    return processes[:n]


def play_alert_sound():
    try:

        winsound.Beep(1000, 500)  # 1000 Hz for 500ms
    except:
        print("🔊 (Alert sound)")


def show_popup(ram_percent, top_processes):

    # Create invisible root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Build message
    message = f"⚠️  HIGH RAM USAGE DETECTED! ⚠️\n\n"
    message += f"RAM Usage: {ram_percent}%\n\n"
    message += "Top processes:\n"

    for i, proc in enumerate(top_processes, 1):
        message += f"  {i}. {proc['name']}: {proc['memory']}%\n"

    message += "\nPlease close some programs!"

    # Show warning popup
    messagebox.showwarning("RAM Alert", message)

    # Clean up
    root.destroy()


def check_and_alert():

    global alert_shown

    # PERCEIVE - Check environment
    ram = get_ram_percent()

    # DECIDE - Is action needed?
    if ram >= RAM_THRESHOLD:
        # RAM is high!
        if not alert_shown:
            print(f"⚠️  HIGH RAM: {ram}% - Showing alert!")

            processes = get_top_processes(3)

            play_alert_sound()  # Sound
            show_popup(ram, processes)  # Popup

            alert_shown = True
            print("✓ Alert shown to user")
        else:
            print(f"⚠️  HIGH RAM: {ram}% (Alert already shown)")
    else:
        # RAM is normal
        if alert_shown:
            print(f"✓ RAM back to normal: {ram}%")
            alert_shown = False
        else:
            print(f"✓ RAM normal: {ram}%")


def alert_agent_loop():

    print("=" * 50)
    print("ALERT AGENT STARTED")
    print(f"Checking RAM every {CHECK_INTERVAL} seconds")
    print(f"Will alert if RAM > {RAM_THRESHOLD}%")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()

    try:
        while True:
            # Perception-Action cycle
            check_and_alert()

            # Sleep before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\nAlert Agent stopped!")


if __name__ == "__main__":
    alert_agent_loop()
