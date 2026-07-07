# Config de nerd-dictation: puntuación por voz en español + mayúsculas automáticas.
# Se aplica a cada texto reconocido antes de escribirlo.
import re

# Frases (se evalúan en orden; las más largas primero para que ganen).
_REPLACEMENTS = [
    (r"\bnuevo p[aá]rrafo\b", "\n\n"),
    (r"\bnueva l[ií]nea\b", "\n"),
    (r"\bsalto de l[ií]nea\b", "\n"),
    (r"\bpunto y aparte\b", ".\n"),
    (r"\bpunto y seguido\b", "."),
    (r"\bpunto y coma\b", ";"),
    (r"\bdos puntos\b", ":"),
    (r"\bpuntos suspensivos\b", "…"),
    (r"\babre interrogaci[oó]n\b", "¿"),
    (r"\bcierra interrogaci[oó]n\b", "?"),
    (r"\bsigno de interrogaci[oó]n\b", "?"),
    (r"\binterrogaci[oó]n\b", "?"),
    (r"\babre exclamaci[oó]n\b", "¡"),
    (r"\bcierra exclamaci[oó]n\b", "!"),
    (r"\bsigno de exclamaci[oó]n\b", "!"),
    (r"\bexclamaci[oó]n\b", "!"),
    (r"\babre par[eé]ntesis\b", "("),
    (r"\bcierra par[eé]ntesis\b", ")"),
    (r"\babre comillas\b", "\""),
    (r"\bcierra comillas\b", "\""),
    (r"\bcomillas\b", "\""),
    (r"\bgui[oó]n\b", "-"),
    (r"\bpunto\b", "."),
    (r"\bcoma\b", ","),
]

# Estado que persiste entre segmentos (el módulo vive mientras dura el dictado).
# _cap_next = si la PRÓXIMA frase debe empezar en mayúscula (arranca True).
# _cap_this = mayúscula para el segmento actual (se fija al empezar cada segmento).
# _prev_input = último texto crudo, para detectar cuándo empieza un segmento nuevo.
_cap_next = True
_cap_this = True
_prev_input = ""

def _capitalize(s, cap_start):
    # Mayúscula al principio del segmento (si cap_start) y tras . ! ? … ¿ ¡ y saltos.
    out = []
    cap = cap_start
    for ch in s:
        if cap and ch.isalpha():
            out.append(ch.upper()); cap = False
        else:
            out.append(ch)
            if ch in ".!?…\n¿¡":
                cap = True
            elif ch not in " \t":
                cap = False
    return "".join(out)

def nerd_dictation_process(text):
    global _cap_next, _cap_this, _prev_input
    # ¿Empieza un segmento nuevo? En modo continuo los parciales van creciendo
    # (el texto nuevo empieza por el anterior); si no, es un segmento nuevo tras una pausa.
    is_new = not (_prev_input and text.startswith(_prev_input))
    if is_new:
        _cap_this = _cap_next
    _prev_input = text

    s = text
    for pat, rep in _REPLACEMENTS:
        s = re.sub(pat, rep, s, flags=re.IGNORECASE)
    s = re.sub(r"\s+([.,;:!?…)\"])", r"\1", s)   # quita espacio antes de signo de cierre
    s = re.sub(r"([¿¡(])\s+", r"\1", s)           # quita espacio tras signo de apertura
    s = re.sub(r"[ \t]{2,}", " ", s)               # colapsa espacios
    s = re.sub(r"[ \t]*\n[ \t]*", "\n", s)         # limpia alrededor de saltos
    s = _capitalize(s, _cap_this)
    s = s.strip()
    # La próxima frase se pone en mayúscula solo si esta termina en signo de cierre
    # de frase (. ! ? …) o en salto de línea. Si no, es continuación → minúscula.
    if s:
        _cap_next = s[-1] in ".!?…\n"
    # En modo --continuous cada pausa cierra un segmento y el siguiente se escribe
    # desde cero (nerd-dictation resetea su buffer). Añadimos un espacio final para
    # que la primera palabra tras la pausa no se pegue a la anterior.
    if s:
        s += " "
    return s
