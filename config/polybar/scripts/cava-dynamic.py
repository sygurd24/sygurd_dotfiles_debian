#!/usr/bin/env python3
import subprocess
import os
import time
import re

# Cava Dynamic Input Switcher
# Monitors PulseAudio events. When default sink changes, updates Cava config to listen to that sink's monitor.
# Prevents fallback to Microphone.

CONFIG_PATH = os.path.expanduser("~/.config/cava/config")

def get_default_sink_monitor():
    try:
        # Get default sink name
        sink_name = subprocess.check_output(["pactl", "get-default-sink"], text=True).strip()
        
        # Get monitor of that sink
        # Usually it is simply <sink_name>.monitor, but let's verify using list-sinks
        sinks_output = subprocess.check_output(["pactl", "list", "sinks", "short"], text=True)
        
        # Check if sink exists and get monitor name convention?
        # PulseAudio convention: monitor source is named "<sink_name>.monitor"
        monitor_name = f"{sink_name}.monitor"
        return monitor_name
    except:
        return None

def update_cava_config(monitor_name):
    if not monitor_name: return
    
    with open(CONFIG_PATH, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    changed = False
    
    for line in lines:
        if line.strip().startswith("source ="):
            current_source = line.split("=")[1].strip().strip("'").strip('"')
            if current_source != monitor_name:
                new_lines.append(f"source = {monitor_name}\n")
                changed = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    if changed:
        with open(CONFIG_PATH, 'w') as f:
            f.writelines(new_lines)
        # Reload Cava
        subprocess.run(["pkill", "-USR1", "cava"])

def main():
    # Initial setup
    current_monitor = get_default_sink_monitor()
    update_cava_config(current_monitor)
    
    # Listen loop
    process = subprocess.Popen(
        ["pactl", "subscribe"],
        stdout=subprocess.PIPE,
        text=True
    )
    
    for line in process.stdout:
        # Event 'change' on 'server' or 'sink' usually implies default might have changed or sink appeared
        if "sink" in line or "server" in line:
            # Wait a split second for PA to stabilize
            time.sleep(0.5)
            new_monitor = get_default_sink_monitor()
            if new_monitor and new_monitor != current_monitor:
                update_cava_config(new_monitor)
                current_monitor = new_monitor

if __name__ == "__main__":
    main()
