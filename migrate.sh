#!/bin/bash
set -e

DOTFILES_DIR="$HOME/dotfiles"
CONFIG_DIR="$HOME/.config"
BACKUP_DIR="$HOME/dotfiles_backup_$(date +%Y%m%d_%H%M%S)"

# Move dotfiles directory checks to avoid recursion
if [[ "$DOTFILES_DIR" == "$PWD" ]]; then
    echo "Warning: Running script inside destination directory."
fi

log() {
    echo "[INFO] $1"
}

move_and_link() {
    local src="$1"
    local dest_rel="$2"
    local dest="$DOTFILES_DIR/$dest_rel"

    if [ -e "$src" ]; then
        if [ -L "$src" ]; then
            log "$src is already a symlink. Skipping."
            return
        fi

        log "Processing $src..."
        
        # Ensure parent directory exists within dotfiles
        mkdir -p "$(dirname "$dest")"
        
        # Move to dotfiles
        mv "$src" "$dest"
        
        # Create symlink back
        ln -s "$dest" "$src"
        
        log "Moved $src to $dest and linked back."
    else
        log "$src does not exist. Skipping."
    fi
}

# Create necessary directories
mkdir -p "$DOTFILES_DIR/home"
mkdir -p "$DOTFILES_DIR/config"

# Home directory files
move_and_link "$HOME/.zshrc" "home/.zshrc"
move_and_link "$HOME/.p10k.zsh" "home/.p10k.zsh"
move_and_link "$HOME/.Xresources" "home/.Xresources"
move_and_link "$HOME/.vimrc" "home/.vimrc" 

# Config directories/files
# Window Manager & Display
move_and_link "$CONFIG_DIR/bspwm" "config/bspwm"
move_and_link "$CONFIG_DIR/sxhkd" "config/sxhkd"
move_and_link "$CONFIG_DIR/polybar" "config/polybar"
move_and_link "$CONFIG_DIR/picom" "config/picom"
move_and_link "$CONFIG_DIR/rofi" "config/rofi"

# Terminal & Shell related
move_and_link "$CONFIG_DIR/kitty" "config/kitty"
move_and_link "$CONFIG_DIR/fastfetch" "config/fastfetch"
move_and_link "$CONFIG_DIR/alacritty" "config/alacritty"

# Theming & Desktop
move_and_link "$CONFIG_DIR/gtk-3.0" "config/gtk-3.0"
move_and_link "$CONFIG_DIR/Thunar" "config/Thunar"
move_and_link "$CONFIG_DIR/mimeapps.list" "config/mimeapps.list"

echo "Migration complete. Current dotfiles are now linked to $DOTFILES_DIR"
