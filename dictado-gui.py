#!/usr/bin/env python3
"""
Overlay de dictado por voz (nerd-dictation + Vosk).

Muestra una "pastilla" flotante, siempre visible y sin robar el foco del teclado:
  - Estado CARGANDO: spinner mientras el modelo Vosk se carga en memoria.
  - Estado GRABANDO: punto rojo pulsante + botón para parar.

Arranca nerd-dictation como subproceso, detecta cuándo empieza a capturar audio
(aparece `parec`) para pasar de "cargando" a "grabando", y al parar llama a
`nerd-dictation end` para volcar el texto final limpiamente.

Diseño intencionadamente simple y orgánico. Se puede arrastrar con el ratón.
Uso:  python3 dictado-gui.py        (lo lanza ~/dictado.sh)
      python3 dictado-gui.py --selftest   (prueba sin lanzar dictado)
"""
import os
import sys
import math
import signal
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt

# Todo relativo a la carpeta del proyecto: auto-contenido, funciona esté donde esté.
BASE = os.path.dirname(os.path.realpath(__file__))
PY = os.path.join(BASE, "venv", "bin", "python")
ND = os.path.join(BASE, "nerd-dictation", "nerd-dictation")
MODEL = os.path.join(BASE, "models", "vosk-model-es-0.42")
CONFIG = os.path.join(BASE, "config", "nerd-dictation.py")

# --- Paleta (diseño simple y orgánico) ---
BG = QtGui.QColor(28, 28, 34, 236)      # carbón cálido translúcido
EDGE = QtGui.QColor(255, 255, 255, 18)  # borde muy sutil
FG = QtGui.QColor(240, 240, 243)
SUBFG = QtGui.QColor(165, 165, 174)
REC = QtGui.QColor(255, 96, 84)         # coral suave (grabando)
ACCENT = QtGui.QColor(126, 178, 246)    # azul suave (cargando)


