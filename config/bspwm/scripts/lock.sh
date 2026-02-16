#!/bin/bash

# Definition of the image file
img=/tmp/screen_locked.png

# Clean up previous image to avoid ghosting/artifacts
rm -f $img

# Take a screenshot
scrot $img

# Blur the image (Standard smooth blur)
# 0x25 is strong enough to obscure text but keeps shapes visible
convert $img -blur 0x25 $img

# Lock screen (Standard i3lock)
# -n: No fork
# -i: Image path
i3lock -n -i $img
