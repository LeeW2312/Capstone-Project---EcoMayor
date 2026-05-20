"""core/sounds.py — Sound management"""
import threading

_enabled = True
_volume  = 0.75

def set_enabled(val: bool):
    global _enabled; _enabled = val

def set_volume(pct: int):
    global _volume; _volume = max(0, min(100, pct)) / 100

def _beep(freq=440, dur=120):
    try:
        import winsound
        winsound.Beep(freq, dur)
    except Exception:
        pass

def play(sound_name: str):
    if not _enabled: return
    freq_map = {
        "correct": 880, "wrong": 220, "upgrade": 660,
        "achieve": 1046, "click": 500, "win": 880, "lose": 220,
    }
    freq = freq_map.get(sound_name, 440)
    threading.Thread(target=_beep, args=(freq, 80), daemon=True).start()