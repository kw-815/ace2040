"""
Extrae ámbitos estratégicos ("acciones") de cada Lineamiento del
documento fuente, limpia escombros OCR (marcadores de página,
notas al pie, headings de siguiente eje) y los inyecta en objs.json.

Estructura resultante por acción:
  { titulo: str, texto: str, plazos: [str] }

titulo   = el fragmento temático inicial (antes de la primera coma)
texto    = descripción operativa condensada
plazos   = ['corto'|'mediano'|'largo'] cuando el documento lo indica
"""
import json, re, sys
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "agenda_crecimiento_ecuador_2040_contexto_IA.md"
OBJS = ROOT / "objs.json"

text = SRC.read_text(encoding="utf-8")

def unwrap(block):
    lines = block.split("\n")
    out, buf = [], ""
    for l in lines:
        s = l.strip()
        if not s:
            if buf: out.append(buf); buf = ""
            continue
        if buf and (buf[-1] not in ".:;!?»)]" or s[0].islower()
                    or re.match(r"(i{1,3}|iv|v|vi{1,3})\)", s)):
            buf += " " + s
        else:
            if buf: out.append(buf)
            buf = s
    if buf: out.append(buf)
    return "\n".join(out)

full = unwrap(text)

# --- Localizar cada Lineamiento (acepta "Lineamiento N." o "Lineamiento N:")
lin_re = re.compile(r"^Lineamiento\s+(\d+)[\.:]\s*(.+)$", re.M)
matches = list(lin_re.finditer(full))
print(f"Lineamientos en md: {len(matches)}", file=sys.stderr)

# --- Patrones de escombro / cortes duros ---
STOP_PATTERNS = [
    r"### ",                    # cualquier heading H3 (ej. ### EJE 2.2)
    r"^## Página",              # marcador de página
    r"^Lineamiento\s+\d+[\.:]", # siguiente lineamiento
    r"^Lineamientos:\s*$",      # índice de lineamientos
    r"^Aportes sectoriales",    # próximo bloque
    r"^Fundamento:",            # intro de siguiente eje
    r"^Fuente:",                # nota fuente
    r"^!\[Página",              # marcador imagen OCR
    r"^---\s*$",                # separador
    r"^\d{2,3}\s+[A-ZÁÉÍÓÚÑ][^.]{5,}\.\s+Disponible en:",  # footnote OCR
    r"^\d{2,3}\s+OECD",         # footnote tipo "28 OECD (2016)..."
    r"^EJE\s+\d+\.\d+",         # próximo eje
]
STOP_RE = re.compile("|".join(f"({p})" for p in STOP_PATTERNS), re.M)

# --- Limpieza post-extracción de escombro OCR ---
DEBRIS_INLINE = [
    r"!\[Página \d+ del documento original\]\(pages/page-\d+\.jpg\)",
    r"---\s*## Página \d+",
    r"^## Página \d+",
    r"### EJE.*",
    r"Fundamento:.*",
    r"Aportes sectoriales.*",
    r"Fuente:.*",
    r"\bDisponible en:\s*https?://\S+",
    r"\bhttps?://\S+",
    r"\b\d{2,3}\s+(?:OECD|BCE|MEF|INEC|Brys|OECD Publishing)[^.]+\.",
]
DEBRIS_RE = re.compile("|".join(DEBRIS_INLINE))

