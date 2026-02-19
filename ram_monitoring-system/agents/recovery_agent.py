"""
Restart Agent

PERCEIVES: RESTART messages from the bus
ACTS: Restarts the system
"""

import os
import time
from core.base_agent import BaseAgent
from core.message_bus import MessageBus


class RestartAgent(BaseAgent):

    def init(self, bus: MessageBus):
        super().init("RestartAgent", bus)
        self.bus.subscribe("RESTART", self.on_restart)

    def run(self):
        print(f"[{self.name}] Ready. Waiting for events...")

    def on_restart(self, message):
        ram = message.payload["ram_percent"]
        print(f"[{self.name}] ⚠️ RAM critically high ({ram}%) — restarting in 10 seconds!")
        print(f"[{self.name}] Press Ctrl+C to cancel!")
        time.sleep(10)
        print(f"[{self.name}] Restarting now...")
        os.system("shutdown /r /t 0")