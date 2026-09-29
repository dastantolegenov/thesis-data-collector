import csv
import os
import time
from pynput import mouse

MOVE_INTERVAL = 0.010  # log at most one move per 10 ms


class MouseLogger:
    def __init__(self, session_id, out_dir="data/raw/custom"):
        self.session_id = session_id
        self.out_dir = out_dir
        self.clock = time.perf_counter
        self.start = None
        self.last_move = 0.0
        self.rows = []

    def _record(self, event, x, y, button="", dx="", dy=""):
        t = self.clock() - self.start
        self.rows.append({
            "session_id": self.session_id,
            "timestamp": round(t, 6),
            "event": event,
            "x": x,
            "y": y,
            "button": button,
            "dx": dx,
            "dy": dy,
        })

    def on_move(self, x, y):
       t = self.clock() - self.start
       if t - self.last_move >= MOVE_INTERVAL:  # thin out moves
           self.last_move = t
           self._record("move", max(0, x), max(0, y))  # clamp to screen

    def on_click(self, x, y, button, pressed):
       event = "press" if pressed else "release"
       self._record(event, x, y, button=str(button).replace("Button.", ""))

    def on_scroll(self, x, y, dx, dy):
        self._record("scroll", x, y, dx=dx, dy=dy)

    def run(self):
       os.makedirs(self.out_dir, exist_ok=True)
       print(f"[mouse] session '{self.session_id}' recording. "
             f"Move, left-click and scroll normally. "
             f"RIGHT-CLICK to stop.")
       self.start = self.clock()
       with mouse.Listener(on_move=self.on_move,
                           on_click=self.on_click,
                           on_scroll=self.on_scroll) as listener:
           listener.join()
       self.save()

    def save(self):
        path = os.path.join(self.out_dir, f"mouse_{self.session_id}.csv")
        fields = ["session_id", "timestamp", "event", "x", "y", "button", "dx", "dy"]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(self.rows)
        print(f"[mouse] saved {len(self.rows)} events to {path}")


if __name__ == "__main__":
    MouseLogger(session_id="test01").run()