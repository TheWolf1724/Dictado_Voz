# 🎙️ Dictado por Voz

**Dictado por voz offline, en español, para Linux.** Habla y el texto aparece en
cualquier aplicación. Privado, gratuito y sin conexión: tu voz nunca sale de tu
ordenador.

<p align="center">
  <img src="images/grabando.png" alt="Interfaz grabando" width="300"><br>
  <em>Burbuja flotante que te avisa en todo momento de que se está grabando.</em>
</p>

---

## ✨ Características

- 🎙️ **Dicta en cualquier campo de texto** — escribe según hablas, en la ventana que tengas activa.
- 🔒 **100% offline y privado** — todo el reconocimiento ocurre en tu equipo (motor [Vosk](https://alphacephei.com/vosk/)). No se envía audio a ningún servidor.
- 🟢 **Interfaz flotante clara** — una burbuja siempre visible te indica cuándo está *cargando* y cuándo está *grabando*, con botón para parar. No roba el foco del teclado.
- ✍️ **Puntuación por voz y mayúsculas automáticas** — di *"punto"*, *"coma"*, *"nueva línea"*… y las convierte en signos.
- 🇪🇸 **Pensado para español** — usa el modelo grande de Vosk; ampliable a otros idiomas.
- ⚡ **Ligero y gratuito.**

<p align="center">
  <img src="images/cargando.png" alt="Cargando modelo" width="300"><br>
  <em>Aviso mientras el modelo se carga en memoria (para que sepas cuándo hablar).</em>
</p>

---

## 📦 Requisitos

Del **sistema** (se instalan una vez con `apt`):

- Linux con **X11** (probado en KDE Plasma / Ubuntu 24.04).
- `python3` + `python3-venv`, `git`, `xdotool`, `curl`, `unzip`.
- `parec` (de `pipewire-pulse` o `pulseaudio`) para capturar audio.

El resto (**vosk**, **PyQt5**, **nerd-dictation** y el **modelo de voz** de ~1.4 GB)
lo instala automáticamente `install.sh` dentro de la carpeta del proyecto.

---

## 🚀 Instalación (automática)

Todo se instala **dentro de la propia carpeta** del proyecto (entorno virtual,
modelo y motor). No ensucia el resto del sistema.

```bash
# 1) Dependencias del sistema (Debian/Ubuntu)
sudo apt install python3 python3-venv git xdotool curl unzip pipewire-pulse

# 2) Clona el repositorio y ejecuta el instalador
git clone https://github.com/TheWolf1724/Dictado_Voz
cd Dictado_Voz
./install.sh
```

El script `install.sh` crea el entorno virtual (con **vosk** y **PyQt5**), clona
**nerd-dictation**, descarga el **modelo español** (~1.4 GB) y registra el lanzador
en el menú de aplicaciones. Es **idempotente**: si lo vuelves a ejecutar, solo hace
lo que falte.

> Puedes clonar el proyecto en cualquier carpeta (por ejemplo `~/Documents/`); todo
> funciona relativo a su propia ubicación.

### Atajo de teclado global (opcional, KDE)

*Preferencias del Sistema → Atajos → Atajos personalizados → Nuevo → Comando/URL
global*. Asigna una tecla (p. ej. **Ctrl+Shift+H**) y como comando pon la ruta a
`dictado.sh` (el instalador te la muestra al terminar). Pulsar el atajo inicia el
dictado; pulsarlo otra vez lo detiene.

### Estructura tras instalar

```
Dictado_Voz/
├── dictado.sh              # toggle (arranca/para) + ajuste de micrófono
├── dictado-gui.py          # interfaz flotante (PyQt5)
├── install.sh              # instalador automático
├── config/nerd-dictation.py   # puntuación por voz + mayúsculas
├── venv/                   # entorno virtual (vosk + PyQt5)         [auto]
├── nerd-dictation/         # motor de captura/escritura            [auto]
└── models/vosk-model-es-0.42/  # modelo de voz español (~1.4 GB)   [auto]
```

---

## 🎧 Uso

1. Haz clic en el campo de texto donde quieras escribir.
2. Pulsa el atajo → aparece la burbuja **"Cargando modelo…"**.
3. Cuando cambie a **"Grabando"** (punto rojo), habla con normalidad.
4. Pulsa el botón **■** de la burbuja o el atajo de nuevo para parar y volcar el texto.

> 💡 El modelo grande tarda ~2-4 s en cargar la primera vez. La burbuja te avisa
> con un spinner para que no empieces a hablar antes de tiempo.

### 🗣️ Comandos de puntuación por voz

| Dices… | Escribe |
|---|---|
| punto | `.` |
| coma | `,` |
| punto y coma | `;` |
| dos puntos | `:` |
| punto y aparte | `.` + salto de línea |
| puntos suspensivos | `…` |
| nueva línea / salto de línea | salto de línea |
| nuevo párrafo | línea en blanco |
| abre/cierra interrogación | `¿` … `?` |
| abre/cierra exclamación | `¡` … `!` |
| abre/cierra paréntesis | `(` … `)` |
| abre/cierra comillas | `"` |
| guion | `-` |

Además pone **mayúscula automática** al inicio y tras cada `.`, `?`, `!` o salto de línea.

---

## 🧩 Cómo funciona

- **`dictado-gui.py`** — interfaz PyQt5 (burbuja flotante). Lanza `nerd-dictation`,
  detecta cuándo el modelo terminó de cargar (aparece el proceso `parec`) para pasar
  de *cargando* a *grabando*, y al parar llama a `nerd-dictation end` para volcar el texto.
- **`dictado.sh`** — script *toggle* que arranca/detiene la interfaz y ajusta la
  ganancia del micrófono para que no sature.
- **`config/nerd-dictation.py`** — post-procesa el texto reconocido: puntuación por
  voz y mayúsculas automáticas.

---

## 🪟 ¿Y Windows?

El **motor (Vosk) y la interfaz son portables**; la parte que ata a Linux es
`nerd-dictation` (usa `xdotool`). Una versión multiplataforma pasaría por leer el
audio directamente con `sounddevice`, escribir el texto con `pyautogui`/portapapeles
y cambiar PyQt5 por PySide6. *(En el horizonte.)*

---

## 📄 Licencia

Publicado bajo **GNU GPL v3** (ver [`LICENSE`](LICENSE)). Es copyleft: cualquier
obra derivada debe distribuirse también bajo GPLv3. Esta licencia viene condicionada
por las dependencias ([nerd-dictation](https://github.com/ideasman42/nerd-dictation)
y [PyQt5](https://www.riverbankcomputing.com/software/pyqt/), ambas GPL).

## 🙏 Créditos

- [Vosk](https://alphacephei.com/vosk/) — motor de reconocimiento de voz offline (Apache-2.0).
- [nerd-dictation](https://github.com/ideasman42/nerd-dictation) — captura y escritura de texto (GPL).
