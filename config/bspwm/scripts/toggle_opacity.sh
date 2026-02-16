#!/bin/bash

# Get the ID of the currently focused window
wid=$(bspc query -N -n)

if [ -z "$wid" ]; then
    exit 1
fi

# Get the current opacity value
opacity=$(xprop -id "$wid" _NET_WM_WINDOW_OPACITY | awk '{print $3}')

# If opacity is not set or is not fully opaque (0xFFFFFFFF = 4294967295)
# Set it to fully opaque. Otherwise, remove the property to use default transparency.
if [ "$opacity" == "4294967295" ]; then
    xprop -id "$wid" -remove _NET_WM_WINDOW_OPACITY
else
    xprop -id "$wid" -f _NET_WM_WINDOW_OPACITY 32c -set _NET_WM_WINDOW_OPACITY 0xFFFFFFFF
fi
