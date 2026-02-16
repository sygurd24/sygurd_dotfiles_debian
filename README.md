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
-   Install necessary dependencies (bspwm, polybar, etc.).
-   Backup existing configuration files.
-   Create symlinks from `~/dotfiles` to your home directory.

## Structure

-   `home/`: Top-level dotfiles (e.g., `.zshrc`, `.Xresources`).
-   `config/`: Directories/files for `~/.config/` (e.g., `bspwm/`, `polybar/`).
-   `install.sh`: Script to safe-install on a new machine.
-   `migrate.sh`: Script used to migrate the initial config (you likely won't need this again).
