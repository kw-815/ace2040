"""
Configuración del producto — ACE 2040.

Estructura del producto: Pilar → Eje → Lineamiento.
El contenido vive en objs.json. Este archivo mantiene metadatos de UI.
"""

# -------------------------------------------------------------------
# Identidad del producto
# -------------------------------------------------------------------
PRODUCT_TITLE = "Agenda de Crecimiento Ecuador 2040"
PRODUCT_SUBTITLE = "Análisis de Keyword"
PRODUCT_DESCRIPTION = (
    "Resumen ejecutivo de la Agenda de Crecimiento Ecuador 2040. "
    "Análisis de Keyword sobre los cuatro pilares del marco estratégico "
    "de política pública económica que orientará al país al año 2040."
)
BREADCRUMB_ROOT = "Agenda de Crecimiento 2040"

# -------------------------------------------------------------------
# Metadatos por pilar — uno por entrada de objs.json, en el mismo orden
#   (nombre_corto_navegacion, nombre_largo, descriptor_completo)
# -------------------------------------------------------------------
META = [
    ("Institucionalidad", "Institucionalidad y Seguridad Jurídica",
     "Reglas claras, previsibilidad regulatoria y seguridad jurídica como base para la inversión productiva."),
    ("Estabilidad Fiscal", "Estabilidad Fiscal",
     "Sostenibilidad de las finanzas públicas y un sistema tributario eficiente para la inversión y la productividad."),
    ("Competitividad", "Competitividad e Inversión Productiva",
     "Formalización laboral, infraestructura, innovación y coordinación público-privada como núcleo operativo de la Agenda."),
    ("Dolarización", "Fortalecimiento de la Dolarización y Profundización Financiera",
     "Sistema financiero capaz de canalizar ahorro y crédito hacia la inversión productiva, sosteniendo el modelo monetario."),
]

# Palabra que describe cada item de un pilar en este producto.
ITEM_WORD = ("lineamiento", "lineamientos")

# Ejes: agrupador visible dentro de cada pilar.
GROUP_AXIS_LABEL = "Eje"

# Título del bloque que agrupa los lineamientos en cada página de pilar.
ROADMAP_EYEBROW = "Lineamientos"
ROADMAP_TITLE   = "Cómo se aterriza este pilar"

# Numeración inline en las tarjetas de lineamiento (1., 2., …).
# Se desactiva: los ejes se numeran a nivel de sección, no cada tarjeta.
SHOW_NUM = False

# -------------------------------------------------------------------
# Marca
# -------------------------------------------------------------------
BRAND_NAME  = "Keyword"
BRAND_EMAIL = "info@keyword.com.ec"
