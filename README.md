# Responsible Data Lab

**Leyes, Ética y Protección de Datos** · Especialización en Análisis Estadístico

Repositorio académico del curso, construido con [Quarto](https://quarto.org/) y
publicable en GitHub Pages. Incluye el sitio navegable, las presentaciones
Reveal.js, los laboratorios en Jupyter y el generador del dataset sintético del
caso transversal.

> Los datos no toman decisiones. Las personas diseñan sistemas que las toman.

---

## Qué es esto

Un curso de nueve semanas que trata la protección de datos **como un problema
de diseño de proyectos de datos**, no como una asignatura de derecho. La
estructura de cada tema es siempre la misma:

```
PROBLEMA → DATOS → DECISIÓN ANALÍTICA → RIESGO → PRINCIPIO → CONTROL → DECISIÓN FINAL
```

La legislación aparece cuando hace falta para resolver un problema concreto, y
no como punto de partida de la explicación.

Dos preguntas atraviesan las nueve semanas:

1. Que algo sea técnicamente posible y estadísticamente válido, ¿significa que
   debemos hacerlo?
2. ¿Qué tendría que cambiar en mi proyecto de datos?

## Estado del contenido

| Material | Estado |
|:--|:--|
| Sitio, identidad visual y navegación | ✅ Completo |
| Encuentro 1 + slides + Lab 1 | ✅ Completo |
| Encuentro 2 + slides + Lab 2 | ✅ Completo |
| Caso DataMarket + dataset sintético | ✅ Completo |
| Caso Facebook · Banco de 12 dilemas | ✅ Completo |
| Actividades 1 a 4 (enunciados y rúbricas) | ✅ Completas |
| Checklist · Mapa de riesgos · Glosario | ✅ Completos |
| Encuentros 3, 4 y 5 | 🔨 Estructura preparada |
| Slides y labs 3 y 4 | 🔨 Pendientes |

---

## Requisitos

- [Quarto](https://quarto.org/docs/get-started/) ≥ 1.4
- Python ≥ 3.10
- Las dependencias de `requirements.txt`

```bash
pip install -r requirements.txt
```

## Uso local

```bash
# 1. Generar el dataset sintético (obligatorio la primera vez)
python scripts/generar_datos.py

# 2. Previsualizar el sitio con recarga automática
quarto preview

# 3. Renderizar todo el sitio a _site/
quarto render
```

Renderizar una sola pieza:

```bash
quarto render encuentros/encuentro-01.qmd
quarto render slides/01-datos-decisiones.qmd
```

### Sobre los laboratorios

Los cuadernos `labs/*.ipynb` se entregan **con las salidas ya ejecutadas**, de
modo que el sitio se renderiza sin necesidad de ejecutar Python. Para
re-ejecutarlos:

```bash
cd labs
jupyter nbconvert --to notebook --execute --inplace lab01.ipynb
jupyter nbconvert --to notebook --execute --inplace lab02.ipynb
```

Los cuadernos resuelven la ruta del CSV automáticamente, así que funcionan
tanto si se abren desde `labs/` como desde la raíz del repositorio.

---

## Estructura

```
leyes-etica-proteccion-datos/
│
├── README.md
├── _quarto.yml                  # configuración del sitio y navegación
├── referencias.bib              # bibliografía (BibTeX)
├── requirements.txt
├── index.qmd                    # portada
├── programa.qmd                 # plan del curso y evaluación
├── metodologia.qmd              # cómo funciona cada encuentro
│
├── encuentros/
│   ├── encuentro-01.qmd         # ✅ Tenemos los datos. ¿Qué podría salir mal?
│   ├── encuentro-02.qmd         # ✅ Del requisito a la decisión
│   ├── encuentro-03.qmd         # 🔨 Ética y ciencia de datos
│   ├── encuentro-04.qmd         # 🔨 Herramientas de protección
│   └── encuentro-05.qmd         # 🔨 Decálogo colaborativo
│
├── slides/
│   ├── 01-datos-decisiones.qmd        # ✅ 24 diapositivas Reveal.js
│   └── 02-reglas-proyectos-datos.qmd  # ✅ 24 diapositivas Reveal.js
│
├── labs/
│   ├── lab01.ipynb              # ✅ ¿Qué sabe realmente esta base sobre nosotros?
│   └── lab02.ipynb              # ✅ Auditoría rápida de un pipeline
│
├── data/
│   └── clientes_sinteticos.csv  # generado por script · 1 512 × 35
│
├── scripts/
│   └── generar_datos.py         # generador reproducible (semilla fija)
│
├── casos/
│   ├── caso-datamarket.qmd      # caso transversal + diccionario de datos
│   ├── caso-facebook.qmd        # caso histórico · alcance territorial
│   └── dilemas.qmd              # banco de 12 dilemas
│
├── actividades/
│   ├── actividad-01.qmd         # Colombia – Brasil – Chile · 25 %
│   ├── actividad-02.qmd         # Auditoría GDPR · 25 %
│   ├── actividad-03.qmd         # Ética en el sector público · 25 %
│   └── actividad-04.qmd         # Anonimización · 25 %
│
├── recursos/
│   ├── checklist-proyecto-datos.qmd   # 12 preguntas
│   ├── mapa-riesgos.qmd               # 12 etapas del pipeline
│   └── glosario.qmd                   # 28 términos operativos
│
├── lecturas/
│   └── index.qmd                # lecturas por semana y fuentes oficiales
│
├── styles/
│   ├── custom.scss              # identidad visual · modo claro
│   ├── custom-dark.scss         # identidad visual · modo oscuro
│   ├── reveal-rds.scss          # tema de las presentaciones
│   ├── extra.css                # tipografía y ajustes menores
│   ├── logo.svg
│   └── favicon.svg
│
└── .github/workflows/
    └── publish.yml              # publicación automática en GitHub Pages
```

---

## El caso transversal

**DataMarket Analytics** es una empresa colombiana ficticia de comercio
electrónico. Todo el curso gira alrededor de su base de clientes, que cambia
de problema cada semana:

| Semana | Situación |
|:--:|:--|
| 1 | Quiere predecir *churn* con 35 variables |
| 2 | Aparecen problemas de origen, finalidad y tratamiento |
| 3 | Quiere operar en Brasil y Chile |
| 4 | Descubre que tiene clientes residentes en la UE |
| 5 | El modelo discrimina por estrato y edad |
| 7 | Necesita compartir la base con un tercero |
| 8 | Tiene que anonimizarla de verdad |
| 9 | Los estudiantes escriben el decálogo |

### El dataset

`data/clientes_sinteticos.csv` — **1 512 registros × 35 variables**, generado
por `scripts/generar_datos.py` con semilla fija.

Está diseñado para que las discusiones del curso aparezcan solas:

- **236 registros** sin evidencia de autorización (lista comprada a un tercero
  y enriquecimiento web).
- **74 registros** con residencia en la Unión Europea.
- Tres variables proxy de datos sensibles: `compras_farmacia_6m`,
  `entrega_asistida`, `busquedas_maternidad`.
- El **83,9 %** de los registros es único con solo cuatro
  cuasi-identificadores.
- La variable objetivo depende parcialmente de los proxies, de modo que el
  «modelo B» del Lab 2 realmente predice mejor (AUC ≈ 0.88 frente a ≈ 0.83) a
  costa de usar variables problemáticas.

```bash
python scripts/generar_datos.py                    # valores por defecto
python scripts/generar_datos.py --n 3000 --semilla 7
```

> ⚠️ **Todos los datos son sintéticos.** Ninguna persona real está
> representada. Nunca sustituya esta base por datos reales de una organización.

---

## Publicar en GitHub Pages

### Opción A · GitHub Actions (recomendada)

El repositorio incluye `.github/workflows/publish.yml`, que renderiza y publica
en cada `push` a `main`.

`_quarto.yml` **ya está configurado** para el repositorio
`wilsonsr/leyes-etica-proteccion-datos`. Si el repositorio se crea con otro
nombre o en otra cuenta, hay que actualizar `site-url`, `repo-url` y el `href`
del icono de GitHub en la barra de navegación.

1. Cree el repositorio en GitHub —**público**, sin README ni `.gitignore`
   iniciales— y suba el proyecto:

   ```bash
   git init
   git add .
   git commit -m "Responsible Data Lab: versión inicial del curso"
   git branch -M main
   git remote add origin https://github.com/wilsonsr/leyes-etica-proteccion-datos.git
   git push -u origin main
   ```

   Con GitHub Desktop: *File → Add Local Repository* → crear → *Commit to main*
   → *Publish repository*, desmarcando *Keep this code private*.

2. En **Settings → Pages**, seleccione:
   - **Source:** GitHub Actions

3. Espere a que el trabajo de la pestaña **Actions** termine en verde. El sitio
   queda en
   `https://wilsonsr.github.io/leyes-etica-proteccion-datos/`.

4. De ahí en adelante, cada `push` a `main` republica el sitio.

### Opción B · Rama `gh-pages` con `quarto publish`

```bash
quarto publish gh-pages
```

Quarto crea la rama `gh-pages`, sube el sitio renderizado y configura el
repositorio. Después, en **Settings → Pages**, seleccione
**Deploy from a branch → gh-pages → / (root)**.

### Opción C · Carpeta `docs/`

```bash
# En _quarto.yml, cambiar:
#   output-dir: docs
quarto render
git add docs && git commit -m "Publicar sitio" && git push
```

Luego, en **Settings → Pages**, seleccione
**Deploy from a branch → main → /docs**.

### Verificación antes de publicar

```bash
quarto render                # debe terminar sin errores
python -m http.server -d _site 8000
```

Abra `http://localhost:8000` y revise que el modo oscuro, las presentaciones y
los enlaces internos funcionen.

---

## Personalizar

### Cambiar la identidad visual

Los colores están definidos como tokens en `styles/custom.scss`
(modo claro), `styles/custom-dark.scss` (modo oscuro) y
`styles/reveal-rds.scss` (presentaciones). Cambiar el acento principal es
editar `--rds-cyan` en los tres archivos.

### Las nueve tarjetas pedagógicas

El material usa un vocabulario visual fijo. Se invocan como `divs` de Pandoc:

```markdown
::: {.rds-card .caso}
Una situación concreta que hay que resolver.
:::

::: {.rds-card .dilema data-label="DILEMA 07 · EL UMBRAL"}
Con etiqueta personalizada.
:::
```

Clases disponibles: `caso`, `datos`, `decide`, `dilema`, `riesgo`, `prueba`,
`codigo`, `reflexiona`, `decision`.

### Añadir un encuentro

1. Crear `encuentros/encuentro-06.qmd`.
2. Crear `slides/06-titulo.qmd` copiando el bloque `format: revealjs` de una
   presentación existente.
3. Añadir ambos a la navegación en `_quarto.yml`.

---

## Licencia

- **Contenido** (textos, materiales didácticos, presentaciones):
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)
- **Código** (scripts, notebooks, hojas de estilo):
  [MIT](https://opensource.org/licenses/MIT)

Las obras citadas conservan sus propias licencias. *Data Feast* es una
publicación de Dejusticia bajo licencia CC BY-NC-SA 4.0.

---

## Créditos y advertencia

Material docente para la Especialización en Análisis Estadístico.

Este repositorio **no constituye asesoría jurídica**. Las referencias
normativas son material didáctico y pueden desactualizarse: los tres regímenes
que se estudian están en movimiento. Verifique siempre la vigencia en las
fuentes oficiales indicadas en [`lecturas/index.qmd`](lecturas/index.qmd).
