#!/bin/bash
set -e

echo "Configuring LightDM and Slick Greeter..."

# Ensure packages are installed
if ! command -v lightdm &> /dev/null; then
    echo "Installing LightDM and Slick Greeter..."
    sudo apt update
    sudo apt install -y lightdm slick-greeter
fi

# Determine Wallpaper
# User mentioned 'pantallabloque_debian.png', let's prioritize that if it exists
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALLPAPER_SRC=""

if [ -f "$REPO_DIR/wallpapers/pantallabloque_debian.png" ]; then
    WALLPAPER_SRC="$REPO_DIR/wallpapers/pantallabloque_debian.png"
elif [ -f "$REPO_DIR/wallpapers/firewatch_noche.png" ]; then
    WALLPAPER_SRC="$REPO_DIR/wallpapers/firewatch_noche.png"
else
    echo "Warning: No suitable wallpaper found in $REPO_DIR/wallpapers."
fi

# Copy wallpaper to system directory to avoid permission issues
if [ -n "$WALLPAPER_SRC" ]; then
    sudo mkdir -p /usr/share/backgrounds/my_setup
    sudo cp "$WALLPAPER_SRC" /usr/share/backgrounds/my_setup/login_wallpaper.png
    WALLPAPER_PATH="/usr/share/backgrounds/my_setup/login_wallpaper.png"
    echo "Wallpaper copied to $WALLPAPER_PATH"
else
    WALLPAPER_PATH="/usr/share/backgrounds/default.png" # Fallback
fi

echo "Writing /etc/lightdm/lightdm.conf..."
cat <<EOF | sudo tee /etc/lightdm/lightdm.conf
[Seat:*]
greeter-session=slick-greeter
user-session=bspwm
EOF

echo "Writing /etc/lightdm/slick-greeter.conf..."
cat <<EOF | sudo tee /etc/lightdm/slick-greeter.conf
[Greeter]
background=$WALLPAPER_PATH
draw-user-backgrounds=false
draw-grid=false
theme-name=Arc-Dark
icon-theme-name=Papirus-Dark
font-name=JetBrainsMono Nerd Font 11
xft-antialias=true
xft-hinting=true
show-clock=true
clock-format=%H:%M
EOF

echo "Enabling LightDM Service..."
sudo systemctl enable lightdm
echo "Done! Reboot to see changes."
