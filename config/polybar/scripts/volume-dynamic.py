#!/usr/bin/env python3
import subprocess
import re
import sys

# Dynamic Volume for Polybar
# Colors:
# - 0-99%: Normal
# - 100-149%: Pastel Orange
# - 150%: Pastel Red

COLOR_NORMAL = "" # Inherit
COLOR_WARN = "%{F#FFC07F}" # Pastel Orange
COLOR_CRIT = "%{F#FF7A7A}" # Pastel Red
COLOR_MUTED = "%{F#707880}" # Gray
COLOR_END = "%{F-}"

def get_volume_info():
    try:
        # Get default sink volume
        # Output format: "Volume: front-left: 65536 / 100% / 0.00 dB,   front-right: 65536 / 100% / 0.00 dB"
        # We need to find the percentage.
        
        # Check Mute first
        mute_out = subprocess.check_output(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], text=True).strip()
        if "yes" in mute_out:
            return f"{COLOR_MUTED}muted{COLOR_END}"
            
        vol_out = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], text=True).strip()
        
        # Extract percentage (take the first one found, assuming channels match)
        match = re.search(r"(\d+)%", vol_out)
        if match:
            vol = int(match.group(1))
            
            # Icon always Turquoise (#00BCD4)
            icon_str = "%{F#00BCD4}  %{F-}"
            color = COLOR_NORMAL
            
            if vol > 150:
                color = COLOR_CRIT
            elif vol > 100:
                color = COLOR_WARN
                
            return f"{icon_str}{color}{vol}%{COLOR_END}"
            
        return "N/A"
    except Exception as e:
        return "Err"

def main():
    # Initial print
    print(get_volume_info(), flush=True)
    
    # Listen to events
    process = subprocess.Popen(
        ["pactl", "subscribe"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    for line in process.stdout:
        # We only care about sink/server changes
        if "sink" in line or "server" in line:
            print(get_volume_info(), flush=True)

if __name__ == "__main__":
    main()
