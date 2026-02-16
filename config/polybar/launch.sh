#!/usr/bin/env bash

# Terminar las instancias de barra que ya se estén ejecutando
killall -q polybar

# Esperar a que los procesos se hayan cerrado
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# Lanzar la barra llamada "example" (definida en el config.ini)
polybar example &


# Kill existing temperature daemon if running
pkill -f temperature-daemon.sh

# Start temperature daemon
~/.config/polybar/scripts/temperature-daemon.sh &

echo "Polybar lanzada..."