class Overlay(QtWidgets.QWidget):
    def __init__(self, selftest=False):
        super().__init__()
        self.selftest = selftest
        self.state = "loading"     # "loading" | "recording"
        self.phase = 0.0
        self.spin = 0.0
        self.proc = None
        self._drag = None

        # Ventana: sin marco, siempre encima, herramienta, y SIN robar el foco.
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.NoFocus)
        self.setWindowTitle("Dictado")

        self.resize(272, 66)
        self._place_top_center()
        self.stop_rect = QtCore.QRect(self.width() - 52, self.height() // 2 - 16, 32, 32)

        # Animación suave (~30 fps).
        self.anim = QtCore.QTimer(self)
        self.anim.timeout.connect(self._tick)
        self.anim.start(33)

        # Arranca el dictado real (salvo en modo prueba).
        if not selftest:
            self._start_dictation()

        # Sondeo: ¿ya captura audio? ¿ha terminado el proceso?
        self.poll = QtCore.QTimer(self)
        self.poll.timeout.connect(self._poll)
        self.poll.start(300)
        self._loading_ticks = 0

        # Permitir que Python atienda señales aunque el bucle sea de Qt.
        self._sig = QtCore.QTimer(self)
        self._sig.timeout.connect(lambda: None)
        self._sig.start(200)
        signal.signal(signal.SIGTERM, lambda *a: self.stop())
        signal.signal(signal.SIGINT, lambda *a: self.stop())

    # ---------- posición ----------
    def _place_top_center(self):
        scr = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.move(scr.center().x() - self.width() // 2, scr.top() + 44)

    # ---------- ciclo de vida del dictado ----------
    def _start_dictation(self):
        cmd = [
            PY, ND, "begin",
            "--vosk-model-dir=%s" % MODEL,
            "--config=%s" % CONFIG,     # puntuación por voz (auto-contenida)
            "--simulate-input-tool=XDOTOOL",
            "--continuous",
            "--idle-time", "0.2",       # menos reproceso => menos reescrituras
        ]
        try:
            self.proc = subprocess.Popen(cmd)
        except Exception as ex:
            sys.stderr.write("No se pudo iniciar el dictado: %s\n" % ex)

    def _is_capturing(self):
        for pat in ("parec --record", "pw-cat --record"):
            try:
                if subprocess.run(["pgrep", "-f", pat],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL).returncode == 0:
                    return True
            except Exception:
                pass
        return False

    def _poll(self):
        # Si el proceso de dictado terminó (timeout, o parado por el atajo), cerrar.
        if self.proc is not None and self.proc.poll() is not None:
            QtWidgets.QApplication.quit()
            return
        if self.state == "loading":
            self._loading_ticks += 1
            # Pasar a "grabando" al detectar captura de audio (o tras ~12s de reserva).
            if self.selftest or self._is_capturing() or self._loading_ticks > 40:
                self.state = "recording"

    def stop(self):
        try:
            subprocess.run([PY, ND, "end"], timeout=6,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        if self.proc is not None:
            try:
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.terminate()
                except Exception:
                    pass
        QtWidgets.QApplication.quit()

    # ---------- animación ----------
    def _tick(self):
        self.phase += 0.055
        self.spin += 6.0
        self.update()

    # ---------- interacción ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.state == "recording" and self.stop_rect.contains(e.pos()):
                self.stop()
                return
            self._drag = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag is not None and (e.buttons() & Qt.LeftButton):
            self.move(e.globalPos() - self._drag)

    def mouseReleaseEvent(self, e):
        self._drag = None

    # ---------- pintura ----------
    def paintEvent(self, _ev):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        r = QtCore.QRectF(self.rect()).adjusted(3, 3, -3, -3)
        radius = r.height() / 2.0

        # Cuerpo (pastilla) con borde sutil.
        path = QtGui.QPainterPath()
        path.addRoundedRect(r, radius, radius)
        p.fillPath(path, BG)
        p.setPen(QtGui.QPen(EDGE, 1.0))
        p.drawPath(path)

        cx = r.left() + 27
        cy = r.center().y()

        if self.state == "loading":
            pen = QtGui.QPen(ACCENT, 3.0, Qt.SolidLine, Qt.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            rad = 10.0
            arc = QtCore.QRectF(cx - rad, cy - rad, rad * 2, rad * 2)
            start = int(self.spin) % 360
            p.drawArc(arc, -start * 16, 250 * 16)
            main, sub = "Cargando modelo…", "un momento"
        else:
            pulse = 0.5 + 0.5 * math.sin(self.phase * 2.3)
            # halo suave
            halo = QtGui.QColor(REC)
            halo.setAlphaF(0.18 * pulse)
            p.setPen(Qt.NoPen)
            p.setBrush(halo)
            hr = 9.0 + 7.0 * pulse
            p.drawEllipse(QtCore.QPointF(cx, cy), hr, hr)
            # punto
            dot = QtGui.QColor(REC)
            dot.setAlphaF(0.7 + 0.3 * pulse)
            p.setBrush(dot)
            dr = 6.5 + 1.5 * pulse
            p.drawEllipse(QtCore.QPointF(cx, cy), dr, dr)
            main, sub = "Grabando", "hablando…"

        # Texto.
        tx = int(cx + 22)
        p.setPen(FG)
        f = p.font()
        f.setPointSizeF(11.5)
        f.setBold(True)
        p.setFont(f)
        p.drawText(QtCore.QRect(tx, int(r.top()) + 12, self.width() - tx - 56, 20),
                   Qt.AlignVCenter | Qt.AlignLeft, main)
        p.setPen(SUBFG)
        f2 = p.font()
        f2.setPointSizeF(8.5)
        f2.setBold(False)
        p.setFont(f2)
        p.drawText(QtCore.QRect(tx, int(r.center().y()) + 2, self.width() - tx - 56, 18),
                   Qt.AlignVCenter | Qt.AlignLeft, sub)

        # Botón parar (solo grabando): cuadrado redondeado con ícono ■.
        if self.state == "recording":
            br = QtCore.QRectF(self.stop_rect)
            bpath = QtGui.QPainterPath()
            bpath.addRoundedRect(br, 9, 9)
            p.setPen(Qt.NoPen)
            p.fillPath(bpath, QtGui.QColor(255, 255, 255, 26))
            p.setBrush(QtGui.QColor(FG))
            sq = 10.0
            p.drawRoundedRect(
                QtCore.QRectF(br.center().x() - sq / 2, br.center().y() - sq / 2, sq, sq),
                2.5, 2.5)


def main():
    selftest = "--selftest" in sys.argv
    if selftest:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    w = Overlay(selftest=selftest)
    w.show()
    if selftest:
        # Recorre estados y sale, para validar que construye y pinta sin errores.
        QtCore.QTimer.singleShot(200, lambda: setattr(w, "state", "recording"))
        QtCore.QTimer.singleShot(600, app.quit)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
