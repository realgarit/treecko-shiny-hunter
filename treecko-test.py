import cv2
import numpy as np
import mss
import subprocess

def get_mgba_window():
    """Finds mGBA's window position and size."""
    output = subprocess.check_output(["wmctrl", "-lG"]).decode()
    for line in output.splitlines():
        if "mGBA - 0.10.4" in line:
            parts = line.split()
            x, y, width, height = map(int, parts[2:6])
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

def scan_screen_for_treecko():
    """Scans the entire screen for Treecko using image recognition."""
    screenshot = capture_mgba_screen()
    if screenshot is None:
        print("Screenshot could not be captured!")
        return
    else:
        print(f"Screenshot shape: {screenshot.shape}")
    
    cv2.imwrite("captured_screen.png", screenshot)
    print("Screenshot saved as captured_screen.png. Check it manually.")
    
    treecko_template = cv2.imread("treecko_normal.png")
    if treecko_template is None:
        print("Treecko template image not found or could not be loaded!")
        return
    else:
        print(f"Treecko template shape: {treecko_template.shape}")
    
    result = cv2.matchTemplate(screenshot, treecko_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > 0.9:
        print(f"Treecko detected at {max_loc} with confidence {max_val}")
    else:
        print("Treecko not detected.")

if __name__ == "__main__":
    scan_screen_for_treecko()
