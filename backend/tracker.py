from config import APPLE_PTS, COOKIE_PTS
from datetime import datetime
import json

class SnackTrack:
    def __init__(self, state_manager):
        self.sm = state_manager

    def overlaps(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)
    
    def snack_counter(self, snack_type):
        s = self.sm.state
        snack_type = snack_type.lower()

        if snack_type == "apple":
            pts = APPLE_PTS
            s["apple_bites"] += 1
            s["healthy_streak"] += 1
        else:
            pts = COOKIE_PTS
            s["cookie_bites"] += 1
            s["healthy_streak"] = 0
            
        s["score"] += pts
        self.sm.log_snack(snack_type, pts)
        self.sm.save_state()
        
class StateManager:
    def __init__(self, file):
        self.file = file
        self.state = {
            "score": 0,
            "apple_bites": 0,
            "cookie_bites": 0,
            "healthy_streak": 0,
            "log": [],
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

    def save_state(self):
        with open(self.file, "w") as f:
            json.dump(self.state, f, indent=2)

    def load_state(self):
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            with open(self.file, "r") as f:
                saved = json.load(f)

            # If same day → load everything
            if saved.get("date") == today:
                for k in self.state:
                    self.state[k] = saved.get(k, self.state[k])
            else:
                # new day → reset date but keep fresh state
                self.state["date"] = today
                self.save_state()

        except (FileNotFoundError, json.JSONDecodeError):
            # file doesn't exist or is broken → create fresh one
            self.save_state()

    def log_snack(self, item, pts):
        self.state["log"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "item": item,
            "pts": pts
        })

    def reset(self):
        self.state = {
            "score": 0,
            "apple_bites": 0,
            "cookie_bites": 0,
            "healthy_streak": 0,
            "log": [],
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        self.save_state()
