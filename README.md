# My Debian Dotfiles

This repository contains my personal configuration for Debian, including:
- **Window Manager**: `bspwm` + `sxhkd` (shortcuts)
- **Status Bar**: `polybar`
- **Themes**: `Arc-Dark` (GTK) + `Papirus-Dark` (Icons) + `JetBrainsMono Nerd Font`
- **Terminal**: `kitty` + `zsh` + `powerlevel10k` theme + plugins (autosuggestions, syntax-highlighting)
- **Launcher**: `rofi`

## Installation

To install these dotfiles on a new system:

1.  Clone the repository:
    ```bash
    git clone https://github.com/sygurd24/sygurd_dotfiles_debian.git ~/dotfiles
    ```
2.  Run the installation script:
    ```bash
    cd ~/dotfiles
    chmod +x install.sh
    ./install.sh
    ```

The `install.sh` script will:
-   **Automatically install** necessary dependencies (bspwm, polybar, kitty, rofi, zsh, etc.) using `apt`.
-   Backup existing configuration files.
-   Create symlinks from `~/dotfiles` to your home directory.

## Structure

-   `home/`: Top-level dotfiles (e.g., `.zshrc`, `.Xresources`).
-   `config/`: Directories/files for `~/.config/` (e.g., `bspwm/`, `polybar/`).
-   `install.sh`: Script to automatically setup the environment on a new machine.
-   `setup_hibernate.sh`: Utility script to configure swap and hibernation (run manually if needed).

## Hibernation
If you want to enable hibernation (suspend-to-disk):
```bash
sudo ./setup_hibernate.sh
```
The script will **automatically detect your RAM** and recommend a swap size (usually RAM + 1GB). It will ask you for confirmation.

*Note: This script modifies GRUB and swap settings.*
