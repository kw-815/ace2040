# ACE 2040 · v1

Sitio de resumen ejecutivo de la Agenda de Crecimiento Ecuador 2040.

## Estructura

```
ace2040/
├── index.html              # Home (9 secciones + De la visión a la acción)
├── 404.html
├── objs.json               # Contenido: 4 pilares → 9 ejes → 47 lineamientos
├── css/styles.css          # Estilos completos (base + adiciones ACE 2040)
├── img/                    # Coloca aquí:
│   ├── logo-keyword-white.svg (placeholder incluido)
│   ├── hero-placeholder.jpg
│   ├── pilar-1-cover.jpg ... pilar-4-cover.jpg
│   ├── pilar-1-photo.jpg ... pilar-4-photo.jpg
│   └── (opcional) voice-noboa.jpg, voice-moya.jpg, voice-goldfajn.jpg
├── pages/                  # Generado por build.py
│   ├── pilar-1.html
│   ├── pilar-2.html
│   ├── pilar-3.html
│   └── pilar-4.html
└── tools/
    ├── build.py            # Generador
    ├── config.py           # Metadatos de UI
    └── icons.py            # Banco de íconos + matcher económico
```

## Regenerar páginas de pilar

```
cd ace2040
python3 tools/build.py
```

Salida: 4 páginas en `pages/`.

## Contenido

- **4 pilares:** Institucionalidad y Seguridad Jurídica · Estabilidad Fiscal · Competitividad e Inversión Productiva · Fortalecimiento de la Dolarización y Profundización Financiera
- **9 ejes** distribuidos: 2 + 2 + 3 + 2
- **47 lineamientos** totales: 11 + 8 + 21 + 7

## Pendientes

- Imágenes reales (placeholders y fotos de pilar)
- Fotos de los tres voceros de la Sección 08 (por ahora placeholders con iniciales: DN, SM, IG)
- Revisión de tono y consistencia terminológica
