#!/bin/bash
# Read from argument or stdin
if [ -n "$1" ]; then
    INPUT="$1"
    echo "Input from Arg"
else
    INPUT=$(cat)
    echo "Input from Stdin"
fi

# Trim whitespace
INPUT=$(echo "$INPUT" | xargs)

# Debug logging (Persistent)
echo "Raw Input: '$INPUT'" >> /tmp/refix_debug.log
echo "Hex Input: $(echo -n "$INPUT" | xxd)" >> /tmp/refix_debug.log

if [[ "$INPUT" =~ ^Image\ (-?[0-9]+)$ ]]; then
    ID="${BASH_REMATCH[1]}"
    IMAGE_PATH="/tmp/greenclip/${ID}.png"
    echo "Matched ID: $ID" >> /tmp/refix_debug.log
    
    if [ -f "$IMAGE_PATH" ]; then
        echo "Image exists, setting selection"
        xclip -selection clipboard -t image/png -i "$IMAGE_PATH"
    else
        echo "Image NOT found: $IMAGE_PATH"
    fi
else
    # Text
    echo "Processing Text"
    # Pipe input to python stdin for safety
    DECODED=$(printf "%s" "$INPUT" | python3 -c "import html, sys; print(html.unescape(sys.stdin.read()), end='')")
    echo "Decoded length: ${#DECODED}"
    printf "%s" "$DECODED" | xclip -selection clipboard || echo "Error calling xclip"
fi

echo "Backgrounding paster"
(
    echo "Paster sleeping"
    sleep 0.2
    echo "Paster invoking xdotool"
    xdotool key --clearmodifiers Ctrl+v
    echo "Paster done"
) &

disown
echo "Script exiting"
exit 0
