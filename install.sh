#!/bin/bash
set -e

DOTFILES_DIR="$HOME/dotfiles"
BACKUP_DIR="$HOME/dotfiles_backup_$(date +%Y%m%d_%H%M%S)"

log() {
    echo "[INFO] $1"
}

warn() {
    echo "[WARN] $1"
}

# 1. Install dependencies
PACKAGES="bspwm sxhkd polybar picom rofi kitty zsh thunar gtk2-engines-murrine gtk2-engines-pixbuf"

log "Dependencies needed: $PACKAGES"
log "Usually you would run: sudo apt update && sudo apt install -y $PACKAGES"

# 2. Link Dotfiles
create_link() {
    local src="$1"
    local dest="$2"

    if [ -L "$dest" ]; then
        if [ "$(readlink -f "$dest")" == "$(readlink -f "$src")" ]; then
            log "$dest is already correctly linked."
            return
        fi
    fi 

    if [ -e "$dest" ]; then
        log "Backing up existing $dest to $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
        # Only move if destination exists and isn't the link we want
        mv "$dest" "$BACKUP_DIR/"
    fi
    
    mkdir -p "$(dirname "$dest")"
    ln -s "$src" "$dest"
    log "Linked $src -> $dest"
}

# Link Home files
if [ -d "$DOTFILES_DIR/home" ]; then
    find "$DOTFILES_DIR/home" -maxdepth 1 -name ".*" -type f | while read file; do
        filename=$(basename "$file")
        create_link "$file" "$HOME/$filename"
    done
fi

# Link Config directories
if [ -d "$DOTFILES_DIR/config" ]; then
    find "$DOTFILES_DIR/config" -maxdepth 1 -mindepth 1 | while read file; do
        filename=$(basename "$file")
        if [[ "$filename" == "config" || "$filename" == "home" || "$filename" == ".git" ]]; then continue; fi
        create_link "$file" "$HOME/.config/$filename"
    done
fi

log "Installation complete!"
