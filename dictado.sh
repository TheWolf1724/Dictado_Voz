#!/usr/bin/env bash
# Dictado por voz (nerd-dictation + Vosk español) — modo toggle con interfaz gráfica.
# Pulsa el atajo para empezar (aparece la pastilla flotante); púlsalo otra vez para
# parar y volcar el texto. También puedes parar con el botón de la propia interfaz.

# Acceso al servidor de audio y a X aunque se lance desde el atajo global.
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DISPLAY="${DISPLAY:-:0}"

# Directorio de este script (para funcionar desde cualquier ubicación).
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"

PY="$HOME/dictado-venv/bin/python"
ND="$HOME/nerd-dictation/nerd-dictation"
GUI="$SCRIPT_DIR/dictado-gui.py"

notify() { command -v notify-send >/dev/null 2>&1 && notify-send -t 1500 -i audio-input-microphone "🎤 Dictado" "$1"; }

# Corrige la ganancia del micro interno para que no sature (evita el "apenas detecta
# palabras"). Sin esto, algunos arranques dejan Capture y "Internal Mic Boost" al
# máximo (+60 dB) y Vosk solo oye distorsión.
fix_mic_gain() {
    for c in 0 1 2 3; do
        if amixer -c "$c" sget 'Internal Mic Boost' >/dev/null 2>&1; then
            amixer -c "$c" sset 'Internal Mic Boost' 0 >/dev/null 2>&1
            amixer -c "$c" sset 'Capture' 80% >/dev/null 2>&1
            break
        fi
    done
}

if pgrep -f "dictado-gui.py" >/dev/null 2>&1 || pgrep -f "dictado-venv/bin/python.* begin" >/dev/null 2>&1; then
    # Ya está en marcha -> parar. La interfaz atiende SIGTERM: llama a
    # `nerd-dictation end` (vuelca el texto final) y se cierra.
    pkill -TERM -f "dictado-gui.py" 2>/dev/null
    # Salvaguarda: si la interfaz no estuviera, cerrar el dictado igualmente.
    if pgrep -f "dictado-venv/bin/python.* begin" >/dev/null 2>&1; then
        "$PY" "$ND" end 2>/dev/null
    fi
    notify "Detenido"
else
    # Arrancar: corrige el micro y lanza la interfaz (que a su vez inicia el dictado).
    # setsid para que sobreviva al cierre de este script lanzado por el atajo.
    fix_mic_gain
    setsid python3 "$GUI" >/dev/null 2>&1 < /dev/null &
fi
