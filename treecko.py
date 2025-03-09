import cv2
import numpy as np
import mss
import subprocess
import time
import sys
import requests  # Added for Discord webhook
import os
import logging
import threading
from logging.handlers import RotatingFileHandler

# Set up logging with log rotation
log_file = os.path.expanduser("~/Downloads/treecko_hunt.log")
handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)  # Max 5MB per file, 3 backups
handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

logging.basicConfig(level=logging.INFO, handlers=[handler])

# Thread-local storage to prevent recursive logging
thread_local = threading.local()
thread_local.is_logging = False  # Track if we are already logging

reset_count = 0  # Counter for the number of resets

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_url"  # Replace with your Discord webhook URL

def log_message(message):
    """Logs message safely, preventing recursive calls."""
    if getattr(thread_local, "is_logging", False):
        return  # Prevent infinite recursion
    
    try:
        thread_local.is_logging = True  # Mark logging as in progress
        logging.info(message)
    finally:
        thread_local.is_logging = False  # Reset flag after logging

def send_discord_notification():
    """Sends a Discord notification when a shiny Treecko is found."""
    data = {"content": f"🔥 **Shiny Treecko found!** 🟢 Total resets: {reset_count} 🚀"}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        log_message("Discord notification sent successfully!")
    else:
        log_message(f"Failed to send Discord notification. Status code: {response.status_code}")

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
        log_message("mGBA window not found!")
        return None
    x, y, width, height = window
    with mss.mss() as sct:
        screenshot = np.array(sct.grab({"left": x, "top": y, "width": width, "height": height}))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

def is_screen_present(template_path, threshold=0.9):
    """Checks if a specific screen (image) is currently displayed."""
    screenshot = capture_mgba_screen()
    if screenshot is None:
        return False
    template = cv2.imread(template_path)
    if template is None:
        log_message(f"Template image {template_path} not found!")
        return False
    
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val > threshold

def wait_for_screen(template_path, description):
    """Waits until a given screen appears before proceeding."""
    log_message(f"Waiting for {description} screen...")
    while not is_screen_present(template_path):
        time.sleep(0.1)
    log_message(f"{description} screen detected!")

def scan_screen_for_treecko():
    """Scans the screen for Treecko only if in battle."""
    if not is_screen_present("battle.png"):
        return
    
    screenshot = capture_mgba_screen()
    if screenshot is None:
        return
    
    treecko_normal = cv2.imread("treecko_normal.png")
    treecko_shiny = cv2.imread("treecko_shiny.png")
    
    if treecko_normal is None or treecko_shiny is None:
        log_message("Treecko template images not found!")
        return
    
    result_normal = cv2.matchTemplate(screenshot, treecko_normal, cv2.TM_CCOEFF_NORMED)
    result_shiny = cv2.matchTemplate(screenshot, treecko_shiny, cv2.TM_CCOEFF_NORMED)
    
    _, max_val_normal, _, max_loc_normal = cv2.minMaxLoc(result_normal)
    _, max_val_shiny, _, max_loc_shiny = cv2.minMaxLoc(result_shiny)
    
    if max_val_shiny > 0.9:
        log_message(f"Shiny Treecko detected at {max_loc_shiny} with confidence {max_val_shiny}!")
        subprocess.run(["notify-send", "Shiny Treecko found!"])
        send_discord_notification()  # Send Discord notification
        sys.exit("Shiny found! Stopping script.")
    elif max_val_normal > 0.9:
        log_message(f"Normal Treecko detected at {max_loc_normal} with confidence {max_val_normal}")
        log_message("Normal Treecko detected, resetting game...")
        reset_game()  # Ensure game resets after detecting a normal Treecko
    else:
        log_message("Treecko not detected.")

def press_key(key):
    """Presses and releases a key using xdotool."""
    subprocess.run(["xdotool", "keydown", key])
    time.sleep(0.1)
    subprocess.run(["xdotool", "keyup", key])

def reset_game():
    """Resets the game and starts a new encounter."""
    global reset_count
    reset_count += 1  # Increment reset counter
    log_message(f"Resetting game... (Total resets: {reset_count})")
    
    get_mgba_window()  # Ensure game window is in focus
    press_key("ctrl+r")
    
    # Wait for the intro screen to appear
    wait_for_screen("intro.png", "intro")
    
    # Intro sequence
    press_key("x")
    log_message("Pressing x...")
    time.sleep(1)
    press_key("x")
    log_message("Pressing x...")
    time.sleep(2)
    press_key("x")
    log_message("Pressing x...")
    time.sleep(3)
    press_key("x")
    log_message("Pressing x...")
    
    log_message("Waiting for bag selection screen...")
    
    # Wait for the bag selection screen
    wait_for_screen("bag.png", "bag")
    
    # Navigating bag selection
    press_key("x")
    log_message("Pressing x...")
    time.sleep(1)
    press_key("Left")
    log_message("Pressing left...")
    time.sleep(1)
    press_key("x")
    log_message("Pressing x...")
    time.sleep(1)
    press_key("x")
    log_message("Pressing x...")
    
    # Wait for the "send Treecko in" screen
    wait_for_screen("send.png", "send Treecko in")
    
    # Send Treecko into battle
    press_key("x")
    log_message("Sending Treecko in...")
    
    while not is_screen_present("battle.png"):
        time.sleep(0.1)  # Wait until battle starts
    
    scan_screen_for_treecko()

if __name__ == "__main__":
    log_message("Treecko Shiny Hunting Bot Started.")
    reset_game()  # Ensure a proper start before sequence begins
    while True:
        scan_screen_for_treecko()
        time.sleep(0.1)
