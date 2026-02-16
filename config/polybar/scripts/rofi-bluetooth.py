#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import time
import shutil

# Bluetooth Rofi Manager
# A robust replacement for the bash script to provide a "Manager-like" experience.

ROFI_CMD = ["rofi", "-dmenu", "-p", "Bluetooth", "-format", "s", "-markup-rows"]
# Match the requested theme or similar
THEME_STR = 'window { width: 800px; } listview { lines: 12; } element-text { font: "JetBrainsMono Nerd Font Mono 11"; }'

# Icons (Nerd Fonts to ensure visibility)
ICON_CONNECTED = ""
ICON_PAIRED = " " 
ICON_NEW = " "
ICON_SCAN = "󰍉" # Search icon
ICON_POWER_ON = "  Activar Bluetooth"
ICON_POWER_OFF = "󰂲  Desactivar Bluetooth"

# Device Type Icons (Simple heuristic based on Icon name from info)
DEVICE_ICONS = {
    "audio-card": "",
    "audio-headset": "",
    "audio-headphones": "",
    "input-keyboard": "⌨",
    "input-mouse": "󰍽",
    "phone": "",
    "computer": "💻",
    "default": ""
}

def run_cmd(args):
    try:
        # Run command and wait for it
        return subprocess.check_output(args, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

def get_device_icon(device_info):
    # bluetoothctl info returns "Icon: audio-card" etc
    match = re.search(r"Icon:\s+(\S+)", device_info)
    if match:
        icon_name = match.group(1)
        for key, icon in DEVICE_ICONS.items():
            if key in icon_name:
                return icon
    return DEVICE_ICONS["default"]

def get_devices(scan_cache_path="/tmp/bt_scan_cache"):
    devices = {}
    
    # 1. Get ALL Known Devices (Paired + Connected + Trusted + Others)
    # 'devices' command lists available/known devices
    raw_all = run_cmd(["bluetoothctl", "devices"])
    for line in raw_all.splitlines():
        parts = line.split(" ", 2)
        if len(parts) >= 2:
            mac = parts[1]
            name = parts[2] if len(parts) > 2 else "Unknown"
            
            # Initial assumption: Not connected/paired yet, will check in loop
            devices[mac] = {"name": name, "paired": False, "connected": False, "trusted": False, "info": ""}

    # 2. Get Scanned Devices
    if os.path.exists(scan_cache_path):
        with open(scan_cache_path, "r") as f:
            for line in f:
                # Format: Device MAC Name
                parts = line.strip().split(" ", 2)
                if len(parts) >= 3 and parts[0] == "Device":
                    mac = parts[1]
                    name = parts[2]
                    if mac not in devices:
                        devices[mac] = {"name": name, "paired": False, "connected": False, "info": ""}

    # 3. Check Details & Filter
    final_devices = {}
    
    for mac, data in devices.items():
        info = run_cmd(["bluetoothctl", "info", mac])
        data["info"] = info
        
        is_connected = "Connected: yes" in info
        is_paired = "Paired: yes" in info
        is_trusted = "Trusted: yes" in info
        
        if is_connected: data["connected"] = True
        if is_paired: data["paired"] = True
        if is_trusted: data["trusted"] = True
        
        data["icon"] = get_device_icon(info)
        
        # FILTER RULE: Show if Correlated (Paired/Connected/Trusted) OR in recent Scan Cache
        # How to check if in scan cache? logic above added it to 'devices'.
        # We can try to guess: if not paired/trusted/connected -> implies it came from scan cache OR bluetoothctl devices (ghost).
        # User wants "si desconecto... se siga mostrando".
        # This implies: If it is Known (bluetoothctl devices), show it?
        # But user also wants clean menu.
        # Compromise: Show if Paired OR Connected OR Trusted.
        # AND Show if explicitly presently in Scan Cache (Scan just ran).
        
        # To distinguish Scan Cache items vs Old Ghosts:
        # We don't track origin easily here.
        # But devices coming from 'bluetoothctl devices' might be old ghosts.
        # Devices from 'scan_cache' are fresh.
        # Let's assume if we are looking at it, and it's NOT connected/paired/trusted, we ONLY show it if it was in the scan cache file?
        # Re-read scan cache to be sure?
        # Actually, simpler: Show everything?
        # User complained about "old records".
        # Let's filter: Keep if (Paired or Trusted or Connected) OR (In Scan Cache).
        
        keep = False
        if is_connected or is_paired or is_trusted:
            keep = True
        else:
            # Check if likely from fresh scan logic?
            # We can check if mac was in scan cache text content?
            # This is expensive I/O again? No, we read it.
            pass

        # Since we added keys from scan cache, we want to keep them.
        # But we also added keys from 'bluetoothctl devices' (all known).
        # Sort out ghosts: If from 'devices' but NOT (P/C/T) -> Ghost?
        # Most "Ghosts" are unpaired devices seen long ago.
        # bluetoothctl devices keeps them? Yes.
        # So we should validly filter them out if not P/C/T.
        # But how to know if it's currently visible (scanned)?
        # Only if we scanned recently.
        
        # Simplified Logic:
        # We only added keys from 'devices' (history) and 'scan_cache' (fresh).
        # We want to keep ALL 'scan_cache' (fresh).
        # We want to keep 'devices' ONLY if P/C/T.
        # But 'devices' dict is merged.
        
        # Let's assume we keep it if:
        # 1. Connect/Paired/Trusted
        # 2. OR it is known to be in the scan results?
        
        # Re-reading scan cache content to check explicit presence
        in_scan = False
        if os.path.exists(scan_cache_path):
             with open(scan_cache_path) as sc:
                 if mac in sc.read():
                     in_scan = True
        
        if keep or in_scan:
             final_devices[mac] = data

    return final_devices

def main_menu():
    # Check Power
    power_state = run_cmd(["bluetoothctl", "show"])
    if "Powered: yes" not in power_state:
        # Power is OFF
        print(f"{ICON_POWER_ON}")
        return

    # Power is ON
    print(f"{ICON_POWER_OFF}")
    print(f"{ICON_SCAN}  Escanear (Descubrir nuevos)")
    
    # List Devices
    devices = get_devices()
    
    # Sort: Connected first, then Paired, then Scanned
    sorted_macs = sorted(devices.keys(), key=lambda x: (
        not devices[x]["connected"], 
        not devices[x]["paired"], 
        devices[x]["name"]
    ))

    for mac in sorted_macs:
        d = devices[mac]
        
        # Status Logic:
        # Connected = Check (Green)
        # Trusted (but not con) = Shield/Bolt (Blue/Yellow)
        # Paired (but not trusted) = Cloud
        # New = Star/Plus
        
        if d["connected"]:
            status_icon = ICON_CONNECTED
        elif d["trusted"]:
            status_icon = " " # Trusted Shield (or ⚡)
        elif d["paired"]:
            status_icon = ICON_PAIRED
        else:
            status_icon = ICON_NEW
            
        dev_icon = d.get("icon", "")
        name = d["name"]
        
        # Pango formatting
        # Status Icon | Device Icon | Name (Bold) | MAC (Small/Transparent)
        display = f"{status_icon}   {dev_icon}  <b>{name}</b> <span size='x-small' alpha='50%'>{mac}</span>"
        print(display)

def handle_scan():
    # Clean old cache
    cache_file = "/tmp/bt_scan_cache"
    
    # Notify
    subprocess.Popen(["notify-send", "Bluetooth", "Escaneando (3s)...", "-i", "bluetooth"])
    
    # Create Expect script provided by user feedback that works
    expect_script_path = "/tmp/bt_scan.exp"
    expect_script_content = """#!/usr/bin/expect -f
set timeout 4
spawn bluetoothctl
expect "#"
send "scan on\\r"
expect "Discovery started"
sleep 3
send "scan off\\r"
expect "Discovery stopped"
send "exit\\r"
"""
    with open(expect_script_path, "w") as f:
        f.write(expect_script_content)
    
    os.chmod(expect_script_path, 0o755)
    
    # Run the expect script synchronously
    subprocess.call(expect_script_path, shell=True)
    
    # Now dump devices to cache
    output = run_cmd(["bluetoothctl", "devices"])
    with open(cache_file, "w") as f:
        f.write(output)
    
    subprocess.Popen(["notify-send", "Bluetooth", "Escaneo finalizado", "-i", "bluetooth"])

def device_submenu(mac, name):
    # Check current status
    info = run_cmd(["bluetoothctl", "info", mac])
    connected = "Connected: yes" in info
    paired = "Paired: yes" in info
    trusted = "Trusted: yes" in info
    
    options = []
    
    if connected:
        options.append(f"󰅖 Desconectar")
    else:
        options.append(f"󰂱 Conectar")
        
    if paired or trusted:
        options.append(f" Desvincular (Unpair)")
    else:
        options.append(f" Vincular (Pair)")
        
    if trusted:
        options.append(f" Quitar Confianza (Untrust)")
    else:
        options.append(f" Confiar (Trust)")
        
    options.append(f" Volver")
    
    # Print options for Rofi
    for opt in options:
        print(opt)

if __name__ == "__main__":
    # Clean cache on startup (Session start)
    if len(sys.argv) == 1:
        # First launch - Clear cache
        if os.path.exists("/tmp/bt_scan_cache"):
            os.remove("/tmp/bt_scan_cache")
    
    # State tracking
    MAC = None 
    
    while True:
        # Generate items
        items = []
        
        # Redirect stdout
        from io import StringIO
        capture = StringIO()
        sys.stdout = capture
        
        PROMPT = "Bluetooth"
        
        if MAC:
            # Submenu
            device_submenu(MAC, "Device")
            PROMPT = f"Action ({MAC})"
        else:
            # Main Menu
            main_menu()
            
        sys.stdout = sys.__stdout__ # Restore
        menu_str = capture.getvalue()
        
        # Run Rofi
        try:
            cmd = ROFI_CMD + ["-theme-str", THEME_STR, "-p", PROMPT]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            chosen, _ = proc.communicate(input=menu_str)
            
            if proc.returncode != 0:
                # Cancel / Escape
                if MAC:
                    MAC = None # Go back to main
                    continue
                else:
                    break # Exit app
            
            chosen = chosen.strip()
            if not chosen: break
            
            # Extract Value: JUST USE CHOSEN STRING
            value = chosen
                
            # Actions
            if value.startswith(ICON_POWER_ON):
                run_cmd(["bluetoothctl", "power", "on"])
                time.sleep(0.2) 
            elif value.startswith(ICON_POWER_OFF):
                run_cmd(["bluetoothctl", "power", "off"])
                time.sleep(0.2)
            elif value.startswith(ICON_SCAN):
                handle_scan()
            elif value.endswith(" Volver"):
                MAC = None
            elif "󰅖 Desconectar" in value:
                run_cmd(["bluetoothctl", "disconnect", MAC])
                subprocess.Popen(["notify-send", "Bluetooth", f"Desconectado: {MAC}", "-i", "bluetooth"])
                # Close menu as requested by user
                break
            elif "󰂱 Conectar" in value:
                subprocess.Popen(["notify-send", "Bluetooth", f"Conectando a {MAC}...", "-i", "bluetooth"])
                res = subprocess.run(["bluetoothctl", "connect", MAC], capture_output=True, text=True)
                if res.returncode == 0:
                    subprocess.Popen(["notify-send", "Bluetooth", f"Conectado: {MAC}", "-i", "bluetooth", "-u", "normal"])
                    # Auto-trust so it persists in list even if disconnected
                    run_cmd(["bluetoothctl", "trust", MAC])
                    # Close menu as requested by user
                    break
                else:
                    err = res.stderr.strip() or res.stdout.strip()
                    subprocess.Popen(["notify-send", "Bluetooth", f"Falló conexión: {err}", "-i", "dialog-error", "-u", "critical"])
                    MAC = None 
            elif " Desvincular" in value:
                run_cmd(["bluetoothctl", "remove", MAC])
                subprocess.Popen(["notify-send", "Bluetooth", f"Desvinculado: {MAC}", "-i", "bluetooth"])
                MAC = None # Device gone, return to main
            elif " Vincular" in value:
                subprocess.Popen(["notify-send", "Bluetooth", f"Vinculando {MAC}...", "-i", "bluetooth"])
                res = subprocess.run(["bluetoothctl", "pair", MAC], capture_output=True, text=True)
                if res.returncode == 0:
                    subprocess.Popen(["notify-send", "Bluetooth", f"Vinculado: {MAC}", "-i", "bluetooth", "-u", "normal"])
                    # Auto-trust on pair
                    run_cmd(["bluetoothctl", "trust", MAC])
                    
                    # Auto-Connect attempt
                    subprocess.Popen(["notify-send", "Bluetooth", f"Auto-conectando...", "-i", "bluetooth"])
                    run_cmd(["bluetoothctl", "connect", MAC])
                else:
                    err = res.stderr.strip() or res.stdout.strip()
                    subprocess.Popen(["notify-send", "Bluetooth", f"Falló vinculación: {err}", "-i", "dialog-error", "-u", "critical"])
                    MAC = None # Go back on error
                
                # Success path: Stay in submenu
                time.sleep(1.0) # Longer wait for Pair+Trust+Connect sequence
            elif " Quitar Confianza" in value:
                run_cmd(["bluetoothctl", "untrust", MAC])
                subprocess.Popen(["notify-send", "Bluetooth", f"Confianza retirada: {MAC}", "-i", "bluetooth"])
                time.sleep(0.5)
            elif " Confiar" in value:
                run_cmd(["bluetoothctl", "trust", MAC])
                subprocess.Popen(["notify-send", "Bluetooth", f"Dispositivo de Confianza: {MAC}", "-i", "bluetooth"])
                time.sleep(0.5)
            else:
                # Device Selection
                # Extract MAC using regex
                match = re.search(r"([0-9A-F]{2}:){5}[0-9A-F]{2}", value)
                if match:
                    MAC = match.group(0)
                    
        except KeyboardInterrupt:
            break
            
        time.sleep(0.1)