def clean_debris(txt):
    txt = DEBRIS_RE.sub("", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = re.sub(r"\s+([,.;:])", r"\1", txt)
    return txt

def stop_at(body):
    """Corta body en el primer patrón de parada."""
    m = STOP_RE.search(body)
    if m:
        return body[:m.start()]
    return body

def strip_introducers(txt):
    """Quita frases meta como 'El alcance de este lineamiento consiste en...'."""
    patterns = [
        r"^El alcance de (?:este lineamiento|las propuestas|estas propuestas|este ámbito)[^.]{0,150}?(?:consiste en|se enfoca en|comprende|se orienta a|busca|apunta a)\s*",
        r"^Las acciones (?:asociadas a este lineamiento|de este lineamiento|de política pública|tratadas dentro de este lineamiento|comprenden)[^.]{0,120}?(?:se orientan a|buscan|apuntan a|se dirigen a|se estructuran en torno a)\s*",
        r"^Las medidas (?:que se encuentran en este lineamiento|de este lineamiento)?[^.]{0,120}?(?:se dirigen a|buscan)\s*",
        r"^Estas acciones (?:buscan|se enmarcan|se orientan)[^.]{0,120}?\s*",
        r"^A nivel macro,?\s*(?:estas medidas)?[^.]{0,120}?\s*",
        r"^En resumen,?\s*",
        r"^Los ámbitos estratégicos son:\s*",
        r"^Las propuestas[^.]{0,80}?buscan\s*",
    ]
    for p in patterns:
        txt = re.sub(p, "", txt, count=1, flags=re.I)
    return txt.strip()

def split_titulo(action_txt):
    """
    Separa acción en (titulo, descripcion).
    Convención del documento: 'Título temático, mediante/a través de/para descripción'.
    """
    # Buscar primera coma después de al menos 15 chars y antes de 90
    m = re.search(r"^([^,]{15,90}?),\s+", action_txt)
    if m:
        titulo = m.group(1).strip().rstrip(":.")
        desc = action_txt[m.end():].strip()
        # Descartar si el título es "trivial" (empieza en minúscula = era mitad de otra frase)
        if titulo and titulo[0].isupper() and len(desc) > 20:
            return titulo, desc
    return None, action_txt

def condense(txt, max_chars=340):
    """Recorta en el punto natural más cercano si excede max_chars."""
    if len(txt) <= max_chars:
        return txt
    # Buscar corte en ; o . o , dentro de un rango razonable
    window = txt[:max_chars]
    for sep in [". ", "; ", ", "]:
        idx = window.rfind(sep)
        if idx > max_chars * 0.6:
            return window[:idx + 1].strip() + "…"
    # Fallback: cortar en el último espacio
    idx = window.rfind(" ")
    return window[:idx].strip() + "…"

extracted = []
for i, m in enumerate(matches):
    titulo_lin = m.group(2).strip().rstrip(".")
    start = m.end()
    end = matches[i+1].start() if i+1 < len(matches) else len(full)
    body = full[start:end]

    # Buscar el párrafo con marcadores romanos i) ii) iii)
    para = None
    for mp in re.finditer(r"^([^\n]*\bi\)\s[^\n]*?)$", body, re.M):
        line = mp.group(1)
        if re.search(r"ii\)|iii\)|iv\)", line):
            para = line
            break

    if not para:
        # Fallback: capturar TODO desde "Alcance de las acciones" hasta un
        # stop pattern real (siguiente lineamiento, ### EJE, ## Página del
        # próximo capítulo, etc.). Los saltos de línea por OCR se limpian
        # después. No paramos en \n\n porque el OCR mete saltos falsos.
        alc = re.search(r"Alcance de las acciones\s*\n+", body, re.I)
        if alc:
            para = body[alc.end():]

    if not para:
        extracted.append({"num": int(m.group(1)), "titulo": titulo_lin, "acciones": []})
        continue

    # Cortar en el primer patrón de stop
    para = stop_at(para)
    para = clean_debris(para)
    para = re.sub(r"\s+", " ", para).strip()

    acciones_raw = []
    fm = re.search(r"\bi\)\s", para)
    if fm:
        # Segmentar por marcadores romanos
        segmented = para[fm.start():]
        parts = re.split(r"\s*;?\s*(?:y,\s*)?\b(i{1,3}v?|iv|v|vi{1,3})\)\s*", " " + segmented)
        if len(parts) > 2:
            for k in range(1, len(parts)-1, 2):
                txt = parts[k+1].strip().rstrip(".;,")
                if len(txt) > 30:
                    acciones_raw.append(txt)
    else:
        cleaned = strip_introducers(para).rstrip(".;,")
        if len(cleaned) > 40:
            acciones_raw.append(cleaned)

    # Post-procesar cada acción: split título + descripción + condensar
    acciones_final = []
    for raw in acciones_raw:
        raw = clean_debris(raw)
        raw = re.sub(r"^\W+", "", raw).strip()
        if not raw or len(raw) < 30:
            continue
        titulo, desc = split_titulo(raw)
        # Aplicar tope de longitud a la descripción
        desc_condensada = condense(desc, max_chars=340)
        acciones_final.append({
            "titulo": titulo,
            "texto": desc_condensada,
        })

    extracted.append({"num": int(m.group(1)), "titulo": titulo_lin, "acciones": acciones_final})

with_acc = sum(1 for e in extracted if e["acciones"])
total_ac = sum(len(e["acciones"]) for e in extracted)
print(f"Con acciones: {with_acc} | Total acciones: {total_ac}", file=sys.stderr)

# === Match con objs.json ===
objs = json.loads(OBJS.read_text(encoding="utf-8"))

# Reset: convertir a formato flat si vino con la estructura anterior
for pilar in objs:
    for eje in pilar["ejes"]:
        new_lins = []
        for l in eje["lineamientos"]:
            if isinstance(l, dict):
                new_lins.append(l["texto"])
            else:
                new_lins.append(l)
        eje["lineamientos"] = new_lins

def norm(s):
    s = s.lower()
    s = re.sub(r"[^\wáéíóúñü ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def detect_plazos(txt):
    p, low = [], txt.lower()
    if re.search(r"corto plazo|6[-–]12 meses|quick win", low): p.append("corto")
    if re.search(r"mediano plazo|12[-–]36 meses", low): p.append("mediano")
    if re.search(r"largo plazo|\+ ?36 meses|más de 36 meses", low): p.append("largo")
    return p

used = set()
matched = 0
for pilar in objs:
    for eje in pilar["ejes"]:
        new_lins = []
        for l_text in eje["lineamientos"]:
            tn = norm(l_text)[:150]
            best_i, best_s = -1, 0.0
            for i, e in enumerate(extracted):
                if i in used: continue
                s = SequenceMatcher(None, tn, norm(e["titulo"])[:150]).ratio()
                if s > best_s:
                    best_s, best_i = s, i
            if best_i >= 0 and best_s >= 0.5:
                used.add(best_i)
                matched += 1
                acs = []
                for a in extracted[best_i]["acciones"]:
                    plazos = detect_plazos(a["texto"] + " " + (a.get("titulo") or ""))
                    acs.append({
                        "titulo": a.get("titulo"),
                        "texto": a["texto"],
                        "plazos": plazos,
                    })
            else:
                acs = []
            new_lins.append({"texto": l_text, "acciones": acs})
        eje["lineamientos"] = new_lins

print(f"Empatados: {matched}/47", file=sys.stderr)
OBJS.write_text(json.dumps(objs, ensure_ascii=False, indent=2), encoding="utf-8")
print("✓ objs.json actualizado", file=sys.stderr)
