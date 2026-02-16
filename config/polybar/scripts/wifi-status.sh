#!/bin/bash

# Wi-Fi Status for Polybar
# Logic:
# - Radio Off: Gray Strikethrough
# - Disconnected (But On): Standard Empty Icon
# - Connected: Bright Green-Cyan Icon (Signal Strength)

# 1. Check Radio Status
radio_status=$(nmcli radio wifi)

if [ "$radio_status" = "disabled" ]; then
    # Gray Strikethrough
    echo "%{F#707880}󰖪 %{F-}"
    exit 0
fi

# 2. Check Connection
# Format nmcli -t: active:signal
active_info=$(nmcli -t -f active,signal dev wifi 2>/dev/null | grep '^yes')

if [ -n "$active_info" ]; then
    signal=$(echo "$active_info" | cut -d: -f2)
    
    # Map input signal to icon
    if [ "$signal" -ge 80 ]; then
        icon="󰤨"
    elif [ "$signal" -ge 60 ]; then
        icon="󰤥"
    elif [ "$signal" -ge 40 ]; then
        icon="󰤢"
    elif [ "$signal" -ge 20 ]; then
        icon="󰤟"
    else
        icon="󰤯"
    fi
    
    # Connected -> Bright Green-Cyan (#00FFB3)
    echo "%{F#00FFB3}$icon%{F-}"
else
    # Disconnected (But On) -> Standard Color (Inherited), Empty Icon
    echo "󰤯"
fi
