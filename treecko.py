import cv2
import numpy as np
import mss
import subprocess
import time
import sys

# Global reset counter
reset_count = 0

def get_mgba_window():
    """Finds and focuses on the mGBA window."""
    output = subprocess.check_output(["wmctrl", "-lG"]).decode()
    for line in output.splitlines():
        if "mGBA - 0.10.4" in line:
            parts = line.split()
            x, y, width, height = map(int, parts[2:6])
            window_id = parts[0]
            subprocess.run(["wmctrl", "-i", "-a", window_id])  # Bring mGBA to focus
            time.sleep(0.5)  # Ensure focus before proceeding
            return x, y, width, height
    return None

def capture_mgba_screen():
    """Captures only the mGBA window."""
    window = get_mgba_window()
    if not window:
        print("mGBA window not found!")
        return None
    x, y, width, height = window
    with mss.mss() as sct:
        screenshot = np.array(sct.grab({"left": x, "top": y, "width": width, "height": height}))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

def is_battle_screen():
    """Checks if the battle screen is displayed."""
    screenshot = capture_mgba_screen()
    if screenshot is None:
        return False
    battle_template = cv2.imread("battle.png")
    if battle_template is None:
        print("Battle template image not found!")
        return False
    
    result = cv2.matchTemplate(screenshot, battle_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val > 0.9

def scan_screen_for_treecko():
    """Scans the screen for Treecko only if in battle."""
    if not is_battle_screen():
        return
    
    screenshot = capture_mgba_screen()
    if screenshot is None:
        return
    
    treecko_normal = cv2.imread("treecko_normal.png")
    treecko_shiny = cv2.imread("treecko_shiny.png")
    
    if treecko_normal is None or treecko_shiny is None:
        print("Treecko template images not found!")
        return
    
    result_normal = cv2.matchTemplate(screenshot, treecko_normal, cv2.TM_CCOEFF_NORMED)
    result_shiny = cv2.matchTemplate(screenshot, treecko_shiny, cv2.TM_CCOEFF_NORMED)
    
    _, max_val_normal, _, max_loc_normal = cv2.minMaxLoc(result_normal)
    _, max_val_shiny, _, max_loc_shiny = cv2.minMaxLoc(result_shiny)
    
    if max_val_shiny > 0.9:
        print(f"Shiny Treecko detected at {max_loc_shiny} with confidence {max_val_shiny}!")
        subprocess.run(["notify-send", "Shiny Treecko found!"])
        sys.exit("Shiny found! Stopping script.")
    elif max_val_normal > 0.9:
        print(f"Normal Treecko detected at {max_loc_normal} with confidence {max_val_normal}")
        print("Normal Treecko detected, resetting game...")
        reset_game()  # Ensure game resets after detecting a normal Treecko
    else:
        print("Treecko not detected.")

def press_key(key):
    """Presses and releases a key using xdotool."""
    subprocess.run(["xdotool", "keydown", key])
    time.sleep(0.1)
    subprocess.run(["xdotool", "keyup", key])

def reset_game():
    """Resets the game and starts a new encounter."""
    global reset_count
    reset_count += 1  # Increment counter
    print(f"Resetting game... (Attempt #{reset_count})")
    
    get_mgba_window()  # Ensure game window is in focus
    press_key("ctrl+r")

    print("Waiting for game to reset...")
    time.sleep(4)
    
    # Intro sequence
    press_key("x")
    print("Pressing x...")
    time.sleep(2)
    press_key("x")
    print("Pressing x...")
    time.sleep(2)
    press_key("x")
    print("Pressing x...")
    time.sleep(2)
    press_key("x")
    print("Pressing x...")
    
    print("Waiting for game to load...")
    time.sleep(3)
    
    # Navigating bag selection
    press_key("x")
    print("Pressing x...")
    time.sleep(1)
    press_key("Left")
    print("Pressing left...")
    time.sleep(1)
    press_key("x")
    print("Pressing x...")
    time.sleep(1)
    press_key("x")
    print("Pressing x...")
    print("Waiting for battle to start...")
    time.sleep(8)
    press_key("x")  # Send in Treecko
    print("Sending Treecko in...")
    
    while not is_battle_screen():
        time.sleep(3)  # Wait until battle starts
    
    scan_screen_for_treecko()

if __name__ == "__main__":
    reset_game()  # Ensure a proper start before sequence begins
    while True:
        scan_screen_for_treecko()
        time.sleep(1)
