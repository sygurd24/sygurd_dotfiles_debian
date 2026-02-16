#!/usr/bin/env python3
import sys
import os

# Configuration
THERMAL_ZONE = "/sys/class/thermal/thermal_zone0/temp"
STATE_FILE = "/tmp/polybar_temp_state"

# Colors
COLOR_CYAN = (0, 188, 212)   # #00BCD4
COLOR_WHITE = (255, 255, 255) # #FFFFFF
COLOR_YELLOW = (255, 235, 59) # #FFEB3B
COLOR_RED = (244, 67, 54)     # #F44336

ICON = ""

def hex_string(rgb):
    return "#%02x%02x%02x" % rgb

def interpolate(start_color, end_color, t):
    r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
    g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
    b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
    return (r, g, b)

def get_color(temp):
    # 0 - 40: Cyan
    if temp <= 40:
        return COLOR_CYAN
    # 41 - 52: White
    elif temp <= 52:
        return COLOR_WHITE
    # 52 - 75: White -> Yellow
    elif temp <= 75:
        t = (temp - 52) / (75 - 52)
        return interpolate(COLOR_WHITE, COLOR_YELLOW, t)
    # 75 - 90: Yellow -> Red
    elif temp <= 90:
        t = (temp - 75) / (90 - 75)
        return interpolate(COLOR_YELLOW, COLOR_RED, t)
    # > 90: Red
    else:
        return COLOR_RED

def main():
    # Handle click script (toggle state)
    if len(sys.argv) > 1 and sys.argv[1] == "toggle":
        if os.path.exists(STATE_FILE):
             os.remove(STATE_FILE)
        else:
             open(STATE_FILE, 'w').close()
        return

    # Read State
    # Default: Text Hidden (Icon only). Toggle to show text.
    show_text = os.path.exists(STATE_FILE)

    try:
        with open(THERMAL_ZONE, 'r') as f:
            temp_millis = int(f.read().strip())
            temp_c = temp_millis / 1000.0
    except:
        return

    color_rgb = get_color(temp_c)
    color_hex = hex_string(color_rgb)
    
    # Construct Output
    # The whole module is clickable via polybar config, so we just output content
    output = f"%{{F{color_hex}}}{ICON}%{{F-}}"
    
    if show_text:
        output += f" %{{F{color_hex}}}{int(temp_c)}°C%{{F-}}"
        
    print(output)

if __name__ == "__main__":
    main()
