"""Extrae acciones del md y las inyecta en objs.json."""
import json, re, sys
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "agenda_crecimiento_ecuador_2040_contexto_IA.md"
OBJS = ROOT / "objs.json"

text = SRC.read_text(encoding="utf-8")

def unwrap(block):
    lines = [l for l in block.split("\n")]
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
lin_re = re.compile(r"^Lineamiento\s+(\d+)[\.:]\s*(.+)$", re.M)
matches = list(lin_re.finditer(full))
print(f"Lineamientos en md: {len(matches)}", file=sys.stderr)

extracted = []
for i, m in enumerate(matches):
    titulo = m.group(2).strip().rstrip(".")
    start = m.end()
    end = matches[i+1].start() if i+1 < len(matches) else len(full)
    body = full[start:end]

    # Recorte al párrafo que contiene los ámbitos i) ii) iii)
    # Buscar bloque con marcadores romanos
    para = None
    for marker_para in re.finditer(r"[^\n]*\bi\)\s[^\n]*(?:ii\)|iii\)|iv\))[^\n]*", body):
        para = marker_para.group(0)
        break
    if not para:
        # Buscar "Alcance de las acciones" seguido de párrafo
        alc = re.search(r"Alcance de las acciones\s*(.+?)(?=\n\n|\Z)", body, re.S | re.I)
        if alc:
            para = re.sub(r"\s+", " ", alc.group(1)).strip()
    if not para:
        extracted.append({"num": int(m.group(1)), "titulo": titulo, "acciones": []})
        continue

    para = re.sub(r"\s+", " ", para).strip()
    # Encontrar el primer i)
    fm = re.search(r"\bi\)\s", para)
    if fm:
        para = para[fm.start():]
        parts = re.split(r"\s*;?\s*(?:y,\s*)?\b(i{1,3}v?|iv|v|vi{1,3})\)\s*", " " + para)
        acciones = []
        if len(parts) > 2:
            for k in range(1, len(parts)-1, 2):
                txt = parts[k+1].strip().rstrip(".;,")
                if len(txt) > 30:
                    acciones.append(txt)
    else:
        # Sin marcadores romanos: guardar el párrafo entero como acción única
        # (limpiar frases introductorias)
        clean = re.sub(r"^(El alcance de las propuestas en este ámbito se enfoca en|"
                       r"El alcance de las propuestas.{0,60}?se enfoca en|"
                       r"Las acciones asociadas a este lineamiento se orientan a|"
                       r"Las acciones de este lineamiento se orientan a|"
                       r"Las acciones tratadas dentro de este lineamiento buscan|"
                       r"Las medidas.{0,80}?buscan|"
                       r"Estas acciones buscan|"
                       r"Las propuestas.{0,60}?buscan)\s*",
                       "", para, flags=re.I).strip()
        acciones = [clean.rstrip(".;,")] if len(clean) > 40 else []
    extracted.append({"num": int(m.group(1)), "titulo": titulo, "acciones": acciones})

with_acc = sum(1 for e in extracted if e["acciones"])
total_acc = sum(len(e["acciones"]) for e in extracted)
print(f"Con acciones: {with_acc} | Total acciones: {total_acc}", file=sys.stderr)

# Match con objs.json
objs = json.loads(OBJS.read_text(encoding="utf-8"))

def norm(s):
    s = s.lower()
    s = re.sub(r"[^\wáéíóúñü ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def detect_plazos(txt):
    p = []; low = txt.lower()
    if re.search(r"corto plazo|6[-–]12 meses|quick win", low): p.append("corto")
    if re.search(r"mediano plazo|12[-–]36 meses", low): p.append("mediano")
    if re.search(r"largo plazo|\+ ?36 meses|más de 36 meses", low): p.append("largo")
    return p

used = set()
matched_count = 0
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
                matched_count += 1
                acs = [{"texto": a, "plazos": detect_plazos(a)}
                       for a in extracted[best_i]["acciones"]]
            else:
                acs = []
            new_lins.append({"texto": l_text, "acciones": acs})
        eje["lineamientos"] = new_lins

print(f"Empatados: {matched_count}/47", file=sys.stderr)
OBJS.write_text(json.dumps(objs, ensure_ascii=False, indent=2), encoding="utf-8")
print("✓ objs.json actualizado", file=sys.stderr)
