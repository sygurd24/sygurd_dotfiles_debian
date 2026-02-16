#!/bin/bash

# Get current volume
# pactl output format varies. Using grep/awk to extract %
current_vol=$(pactl get-sink-volume @DEFAULT_SINK@ | grep -Po '\d+(?=%)' | head -n 1)

# Launch Yad Scale
# --print-partial allows updating while dragging (if implemented loop)
# But simple approach: set value on exit.
# Better: Use 'pactl' on change.
# scale command: echo value | pactl ...

val=$(yad --scale --min-value=0 --max-value=150 --value="$current_vol" --title="Volume" --width=50 --height=300 --vertical --undecorated --no-buttons --print-partial --close-on-unfocus --mouse --on-top --escape-ok)

# Yad --print-partial prints values to stdout as they change.
# We can pipe this loop?
# Complex.
# Simpler: Execute functionality directly in 'changed' action?
# yad --scale --print-partial | while read vol; do pactl set-sink-volume @DEFAULT_SINK@ ${vol}%; done

# Let's write the piped version.
# Note: we need to handle "close-on-unfocus" to mimic a popup.
# We use a known geometry styling to make it look nice (pop up near mouse or bar).

yad --scale --min-value=0 --max-value=100 --value="$current_vol" --title="Volume" \
    --width=40 --height=200 --vertical --undecorated --no-buttons \
    --print-partial --close-on-unfocus --mouse --on-top --sticky \
    --window-icon="audio-volume-high" | while read vol; do
        # Check if empty (sometimes happens on exit)
        if [[ "$vol" =~ ^[0-9]+$ ]]; then
            pactl set-sink-volume @DEFAULT_SINK@ "${vol}%"
        fi
    done
