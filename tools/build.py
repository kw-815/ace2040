#!/usr/bin/env python3
"""
Generador de páginas de pilar — ACE 2040.

Estructura del contenido: pilar → ejes[] → lineamientos[].
Se toca este archivo solo si cambia la arquitectura del producto.
Contenido y metadatos: objs.json + config.py.
"""
import json, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icons import pick_icon, svg
import config as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "pages")
OBJS = os.path.join(ROOT, "objs.json")

objs = json.load(open(OBJS))
N_OBJS = len(objs)

assert len(C.META) == N_OBJS, (
    f"config.META tiene {len(C.META)} entradas pero objs.json tiene {N_OBJS} pilares.")

# Clases CSS de eje (sección dentro del pilar). Rotan si hay más ejes que clases.
EJE_CLASSES = ["inmediata", "1", "2", "3"]

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
        '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" />')

DIANA = ('<svg class="phase__diana" viewBox="0 0 48 48" fill="none" stroke="currentColor" '
         'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<circle cx="21" cy="27" r="15"/><circle cx="21" cy="27" r="9.5"/>'
         '<circle cx="21" cy="27" r="4"/>'
         '<path d="M21 27 40 8"/><path d="M33 8h7v7"/>'
         '<circle cx="36" cy="12" r="6.5"/><path d="M33.2 12l2 2 3.6-3.8"/></svg>')

VARIANTS = ["v1", "v2", "v3", "v1", "v4", "v2", "v5", "v1", "v6", "v2", "v7", "v1"]

def esc(s):
    return html.escape(s.strip())

# Palabras que NO deben cerrar la frase resaltada (artículos, preposiciones,
# conjunciones, pronombres, auxiliares). Si el corte cae aquí, se extiende
# hasta la siguiente palabra de contenido para que la "frase fuerza" quede
# completa y no se lea entrecortada.
_STOP_TAIL = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "lo",
    "de", "del", "al", "a", "ante", "bajo", "con", "contra", "desde",
    "en", "entre", "hacia", "hasta", "para", "por", "según", "sin",
    "sobre", "tras", "durante", "mediante", "vía",
    "y", "e", "o", "u", "ni", "pero", "mas", "sino", "que", "como",
    "su", "sus", "mi", "mis", "tu", "tus", "nuestro", "nuestra",
    "le", "les", "se", "me", "te", "nos",
    "es", "son", "ser", "está", "están",
}

def _clean(w):
    return w.lower().strip(",.;:()[]«»\"'¿?¡!")

def split_lead(body):
    # 1) Preferir cortes en coma o dos puntos si caen dentro del rango.
    for sep in (", ", ": "):
        i = body.find(sep)
        if 18 <= i <= 95 and len(body) - i > 25:
            return body[:i + 1], body[i + 1:].strip()

    # 2) Corte por palabras: arrancar en 7 y extender mientras la última
    #    palabra sea un "stop_tail" (artículo, preposición, conjunción...),
    #    o mientras la primera palabra del resto sea un sustantivo pegado
    #    a la anterior por preposición/artículo (evita cortar "la gestión",
    #    "los marcos", "el sistema", etc.).
    words = body.split()
    if len(words) > 11:
        k = 7
        max_k = len(words) - 3  # dejar al menos 3 palabras al resto
        while k < max_k and _clean(words[k - 1]) in _STOP_TAIL:
            k += 1
        return " ".join(words[:k]), " ".join(words[k:])
    return body, ""

def rich_text(body):
    lead, rest = split_lead(body)
    if rest:
        return f'<b>{esc(lead)}</b> <span>{esc(rest)}</span>'
    return f'<b>{esc(lead)}</b>'

# --- Resaltado de frase de impacto para acciones SIN título ---
# Detecta marcadores de transición fuertes ("que busca", "orientada a",
# "enfocada en", etc.) y resalta lo que va después hasta el primer punto
# o punto y coma. Si el corte no es limpio, no resalta (mejor plano que
# fragmento roto).
_TRANSITION_RE = re.compile(
    r"\b("
    r"que\s+busca(?:n|ron|se)?|"
    r"que\s+comprende[n]?|"
    r"que\s+permit[ae]n?|"
    r"que\s+garantic[eé]n?|"
    r"que\s+promuev[ae]n?|"
    r"que\s+doten|"
    r"orientad[oa]s?\s+a|"
    r"enfocad[oa]s?\s+en|"
    r"tendientes?\s+a|"
    r"dirigid[oa]s?\s+a|"
    r"apunta[n]?\s+a"
    r")\s+",
    re.IGNORECASE,
)

