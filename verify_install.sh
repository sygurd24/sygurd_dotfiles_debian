#!/bin/bash
set -e

echo ">>> VERIFICACIÓN DE INSTALACIÓN DOTFILES <<<"
echo ""

check_file() {
    if [ -f "$1" ]; then
        echo "✅ [OK] Archivo encontrado: $1"
    else
        echo "❌ [ERROR] Archivo faltante: $1"
        EXIT_CODE=1
    fi
}

check_link() {
    if [ -L "$1" ]; then
        echo "✅ [OK] Enlace simbólico correcto: $1 -> $(readlink -f $1)"
    else
        echo "❌ [ERROR] No es un enlace simbólico: $1"
        EXIT_CODE=1
    fi
}

check_command() {
    if command -v "$1" &> /dev/null; then
        echo "✅ [OK] Comando encontrado: $1"
    else
        echo "❌ [ERROR] Comando faltante: $1"
        EXIT_CODE=1
    fi
}

EXIT_CODE=0

echo "--- 1. Archivos Críticos ---"
check_link "$HOME/.config/bspwm"
check_link "$HOME/.config/sxhkd"
check_link "$HOME/.config/polybar"
check_link "$HOME/.zshrc"
check_link "$HOME/.p10k.zsh"
check_link "$HOME/Pictures/Wallpapers"

echo ""
echo "--- 2. Scripts de Utilidad & Wrappers ---"
check_file "$HOME/.config/bspwm/scripts/greenclip_wrapper.sh"
check_file "$HOME/.config/polybar/scripts/volume.sh"
check_file "$HOME/.config/polybar/scripts/brightness.sh"
check_file "$HOME/.config/bspwm/scripts/dynamic_wallpaper.sh"

echo ""
echo "--- 3. Binarios & Herramientas  ---"
check_command "greenclip"
check_command "rofi"
check_command "polybar"
check_command "picom"
check_command "lsd"
check_command "batcat"  # Debian usa batcat por defecto

echo ""
echo "--- 4. Fuentes ---"
if fc-list | grep -q "JetBrainsMono Nerd Font"; then
    echo "✅ [OK] Fuente JetBrainsMono Nerd Font detectada."
else
    echo "❌ [ERROR] Fuente JetBrainsMono Nerd Font NO detectada."
    EXIT_CODE=1
fi

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo ">>> ✅ TODO PARECE CORRECTO. TU SISTEMA ESTÁ LISTO. <<<"
else
    echo ">>> ⚠️ HUBIERON ERRORES. REVISA LA SALIDA ARRIBA. <<<"
fi
