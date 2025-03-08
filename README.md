# Treecko Shiny Hunting Bot

This is an automated script designed for shiny hunting Treecko in Pokémon Emerald using the mGBA emulator on Linux. The script automates the process of resetting the game, navigating through the starter selection, and detecting whether the encountered Treecko is shiny. If a shiny Treecko is found, the script stops immediately and sends a desktop notification.

---

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Notes](#notes)

---

## Requirements
- Linux OS
- [mGBA 0.10.4](https://mgba.io/)
- Python 3.12+
- Required Python packages:
  - OpenCV (`cv2`)
  - NumPy
  - MSS
- `wmctrl` and `xdotool` (installed via package manager)

To install dependencies:
```bash
pip install opencv-python numpy mss
sudo apt install wmctrl xdotool
```

---

## Setup
1. Ensure mGBA is running with Pokémon Emerald loaded.
2. Save two reference images in the script directory:
   - `treecko_normal.png` (for detecting normal Treecko)
   - `treecko_shiny.png` (for detecting shiny Treecko)
   - `battle.png` (for detecting the battle start screen)
3. Run the script:
```bash
python3 treecko.py
```

---

## Usage
- The script starts by resetting the game and automating button presses to select Treecko.
- Once in battle, it checks if Treecko is shiny.
- If a shiny is detected, the script stops and sends a notification.
- If a normal Treecko appears, the game resets and the process repeats.
- The total number of resets is displayed in the terminal.

To stop the script, simply close the terminal.

---

## How It Works
1. **Window Detection:** The script locates the mGBA window using `wmctrl` and brings it to focus.
2. **Screen Capture:** Uses `mss` to capture the emulator screen.
3. **Battle Detection:** Checks if the battle screen is displayed using `battle.png`.
4. **Image Matching:** Uses OpenCV to match the current screen with `treecko_normal.png` and `treecko_shiny.png`.
5. **Reset Logic:** If Treecko is not shiny, the script resets the game and starts over.
6. **Counter:** The script keeps track of the number of resets.

---

## Configuration
- You can replace `treecko_normal.png` and `treecko_shiny.png` with different images for better accuracy.
- The script assumes `X` is mapped to the A button and `CTRL + R` resets the game.
- If the recognition confidence is too strict, adjust the threshold in:
  ```python
  if max_val_shiny > 0.9:
  ```

---

## Notes
- This script is designed for Linux and requires `wmctrl` and `xdotool` for key inputs.
- Ensure the emulator is in windowed mode with a fixed size.
- The script does not interfere with other applications but requires focus on the emulator.
- If detection fails, verify the template images and screen resolution.