def find_highlight(text):
    """Devuelve (pre, highlight, post) o None si no hay corte limpio.

    Reglas:
    - Sólo se resalta lo que sigue a un marcador de transición fuerte.
    - El corte termina en el primer '. ' o '; ' posterior al marcador.
    - La primera palabra del resaltado debe ser un verbo en infinitivo
      (-ar/-er/-ir), para evitar arrancar en artículo, preposición o
      sustantivo suelto (p.ej. "al inversionista", "una asignación",
      "resultados verificables").
    - Longitud útil: 40–250 chars. Fuera de rango, no se resalta.
    """
    if not text:
        return None
    m = _TRANSITION_RE.search(text)
    if not m:
        return None
    start = m.end()
    rest = text[start:]
    end_m = re.search(r"[.;](?:\s|$)", rest)
    end = start + end_m.end() if end_m else len(text)
    highlight = text[start:end].strip()
    if not (40 <= len(highlight) <= 250):
        return None
    # Verificar que arranca con infinitivo (ar/er/ir). Es un filtro simple
    # que elimina casi todos los falsos positivos sin exigir un lexicón.
    first_word = re.match(r"[a-záéíóúñü]+", highlight, re.I)
    if not first_word:
        return None
    fw = first_word.group(0).lower()
    if not (fw.endswith("ar") or fw.endswith("er") or fw.endswith("ir")):
        return None
    pre = text[:start].rstrip()
    post = text[end:].lstrip()
    return pre, highlight, post

def nav(current):
    out = []
    for i, (short, _, _) in enumerate(C.META, 1):
        cur = ' aria-current="page"' if i == current else ""
        out.append(
            f'      <a class="obj-nav-top__item obj-nav-top__item--{i}" '
            f'href="pilar-{i}.html"{cur}>\n'
            f'        <small>0{i}</small><span>{esc(short)}</span>\n'
            f'      </a>'
        )
    return "\n".join(out)

def pager(n):
    prev_i = n - 1 if n > 1 else None
    next_i = n + 1 if n < N_OBJS else None
    parts = []
    if prev_i:
        parts.append(
            f'      <a class="obj-pager__link obj-pager__link--prev" href="pilar-{prev_i}.html">\n'
            f'        <small>← Pilar 0{prev_i}</small>\n'
            f'        <strong>{esc(C.META[prev_i-1][1])}</strong>\n'
            f'      </a>'
        )
    if next_i:
        parts.append(
            f'      <a class="obj-pager__link obj-pager__link--next" href="pilar-{next_i}.html">\n'
            f'        <small>Pilar 0{next_i} →</small>\n'
            f'        <strong>{esc(C.META[next_i-1][1])}</strong>\n'
            f'      </a>'
        )
    else:
        # Último pilar: cerrar el recorrido con retorno al índice de pilares
        # del home para continuar con la revisión de la Agenda.
        parts.append(
            f'      <a class="obj-pager__link obj-pager__link--next" href="../index.html#pilares">\n'
            f'        <small>Volver a la Agenda →</small>\n'
            f'        <strong>Continuar con los pilares</strong>\n'
            f'      </a>'
        )
    return "\n".join(parts)

