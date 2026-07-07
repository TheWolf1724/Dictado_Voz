#!/usr/bin/env bash
# ============================================================================
#  Instalador de "Dictado por Voz".
#  Idempotente: puedes reejecutarlo; solo hace lo que falte.
#  Tras clonar el repositorio, ejecútalo y deja todo listo para funcionar:
#      git clone https://github.com/TheWolf1724/Dictado_Voz
#      cd Dictado_Voz && ./install.sh
#  Descarga las dependencias DENTRO de la propia carpeta (venv, modelo,
#  nerd-dictation), así el proyecto es auto-contenido y portable.
# ============================================================================
set -euo pipefail

BASE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
MODEL_NAME="vosk-model-es-0.42"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"
ND_REPO="https://github.com/ideasman42/nerd-dictation"

echo "==> Instalando en: $BASE"

# 1) Comprobación de dependencias del sistema (no instala sin tu permiso).
missing=()
for c in python3 git xdotool curl unzip; do
    command -v "$c" >/dev/null 2>&1 || missing+=("$c")
done
command -v parec >/dev/null 2>&1 || command -v pw-cat >/dev/null 2>&1 || missing+=("parec (pipewire-pulse/pulseaudio)")
if [ "${#missing[@]}" -gt 0 ]; then
    echo "!! Faltan dependencias del sistema: ${missing[*]}"
    echo "   Debian/Ubuntu:  sudo apt install python3 python3-venv git xdotool curl unzip pipewire-pulse"
    echo "   (Instálalas y vuelve a ejecutar este script.)"
fi

# 2) Entorno virtual con vosk (motor) + PyQt5 (interfaz).
if [ ! -x "$BASE/venv/bin/python" ]; then
    echo "==> Creando entorno virtual…"
    python3 -m venv "$BASE/venv"
fi
echo "==> Instalando vosk + PyQt5 en el venv…"
"$BASE/venv/bin/pip" install --quiet --upgrade pip
"$BASE/venv/bin/pip" install --quiet vosk PyQt5

# 3) nerd-dictation (captura de audio y escritura de texto).
if [ ! -f "$BASE/nerd-dictation/nerd-dictation" ]; then
    echo "==> Clonando nerd-dictation…"
    git clone --depth 1 "$ND_REPO" "$BASE/nerd-dictation"
else
    echo "==> nerd-dictation ya presente, salto."
fi

# 4) Modelo español grande de Vosk (~1.4 GB).
if [ ! -d "$BASE/models/$MODEL_NAME/am" ]; then
    echo "==> Descargando modelo $MODEL_NAME (~1.4 GB, puede tardar)…"
    mkdir -p "$BASE/models"
    curl -L -o "$BASE/models/$MODEL_NAME.zip" "$MODEL_URL"
    ( cd "$BASE/models" && unzip -q "$MODEL_NAME.zip" && rm -f "$MODEL_NAME.zip" )
else
    echo "==> Modelo ya presente, salto."
fi

# 5) Lanzador de escritorio (aparece como app nativa en el menú).
APPS="$HOME/.local/share/applications"
mkdir -p "$APPS"
cat > "$APPS/dictado-voz.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=Dictado por Voz
GenericName=Dictado por voz offline
Comment=Inicia/para el dictado por voz (Vosk, offline)
Exec=$BASE/dictado.sh
Icon=audio-input-microphone
Terminal=false
Categories=Utility;
Keywords=dictado;voz;voice;dictation;speech;vosk;
StartupNotify=false
DESK
update-desktop-database "$APPS" 2>/dev/null || true
chmod +x "$BASE/dictado.sh"
echo "==> Lanzador instalado en el menú de aplicaciones."

cat <<FIN

======================================================================
 ¡Listo! "Dictado por Voz" instalado y auto-contenido en:
   $BASE

 Cómo usarlo:
   - Búscalo como "Dictado por Voz" en el menú de aplicaciones, o
   - Ejecuta directamente:  $BASE/dictado.sh   (de nuevo para parar)

 Atajo de teclado global (opcional, KDE):
   Preferencias del Sistema > Atajos > Atajos personalizados >
   Nuevo > Comando/URL global. Asigna, p.ej., Ctrl+Shift+H y pon:
       $BASE/dictado.sh
======================================================================
FIN
