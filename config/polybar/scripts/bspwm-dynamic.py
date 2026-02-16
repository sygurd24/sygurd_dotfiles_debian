#!/usr/bin/env python3
import subprocess
import json
import socket
import os
import sys
import math

# Dynamic BSPWM for Polybar
# Features:
# - Heatmap color for occupied workspaces (White -> Red) based on window count.
# - Consistent icons with existing config (Filled circle, Open circle, etc.)

# Colors
COLOR_FOCUSED = "#00BCD4" # Primary
COLOR_URGENT = "#cb0e0eff" # Alert
COLOR_EMPTY = "#333333" # Disbaled
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)

# Icons
ICON_FOCUSED = ""
ICON_OCCUPIED = ""
ICON_EMPTY = ""
ICON_URGENT = ""

def hex_to_rgb(hex_col):
    h = hex_col.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

def interpolate_color(count):
    # Map count 1..5 to White..Red
    # 1 -> 0% Red
    # 5 -> 100% Red
    
    if count <= 1:
        return rgb_to_hex(COLOR_WHITE)
    if count >= 5:
        return rgb_to_hex(COLOR_RED)
        
    # Steps: 2, 3, 4
    # Progress:
    # 1 -> 0.0
    # 2 -> 0.25
    # 3 -> 0.5
    # 4 -> 0.75
    # 5 -> 1.0
    
    t = (count - 1) / 4.0
    
    r = int(COLOR_WHITE[0] + (COLOR_RED[0] - COLOR_WHITE[0]) * t)
    g = int(COLOR_WHITE[1] + (COLOR_RED[1] - COLOR_WHITE[1]) * t)
    b = int(COLOR_WHITE[2] + (COLOR_RED[2] - COLOR_WHITE[2]) * t)
    
    return rgb_to_hex((r, g, b))

def get_state():
    try:
        # Check if bspwm socket exists
        # We use 'bspc wm -d' to get full JSON dump
        output = subprocess.check_output(["bspc", "wm", "-d"], text=True)
        dump = json.loads(output)
        return dump
    except Exception as e:
        return None

def generate_polybar_string(dump):
    if not dump: return ""
    
    monitors = dump.get("monitors", [])
    
    # Sort desktops? Usually they are ordered.
    # We want to iterate desktops in global order or per monitor?
    # Polybar internal/bspwm usually shows all or per monitor.
    # We will show ALL for simplicity, or filter if requested.
    
    output = []
    
    # We need to know which desktop is focused globally or per monitor
    # dump['focusedMonitorId']
    
    for mon in monitors:
        focused_desktop_id = mon['focusedDesktopId']
        
        for desk in mon['desktops']:
            name = desk['name']
            
            # State detection
            is_focused = (desk['id'] == focused_desktop_id) and (mon['id'] == dump['focusedMonitorId'])
            # Actually focusedDesktopId is per monitor. 
            # If (monitor is focused) AND (desktop is focused), then Global Focus.
            # But usually we highlight the focused desktop on EACH monitor?
            # Polybar 'internal/bspwm' highlights focused desktop of the monitor the bar is on.
            # Since this is a custom script running ONCE, it displays globally?
            # Polybar custom script module has no knowledge of which monitor it is on easily.
            # We will render ALL desktops.
            
            # Check occupied
            root = desk.get('root')
            window_count = 0
            
            if root:
                # Count leaves (windows) recursively?
                # Faster: bspc query -N -n .window -d NAME | wc -l
                # But calling bspc for each desktop is slow.
                # Let's verify if 'root' implies occupied. Yes.
                # To get count, we need to traverse JSON or use bspc.
                # Traversing JSON is instant.
                
                def count_windows(node):
                    c = 0
                    if not node: return 0
                    if node.get('client'): c += 1
                    c += count_windows(node.get('firstChild'))
                    c += count_windows(node.get('secondChild'))
                    return c
                
                window_count = count_windows(root)
            
            is_occupied = (window_count > 0)
            is_urgent = False # Need to check separate urgency flags? 'client.urgent'
            # Urgency in JSON matches 'urgent' property in client?
            # We skip detailed urgency check for speed unless requested.
            
            # Icon & Color
            icon = ICON_EMPTY
            color = COLOR_EMPTY
            padding = 1
            
            # Priority: Focused > Urgent > Occupied > Empty
            if is_focused:
                icon = ICON_FOCUSED
                color = COLOR_FOCUSED
            elif is_occupied:
                icon = ICON_OCCUPIED
                # Heatmap Logic
                color = interpolate_color(window_count)
            else:
                icon = ICON_EMPTY
                color = COLOR_EMPTY # Gray ring
            
            # Format
            # Click action: focus desktop
            # %{A1:bspc desktop -f NAME:} ... %{A}
            
            item = f"%{{A1:bspc desktop -f {name}:}}%{{F{color}}}{icon}%{{F-}}%{{A}}"
            
            # Add padding
            item = f" {item} "
            
            output.append(item)
            
    return "".join(output)

def main():
    # Listen to events
    # We can perform a loop with 'bspc subscribe report' which is efficient
    
    process = subprocess.Popen(
        ["bspc", "subscribe", "report"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    # Initial print
    print(generate_polybar_string(get_state()), flush=True)
    
    for line in process.stdout:
        # On any report event, re-generate string
        # 'report' covers focus change, window open/close/move
        print(generate_polybar_string(get_state()), flush=True)

if __name__ == "__main__":
    main()
