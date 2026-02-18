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
PACKAGES="bspwm sxhkd polybar picom rofi kitty zsh thunar gtk2-engines-murrine gtk2-engines-pixbuf lsd bat xinput xss-lock feh scrot imagemagick libinput-tools libnotify-bin arc-theme papirus-icon-theme firefox-esr"

log "Detected Debian/Ubuntu system. Installing packages..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y $PACKAGES
    
    # Try to install fastfetch if available, otherwise warn
    if apt-cache search fastfetch | grep -q fastfetch; then
        sudo apt install -y fastfetch
    else
        warn "Fastfetch not found in default repos. You might need to install it manually from GitHub releases."
    fi
else
    warn "Package manager 'apt' not found. Please install these manually: $PACKAGES"
fi

# 1.1 Install Powerlevel10k
if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k" ]; then
    log "Installing Powerlevel10k..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k
    log "Powerlevel10k installed to ~/powerlevel10k"
else
    log "Powerlevel10k already installed."
fi



# 1.2 Install Zsh Plugins
mkdir -p "$HOME/.zsh"
if [ ! -d "$HOME/.zsh/zsh-autosuggestions" ]; then
    log "Installing zsh-autosuggestions..."
    git clone https://github.com/zsh-users/zsh-autosuggestions "$HOME/.zsh/zsh-autosuggestions"
fi
if [ ! -d "$HOME/.zsh/zsh-syntax-highlighting" ]; then
    log "Installing zsh-syntax-highlighting..."
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$HOME/.zsh/zsh-syntax-highlighting"
fi

# 1.3 Install Fonts
if [ -d "$DOTFILES_DIR/fonts" ]; then
    log "Installing Fonts..."
    mkdir -p "$HOME/.local/share/fonts"
    cp -rn "$DOTFILES_DIR/fonts/"* "$HOME/.local/share/fonts/"
    if command -v fc-cache &> /dev/null; then
        fc-cache -f
    fi
fi

# 1.4 Install Binaries (Greenclip, etc.)
if [ -d "$DOTFILES_DIR/bin" ]; then
    log "Installing Binaries..."
    mkdir -p "$HOME/.local/bin"
    cp -rn "$DOTFILES_DIR/bin/"* "$HOME/.local/bin/"
    chmod +x "$HOME/.local/bin/"*
fi

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

# Link Wallpapers
if [ -d "$DOTFILES_DIR/wallpapers" ]; then
    log "Linking Wallpapers..."
    mkdir -p "$HOME/Pictures"
    create_link "$DOTFILES_DIR/wallpapers" "$HOME/Pictures/Wallpapers"
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

# Configure Greenclip Static History File (Optional but recommended)
if [ ! -f "$HOME/.config/greenclip.toml" ]; then
    echo '[greenclip]
  history_file = "~/.cache/greenclip.history"
  max_history_length = 50
  max_selection_length_bytes = 1450
  trim_space_from_selection = true
  use_primary_selection_as_input = false
  blacklisted_applications = []
  clipboard_selection_timeout_millis = 1000' > "$HOME/.config/greenclip.toml"
fi
