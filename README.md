# Leyes, Ética y Protección de Datos

**Especialización en Análisis Estadístico para Ciencia de Datos**
Docente: **Wilson Sandoval Rodríguez**

Sitio del curso: **<https://wilsonsr.github.io/leyes-etica-proteccion-datos/>**

Repositorio académico construido con [Quarto](https://quarto.org/) y publicado
automáticamente en GitHub Pages. Incluye el sitio navegable, las presentaciones
Reveal.js, los cuadernos de laboratorio en versión estudiante y solución, y el
generador del dataset sintético del caso transversal.

> Los datos no toman decisiones. Las personas diseñan sistemas que las toman.

---

## De qué trata

El curso aborda los **fundamentos legales** de la protección de datos, los
**marcos de ética de los datos** y las **técnicas específicas de protección**
aplicables a proyectos de analítica, inteligencia artificial y datos masivos.
Busca fortalecer la capacidad del especialista en análisis estadístico para
reconocer e integrar consideraciones legales, éticas y técnicas en la toma de
decisiones sobre datos.

Todo tema recorre la misma ruta de aprendizaje:

```
PROBLEMA → DATOS → ANÁLISIS → DECISIÓN → IMPLICACIÓN LEGAL/ÉTICA → CONTROL Y EVIDENCIA
```

La legislación aparece cuando hace falta para resolver un problema concreto, no
como punto de partida de la explicación.

## Las tres unidades

| | Unidad | Pregunta | Semanas | Peso |
|:--:|:--|:--|:--:|:--:|
| 1 | Fundamentos legales de la protección de datos y regulaciones relacionadas con ciencia de datos | ¿Podemos hacerlo? | 1–4 | 50 % |
| 2 | Ética de los datos aplicada a proyectos de analítica y gestión de datos en los sectores público y privado | ¿Debemos hacerlo? | 5–7 | 25 % |
| 3 | Técnicas de protección de datos, inteligencia artificial y datos masivos | ¿Cómo lo hacemos responsablemente? | 8–9 | 25 % |

## Estado del contenido

| Material | Estado |
|:--|:--|
| Sitio, identidad visual, navegación por unidades | ✅ Completo |
| Portada, página de unidades, marco legal, sobre el docente | ✅ Completo |
| Encuentro 1 + presentación + Laboratorio 1 | ✅ Completo |
| Encuentro 2 + presentación + Laboratorio 2 | ✅ Completo |
| Caso DataMarket + dataset sintético + simulador | ✅ Completo |
| Caso Facebook · Banco de 12 dilemas | ✅ Completo |
| Actividades 1 a 4 con rúbricas | ✅ Completas |
| Checklist · Mapa de riesgos · Glosario · Bibliografía | ✅ Completos |
| Guía docente con notas de conducción y soluciones | ✅ Completa |
| Encuentros 3, 4 y 5 | 🔨 Estructura y guion preparados |
| Presentaciones y laboratorios 3 y 4 | 🔨 Pendientes |

---

## Uso local

Requisitos: [Quarto](https://quarto.org/docs/get-started/) ≥ 1.4 y Python ≥ 3.10.

```bash
pip install -r requirements.txt
python scripts/generar_datos.py      # genera el dataset sintético
quarto preview                       # sitio con recarga automática
quarto render                        # sitio completo en _site/
```

Los cuadernos se entregan ya ejecutados en su versión de solución, de modo que
**el sitio se renderiza sin necesidad de ejecutar Python**.

### Los cuadernos

Se generan desde una sola fuente para que las dos versiones no se
desincronicen:

```bash
python scripts/construir_labs.py
cd labs
jupyter nbconvert --to notebook --execute --inplace lab01-solucion.ipynb
jupyter nbconvert --to notebook --execute --inplace lab02-solucion.ipynb
```

| Archivo | Para quién | Contenido |
|:--|:--|:--|
| `labs/lab0N-estudiante.ipynb` | Estudiante | Sin salidas, con bloques `TODO` |
| `labs/lab0N-solucion.ipynb` | Docente | Ejecutado, con respuestas orientativas plegadas |

Los cuadernos buscan el CSV en la carpeta local y, si no lo encuentran, lo
descargan del repositorio. Así funcionan en **Google Colab sin instalar nada**,
que es la vía recomendada para los estudiantes.

---

## Estructura

```
leyes-etica-proteccion-datos/
│
├── index.qmd                    # portada
├── unidades.qmd                 # las tres unidades y la ruta de aprendizaje
├── programa.qmd                 # plan y evaluación
├── metodologia.qmd              # cómo funciona cada encuentro
├── docente.qmd                  # sobre el docente
├── _quarto.yml                  # configuración, navegación y tema
├── referencias.bib
│
├── marco-legal/index.qmd        # material de consulta permanente
├── guia-docente/index.qmd       # notas de conducción y soluciones
│
├── encuentros/encuentro-0{1..5}.qmd
├── laboratorios/lab-0{1,2}.qmd  # páginas web de los laboratorios
├── slides/0{1,2}-*.qmd          # presentaciones Reveal.js
├── labs/lab0{1,2}-{estudiante,solucion}.ipynb
├── casos/                       # DataMarket · Facebook · dilemas
├── actividades/actividad-0{1..4}.qmd
├── recursos/                    # checklist · mapa de riesgos · glosario
├── lecturas/index.qmd
│
├── data/clientes_sinteticos.csv # 1 512 × 35, sintético y reproducible
├── scripts/generar_datos.py
├── scripts/construir_labs.py
├── assets/                      # imagen del docente y datos del simulador
├── styles/                      # tema claro, oscuro, Reveal y componentes
└── .github/workflows/publish.yml
```

---

## El caso transversal

**DataMarket Analytics** es una empresa colombiana ficticia de comercio
electrónico. Su base de clientes cambia de problema cada semana:

| Semana | Situación | Unidad |
|:--:|:--|:--:|
| 1 | Quiere predecir abandono con 35 variables | 1 |
| 2 | Aparecen problemas de origen, finalidad y tratamiento | 1 |
| 3 | Quiere operar en Brasil y Chile | 1 |
| 4 | Descubre clientes residentes en la Unión Europea | 1 |
| 5 | El modelo predice mejor usando variables que discriminan | 2 |
| 7 | Necesita compartir la base con un proveedor externo | 2 |
| 8 | Tiene que anonimizar de verdad, y medirlo | 3 |
| 9 | El grupo escribe el decálogo | 3 |

### El dataset

`data/clientes_sinteticos.csv` — **1 512 registros × 35 variables**, generado
por `scripts/generar_datos.py` con semilla fija. Diseñado para que las
discusiones aparezcan solas:

- **236 registros** sin evidencia de autorización.
- **74 registros** con residencia en la Unión Europea.
- Tres variables proxy de datos sensibles.
- El **83,9 %** de los registros es único con solo cuatro cuasi-identificadores;
  baja a **10,6 %** tras generalizar.
- La variable objetivo depende parcialmente de los proxies, de modo que el
  «modelo B» del Laboratorio 2 realmente predice mejor (AUC 0,875 frente a
  0,833) a costa de usar variables problemáticas.

> ⚠️ **Todos los datos son sintéticos.** Ninguna persona real está
> representada. Nunca sustituya esta base por datos reales de una organización.

---

## Componentes interactivos

El sitio no depende de librerías externas. Todo está en `styles/`:

| Componente | Cómo se usa |
|:--|:--|
| Ficha pedagógica | `<div class="ix-ficha">` con qué aprenderá, qué hacer, duración, evidencia, unidad y siguiente paso |
| Pregunta con retroalimentación | `::: {.ix-quiz}` con opciones `::: {.ix-op data-valor="bien\|mal\|parcial" data-fb="…"}` |
| Pista y respuesta | `::: {.ix-pista}` y `::: {.ix-respuesta}` — `<details>` nativo |
| Checklist con memoria | `<ul class="ix-check" data-id="…">` — recuerda el avance en el navegador |
| Simulador de reidentificación | `<div class="ix-sim" data-sim="reident" data-src="…/assets/reident.json">` |
| Tarjetas del curso | `::: {.rds-card .caso}` — `caso`, `datos`, `decide`, `dilema`, `riesgo`, `prueba`, `codigo`, `reflexiona`, `decision` |

Los datos del simulador se precalculan sobre la base real del curso. Si cambia
la semilla o el tamaño del dataset, hay que regenerarlos.

---

## Publicación

El repositorio incluye `.github/workflows/publish.yml`, que renderiza y publica
en cada `push` a `main`. En **Settings → Pages** debe estar seleccionado
*Source: GitHub Actions* (configuración de una sola vez, ya realizada).

Con GitHub Desktop: escribir el mensaje → **Commit to main** → **Push origin**.
El sitio se actualiza solo en un minuto y medio.

---

## Licencia

- **Contenido** (textos, materiales didácticos, presentaciones):
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)
- **Código** (scripts, cuadernos, hojas de estilo):
  [MIT](https://opensource.org/licenses/MIT)

Las obras citadas conservan sus propias licencias.

Este repositorio **no constituye asesoría jurídica**. Las referencias normativas
son material didáctico y pueden desactualizarse. La página de
[Marco legal](marco-legal/index.qmd) lleva fecha de última verificación;
confirme siempre la vigencia en las fuentes oficiales allí indicadas.
