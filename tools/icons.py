#!/usr/bin/env python3
"""
Librería de íconos monolineales + matcher por palabra clave.
Réplica del tratamiento del PDF: íconos grandes, trazo fino, blanco/currentColor.
"""

# Cada ícono: viewBox 0 0 48 48, trazo 1.2, sin relleno.
ICONS = {
"escudo": '<path d="M24 5 8 12v11c0 10 7 16 16 20 9-4 16-10 16-20V12L24 5z"/><path d="M17 24l5 5 10-10"/>',
"policia": '<path d="M24 5l4 8 9 1-6.5 6.5L32 30l-8-4.5L16 30l1.5-9.5L11 14l9-1 4-8z"/><path d="M12 34h24M14 40h20"/>',
"radar": '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="9"/><circle cx="24" cy="24" r="2.5"/><path d="M24 7v10M24 31v10M7 24h10M31 24h10"/>',
"ojo": '<path d="M3 24s8-12 21-12 21 12 21 12-8 12-21 12S3 24 3 24z"/><circle cx="24" cy="24" r="6"/>',
"mapa": '<path d="M6 12l12-5 12 5 12-5v29l-12 5-12-5-12 5V12z"/><path d="M18 7v29M30 12v29"/>',
"frontera": '<path d="M12 6v36M12 8h22l-5 6 5 6H12"/><circle cx="12" cy="44" r="2"/>',
"red": '<circle cx="24" cy="24" r="4"/><circle cx="9" cy="10" r="3.5"/><circle cx="39" cy="10" r="3.5"/><circle cx="9" cy="38" r="3.5"/><circle cx="39" cy="38" r="3.5"/><path d="M11.5 12.5 21 21M36.5 12.5 27 21M11.5 35.5 21 27M36.5 35.5 27 27"/>',
"cyber": '<path d="M24 6 10 12v10c0 9 6 15 14 18 8-3 14-9 14-18V12L24 6z"/><rect x="18" y="21" width="12" height="9" rx="1.5"/><path d="M21 21v-3a3 3 0 0 1 6 0v3"/>',
"antena": '<path d="M24 20v22"/><circle cx="24" cy="16" r="3.5"/><path d="M15 25a12 12 0 0 1 0-18M33 25a12 12 0 0 0 0-18M11 30a18 18 0 0 1 0-28M37 30a18 18 0 0 0 0-28"/>',
"mineria": '<path d="M6 40l14-26 10 15 5-7 7 18z"/><path d="M20 14l-4-6M30 29l6-9"/>',
"arbol": '<path d="M24 42V24"/><path d="M24 24c0-7-6-11-6-11s-3 8 2 11c3 1.8 4 0 4 0z"/><path d="M24 28c0-7 6-11 6-11s3 8-2 11c-3 1.8-4 0-4 0z"/><path d="M16 42h16"/>',
"globo": '<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6a26 26 0 0 1 0 36M24 6a26 26 0 0 0 0 36"/>',
"balanza": '<path d="M24 8v32M12 40h24M24 12 10 20M24 12l14 8"/><path d="M4 20a6 6 0 0 0 12 0zM32 20a6 6 0 0 0 12 0z"/>',
"documento": '<path d="M12 5h16l8 8v30H12z"/><path d="M28 5v8h8"/><path d="M18 24h12M18 31h12M18 17h5"/>',
"edificio": '<path d="M8 42V16l16-9 16 9v26"/><path d="M4 42h40"/><path d="M18 42V29h12v13"/><path d="M15 21h4M29 21h4"/>',
"columnas": '<path d="M6 18 24 7l18 11"/><path d="M4 42h40M8 42V18M16 42V18M24 42V18M32 42V18M40 42V18"/>',
"reja": '<rect x="8" y="8" width="32" height="32" rx="2"/><path d="M17 8v32M24 8v32M31 8v32"/>',
"personas": '<circle cx="17" cy="16" r="6"/><circle cx="33" cy="18" r="5"/><path d="M6 40c0-7 5-11 11-11s11 4 11 11M30 40c0-6 3-9 8-9s6 3 6 9"/>',
"educacion": '<path d="M24 10 4 19l20 9 20-9-20-9z"/><path d="M12 23v10c0 3 5.4 6 12 6s12-3 12-6V23"/><path d="M44 19v11"/>',
"trabajo": '<rect x="5" y="15" width="38" height="26" rx="2"/><path d="M18 15v-4a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v4"/><path d="M5 26h38M22 26v4h4v-4"/>',
"moneda": '<circle cx="24" cy="24" r="17"/><path d="M24 12v24M30 17h-9a4.5 4.5 0 0 0 0 9h6a4.5 4.5 0 0 1 0 9h-9"/>',
"grafico": '<path d="M6 40h36M6 40V8"/><path d="M12 32l8-9 7 6 11-14"/><circle cx="12" cy="32" r="1.8"/><circle cx="20" cy="23" r="1.8"/><circle cx="27" cy="29" r="1.8"/><circle cx="38" cy="15" r="1.8"/>',
"banco": '<path d="M4 18 24 7l20 11"/><path d="M4 42h40"/><path d="M9 18v24M19 18v24M29 18v24M39 18v24"/>',
"alerta": '<path d="M24 6 3 40h42L24 6z"/><path d="M24 19v9M24 33h.02"/>',
"engranaje": '<circle cx="24" cy="24" r="6"/><path d="M24 4v6M24 38v6M44 24h-6M10 24H4M38 10l-4 4M14 34l-4 4M38 38l-4-4M14 14l-4-4"/><circle cx="24" cy="24" r="14"/>',
"barco": '<path d="M6 32h36l-5 10H11z"/><path d="M24 32V12M24 12l12 8H12l12-8z"/><path d="M14 32V22"/>',
"avion": '<path d="M24 4c2 0 3 3 3 8v6l16 9v4l-16-4v9l5 4v3l-8-2-8 2v-3l5-4v-9L5 31v-4l16-9v-6c0-5 1-8 3-8z"/>',
"camion': ": '<rect x="3" y="14" width="24" height="17" rx="1.5"/><path d="M27 20h8l6 7v4h-14"/><circle cx="11" cy="35" r="3.5"/><circle cx="34" cy="35" r="3.5"/>',
"camion": '<rect x="3" y="14" width="24" height="17" rx="1.5"/><path d="M27 20h8l6 7v4h-14"/><circle cx="11" cy="35" r="3.5"/><circle cx="34" cy="35" r="3.5"/>',
"corazon": '<path d="M24 41S6 30 6 18a9 9 0 0 1 18-3 9 9 0 0 1 18 3c0 12-18 23-18 23z"/>',
"agua": '<path d="M24 5s12 13 12 22a12 12 0 0 1-24 0c0-9 12-22 12-22z"/>',
"energia": '<path d="M26 4 10 27h11l-3 17 17-24H24l2-16z"/>',
"reloj": '<circle cx="24" cy="24" r="18"/><path d="M24 13v11l8 5"/>',
"candado": '<rect x="10" y="21" width="28" height="20" rx="3"/><path d="M16 21v-6a8 8 0 0 1 16 0v6"/><circle cx="24" cy="30" r="2.5"/>',
"manos": '<path d="M24 40s-14-8-14-18a7 7 0 0 1 14-3 7 7 0 0 1 14 3c0 10-14 18-14 18z"/><path d="M17 20l5 5 9-9"/>',
"defecto": '<circle cx="24" cy="24" r="17"/><path d="M24 15v9l6 6"/>',
}

