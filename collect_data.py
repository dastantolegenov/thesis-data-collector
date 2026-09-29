import time
from pynput import keyboard, mouse

from logger_keystroke import KeystrokeLogger
from logger_mouse import MouseLogger


def collect(session_id, out_dir="data/raw/custom"):
    """
    Run keystroke and mouse logging together on one shared clock.
    Press ESC to stop both.
    """
    clock = time.perf_counter
    start = clock()

    # Shared clock and start time for both loggers, so files line up in time
    ks = KeystrokeLogger(session_id, out_dir)
    ms = MouseLogger(session_id, out_dir)
    ks.clock = ms.clock = clock
    ks.start = ms.start = start

    mouse_listener = mouse.Listener(
        on_move=ms.on_move,
        on_click=ms.on_click,
        on_scroll=ms.on_scroll,
    )

    def on_press(key):
        if key == keyboard.Key.esc:
            return False  # stops the keyboard listener
        ks._record("down", key)

    def on_release(key):
       ks._record("up", key)

    print(f"\n=== Session '{session_id}' ===")
    print("Recording keyboard + mouse. Type and move normally.")
    print("Do NOT type real passwords. Press ESC to stop.\n")

    mouse_listener.start()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as kl:
        kl.join()          # waits until ESC
    mouse_listener.stop()  # stop mouse together with keyboard

    ks.save()
    ms.save()
    print(f"\nSession '{session_id}' finished.")


if __name__ == "__main__":
    sid = input("Enter participant/session ID (e.g. P01): ").strip()
    if not sid:
        sid = "test01"
    collect(sid)