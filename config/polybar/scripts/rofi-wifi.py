#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil

# Rofi Wifi Manager for Polybar
# Advanced logic for Submenus and Actions

# Theme (Same as Bluetooth for consistency)
THEME_STR = 'window { width: 800px; } listview { lines: 12; } element-text { font: "JetBrainsMono Nerd Font Mono 11"; }'

# Icons
ICON_CONNECTED = ""
ICON_SAVED = " " # Saved but not connected
ICON_LOCK = ""
ICON_OPEN = ""

def run_cmd(args):
    try:
        return subprocess.check_output(args, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

def get_signal_icon(strength):
    try:
        s = int(strength)
        if s >= 80: return "󰤨"
        elif s >= 60: return "󰤥"
        elif s >= 40: return "󰤢"
        elif s >= 20: return "󰤟"
        else: return "󰤯"
    except:
        return "󰤯"

def get_saved_connections():
    # Returns list of saved connection names
    raw = run_cmd(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"])
    saved = set()
    for line in raw.splitlines():
        if ":802-11-wireless" in line:
            name = line.split(":")[0]
            saved.add(name)
    return saved

def get_networks():
    networks = {}
    
    # Get Active SSID
    active_ssid = run_cmd(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"])
    active_ssid_name = ""
    for line in active_ssid.splitlines():
        if line.startswith("yes:"):
            active_ssid_name = line.split(":")[1]
            break

    # Get Saved List
    saved_connections = get_saved_connections()

    # Scan List
    # SSID, SECURITY, SIGNAL, BARS
    raw = run_cmd(["nmcli", "-t", "-f", "SSID,SECURITY,SIGNAL", "device", "wifi", "list"])
    
    # Process
    for line in raw.splitlines():
        # Clean colons
        # nmcli -t escapes colons with \, but here we split simply.
        # This layout is consistent mostly.
        parts = line.split(":")
        if len(parts) < 3: continue
        
        ssid = parts[0]
        if not ssid: continue # Skip hidden
        
        # Determine security
        security = "OPEN"
        if len(parts) >= 2 and parts[1]:
            security = parts[1]
        
        signal = "0"
        if len(parts) >= 3:
            signal = parts[2]
            
        # Is Active?
        is_active = (ssid == active_ssid_name)
        
        # Is Saved?
        is_saved = (ssid in saved_connections)
        
        # Prioritize Active, then Saved, then Strongest
        # We store just one entry per SSID (strongest usually comes first in nmcli list)
        if ssid not in networks:
            networks[ssid] = {
                "ssid": ssid,
                "security": security,
                "signal": signal,
                "active": is_active,
                "saved": is_saved
            }
            
    return networks

def submenu(net):
    ssid = net["ssid"]
    options = []
    
    if net["active"]:
        options.append(f"󰅖 Desconectar")
        options.append(f" Olvidar (Borrar perfil)")
    elif net["saved"]:
        options.append(f"󰂱 Conectar")
        options.append(f" Olvidar (Borrar perfil)")
    else:
        # New Network
        options.append(f"󰂱 Conectar")
        
    options.append(f" Volver")
    
    # Run Rofi Submenu
    menu_str = "\n".join(options)
    prompt = f"Action ({ssid})"
    
    cmd = ["rofi", "-dmenu", "-theme-str", THEME_STR, "-p", prompt, "-format", "s"]
    res = subprocess.run(cmd, input=menu_str, text=True, capture_output=True)
    
    if res.returncode != 0: return # Cancel
    
    choice = res.stdout.strip()
    
    if "Desconectar" in choice:
        # Use connection down instead of device disconnect to avoid needing interface name (wlan0)
        run_cmd(["nmcli", "connection", "down", "id", ssid]) 
        subprocess.Popen(["notify-send", "WiFi", f"Desconectado de {ssid}", "-i", "network-wireless-disconnected"])
        
    elif "Conectar" in choice:
        if net["saved"]:
            # Known network, just up
            subprocess.Popen(["notify-send", "WiFi", f"Conectando a {ssid}...", "-i", "network-wireless-acquiring"])
            res = subprocess.run(["nmcli", "connection", "up", "id", ssid], capture_output=True, text=True)
            if res.returncode == 0:
                subprocess.Popen(["notify-send", "WiFi", f"Conectado: {ssid}", "-i", "network-wireless-connected"])
            else:
                 subprocess.Popen(["notify-send", "WiFi", f"Error: {res.stderr}", "-i", "dialog-error"])
        else:
            # New Network -> Password?
            # Check security
            if "WPA" in net["security"] or "WEP" in net["security"]:
                # Ask Password
                pass_cmd = ["rofi", "-dmenu", "-theme-str", THEME_STR, "-p", f"Password for {ssid}", "-password"]
                pass_res = subprocess.run(pass_cmd, input="", text=True, capture_output=True)
                password = pass_res.stdout.strip()
                
                if not password: return
                
                subprocess.Popen(["notify-send", "WiFi", f"Conectando a {ssid}...", "-i", "network-wireless-acquiring"])
                res = subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password], capture_output=True, text=True)
                
                if res.returncode == 0:
                    subprocess.Popen(["notify-send", "WiFi", f"Conectado: {ssid}", "-i", "network-wireless-connected"])
                else:
                    subprocess.Popen(["notify-send", "WiFi", f"Error: {res.stderr}", "-i", "dialog-error"])
            else:
                # Open Network
                subprocess.Popen(["notify-send", "WiFi", f"Conectando a {ssid} (Open)...", "-i", "network-wireless-acquiring"])
                res = subprocess.run(["nmcli", "device", "wifi", "connect", ssid], capture_output=True, text=True)
                if res.returncode == 0:
                     subprocess.Popen(["notify-send", "WiFi", f"Conectado: {ssid}", "-i", "network-wireless-connected"])

    elif "Olvidar" in choice:
        run_cmd(["nmcli", "connection", "delete", "id", ssid])
        subprocess.Popen(["notify-send", "WiFi", f"Olvidada: {ssid}", "-i", "network-wireless-disconnected"])

def main():
    networks = get_networks()
    
    # Sort
    # Active First, then Saved, then Signal Strength
    # Signal is string "80", convert to int
    sorted_ssids = sorted(networks.keys(), key=lambda x: (
        not networks[x]["active"],
        not networks[x]["saved"],
        -int(networks[x]["signal"])
    ))
    
    rofi_rows = []
    
    toggle_line = "󰖩  Enable/Disable Wi-Fi"
    rofi_rows.append(toggle_line)
    
    for ssid in sorted_ssids:
        net = networks[ssid]
        
        # Icon Logic
        sig_icon = get_signal_icon(net["signal"])
        
        status = ""
        if net["active"]:
            status = ICON_CONNECTED
        elif net["saved"]:
            status = ICON_SAVED
        else:
            status = "  "
            
        sec_icon = ICON_LOCK if ("WPA" in net["security"] or "WEP" in net["security"]) else ICON_OPEN
        
        # Format
        # Status | Signal | SSID | Security
        display = f"{status}  {sig_icon}   <b>{ssid}</b> <span size='small' alpha='50%'>{sec_icon} {net['signal']}%</span>"
        rofi_rows.append(display)
        
    input_str = "\n".join(rofi_rows)
    
    cmd = ["rofi", "-dmenu", "-theme-str", THEME_STR, "-p", "WiFi", "-format", "s", "-markup-rows"]
    res = subprocess.run(cmd, input=input_str, text=True, capture_output=True)
    
    if res.returncode != 0: return
    
    chosen = res.stdout.strip()
    
    if not chosen: return
    
    if "Enable/Disable" in chosen:
        # Simple Toggle
        status = run_cmd(["nmcli", "radio", "wifi"])
        if "enabled" in status:
            run_cmd(["nmcli", "radio", "wifi", "off"])
            subprocess.Popen(["notify-send", "WiFi", "Desactivado", "-i", "network-wireless-disconnected"])
        else:
            run_cmd(["nmcli", "radio", "wifi", "on"])
            subprocess.Popen(["notify-send", "WiFi", "Activado", "-i", "network-wireless-connected"])
        return

    # Extract SSID
    # We used Pango markup, so chosen string contains it.
    # Regex to extract <b>SSID</b>
    # Format: ... <b>{ssid}</b> ...
    import re
    match = re.search(r"<b>(.*?)</b>", chosen)
    if match:
        ssid = match.group(1)
        if ssid in networks:
            submenu(networks[ssid])

if __name__ == "__main__":
    main()