def render_acciones(acciones):
    """Renderiza la lista de acciones bajo un lineamiento (sin accordion).

    - Label fijo "Acciones" (sin conteo).
    - Bullet visual coloreado en lugar de numeración.
    - Título en negrita cuando existe; si no existe, se intenta detectar
      una frase de impacto tras un marcador de transición y se resalta.
      Si no hay marcador claro, el texto queda plano.
    - Los chips de plazo (corto/mediano/largo) se ocultan por decisión
      editorial: generaban ambigüedad. El dato sigue en objs.json por si
      se retoma en el futuro.
    """
    if not acciones:
        return ""
    items = []
    for a in acciones:
        titulo = a.get("titulo") if isinstance(a, dict) else None
        texto = a.get("texto", "") if isinstance(a, dict) else a

        if titulo:
            # Título bold al inicio, texto continúa (patrón mayoritario).
            text_html = (
                f'<span class="accion__titulo">{esc(titulo)}</span> '
                f'{esc(texto)}'
            )
        else:
            # Sin título: intentar resaltar la frase de impacto.
            hl = find_highlight(texto)
            if hl:
                pre, highlight, post = hl
                parts = [esc(pre), f'<span class="accion__highlight">{esc(highlight)}</span>']
                if post:
                    parts.append(esc(post))
                text_html = " ".join(parts)
            else:
                text_html = esc(texto)

        items.append(
            f'                <li class="accion">\n'
            f'                  <span class="accion__bullet" aria-hidden="true"></span>\n'
            f'                  <div class="accion__body">\n'
            f'                    <p class="accion__text">{text_html}</p>\n'
            f'                  </div>\n'
            f'                </li>'
        )
    return (
        f'              <div class="acciones-wrap">\n'
        f'                <p class="acciones-wrap__label">Acciones</p>\n'
        f'                <ul class="acciones">\n'
        + "\n".join(items) + "\n"
        f'                </ul>\n'
        f'              </div>\n'
    )

def build_ejes(ejes):
    """Renderiza cada eje como una sección .phase con su framing y sus lineamientos."""
    singular, plural = C.ITEM_WORD
    blocks = []
    for i, eje in enumerate(ejes, 1):
        lineamientos = eje.get("lineamientos", [])
        n = len(lineamientos)
        word = plural if n != 1 else singular
        cls = EJE_CLASSES[(i - 1) % len(EJE_CLASSES)]

        cards = []
        for k, l in enumerate(lineamientos, 1):
            # Compatibilidad: cada lineamiento puede ser string (legacy) o
            # dict {texto, acciones} (nueva estructura enriquecida).
            if isinstance(l, dict):
                text = l.get("texto", "")
                acciones = l.get("acciones", [])
            else:
                text = l
                acciones = []
            icon = pick_icon(text)
            # Nueva clasificación por eje: cada card lleva strat--eje-N,
            # que en el CSS por pilar define tono derivado del color del
            # pilar (mismo hue, distinta saturación). Se elimina la
            # rotación aleatoria v1..v7 que confundía la jerarquía.
            cards.append(
                f'          <article class="strat strat--eje-{i}">\n'
                f'            <div class="strat__body">\n'
                f'              <div class="strat__head">\n'
                f'                <span class="strat__index" aria-hidden="true">'
                f'L{k:02d}</span>\n'
                f'                {svg(icon)}\n'
                f'              </div>\n'
                f'              <p class="strat__text">{rich_text(text)}</p>\n'
                f'{render_acciones(acciones)}'
                f'            </div>\n'
                f'          </article>'
            )

        framing = eje.get("framing", "").strip()
        framing_html = (
            f'        <p class="phase__framing">{esc(framing)}</p>\n'
            if framing else ""
        )
        blocks.append(
            f'      <section class="phase phase--{cls} phase--eje-{i}">\n'
            f'        <header class="phase__head">\n'
            f'          <span class="phase__flag">{DIANA}'
            f'<small>Eje 0{i}</small>{esc(eje["name"])}</span>\n'
            f'          <span class="phase__n">{n} {word}</span>\n'
            f'        </header>\n'
            f'{framing_html}'
            f'        <div class="phase__grid phase__grid--stacked">\n'
            + "\n".join(cards) + "\n"
            f'        </div>\n'
            f'      </section>'
        )
    return "\n\n".join(blocks)

def total_lineamientos(pilar):
    return sum(len(e.get("lineamientos", [])) for e in pilar.get("ejes", []))

def total_acciones(pilar):
    tot = 0
    for e in pilar.get("ejes", []):
        for l in e.get("lineamientos", []):
            if isinstance(l, dict):
                tot += len(l.get("acciones", []))
    return tot

TPL = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Pilar {n} · {long} — {product}</title>
  <meta name="description" content="Pilar {n} de {product}: {desc_plain} {subtitle}." />
  {font}
  <link rel="stylesheet" href="../css/styles.css" />