# Prioridad importa: el primer match gana.
MATCH = [
 # --- vocabulario económico (ACE 2040) ---
 (("app","asociación público","asociacion publico","contratos de inversión","delegación","concesion","concesión"), "manos"),
 (("bancab","factoring","garantía","garantia","fideicomiso","mercado de valores","mercado bursátil","crédito","credito","financiam","banca"), "banco"),
 (("regulación prudencial","supervisión","seguros inclusivos","inclusión financiera","inclusion financiera","riesgo financiero","estabilidad financiera","supervisión basada en riesgos"), "grafico"),
 (("arancel","aduanero","aduana","comercio exterior","exportador","exportación","inserción internacional","senae"), "barco"),
 (("infraestructura vial","corredor","corredores","conectividad territorial","logística","logistic","red vial"), "camion"),
 (("energía","electric","hidrocarbur","transición energética","transicion energetica","matriz energética"), "energia"),
 (("telecomunicaciones","conectividad digital","conectividad de","banda ancha","interoperabilidad"), "antena"),
 (("mercado de valores","mercado bursátil","mercado bursatil","bolsa"), "grafico"),
 (("gasto tributario","incentivos fiscales","régimen tributario","regimen tributario","gasto público","gasto publico","política fiscal","politica fiscal","sostenibilidad fiscal","sercop","contratación pública","contratacion publica","tributaria","tributario"), "moneda"),
 (("sri","recaudación","recaudacion","administración tributaria","administracion tributaria","formalización económica","formalizacion economica","base tributaria"), "grafico"),
 (("mineri","catastro minero"), "mineria"),
 (("marca país","turismo","turístic","turistic","agroturíst","agroturist"), "globo"),
 (("investigación","investigacion","innovación","innovacion","i+d","tecnología","tecnologia","desarrollo tecnológico"), "engranaje"),
 (("mipyme","pyme","emprend","asociatividad","cooperativismo","encadenamiento","productiv"), "personas"),
 (("laboral","empleo","trabajo","modalidades contractuales","empleador","informalidad"), "trabajo"),
 (("educación","educacion","educativ","capacitación","capacitacion","formación técnica","formacion tecnica","talento humano","senescyt","pasantías","dual","competencias laborales"), "educacion"),
 (("bienestar","seguridad laboral","protección social","proteccion social","salud"), "corazon"),
 (("normativ","reforma","marco legal","marco contractual","arbitraje","seguridad jurídica","seguridad juridica","resolución de conflictos","resolucion de conflictos","judic"), "balanza"),
 (("carrera administrativa","gestión pública","gestion publica","servicio ciudadano","estatal","interinstitucional","institucional","gobernanza","gad","subnacional"), "columnas"),
 (("transparencia","rendición de cuentas","rendicion de cuentas","integridad","auditando","auditor"), "candado"),
 (("infraestructura estadística","infraestructura estadistica","sistemas de información","sistemas de informacion","estadístic","estadistic","inec"), "documento"),
 (("estándar","estandar","certificación","certificacion","calidad"), "documento"),
 (("simplificación","simplificacion","trámite","tramite","digitalización","digitalizacion","interoperabilidad"), "engranaje"),
 (("climático","climatic","riesgo climático","desastre","resilienc","mitigación","mitigacion"), "alerta"),
 (("ambiental","conflictos socioambientales","territorial","territorio productivo"), "mapa"),
 (("inversión","inversion","atracción de capitales","atraccion de capitales","desarrollo sectorial","competitividad"), "grafico"),
 (("apertura","mercados","competencia","adecuación competitiva","adecuacion competitiva","diversificación","diversificacion"), "red"),
]

def pick_icon(text):
    t = text.lower()
    for keys, name in MATCH:
        for k in keys:
            if k in t:
                return name
    return "defecto"

def svg(name, size=96, stroke=1.2):
    body = ICONS.get(name, ICONS["defecto"])
    return (f'<svg class="strat__glyph" width="{size}" height="{size}" viewBox="0 0 48 48" '
            f'fill="none" stroke="currentColor" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')

if __name__ == "__main__":
    import json
    objs = json.load(open("/home/claude/objs.json"))
    from collections import Counter
    c = Counter()
    for o in objs:
        for s in o["strategies"]:
            c[pick_icon(s["s"])] += 1
    print("Distribución de íconos sobre las 65 estrategias:")
    for k, v in c.most_common():
        print(f"  {v:2}× {k}")
    print(f"\n{len(c)} íconos distintos en uso · 'defecto' = {c['defecto']}")
