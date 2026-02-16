#!/usr/bin/env python3
import sys
import html
import subprocess
import os

# Robust wrapper for Greenclip in Rofi
# - Handles special characters safely
# - Outputs icon path for images
# - Displays standard text for text entries

def get_greenclip_history():
    greenclip_path = os.path.expanduser("~/.local/bin/greenclip")
    try:
        # Run greenclip print
        result = subprocess.check_output([greenclip_path, "print"], text=True)
        return result.splitlines()
    except Exception as e:
        return [f"Error running greenclip: {e}"]

def main():
    history = get_greenclip_history()
    
    for line in history:
        if not line:
            continue
            
        if line.startswith("image/png"):
            parts = line.split()
            if len(parts) >= 2:
                img_id = parts[-1] 
                # Display "Image" or just the ID but cleaner, and add the icon
                # User liked "small images", so we just need the icon path
                print(f'Image {img_id}\0icon\x1f/tmp/greenclip/{img_id}.png')
        else:
            # Escape text to prevent Rofi markup errors (invisible items bug)
            escaped_text = html.escape(line)
            print(escaped_text)

if __name__ == "__main__":
    main()
