# bio_demo/bio_input.py
import time
import numpy as np
from pynput import keyboard

PHRASE = "security"     # exact phrase user types
FEATURE_LEN = 32

def _quantize(vec: np.ndarray, out_len: int = FEATURE_LEN) -> np.ndarray:
    if vec.size == 0:
        return np.zeros(out_len, dtype=np.uint8)
    
    # Much more aggressive quantization - only 16 levels (0-15) instead of 64
    z = (vec - np.median(vec)) / (np.std(vec) + 1e-6)
    z = np.clip(z, -1.5, 1.5)  # Very narrow range for maximum tolerance
    q = ((z + 1.5) / 3 * 15).astype(np.uint8)  # Only 16 levels (0-15)
    
    out = np.zeros(out_len, dtype=np.uint8)
    out[:min(out_len, q.size)] = q[:out_len]
    return out

def _capture_once(prompt: str, phrase: str = PHRASE) -> np.ndarray:
    print(f"\n[{prompt}] Type exactly: '{phrase}' (no Backspace/Enter)")
    print("🎹 Starting keyboard listener...")

    # Use a list to store the state so it can be accessed by nested functions
    state = {
        'downs': [],
        'ups': [],
        'i_down': 0,
        'i_up': 0,
        'done': False
    }
    want = phrase

    def on_press(k):
        if state['done']: 
            return False
        try:
            # Handle space character and other special cases
            ch = getattr(k, "char", None)
            if ch is None:
                # Check if it's a space key
                if hasattr(k, 'name') and k.name == 'space':
                    ch = ' '
                else:
                    # Skip non-character keys
                    return True
            
            if ch and state['i_down'] < len(want) and ch == want[state['i_down']]:
                state['downs'].append(time.perf_counter())
                state['i_down'] += 1
                print(f"✅ Key '{ch}' pressed ({state['i_down']}/{len(want)})")
                if state['i_down'] == len(want) and state['i_up'] == len(want):
                    print("🎯 All keys captured! Finishing...")
                    state['done'] = True
                    return False
            elif ch:
                print(f"❌ Wrong character '{ch}', resetting...")
                state['downs'].clear()
                state['ups'].clear()
                state['i_down'] = 0
                state['i_up'] = 0
        except Exception as e:
            print(f"Error in on_press: {e}")
            return False

    def on_release(k):
        if state['done']: 
            return False
        try:
            # Handle space character and other special cases
            ch = getattr(k, "char", None)
            if ch is None:
                # Check if it's a space key
                if hasattr(k, 'name') and k.name == 'space':
                    ch = ' '
                else:
                    # Skip non-character keys
                    return True
            
            if ch and state['i_up'] < len(want) and ch == want[state['i_up']]:
                state['ups'].append(time.perf_counter())
                state['i_up'] += 1
                print(f"🔄 Key '{ch}' released ({state['i_up']}/{len(want)})")
                if state['i_up'] == len(want) and state['i_down'] == len(want):
                    print("🎯 All keys captured! Finishing...")
                    state['done'] = True
                    return False
            elif ch:
                state['downs'].clear()
                state['ups'].clear()
                state['i_down'] = 0
                state['i_up'] = 0
        except Exception as e:
            print(f"Error in on_release: {e}")
            return False

    # Use a context manager to ensure proper cleanup
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Type the phrase now...")
        listener.join()

    if not (len(state['downs']) == len(state['ups']) == len(want)):
        print(f"⚠️  Incomplete input: downs={len(state['downs'])}, ups={len(state['ups'])}, want={len(want)}")
        return np.zeros(FEATURE_LEN, dtype=np.uint8)

    print("✅ All keys captured successfully!")
    t_d = np.array(state['downs'])
    t_u = np.array(state['ups'])
    
    # Much more aggressive rounding - 50ms precision instead of 10ms
    dd = np.round(np.diff(t_d) * 20.0) / 20.0 * 1000.0      # Round to 50ms precision
    ud = np.round((t_d[1:] - t_u[:-1]) * 20.0) / 20.0 * 1000.0  # Round to 50ms precision
    hold = np.round((t_u - t_d) * 20.0) / 20.0 * 1000.0     # Round to 50ms precision
    
    # Use only the most stable features - reduce sensitivity
    dd_mean = np.mean(dd)
    dd_std = np.std(dd)
    hold_mean = np.mean(hold)
    hold_std = np.std(hold)
    total_time = (t_u[-1] - t_d[0]) * 1000.0
    
    # Create a much simpler, more stable feature vector
    feats = np.array([
        dd_mean, dd_std,           # Inter-key timing (mean and variation)
        hold_mean, hold_std,       # Hold time (mean and variation)
        total_time,                 # Total duration
        len(dd)                    # Number of keys
    ])
    
    return _quantize(feats, FEATURE_LEN)

def capture_enroll() -> np.ndarray:
    return _capture_once("ENROLL")

def capture_auth() -> np.ndarray:
    return _capture_once("AUTH")
