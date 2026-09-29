import csv
import hashlib
import os
import time
from pynput import keyboard


def make_salt():
    """Random per-session salt. Never saved, so key hashing is irreversible."""
    return os.urandom(32)


def hash_key(salt, raw_key):
    """Anonymous, per-session key id. Same key -> same id within a session."""
    digest = hashlib.sha256(salt + str(raw_key).encode())
    return digest.hexdigest()[:8]


def categorize(key):
    """Coarse key category. Does not reveal which letter/digit was typed."""
    if isinstance(key, keyboard.KeyCode) and key.char is not None:
        ch = key.char
        if ch.isalpha():
            return "letter"
        if ch.isdigit():
            return "digit"
        return "punct"
    # Special keys (Key.enter, Key.shift, ...) -> keep the name only
    name = str(key).replace("Key.", "")
    # Prefix arrow keys so they don't clash with the "down"/"up" event names
    if name in ("up", "down", "left", "right"):
        name = "arrow_" + name
    return name


class KeystrokeLogger:
    def __init__(self, session_id, out_dir="data/raw/custom"):
        self.session_id = session_id
        self.out_dir = out_dir
        self.salt = make_salt()
        self.clock = time.perf_counter
        self.start = None
        self.rows = []

    def _record(self, event, key):
        t = self.clock() - self.start
        raw = key.char if isinstance(key, keyboard.KeyCode) and key.char else str(key)
        self.rows.append({
            "session_id": self.session_id,
            "timestamp": round(t, 6),
            "event": event,
            "key_category": categorize(key),
            "key_id": hash_key(self.salt, raw),
        })

    def on_press(self, key):
        # ESC ends the session
        if key == keyboard.Key.esc:
            return False
        self._record("down", key)

    def on_release(self, key):
        self._record("up", key)

    def run(self):
        os.makedirs(self.out_dir, exist_ok=True)
        print(f"[keystroke] session '{self.session_id}' recording. Press ESC to stop.")
        self.start = self.clock()
        with keyboard.Listener(on_press=self.on_press,
                               on_release=self.on_release) as listener:
            listener.join()
        self.save()

    def _drop_unpaired(self, rows):
       """
       Remove events that have no matching pair:
       - an 'up' whose key was never 'down' (e.g. stop key released after ESC)
       - a 'down' that was never released (key still held at stop time)
       Keeps only complete down->up pairs, matched per key_id in time order.
       """
       open_downs = {}   # key_id -> index of its 'down' row
       keep = [False] * len(rows)
       for i, r in enumerate(rows):
           k = r["key_id"]
           if r["event"] == "down":
               open_downs.setdefault(k, []).append(i)
           elif r["event"] == "up" and open_downs.get(k):
               down_idx = open_downs[k].pop(0)
               keep[down_idx] = True   # keep the matched down
               keep[i] = True          # keep this up
       return [r for r, k in zip(rows, keep) if k]

    def save(self):
       path = os.path.join(self.out_dir, f"keystroke_{self.session_id}.csv")
       fields = ["session_id", "timestamp", "event", "key_category", "key_id"]
       clean = self._drop_unpaired(self.rows)
       dropped = len(self.rows) - len(clean)
       with open(path, "w", newline="") as f:
           writer = csv.DictWriter(f, fieldnames=fields)
           writer.writeheader()
           writer.writerows(clean)
       note = f" ({dropped} unpaired dropped)" if dropped else ""
       print(f"[keystroke] saved {len(clean)} events to {path}{note}")


if __name__ == "__main__":
    KeystrokeLogger(session_id="test01").run()