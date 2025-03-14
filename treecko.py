import cv2
import numpy as np
import mss
import subprocess
import time
import sys
import requests
import os
import logging
import random

# Set up logging
log_file = os.path.expanduser("~/Downloads/treecko_hunt.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

reset_count = 0  # Reset counter

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_url_here"

def log_message(message):
    logging.info(message)

def send_discord_notification():
    data = {"content": f"🔥 **Shiny Treecko found!** 🟢 Total resets: {reset_count} 🚀"}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        log_message("Discord notification sent successfully!")
    else:
        log_message(f"Failed to send Discord notification. Status: {response.status_code}")

def get_mgba_window():
    output = subprocess.check_output(["wmctrl", "-lG"]).decode()
    for line in output.splitlines():
        if "mGBA - 0.10.4" in line:
            parts = line.split()
            x, y, width, height = map(int, parts[2:6])
            window_id = parts[0]
            subprocess.run(["wmctrl", "-i", "-a", window_id])
            time.sleep(0.5)
            return x, y, width, height
    return None

def capture_mgba_screen():
    window = get_mgba_window()
    if not window:
        log_message("mGBA window not found!")
        return None
    x, y, width, height = window
    with mss.mss() as sct:
        screenshot = np.array(sct.grab({"left": x, "top": y, "width": width, "height": height}))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

def is_screen_present(template_path, threshold=0.9):
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
    log_message(f"Waiting for {description} screen...")
    while not is_screen_present(template_path):
        time.sleep(0.1)
    log_message(f"{description} screen detected!")

def press_key(key):
    subprocess.run(["xdotool", "keydown", key])
    time.sleep(0.1)
    subprocess.run(["xdotool", "keyup", key])

def reset_game():
    global reset_count
    reset_count += 1
    log_message(f"Resetting game... (Total resets: {reset_count})")

    # Randomized wait to help alter RNG
    random_wait = random.uniform(0.5, 6.0)
    log_message(f"Randomized pre-reset wait: {random_wait:.2f} seconds")

    time.sleep(random_wait)

    get_mgba_window()
    press_key("ctrl+r")

    wait_for_screen("intro.png", "intro")

    press_key("x")
    time.sleep(1)
    press_key("x")
    time.sleep(2)
    press_key("x")
    time.sleep(3)
    press_key("x")

    wait_for_screen("bag.png", "bag")

    time.sleep(random_wait)

    press_key("x")
    time.sleep(1)
    press_key("Left")
    time.sleep(1)
    press_key("x")
    time.sleep(1)
    press_key("x")

    wait_for_screen("send.png", "send Treecko in")

    press_key("x")
    log_message("Sending Treecko in...")

if __name__ == "__main__":
    log_message("Treecko Shiny Hunting Bot Started.")

    while True:
        reset_game()

        while not is_screen_present("battle.png"):
            time.sleep(0.1)

        screenshot = capture_mgba_screen()
        if screenshot is None:
            continue

        treecko_normal = cv2.imread("treecko_normal.png")
        treecko_shiny = cv2.imread("treecko_shiny.png")

        if treecko_normal is None or treecko_shiny is None:
            log_message("Treecko template images not found!")
            continue

        result_normal = cv2.matchTemplate(screenshot, treecko_normal, cv2.TM_CCOEFF_NORMED)
        result_shiny = cv2.matchTemplate(screenshot, treecko_shiny, cv2.TM_CCOEFF_NORMED)

        _, max_val_normal, _, max_loc_normal = cv2.minMaxLoc(result_normal)
        _, max_val_shiny, _, max_loc_shiny = cv2.minMaxLoc(result_shiny)

        if max_val_shiny > 0.9:
            log_message(f"Shiny Treecko detected at {max_loc_shiny} with confidence {max_val_shiny}!")
            subprocess.run(["notify-send", "Shiny Treecko found!"])
            send_discord_notification()
            sys.exit("Shiny found! Stopping script.")
        elif max_val_normal > 0.9:
            log_message(f"Normal Treecko detected at {max_loc_normal} with confidence {max_val_normal}")
            log_message("Normal Treecko detected, restarting...")
        else:
            log_message("Treecko not detected.")

        time.sleep(0.1)
