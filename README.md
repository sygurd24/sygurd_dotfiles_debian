# My Debian Dotfiles

This repository contains my personal configuration for Debian, including bspwm, polybar, rofi, zsh, and more.

## Installation

To install these dotfiles on a new system:

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/dotfiles.git ~/dotfiles
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
