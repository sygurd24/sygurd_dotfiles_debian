#!/bin/bash

# Opciones
shutdown=" Apagar"
reboot=" Reiniciar"
lock=" Bloquear"
suspend=" Suspender"
hibernate=" Hibernar"
logout=" Cerrar Sesión"

# Mostrar menú
selected_option=$(echo "$lock
$shutdown
$reboot
$suspend
$hibernate
$logout" | rofi -dmenu -i -p "Energía" -config ~/.config/rofi/config.rasi)

# Acciones
if [ "$selected_option" == "$shutdown" ]; then
    systemctl poweroff
elif [ "$selected_option" == "$reboot" ]; then
    systemctl reboot
elif [ "$selected_option" == "$lock" ]; then
    /home/sygurd/.config/bspwm/scripts/lock.sh
elif [ "$selected_option" == "$logout" ]; then
    bspc quit
elif [ "$selected_option" == "$suspend" ]; then
    systemctl suspend
elif [ "$selected_option" == "$hibernate" ]; then
    systemctl hibernate
fi