</head>
<body class="obj-page--{n}">

<header class="site-header">
  <div class="wrap site-header__inner">
    <a href="../index.html" class="brand" aria-label="{brand} — inicio">
      <img src="../img/logo-keyword-white.svg" alt="{brand}" class="brand__logo" />
    </a>
    <nav class="nav-crumbs" aria-label="Ruta de navegación">
      <a href="../index.html">{crumb_root}</a> · <span>Pilar {n}</span>
    </nav>
  </div>
</header>

<main>

<nav class="wrap obj-nav-top" aria-label="Pilares de la Agenda">
  <div class="obj-nav-top__grid">
{nav}
  </div>
</nav>

<section class="obj-hero obj-hero--{n}" aria-labelledby="titulo-pilar">
  <div class="wrap">
    <p class="obj-hero__kicker">Pilar</p>
    <div class="obj-hero__row">
      <h1 class="obj-hero__name" id="titulo-pilar">{short}</h1>
      <span class="obj-hero__num" aria-hidden="true">0{n}</span>
    </div>

    <div class="obj-intro">
      <div class="obj-intro__card">
        <p class="obj-intro__label">Pilar {n}:</p>
        <p class="obj-intro__text">{desc_rich}</p>
      </div>
      <span class="obj-intro__badge" aria-hidden="true">
        <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="24" r="19"/><circle cx="24" cy="24" r="11"/><circle cx="24" cy="24" r="3.5"/></svg>
      </span>
      <div class="obj-intro__photo">
        <img src="../img/pilar-{n}-photo.jpg" alt="" loading="lazy" />
      </div>
    </div>

    <div class="pilar-framing">
      <p class="pilar-framing__eyebrow">Fundamento del pilar</p>
      <p class="pilar-framing__text">{pilar_framing}</p>
    </div>

    <div class="roadmap">
      <header class="roadmap__head">
        <div>
          <p class="roadmap__eyebrow">{roadmap_eyebrow}</p>
          <h2 class="roadmap__title">{roadmap_title}</h2>
        </div>
        <p class="roadmap__count">{total} {total_word}, organizados en {n_ejes} {ejes_word}</p>
      </header>

{ejes}
    </div>

    <nav class="obj-pager" aria-label="Navegación entre pilares">
{pager}
    </nav>
  </div>
</section>

</main>

<footer class="site-footer">
  <div class="wrap site-footer__inner">
    <img src="../img/logo-keyword-white.svg" alt="{brand}" class="site-footer__logo" />
    <p class="site-footer__copy">©Todos los derechos reservados</p>
    <p class="site-footer__contact">Contacto: <a href="mailto:{email}">{email}</a></p>
  </div>
</footer>

</body>
</html>
"""

os.makedirs(OUT, exist_ok=True)
singular, plural = C.ITEM_WORD
for i, obj in enumerate(objs, 1):
    short, long, desc = C.META[i-1]
    total = total_lineamientos(obj)
    n_ejes = len(obj.get("ejes", []))
    ejes_word = "ejes" if n_ejes != 1 else "eje"
    page = TPL.format(
        n=i,
        short=esc(short),
        long=esc(long),
        desc_rich=rich_text(desc),
        desc_plain=esc(desc),
        font=FONT,
        nav=nav(i),
        pilar_framing=esc(obj.get("framing", "")),
        ejes=build_ejes(obj.get("ejes", [])),
        pager=pager(i),
        total=total,
        total_word=plural if total != 1 else singular,
        n_ejes=n_ejes,
        ejes_word=ejes_word,
        roadmap_eyebrow=esc(C.ROADMAP_EYEBROW),
        roadmap_title=esc(C.ROADMAP_TITLE),
        product=esc(C.PRODUCT_TITLE),
        subtitle=esc(C.PRODUCT_SUBTITLE),
        brand=esc(C.BRAND_NAME),
        email=esc(C.BRAND_EMAIL),
        crumb_root=esc(C.BREADCRUMB_ROOT),
    )
    with open(f"{OUT}/pilar-{i}.html", "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✓ pilar-{i}.html — {total} {plural if total!=1 else singular} en {n_ejes} {ejes_word}")

print(f"\nListo: {N_OBJS} páginas de pilar generadas.")
