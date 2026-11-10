"""
construir_labs.py
=================

Genera los seis cuadernos del curso a partir de una sola fuente:

    labs/lab01-estudiante.ipynb    labs/lab01-solucion.ipynb
    labs/lab02-estudiante.ipynb    labs/lab02-solucion.ipynb
    labs/lab03-estudiante.ipynb    labs/lab03-solucion.ipynb

Por qué existe este script
--------------------------
1. Evita que las dos versiones de un laboratorio se desincronicen.
2. La versión **estudiante** se entrega sin salidas y con bloques `TODO`:
   quien la abra tiene que ejecutar y decidir, no leer respuestas.
3. La versión **solución** lleva las respuestas orientativas y se usa para
   preparar la sesión y para revisar entregas.

Uso
---
    python scripts/construir_labs.py
    cd labs && jupyter nbconvert --to notebook --execute --inplace lab01-solucion.ipynb

Los cuadernos cargan los datos desde el repositorio publicado si no encuentran
el CSV local, de modo que funcionan en Google Colab sin instalar ni descargar
nada.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "labs"

URL_DATOS = (
    "https://raw.githubusercontent.com/wilsonsr/"
    "leyes-etica-proteccion-datos/main/data/clientes_sinteticos.csv"
)

CARGA = f'''
from pathlib import Path
import pandas as pd

# Funciona en tres sitios sin cambiar nada:
#   - dentro del repositorio (labs/ o raíz)
#   - en Google Colab
#   - en cualquier equipo con internet
RUTA = Path("../data/clientes_sinteticos.csv")
if not RUTA.exists():
    RUTA = Path("data/clientes_sinteticos.csv")
if not RUTA.exists():
    RUTA = "{URL_DATOS}"

print("Origen de los datos:", RUTA)
'''.strip()


class Cuaderno:
    """Acumula celdas y las escribe en las dos variantes."""

    def __init__(self, titulo: str, subtitulo: str):
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.celdas: list[tuple[str, str, str]] = []   # (tipo, estudiante, solucion)

    # --- API de construcción ---------------------------------------------
    def md(self, texto: str):
        self.celdas.append(("md", texto.strip("\n"), texto.strip("\n")))

    def md_var(self, estudiante: str, solucion: str):
        """Markdown distinto en cada versión."""
        self.celdas.append(("md", estudiante.strip("\n"), solucion.strip("\n")))

    def code(self, texto: str):
        self.celdas.append(("code", texto.strip("\n"), texto.strip("\n")))

    def code_var(self, estudiante: str, solucion: str):
        """Código con TODO en la versión del estudiante."""
        self.celdas.append(("code", estudiante.strip("\n"), solucion.strip("\n")))

    def pregunta(self, etiqueta: str, texto: str, respuesta: str):
        """Pregunta visible en ambas; la respuesta solo en la solución."""
        base = f"::: {{.rds-card .{etiqueta}}}\n{texto.strip()}\n:::"
        sol = base + (
            "\n\n::: {.callout-note collapse=\"true\"}\n"
            "## Respuesta orientativa (versión docente)\n\n"
            f"{respuesta.strip()}\n:::"
        )
        self.celdas.append(("md", base, sol))

    # --- escritura --------------------------------------------------------
    def escribir(self, nombre: str):
        for variante, idx in (("estudiante", 1), ("solucion", 2)):
            nb = nbf.v4.new_notebook()
            celdas = []

            encabezado = (
                f"# {self.titulo}\n\n"
                f"**{self.subtitulo}**\n\n"
                f"Leyes, Ética y Protección de Datos · Especialización en Análisis "
                f"Estadístico para Ciencia de Datos · Docente: Wilson Sandoval Rodríguez\n\n"
                f"---\n\n"
            )
            if variante == "estudiante":
                encabezado += (
                    "> **Versión del estudiante.** Las celdas están sin ejecutar y hay "
                    "bloques marcados con `TODO` que usted debe completar. Ejecute de "
                    "arriba hacia abajo y responda cada pregunta antes de continuar.\n\n"
                    "> Todos los datos son **sintéticos**. Ninguna persona real está "
                    "representada.\n"
                )
            else:
                encabezado += (
                    "> **Versión con soluciones.** Material de apoyo docente. "
                    "Incluye respuestas orientativas y las celdas ya ejecutadas.\n\n"
                    "> Todos los datos son **sintéticos**. Ninguna persona real está "
                    "representada.\n"
                )
            celdas.append(nbf.v4.new_markdown_cell(encabezado))

            for tipo, est, sol in self.celdas:
                texto = est if variante == "estudiante" else sol
                if tipo == "md":
                    celdas.append(nbf.v4.new_markdown_cell(texto))
                else:
                    celdas.append(nbf.v4.new_code_cell(texto))

            nb["cells"] = celdas
            nb.metadata["kernelspec"] = {
                "display_name": "Python 3", "language": "python", "name": "python3"
            }
            nb.metadata["language_info"] = {"name": "python", "version": "3.11"}

            DESTINO.mkdir(parents=True, exist_ok=True)
            salida = DESTINO / f"{nombre}-{variante}.ipynb"
            nbf.write(nb, salida)
            print("escrito:", salida.relative_to(RAIZ), f"({len(celdas)} celdas)")


# ==========================================================================
# LABORATORIO 1
# ==========================================================================

def lab01() -> Cuaderno:
    c = Cuaderno(
        "Laboratorio 1 · ¿Qué sabe realmente esta base sobre nosotros?",
        "Explorar → Analizar → Experimentar → Decidir → Justificar → Reflexionar",
    )

    c.md("""
## Qué va a hacer aquí

| | |
|:--|:--|
| **Aprenderá a** | Clasificar variables por el riesgo que introducen y medir el riesgo de reidentificación de una base |
| **Duración** | 35 minutos |
| **Evidencia** | Sus respuestas a las 9 preguntas y la base minimizada que construya |
| **Unidad** | 1 · Fundamentos legales |

Este cuaderno **no es una clase de programación**. El código es corto a
propósito. Lo que se evalúa es la decisión que usted toma después de leer la
salida.
""")

    # ------------------------------------------------ EXPLORAR
    c.md("---\n\n# 1 · EXPLORAR\n\n*¿Qué hay en esta base?*")
    c.code(CARGA)
    c.code("""
df = pd.read_csv(RUTA)
pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 130)

print(f"Registros: {len(df)}   Variables: {df.shape[1]}")
df.head(3)
""")

    c.pregunta(
        "decide",
        "**Pregunta 1.** Mire las tres primeras filas. Sin contar todavía las "
        "columnas: ¿cuántas de las que alcanza a ver le permitirían, por sí solas, "
        "llamar por teléfono a esa persona?",
        "Cinco: `nombre`, `email`, `telefono`, `documento` y `direccion`. La "
        "respuesta importa menos que la reacción: casi nadie espera encontrar "
        "cinco identificadores directos en una base «de comportamiento de compra».",
    )

    c.code("""
for i, col in enumerate(df.columns, start=1):
    print(f"{i:>2}. {col}")
""")

    c.code("""
resumen = pd.DataFrame({
    "tipo": df.dtypes.astype(str),
    "no_nulos": df.notna().sum(),
    "distintos": df.nunique(),
})
resumen["% distintos"] = (resumen["distintos"] / len(df) * 100).round(1)
resumen.sort_values("% distintos", ascending=False).head(12)
""")

    c.pregunta(
        "decide",
        "**Pregunta 2.** Las variables con un porcentaje de valores distintos "
        "cercano al 100 % son casi siempre identificadores. ¿Cuáles aparecen "
        "arriba y cuál de ellas *no* esperaba encontrar ahí?",
        "`cliente_id`, `documento`, `direccion`, `email`, `telefono` y también "
        "`ip`. La que sorprende es `ip`: es un identificador en línea, se trata "
        "como dato personal y casi nunca se documenta como tal.",
    )

    # ------------------------------------------------ ANALIZAR
    c.md("---\n\n# 2 · ANALIZAR\n\n*¿Qué significa lo que hay?*")

    c.md("""
### Los faltantes no siempre son un problema de imputación

La pregunta útil no es *cuántos* faltan, sino *por qué* faltan.
""")

    c.code("""
faltantes = (
    df.isna().sum().loc[lambda s: s > 0]
      .sort_values(ascending=False).to_frame("faltantes")
)
faltantes["%"] = (faltantes["faltantes"] / len(df) * 100).round(1)
faltantes
""")

    c.code("""
# ¿Los faltantes de fecha_autorizacion están repartidos al azar?
pd.crosstab(
    df["origen_dato"],
    df["fecha_autorizacion"].isna().map({True: "sin fecha", False: "con fecha"}),
)
""")

    c.pregunta(
        "riesgo",
        "**Pregunta 3.** Los faltantes de `fecha_autorizacion` no están "
        "repartidos al azar: se concentran en dos orígenes. ¿Cuáles? ¿Y qué "
        "significa, en términos prácticos, no tener fecha de autorización para "
        "esos registros?\n\nEsto no es un problema de imputación. Es un problema "
        "de **evidencia**.",
        "`lista_comprada_tercero` (144 registros) y `enriquecimiento_web` (92). "
        "Suman 236, el 15,6 % de la base. Significa que no se puede acreditar que "
        "esas personas hayan autorizado nada. Imputar esa fecha sería fabricar "
        "evidencia. Lo correcto es aislarlos, no borrarlos: borrarlos destruiría "
        "la prueba de que existieron.",
    )

    c.md("""
### Clasificar por riesgo, no por tipo

El tipo que infiere `pandas` no dice nada sobre el riesgo. `object` puede ser un
nombre propio o una categoría inofensiva.

| Etiqueta | Significa |
|:--|:--|
| `directo` | Identifica a la persona por sí solo |
| `indirecto` | Identifica vía dispositivo, cuenta o ubicación precisa |
| `cuasi` | Solo no identifica; combinado con otros, sí |
| `comportamiento` | Lo que la persona hizo |
| `inferido` | Lo que la empresa dedujo |
| `proxy_sensible` | No es sensible, pero permite inferir uno |
| `control` | Metadato del tratamiento (origen, autorización) |
| `objetivo` | La variable que queremos predecir |
""")

    c.code_var(
        """
# TODO: complete la clasificación de las 35 variables.
# Están resueltas las cinco primeras como ejemplo.
# Discuta las dudosas antes de decidir: latitud, longitud,
# ingresos_mensuales y categoria_top admiten más de una respuesta.

clasificacion = {
    "cliente_id": "indirecto",
    "nombre": "directo",
    "email": "directo",
    "telefono": "directo",
    "documento": "directo",
    # ... complete el resto
}

faltan = set(df.columns) - set(clasificacion)
print(f"Le faltan {len(faltan)} variables por clasificar:")
print(sorted(faltan))
""",
        """
clasificacion = {
    # identificadores directos
    "nombre": "directo", "email": "directo", "telefono": "directo",
    "documento": "directo", "direccion": "directo",
    # identificadores indirectos
    "cliente_id": "indirecto", "ip": "indirecto", "dispositivo": "indirecto",
    "latitud": "indirecto", "longitud": "indirecto",
    # cuasi-identificadores
    "fecha_nacimiento": "cuasi", "edad": "cuasi", "sexo": "cuasi",
    "ciudad": "cuasi", "barrio": "cuasi", "ocupacion": "cuasi",
    "estrato": "cuasi", "ingresos_mensuales": "cuasi",
    "pais_residencia": "cuasi",
    # comportamiento
    "visitas_web": "comportamiento", "productos_vistos": "comportamiento",
    "categoria_top": "comportamiento", "compras_6m": "comportamiento",
    "monto_compras": "comportamiento", "fecha_ultima_compra": "comportamiento",
    "canal_adquisicion": "comportamiento",
    # proxies de datos sensibles
    "compras_farmacia_6m": "proxy_sensible",
    "entrega_asistida": "proxy_sensible",
    "busquedas_maternidad": "proxy_sensible",
    # datos inferidos por la empresa
    "score_riesgo_interno": "inferido", "segmento": "inferido",
    # metadatos de tratamiento
    "origen_dato": "control", "fecha_autorizacion": "control",
    "consentimiento_marketing": "control",
    # objetivo
    "churn": "objetivo",
}

faltan = set(df.columns) - set(clasificacion)
print("Variables sin clasificar:", sorted(faltan) or "ninguna")
""",
    )

    c.code("""
mapa = pd.Series(clasificacion, name="categoria").rename_axis("variable")
mapa.value_counts().to_frame("n_variables")
""")

    c.pregunta(
        "decide",
        "**Pregunta 4.** Esta clasificación es **discutible a propósito**. Elija "
        "dos variables que usted habría puesto en otra categoría y defienda el "
        "cambio.\n\nCandidatas frecuentes: `latitud`/`longitud` (¿indirecto o "
        "cuasi?), `ingresos_mensuales` (¿cuasi o proxy sensible?), "
        "`categoria_top` (¿comportamiento o proxy sensible, cuando el valor es "
        "`salud_bienestar`?).",
        "No hay una respuesta correcta; hay respuestas argumentadas. "
        "`latitud`/`longitud` con ruido de ±3 km funcionan más como "
        "cuasi-identificador que como identificador directo, pero combinadas con "
        "`barrio` se vuelven muy identificadoras. `ingresos_mensuales` es proxy "
        "socioeconómico y por tanto proxy de un atributo que puede discriminar. "
        "`categoria_top = salud_bienestar` es exactamente un proxy sensible. "
        "Lo que se evalúa es que el estudiante note que la categoría depende del "
        "**uso**, no solo del contenido.",
    )

    # ------------------------------------------------ EXPERIMENTAR
    c.md("---\n\n# 3 · EXPERIMENTAR\n\n*¿Qué pasa si…?*")

    c.md("""
### El experimento central del laboratorio

Ninguna de estas columnas identifica sola. Veamos qué ocurre al combinarlas.
""")

    c.code("""
def riesgo_unicidad(datos, columnas):
    # Cuenta cuántos registros quedan SOLOS en su grupo (k = 1).
    grupos = datos.groupby(columnas, dropna=False, observed=True).size()
    unicos = int((grupos == 1).sum())
    return {
        "variables": " + ".join(columnas),
        "combinaciones": int(len(grupos)),
        "registros k=1": unicos,
        "% en riesgo": round(unicos / len(datos) * 100, 1),
        "k mínimo": int(grupos.min()),
    }


combinaciones = [
    ["ciudad"],
    ["ciudad", "sexo"],
    ["ciudad", "sexo", "edad"],
    ["ciudad", "sexo", "edad", "ocupacion"],
    ["ciudad", "barrio", "sexo", "edad"],
    ["ciudad", "barrio", "sexo", "edad", "ocupacion", "estrato"],
]

pd.DataFrame([riesgo_unicidad(df, c) for c in combinaciones])
""")

    c.pregunta(
        "riesgo",
        "**Pregunta 5.** Con una sola variable el riesgo es cero. ¿A partir de "
        "cuántas variables la mayoría de las personas de esta base queda sola en "
        "su grupo?\n\nAnote el número. Es el argumento que va a necesitar la "
        "próxima vez que alguien diga «ya le quitamos los nombres».",
        "Con cuatro variables (ciudad, sexo, edad, ocupación) el 83,9 % de los "
        "registros queda solo. Con seis, el 97,9 %. El salto grande ocurre al "
        "agregar `edad`, que por sí sola tiene 65 valores posibles.",
    )

    c.md("""
### Ahora al revés: reducir el riesgo y medirlo

La anonimización es un **resultado que se mide**, no una operación que se
aplica. Apliquemos tres generalizaciones y volvamos a medir.
""")

    c.code_var(
        """
caso = df[["edad", "sexo", "ciudad", "ocupacion"]].copy()
caso_v2 = caso.copy()

# (a) Edad en rangos de 5 años
caso_v2["edad"] = pd.cut(caso_v2["edad"], bins=range(15, 90, 5)).astype(str)

# TODO (b): agrupe `ocupacion` en 3 o 4 categorías amplias con un diccionario.
# TODO (c): agrupe `ciudad` en regiones.
# Después ejecute la comparación de abajo y vea cuánto bajó el riesgo.

pd.DataFrame([
    {"versión": "original", **riesgo_unicidad(caso, ["edad", "sexo", "ciudad", "ocupacion"])},
    {"versión": "generalizada", **riesgo_unicidad(caso_v2, ["edad", "sexo", "ciudad", "ocupacion"])},
])
""",
        """
caso = df[["edad", "sexo", "ciudad", "ocupacion"]].copy()
caso_v2 = caso.copy()

# (a) Edad en rangos de 5 años
caso_v2["edad"] = pd.cut(caso_v2["edad"], bins=range(15, 90, 5)).astype(str)

# (b) Ocupación en tres bloques amplios
grandes = {
    "Ingeniero/a": "técnico-profesional", "Tecnico/a": "técnico-profesional",
    "Disenador/a": "técnico-profesional", "Contador/a": "técnico-profesional",
    "Abogado/a": "técnico-profesional", "Administrador/a": "técnico-profesional",
    "Docente": "servicios", "Enfermero/a": "servicios",
    "Comerciante": "servicios", "Independiente": "servicios",
    "Estudiante": "sin actividad remunerada",
    "Pensionado/a": "sin actividad remunerada",
}
caso_v2["ocupacion"] = caso_v2["ocupacion"].map(grandes).fillna("otro")

# (c) Ciudad en regiones
regiones = {
    "Bogota": "Centro", "Ibague": "Centro", "Villavicencio": "Centro",
    "Medellin": "Antioquia-Eje", "Pereira": "Antioquia-Eje", "Manizales": "Antioquia-Eje",
    "Cali": "Pacífico", "Pasto": "Pacífico",
    "Barranquilla": "Caribe", "Cartagena": "Caribe", "Santa Marta": "Caribe",
    "Bucaramanga": "Nororiente",
}
caso_v2["ciudad"] = caso_v2["ciudad"].map(regiones).fillna("otro")

pd.DataFrame([
    {"versión": "original", **riesgo_unicidad(caso, ["edad", "sexo", "ciudad", "ocupacion"])},
    {"versión": "generalizada", **riesgo_unicidad(caso_v2, ["edad", "sexo", "ciudad", "ocupacion"])},
])
""",
    )

    c.pregunta(
        "prueba",
        "**Pregunta 6.** El porcentaje en riesgo bajó. ¿Bajó lo suficiente?\n\n"
        "No hay un umbral universal. Lo que sí hay es una obligación: **decir "
        "cuál es el umbral que se aceptó y por qué**. Escriba el suyo.\n\nY la "
        "contrapartida: ¿qué análisis dejó de ser posible con la base "
        "generalizada? ¿Vale la pena?",
        "De 83,9 % a 10,6 %. Sigue habiendo 160 personas solas en su grupo, así "
        "que la base **no** es anónima: es menos riesgosa. Lo que se pierde: "
        "cualquier análisis por municipio, cualquier análisis de la relación "
        "edad–comportamiento con resolución fina y cualquier segmentación "
        "ocupacional específica. El criterio profesional es declarar el umbral "
        "(por ejemplo *k* ≥ 5 para el 95 % de los registros) y mostrar el número.",
    )

    # ------------------------------------------------ DECIDIR
    c.md("---\n\n# 4 · DECIDIR\n\n*¿Qué hacemos?*")

    c.md("""
### Minimizar no es «quitar columnas»

Minimizar es responder, para cada columna, **por qué la necesito para esta
finalidad concreta**. La finalidad declarada aquí es: *predecir abandono para
una campaña de retención*.
""")

    c.code_var(
        """
# TODO: construya la lista mínima de variables que justificaría ante la
# Dirección Comercial. Debe poder decir en una frase por qué cada una está.

variables_minimas = [
    "cliente_id",   # necesario para poder actuar sobre el cliente
    # ... complete
    "churn",        # variable objetivo
]

df_min = df[variables_minimas].copy()
print(f"Original: {df.shape[1]} variables  ->  Minimizada: {df_min.shape[1]}")
""",
        """
variables_minimas = [
    "cliente_id",            # necesario para actuar sobre el cliente
    "visitas_web",
    "productos_vistos",
    "compras_6m",
    "monto_compras",
    "fecha_ultima_compra",
    "canal_adquisicion",
    "churn",
]

df_min = df[variables_minimas].copy()
print(f"Original: {df.shape[1]} variables  ->  Minimizada: {df_min.shape[1]}")
print(f"Reducción: {100 - df_min.shape[1] / df.shape[1] * 100:.0f} %")
""",
    )

    c.md("""
### Seudonimizar no es anonimizar

Reemplazamos el identificador por un hash. Es buena práctica **y no es
anonimización**: la celda siguiente muestra por qué.
""")

    c.code("""
import hashlib

SAL = "curso-lepd-2026"   # en producción: secreto, rotado y fuera del código


def seudonimizar(valor, sal=SAL, largo=12):
    return hashlib.sha256(f"{sal}{valor}".encode("utf-8")).hexdigest()[:largo].upper()


df_seudo = df_min.copy()
df_seudo["cliente_id"] = df_seudo["cliente_id"].map(seudonimizar)
df_seudo.head(4)
""")

    c.code("""
# La tabla de equivalencias: esto es lo que impide llamarlo anonimización.
tabla_equivalencias = pd.DataFrame({
    "cliente_id": df["cliente_id"],
    "seudonimo": df["cliente_id"].map(seudonimizar),
    "nombre": df["nombre"],
})
tabla_equivalencias.head(4)
""")

    c.pregunta(
        "decision",
        "**Pregunta 7.** Mientras exista la tabla anterior, los datos siguen "
        "siendo datos personales.\n\nY la tabla **tiene que existir**, porque sin "
        "ella la empresa no puede contactar al cliente que el modelo señaló. Ese "
        "es el nudo: la finalidad del proyecto —actuar sobre personas concretas— "
        "es incompatible con la anonimización real.\n\n¿Dónde debería vivir esa "
        "tabla y quién debería poder leerla?",
        "En un sistema separado del entorno de análisis, con control de acceso "
        "por rol y registro de consultas. El equipo de analítica trabaja con "
        "seudónimos; solo el proceso que ejecuta la campaña resuelve la "
        "equivalencia, y queda traza de cada resolución. La diferencia entre las "
        "tres nociones del curso: **minimizar** es no traer lo que no se necesita; "
        "**seudonimizar** es sustituir el identificador conservando la "
        "reversibilidad; **anonimizar** es lograr que nadie sea reidentificable "
        "con medios razonables, y se mide.",
    )

    # ------------------------------------------------ JUSTIFICAR
    c.md("---\n\n# 5 · JUSTIFICAR\n\n*¿Con qué evidencia?*")

    c.md("""
Una decisión sin evidencia no cuenta como decisión. Cerramos escribiendo el
registro del laboratorio.
""")

    c.code_var(
        """
# TODO: complete el registro con SUS decisiones y SU umbral.

registro = pd.DataFrame([{
    "proyecto": "DataMarket · modelo de abandono",
    "fecha": str(pd.Timestamp("today").date()),
    "variables_originales": df.shape[1],
    "variables_conservadas": df_min.shape[1],
    "criterio_minimizacion": "TODO: ¿por qué esas y no otras?",
    "umbral_riesgo_aceptado": "TODO: ¿qué k mínimo acepta y por qué?",
    "registros_sin_evidencia_origen": int(df["fecha_autorizacion"].isna().sum()),
    "decision_sobre_esos_registros": "TODO: ¿excluir, aislar, regularizar?",
    "responsable": "TODO: su nombre",
}])

registro.T.rename(columns={0: "valor"})
""",
        """
registro = pd.DataFrame([{
    "proyecto": "DataMarket · modelo de abandono",
    "fecha": str(pd.Timestamp("today").date()),
    "variables_originales": df.shape[1],
    "variables_conservadas": df_min.shape[1],
    "criterio_minimizacion": ("solo comportamiento de compra y navegación; "
                              "sin demografía ni proxies de datos sensibles"),
    "umbral_riesgo_aceptado": "k >= 5 para al menos el 95 % de los registros",
    "registros_sin_evidencia_origen": int(df["fecha_autorizacion"].isna().sum()),
    "decision_sobre_esos_registros": "aislados, no borrados; excluidos del entrenamiento",
    "responsable": "equipo de analítica + Dirección Comercial",
}])

registro.to_csv("registro_lab01.csv", index=False, encoding="utf-8")
registro.T.rename(columns={0: "valor"})
""",
    )

    c.pregunta(
        "decision",
        "**Pregunta 8.** Suponga que esta base se va a compartir con un "
        "proveedor externo de analítica. Con lo que midió hoy, ¿la entregaría?\n\n"
        "Si su respuesta es «sí, con condiciones», enumere las condiciones.",
        "Tres salidas son defendibles: (1) entregar la versión generalizada, con "
        "el riesgo medido y aceptado por escrito; (2) entregar la seudonimizada "
        "bajo contrato de encargo del tratamiento, ambiente controlado, "
        "prohibición de cruce y plazo de destrucción; (3) no entregarla y ofrecer "
        "que el proveedor entrene dentro del perímetro, o entregar datos "
        "sintéticos. Lo que no es defendible es entregarla sin medir.",
    )

    # ------------------------------------------------ REFLEXIONAR
    c.md("---\n\n# 6 · REFLEXIONAR\n\n*¿Y en mi trabajo?*")

    c.pregunta(
        "reflexiona",
        "**Pregunta 9 · de salida.** Tome una base con la que trabaje realmente. "
        "Ejecute mentalmente el bloque 3 sobre ella: ¿cuántas variables "
        "cuasi-identificadoras tiene?\n\n"
        "> **¿Qué tendría que cambiar en mi proyecto de datos?**\n\n"
        "Tres líneas. Nombre una variable concreta y un cambio ejecutable.",
        "Lo que se busca no es una reflexión general sino un cambio nombrado: "
        "«voy a dejar de cargar `documento` en el dataset de modelado», «voy a "
        "medir k antes de entregar el tablero al área comercial». Si la respuesta "
        "es «ser más cuidadoso», no cuenta.",
    )

    c.md("""
---

## Lo que hicimos

1. Exploramos el tamaño real del problema: 1 512 registros × 35 variables.
2. Descubrimos que los faltantes de `fecha_autorizacion` no eran ruido sino la
   huella del origen de los datos.
3. Clasificamos las variables por riesgo, no por tipo.
4. Medimos que cuatro cuasi-identificadores dejan sola a la gran mayoría de las
   personas de la base.
5. Construimos una base minimizada para una finalidad declarada.
6. Seudonimizamos y vimos por qué eso no anonimiza.
7. Generalizamos y **medimos** cuánto bajó el riesgo, y cuánta utilidad costó.

**Siguiente paso:** Laboratorio 2 · auditoría de un pipeline completo, y el
dilema entre un modelo que predice mejor y uno que usa menos.

**Marco legal relacionado:** la excepción para fines estadísticos y científicos
del art. 10 de la Ley 1581 de 2012 exige suprimir la identidad de los titulares.
Este laboratorio muestra por qué eso no es trivial.
""")

    return c


# ==========================================================================
# LABORATORIO 2
# ==========================================================================

def lab02() -> Cuaderno:
    c = Cuaderno(
        "Laboratorio 2 · Auditoría de un pipeline de datos",
        "Explorar → Analizar → Experimentar → Decidir → Justificar → Reflexionar",
    )

    c.md("""
## Qué va a hacer aquí

| | |
|:--|:--|
| **Aprenderá a** | Auditar un pipeline etapa por etapa y comparar dos modelos que difieren en desempeño y en lo que están dispuestos a usar |
| **Duración** | 40 minutos |
| **Evidencia** | La matriz de auditoría, el registro de decisión y sus respuestas |
| **Unidad** | 1 · Fundamentos legales (prepara la Unidad 2) |

**No es un ejercicio de rendimiento predictivo.** Las métricas están aquí para
sostener una discusión, no para ganar una competencia.
""")

    # ------------------------------------------------ EXPLORAR
    c.md("---\n\n# 1 · EXPLORAR\n\n*¿De dónde vienen estos datos?*")

    c.code(CARGA)
    c.code("""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 140)
plt.rcParams.update({"figure.figsize": (7.2, 4.2), "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10})

df = pd.read_csv(RUTA, parse_dates=["fecha_ultima_compra", "fecha_autorizacion"])
print(f"{df.shape[0]} registros · {df.shape[1]} variables")
""")

    c.code("""
origen = (
    df["origen_dato"].value_counts().to_frame("registros")
      .assign(**{"%": lambda d: (d["registros"] / len(df) * 100).round(1)})
)
origen["con_autorizacion_fechada"] = df.groupby("origen_dato")["fecha_autorizacion"].apply(lambda s: s.notna().sum())
origen["consent_marketing"] = df.groupby("origen_dato")["consentimiento_marketing"].sum()
origen
""")

    c.pregunta(
        "riesgo",
        "**Pregunta 1.** Dos orígenes no tienen ni una sola autorización fechada. "
        "¿Cuáles son y cuántos registros suman?\n\nFíjese también en "
        "`consent_marketing`: la autorización de marketing no se distribuye de "
        "forma pareja. ¿Qué implicación tiene para la petición de «publicidad "
        "personalizada» que llegó esta semana?",
        "`lista_comprada_tercero` y `enriquecimiento_web`, 236 registros. Para "
        "publicidad personalizada el problema es doble: no hay evidencia de "
        "autorización en esos registros, y en los demás la autorización de "
        "marketing solo es mayoritaria en `programa_fidelizacion`. Segmentar "
        "internamente y comunicar datos a una plataforma publicitaria son dos "
        "finalidades distintas.",
    )

    c.code("""
UE = {"Espana", "Alemania", "Francia", "Italia"}
territorio = df["pais_residencia"].value_counts().to_frame("registros")
territorio["régimen probable"] = np.where(
    territorio.index.isin(UE), "GDPR (UE)",
    np.where(territorio.index == "Colombia", "Ley 1581 de 2012", "otro · verificar"))
territorio
""")

    c.pregunta(
        "decide",
        "**Pregunta 2.** ¿Cuántos residentes en la Unión Europea hay? Es un "
        "número pequeño frente al total.\n\n¿Cambia algo que sean pocos? ¿Por qué "
        "sí o por qué no?",
        "74 registros. No cambia nada: el ámbito de aplicación del GDPR no tiene "
        "umbral cuantitativo. Lo que sí cambia es la proporcionalidad de la "
        "respuesta organizativa. Este es el punto de partida de la Actividad 2.",
    )

    # ------------------------------------------------ ANALIZAR
    c.md("---\n\n# 2 · ANALIZAR\n\n*¿Qué hace el pipeline con ellos?*")

    c.md("""
### Aislar, no borrar

Los registros sin evidencia de origen se marcan y se separan. Borrarlos
destruiría la prueba de que existieron.
""")

    c.code("""
SIN_EVIDENCIA = ["lista_comprada_tercero", "enriquecimiento_web"]
df["evidencia_origen"] = np.where(
    df["origen_dato"].isin(SIN_EVIDENCIA), "sin evidencia", "con evidencia")

df_apto = df[df["evidencia_origen"] == "con evidencia"].copy()
df_aislado = df[df["evidencia_origen"] == "sin evidencia"].copy()

print(f"Base original            : {len(df):>5}")
print(f"Aptos para entrenamiento : {len(df_apto):>5}")
print(f"Aislados                 : {len(df_aislado):>5}  ({len(df_aislado)/len(df)*100:.1f} %)")
""")

    c.pregunta(
        "decide",
        "**Pregunta 3.** Perdimos un 15 % de los registros. La Dirección "
        "Comercial va a preguntar por qué el modelo se entrenó con menos "
        "datos.\n\nEscriba la respuesta en **dos frases**, sin usar la palabra "
        "«ley».",
        "Ejemplo: «No podemos acreditar de dónde salieron esos 236 registros ni "
        "que esas personas hayan aceptado que los usemos. Si mañana uno de ellos "
        "pregunta, no tendríamos qué responder, y el modelo quedaría "
        "comprometido entero.» El punto pedagógico es que el argumento de "
        "trazabilidad se sostiene solo, sin apelar a la autoridad de la norma.",
    )

    c.md("""
### Feature engineering: las inferencias que creamos nosotros

Esta es la etapa donde el analista **fabrica** datos nuevos sobre personas.
""")

    c.code("""
CORTE = pd.Timestamp("2026-08-31")   # fecha de corte del análisis

df_apto["dias_desde_ultima_compra"] = (CORTE - df_apto["fecha_ultima_compra"]).dt.days
df_apto["ticket_promedio"] = np.where(
    df_apto["compras_6m"] > 0, df_apto["monto_compras"] / df_apto["compras_6m"], 0)
df_apto["intensidad_navegacion"] = (
    df_apto["productos_vistos"] / df_apto["visitas_web"].clip(lower=1))

df_apto[["dias_desde_ultima_compra", "ticket_promedio", "intensidad_navegacion"]].describe().round(2)
""")

    c.pregunta(
        "decide",
        "**Pregunta 4.** Las tres variables anteriores son inofensivas.\n\n"
        "Ahora piense en tres más que el equipo de marketing *podría* pedir y que "
        "no lo serían. Escríbalas con el nombre que tendrían en el código.\n\n"
        "Pista: con `compras_farmacia_6m`, `busquedas_maternidad` y `edad` se "
        "pueden construir varias.",
        "Por ejemplo `indice_probable_embarazo`, `flag_consumo_cronico`, "
        "`riesgo_salud_estimado`. El punto: la misma línea de código que crea "
        "`dias_desde_ultima_compra` crea `indice_probable_embarazo`. La "
        "diferencia no es técnica, es de criterio, y no hay nada en el lenguaje "
        "de programación que lo señale.",
    )

    c.md("""
### Una advertencia estadística antes de seguir

En el laboratorio anterior miramos correlaciones. Conviene ser preciso:

::: {.callout-warning}
## Tres errores de lectura que hay que evitar

**Correlación baja no significa variable inútil.** Una variable con correlación
lineal cercana a cero puede ser muy predictiva en interacción con otras, o de
forma no lineal. Descartar variables por su correlación marginal es una mala
práctica de modelado, además de una mala justificación de minimización: la
minimización se argumenta por **finalidad**, no por correlación.

**Correlación alta no significa causa.** Que `dias_desde_ultima_compra`
prediga el abandono no significa que esperar cause abandono. El modelo describe
asociación en estos datos, no un mecanismo.

**Cuidado con la fuga de información.** `score_riesgo_interno` y `segmento` se
derivan de un modelo anterior de la propia empresa. Usarlos como predictores
mezcla la salida de un sistema con la entrada de otro, infla artificialmente el
desempeño y hace imposible auditar de dónde salió una decisión. Por eso quedan
**fuera de los dos modelos** de este laboratorio.
:::
""")

    # ------------------------------------------------ EXPERIMENTAR
    c.md("---\n\n# 3 · EXPERIMENTAR\n\n*Dos modelos, una diferencia incómoda*")

    c.code("""
VARIABLES_A = [
    "visitas_web", "productos_vistos", "compras_6m", "monto_compras",
    "dias_desde_ultima_compra", "ticket_promedio", "intensidad_navegacion",
]

VARIABLES_EXTRA_B = [
    "edad",                   # cuasi-identificador
    "estrato",                # proxy socioeconómico
    "ingresos_mensuales",     # proxy socioeconómico
    "compras_farmacia_6m",    # proxy de salud
    "entrega_asistida",       # proxy de discapacidad o edad avanzada
    "busquedas_maternidad",   # proxy de embarazo
]

VARIABLES_B = VARIABLES_A + VARIABLES_EXTRA_B
print(f"Modelo A: {len(VARIABLES_A)} variables (solo comportamiento)")
print(f"Modelo B: {len(VARIABLES_B)} variables (+ demografía y proxies)")
""")

    c.code("""
y = df_apto["churn"]


def entrenar(variables, etiqueta, semilla=42):
    X = df_apto[variables].copy()
    X = X.fillna(X.median(numeric_only=True))
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.30, random_state=semilla, stratify=y)
    modelo = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    modelo.fit(X_tr, y_tr)
    p_te = modelo.predict_proba(X_te)[:, 1]
    return {"etiqueta": etiqueta, "modelo": modelo, "variables": variables,
            "auc": roc_auc_score(y_te, p_te), "X_te": X_te, "y_te": y_te, "p_te": p_te}


modelo_a = entrenar(VARIABLES_A, "Modelo A · solo comportamiento")
modelo_b = entrenar(VARIABLES_B, "Modelo B · + demografía y proxies")

print(f"{modelo_a['etiqueta']:<42} AUC = {modelo_a['auc']:.3f}")
print(f"{modelo_b['etiqueta']:<42} AUC = {modelo_b['auc']:.3f}")
print(f"{'Diferencia':<42}     + {modelo_b['auc'] - modelo_a['auc']:.3f}")
""")

    c.code("""
fig, ax = plt.subplots()
for m, color in [(modelo_a, "#0e7490"), (modelo_b, "#db2777")]:
    fpr, tpr, _ = roc_curve(m["y_te"], m["p_te"])
    ax.plot(fpr, tpr, color=color, lw=2, label=f"{m['etiqueta']}  (AUC {m['auc']:.3f})")
ax.plot([0, 1], [0, 1], color="#94a3b8", lw=1, ls="--", label="Azar")
ax.set_xlabel("Tasa de falsos positivos")
ax.set_ylabel("Tasa de verdaderos positivos")
ax.set_title("Curvas ROC · modelo A vs modelo B", loc="left", fontsize=11)
ax.legend(loc="lower right", frameon=False, fontsize=9)
plt.tight_layout(); plt.show()
""")

    c.md("### ¿Qué variables aportan la diferencia?")

    c.code("""
coefs = pd.Series(
    modelo_b["modelo"].named_steps["logisticregression"].coef_[0],
    index=VARIABLES_B, name="coeficiente").sort_values(key=abs, ascending=False)

tabla = coefs.to_frame().round(3)
tabla["tipo"] = np.where(tabla.index.isin(VARIABLES_EXTRA_B),
                         "demografía / proxy", "comportamiento")
tabla
""")

    c.code("""
fig, ax = plt.subplots(figsize=(7.2, 5))
colores = ["#db2777" if v in VARIABLES_EXTRA_B else "#0e7490" for v in coefs.index]
ax.barh(coefs.index[::-1], coefs.values[::-1], color=colores[::-1])
ax.axvline(0, color="#475569", lw=1)
ax.set_title("Modelo B · peso de cada variable (coeficientes estandarizados)",
             loc="left", fontsize=11)
ax.set_xlabel("← menos probabilidad de abandono    |    más probabilidad de abandono →")
plt.tight_layout(); plt.show()
""")

    c.pregunta(
        "riesgo",
        "**Pregunta 5.** Mire las barras magenta: son las variables que el modelo "
        "A no tiene.\n\nSi alguna está entre las de mayor peso, el modelo B no "
        "está prediciendo mejor *el comportamiento*: está prediciendo mejor *la "
        "condición social o de salud de la persona*, y usándola para decidir "
        "sobre ella.\n\n¿Cuál es la variable de mayor peso del bloque magenta? "
        "¿Se siente cómodo explicándosela a un cliente?",
        "`entrega_asistida` y `estrato` aparecen entre las de mayor peso. "
        "`entrega_asistida` es un proxy de discapacidad o edad avanzada: "
        "explicarle a un cliente que recibió una oferta distinta porque necesita "
        "entrega asistida es exactamente el tipo de conversación que ningún "
        "equipo quiere tener. Nota estadística: los coeficientes son comparables "
        "entre sí porque las variables están estandarizadas, pero siguen siendo "
        "asociaciones condicionales, no efectos causales.",
    )

    c.md("### ¿Sobre quién se equivoca cada modelo? {#por-grupo}")

    c.code("""
UMBRAL = 0.50


def error_por_grupo(m, variable_grupo):
    grupo = df_apto.loc[m["X_te"].index, variable_grupo]
    pred = (m["p_te"] >= UMBRAL).astype(int)
    ev = pd.DataFrame({"grupo": grupo, "real": m["y_te"].values, "pred": pred})
    filas = []
    for nombre, sub in ev.groupby("grupo", dropna=True):
        if len(sub) < 20:       # grupos muy pequeños: no se reporta
            continue
        tn, fp, fn, tp = confusion_matrix(sub["real"], sub["pred"], labels=[0, 1]).ravel()
        filas.append({"grupo": nombre, "n": len(sub),
                      "tasa_churn_real": round(sub["real"].mean(), 3),
                      "marcados_como_riesgo": round(sub["pred"].mean(), 3),
                      "falsos_positivos": round(fp / max(tn + fp, 1), 3),
                      "falsos_negativos": round(fn / max(tp + fn, 1), 3)})
    return pd.DataFrame(filas).set_index("grupo")


print("=== MODELO A · por estrato ===")
print(error_por_grupo(modelo_a, "estrato").to_string())
print()
print("=== MODELO B · por estrato ===")
print(error_por_grupo(modelo_b, "estrato").to_string())
""")

    c.pregunta(
        "riesgo",
        "**Pregunta 6.** Compare la columna `marcados_como_riesgo` entre estratos "
        "en cada modelo.\n\nSi el modelo B marca como «en riesgo» a una "
        "proporción mucho mayor de clientes de estratos bajos, y la acción "
        "asociada es *dar menos beneficios a quien se va a ir de todos modos*, el "
        "modelo acaba de convertirse en un mecanismo de exclusión con apariencia "
        "técnica.\n\n¿Ocurre aquí? Responda con los números de la tabla, no con "
        "la intuición.",
        "Sí ocurre. El modelo B marca cerca del 29 % de los estratos 1 y 2 frente "
        "a menos del 9 % en estratos 5 y 6; el modelo A reparte de forma mucho "
        "más pareja. Matiz honesto: la tasa real de abandono también es más alta "
        "en estratos bajos en estos datos sintéticos, así que parte de la "
        "diferencia es señal, no sesgo. Eso es justamente lo que hace difícil la "
        "discusión, y es el material del Encuentro 3.",
    )

    # ------------------------------------------------ DECIDIR
    c.md("---\n\n# 4 · DECIDIR {#decidir}\n\n*La decisión no está en el modelo*")

    c.code("""
acciones = pd.DataFrame([
    dict(accion="Oferta de retención (descuento)",
         falso_positivo="Descuento a quien no se iba a ir → costo para la empresa",
         falso_negativo="Se pierde un cliente retenible → costo para la empresa",
         dano="La empresa"),
    dict(accion="Menor prioridad en atención al cliente",
         falso_positivo="Peor servicio a quien no se iba a ir → daño a la persona",
         falso_negativo="Servicio normal a quien se va → costo menor",
         dano="La persona"),
    dict(accion="Precio personalizado más alto",
         falso_positivo="Sobreprecio a quien no se iba a ir → daño a la persona",
         falso_negativo="Precio normal → sin daño",
         dano="La persona"),
])
for _, f in acciones.iterrows():
    print(f"\\n▸ {f['accion']}")
    print(f"   FP: {f['falso_positivo']}")
    print(f"   FN: {f['falso_negativo']}")
    print(f"   Daño: lo asume {f['dano'].lower()}")
""")

    c.pregunta(
        "dilema",
        "**Pregunta 7.** El modelo es exactamente el mismo en las tres filas. Lo "
        "que cambia es quién asume el daño del error.\n\nEscriba la decisión "
        "final:\n\n1. ¿Qué modelo se despliega, A o B?\n2. ¿Con qué acción "
        "asociada?\n3. ¿Qué condición tendría que cumplirse para cambiar de "
        "opinión?",
        "Una respuesta defendible: se despliega A con oferta de retención, porque "
        "la ganancia de B (+0,04 de AUC) no compensa usar proxies de salud y "
        "condición socioeconómica sin finalidad documentada ni control sobre el "
        "efecto. Condición para revisar: que exista base documentada, revisión "
        "humana significativa antes de aplicar la acción y monitoreo de error por "
        "grupo. También es defendible desplegar B **si** la acción solo puede "
        "beneficiar a la persona y hay auditoría por grupo. Lo que no es "
        "defendible es desplegar B sin mirar la tabla del bloque anterior.",
    )

    # ------------------------------------------------ JUSTIFICAR
    c.md("---\n\n# 5 · JUSTIFICAR\n\n*La auditoría como artefacto del proyecto*")

    c.md("""
La matriz de auditoría no es un documento de Word que nadie actualiza: se
construye en código y se versiona con el proyecto.
""")

    c.code_var(
        """
# TODO: complete las filas que faltan con SU análisis.

auditoria = pd.DataFrame([
    dict(etapa="Origen", dato="origen_dato, fecha_autorizacion",
         riesgo="236 registros sin evidencia de autorización",
         pregunta="¿De dónde vienen y para qué se recogieron?",
         control="Aislar los registros sin evidencia",
         decision="Excluidos del entrenamiento; conservados aparte"),
    dict(etapa="Datos", dato="identificadores directos",
         riesgo="TODO", pregunta="TODO", control="TODO", decision="TODO"),
    dict(etapa="Modelo", dato="estrato, ingresos, proxies de salud",
         riesgo="TODO", pregunta="TODO", control="TODO", decision="TODO"),
    dict(etapa="Decisión", dato="acción comercial asociada al score",
         riesgo="TODO", pregunta="TODO", control="TODO", decision="TODO"),
    dict(etapa="Publicación", dato="tablero y archivo a terceros",
         riesgo="TODO", pregunta="TODO", control="TODO", decision="TODO"),
])
auditoria
""",
        """
auditoria = pd.DataFrame([
    dict(etapa="Origen", dato="origen_dato, fecha_autorizacion",
         riesgo="236 registros sin evidencia de autorización",
         pregunta="¿De dónde vienen y para qué se recogieron?",
         control="Aislar los registros sin evidencia",
         decision="Excluidos del entrenamiento; conservados aparte"),
    dict(etapa="Datos", dato="nombre, email, telefono, documento, direccion",
         riesgo="Identificadores directos en el archivo de trabajo",
         pregunta="¿Los necesito para esta finalidad?",
         control="Lista blanca de variables; no cargarlos",
         decision="Excluidos; se conserva solo cliente_id"),
    dict(etapa="Finalidad", dato="toda la base",
         riesgo="Uso secundario: publicidad con datos de facturación",
         pregunta="¿Es la misma finalidad de recolección?",
         control="Separar analítica interna de comunicación a terceros",
         decision="Publicidad personalizada requiere autorización específica"),
    dict(etapa="Procesamiento", dato="variables derivadas",
         riesgo="Crear inferencias sobre condiciones sensibles",
         pregunta="¿Qué deduzco que la persona no declaró?",
         control="Lista blanca de variables derivadas permitidas",
         decision="Solo recencia, ticket e intensidad de navegación"),
    dict(etapa="Modelo", dato="estrato, ingresos, proxies de salud",
         riesgo="Perfilamiento con proxies de atributos protegidos",
         pregunta="¿El modelo distingue por condición socioeconómica o de salud?",
         control="Comparar A y B; medir error por grupo",
         decision="Se despliega A; B queda documentado y descartado"),
    dict(etapa="Resultado", dato="probabilidad de abandono",
         riesgo="Score tratado como verdad sobre la persona",
         pregunta="¿Qué error es aceptable y para quién?",
         control="Umbral documentado y matriz de confusión por grupo",
         decision="Umbral fijado con la Dirección, no por el analista"),
    dict(etapa="Decisión", dato="acción comercial asociada al score",
         riesgo="Decisión totalmente automatizada con efecto sobre la persona",
         pregunta="¿Hay intervención humana significativa?",
         control="Revisión humana antes de aplicar la acción",
         decision="La campaña se aprueba por lote, con registro"),
    dict(etapa="Publicación", dato="tablero y archivo entregado a terceros",
         riesgo="Reidentificación por cruce de cuasi-identificadores",
         pregunta="¿Alguien puede ser identificado en lo que publico?",
         control="Agregación y supresión de celdas pequeñas",
         decision="Umbral mínimo de celda definido en la Actividad 4"),
])
auditoria.to_csv("auditoria_pipeline_datamarket.csv", index=False, encoding="utf-8")
auditoria
""",
    )

    c.pregunta(
        "decision",
        "**Pregunta 8.** De las ocho etapas, ¿cuál es la que en su organización "
        "real está peor documentada?\n\nNo la que tiene más riesgo: la que nadie "
        "escribió nunca.",
        "En la mayoría de equipos son *Integración* y *Feature engineering*: el "
        "cruce de bases y la creación de variables derivadas ocurren dentro de "
        "scripts que nadie revisa, y son justamente las dos etapas donde se "
        "fabrican los datos nuevos sobre las personas.",
    )

    # ------------------------------------------------ REFLEXIONAR
    c.md("---\n\n# 6 · REFLEXIONAR\n\n*¿Y en mi trabajo?*")

    c.pregunta(
        "reflexiona",
        "**Pregunta 9 · de salida.**\n\n> **¿Qué tendría que cambiar en mi "
        "proyecto de datos?**\n\nHoy con una restricción: la respuesta debe "
        "nombrar **una etapa del pipeline** y **un cambio ejecutable**. No vale "
        "«ser más cuidadoso».",
        "Se busca la forma «en la etapa X voy a hacer Y y va a quedar la "
        "evidencia Z». Por ejemplo: «en Publicación voy a fijar un umbral mínimo "
        "de celda de 5 en el tablero territorial, y voy a dejar el conteo de "
        "celdas suprimidas en el pie del tablero».",
    )

    c.md("""
---

## Lo que queda del laboratorio

- `auditoria_pipeline_datamarket.csv` — la matriz de las ocho etapas.
- Su decisión sobre qué modelo desplegar, con qué acción y bajo qué condición.

Ninguno de los dos es un documento legal. Los dos son **evidencia de
ingeniería**: si en seis meses alguien pregunta por qué el modelo no usa
estrato, la respuesta existe y tiene fecha.

**Marco legal relacionado:** decisiones automatizadas y perfilamiento — GDPR
art. 22, LGPD art. 20, y el proyecto de reforma colombiano.

**Siguiente paso:** Actividad 1 (tres países) y Actividad 2 (GDPR).
""")

    return c



# ==========================================================================
# LABORATORIO 3 · CAJA DE HERRAMIENTAS DE ANONIMIZACIÓN
# ==========================================================================

ICONOS_PREGUNTA = {
    "decide": "🟡 Decida",
    "riesgo": "🔴 Riesgo",
    "prueba": "🔵 Pruebe",
    "decision": "🟣 Decisión",
    "reflexiona": "🟢 Reflexione",
}


def pregunta_nb(c: Cuaderno, tipo: str, numero: int, texto: str, respuesta: str):
    """Pregunta que se ve bien en Jupyter y en Colab (sin divs de Quarto)."""
    cuerpo = "\n".join("> " + linea if linea else ">" for linea in texto.strip().split("\n"))
    base = (
        f"> ### {ICONOS_PREGUNTA[tipo]} · Pregunta {numero}\n>\n{cuerpo}\n\n"
        "✍️ *Escriba su respuesta en la celda de abajo antes de seguir.*"
    )
    sol = base + (
        "\n\n<details><summary><b>Respuesta orientativa (versión docente)</b></summary>\n\n"
        f"{respuesta.strip()}\n\n</details>"
    )
    c.celdas.append(("md", base, sol))
    c.celdas.append(("md", "**Mi respuesta:** …", "**Mi respuesta:** …"))


def lab03() -> Cuaderno:
    c = Cuaderno(
        "Laboratorio 3 · Caja de herramientas de anonimización",
        "Atacar → Medir → Transformar → Comparar → Decidir → Entregar",
    )
    n = iter(range(1, 50))

    c.md("""
## «Anonimícenla y se la mandamos el viernes»

El proveedor del motor de recomendación pide la base de DataMarket. En este
laboratorio usted va a hacer **lo que casi nadie hace antes de entregar una
base**: atacarla, medirla, transformarla con varias técnicas y decidir con
números.

| | |
|:--|:--|
| **Aprenderá a** | Aplicar ocho técnicas de protección, medir el riesgo y la utilidad que deja cada una, y sostener una decisión de entrega |
| **Duración** | ≈ 45 minutos en clase (ruta 🟢) · el resto se completa en la Actividad 4 |
| **Evidencia** | Bitácora de técnicas, comparación riesgo-pérdida-utilidad, base entregable y dictamen generado |
| **Unidad** | 3 · Técnicas de protección, IA y datos masivos |

### Mapa del laboratorio

| Parte | Qué pasa | Ruta | Tiempo |
|:--|:--|:--:|:--:|
| **0 · Preparar** | Cargar datos y la caja de herramientas | 🟢 | 2 min |
| **1 · Atacar** | Reidentificamos clientes con una sola línea de código | 🟢 | 6 min |
| **2 · Medir** | *k*-anonimato, *l*-diversidad y riesgo 1/*k* | 🟢 | 7 min |
| **3 · Transformar** | Estaciones 1–4 (eliminar, sustituir, generalizar, suprimir) | 🟢 | 15 min |
| | Estaciones 5–8 (colas, ruido, privacidad diferencial, sintéticos) | 🔵 | 25 min |
| **4 · Comparar** | Riesgo, pérdida y utilidad de cinco versiones | 🟢 | 8 min |
| **5 · Decidir y entregar** | Verificación automática + dictamen | 🟢 | 5 min |
| **6 · Reflexionar** | Big Data, IA y una regla para el decálogo | 🔵 | 10 min |

🟢 **En clase** (≈ 45 min) · 🔵 **Profundización** en casa o en la Actividad 4.
Todas las celdas se ejecutan igual: las 🔵 se pueden correr sin detenerse a
responder y volver después.

> 🎛️ Las celdas marcadas con **PERILLA** tienen parámetros para mover. Cámbielos,
> vuelva a ejecutar y mire qué pasa. Ese es el laboratorio.
""")

    # ------------------------------------------------------------ PREPARAR
    c.md("---\n\n# 0 · PREPARAR")
    c.code(CARGA)
    c.code(r"""
import hashlib
import hmac
import secrets
import warnings

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 140)

df = pd.read_csv(RUTA)
# Recencia en días: más útil para el modelo que una fecha.
df["recencia_dias"] = (
    pd.to_datetime(df["fecha_ultima_compra"]).max() - pd.to_datetime(df["fecha_ultima_compra"])
).dt.days

print(f"Registros: {len(df):,}   Variables: {df.shape[1]}")
df.head(3)
""")

    c.md("""
### La caja de herramientas

La celda siguiente define todas las funciones del laboratorio. **No necesita
modificarla**, pero vale la pena leerla: son unas 120 líneas y ninguna es magia.

| Función | Para qué sirve |
|:--|:--|
| `perfil_riesgo()` | *k* mínimo, % de registros con *k*=1 y *k*<5, riesgo medio 1/*k* y *l*-diversidad, para un escenario de atacante |
| `grafico_grupos()` | Cuántos registros quedan en grupos de tamaño 1, 2, 3–4, 5–9 y 10+ |
| `ataque_vinculacion()` | Cruza una fuente pública con la base liberada y cuenta a quién reidentifica |
| `generalizar()` | Generaliza edad, sexo, ciudad, ocupación y estrato con perillas |
| `ncp()` | Pérdida de información: 0 % si el dato es exacto, 100 % si se suprime |
| `utilidad_cv()` | AUC del modelo de abandono en 5 pliegues, comparable entre versiones y sin fugas |
| `dif_tasas()` | Cuánto cambia la tasa de abandono por categoría (puntos porcentuales) |
| `registrar()` | Anota cada paso en la **bitácora** que alimenta el dictamen final |
""")

    c.code(r"""
# ===================== CAJA DE HERRAMIENTAS · no necesita modificarla =====================
from sklearn.metrics import roc_auc_score

COLOR = {"antes": "#94a3b8", "despues": "#0891b2", "alerta": "#dc2626",
         "ok": "#16a34a", "acento": "#7c3aed", "ambar": "#d97706"}
plt.rcParams.update({"figure.figsize": (9, 4), "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold",
                     "axes.titlesize": 12, "font.size": 10})

# Dos escenarios de atacante. Hay que DECLARAR cuál se mide: k depende de él.
CUASI = ["edad", "sexo", "ciudad", "ocupacion"]       # escenario básico
CUASI_AMPLIADO = CUASI + ["estrato"]                   # + estrato (se deduce de la dirección)
SENSIBLE = "categoria_top"                             # lo que no queremos revelar
K_OBJETIVO = 5                                         # umbral de referencia del curso (no es legal)
COLS_MODELO = ["edad", "sexo", "ciudad", "ocupacion", "estrato", "visitas_web", "productos_vistos",
               "compras_6m", "monto_compras", "recencia_dias", "canal_adquisicion", "categoria_top"]


def tam_grupo(datos, cuasi):
    # Tamaño del grupo de equivalencia al que pertenece cada registro.
    return datos.assign(_u=1).groupby(cuasi, dropna=False, observed=True)["_u"].transform("size")


def perfil_riesgo(datos, cuasi=CUASI, sensible=SENSIBLE, k=K_OBJETIVO):
    tam = tam_grupo(datos, cuasi)
    res = {
        "registros": len(datos),
        "combinaciones": int(datos.groupby(cuasi, dropna=False, observed=True).ngroups),
        "k mínimo": int(tam.min()),
        "% k=1": round((tam == 1).mean() * 100, 1),
        f"% k<{k}": round((tam < k).mean() * 100, 1),
        # Riesgo del «fiscal»: el atacante SABE que la persona está en la base y elige al azar en su grupo.
        "riesgo medio 1/k %": round((1 / tam).mean() * 100, 1),
    }
    if sensible is not None and sensible in datos.columns:
        l = datos.groupby(cuasi, dropna=False, observed=True)[sensible].transform("nunique")
        res["l mínimo"] = int(l.min())
        # Grupos con k>=2 donde todos comparten el valor sensible: identidad protegida, atributo expuesto.
        res["% homogéneos (k≥2)"] = round(((l == 1) & (tam >= 2)).mean() * 100, 1)
    return res


def grafico_grupos(versiones, cuasi=CUASI, titulo="¿En qué tamaño de grupo queda cada persona?"):
    cortes = [0, 1, 2, 4, 9, np.inf]
    etiquetas = ["k=1\n(sola)", "k=2", "k=3–4", "k=5–9", "k≥10"]
    fig, ax = plt.subplots()
    ancho = 0.8 / len(versiones)
    paleta = [COLOR["antes"], COLOR["despues"], COLOR["acento"], COLOR["ambar"], COLOR["ok"]]
    for i, (nombre, datos) in enumerate(versiones.items()):
        tam = tam_grupo(datos, cuasi)
        pct = pd.cut(tam, cortes, labels=etiquetas).value_counts(normalize=True).reindex(etiquetas) * 100
        x = np.arange(len(etiquetas)) + i * ancho - 0.4 + ancho / 2
        barras = ax.bar(x, pct.values, ancho, label=nombre, color=paleta[i % len(paleta)])
        ax.bar_label(barras, fmt="%.0f%%", fontsize=8, padding=2)
    ax.axvspan(-0.5, 2.5, color=COLOR["alerta"], alpha=0.06)
    ax.text(1, ax.get_ylim()[1] * 0.92, "zona de riesgo (k<5)", ha="center", color=COLOR["alerta"], fontsize=9)
    ax.set_xticks(range(len(etiquetas)), etiquetas)
    ax.set_ylabel("% de registros")
    ax.set_title(titulo + f"\n(atacante conoce: {', '.join(cuasi)})", fontsize=11)
    ax.legend(frameon=False)
    plt.show()


def ataque_vinculacion(publica, liberada, claves, mostrar=True):
    # publica: nombre + claves (+ _verdad solo para verificar el experimento).
    # liberada: claves + lo que se entregó (+ _verdad, que el atacante NO ve).
    publica = publica.reset_index(drop=True).rename_axis("_pid").reset_index()
    cruce = publica.merge(liberada, on=claves, how="inner", suffixes=("_pub", "_lib"))
    candidatos = cruce.groupby("_pid")["_verdad_lib"].transform("size")
    unicos = cruce[candidatos == 1]
    aciertos = unicos[unicos["_verdad_pub"] == unicos["_verdad_lib"]]
    tam = publica.merge(liberada.groupby(claves, dropna=False).size().rename("k").reset_index(),
                        on=claves, how="left")["k"]
    prob = (1 / tam).fillna(0).mean() * 100   # quien fue suprimido no puede ser acertado: aporta 0
    res = {"personas en la fuente pública": len(publica),
           "reidentificadas con certeza (k=1)": len(aciertos),
           "% reidentificadas": round(len(aciertos) / len(publica) * 100, 1),
           "acierto esperado adivinando 1/k %": round(prob, 1)}
    if mostrar:
        print("ATAQUE DE VINCULACIÓN · claves:", ", ".join(claves))
        for k_, v_ in res.items():
            print(f"  {k_:<36}: {v_}")
    return res, aciertos


REGIONES = {
    "Bogota": "Centro", "Ibague": "Centro", "Villavicencio": "Centro",
    "Medellin": "Antioquia-Eje", "Pereira": "Antioquia-Eje", "Manizales": "Antioquia-Eje",
    "Cali": "Pacífico", "Pasto": "Pacífico",
    "Barranquilla": "Caribe", "Cartagena": "Caribe", "Santa Marta": "Caribe",
    "Bucaramanga": "Nororiente",
}
GRUPOS_OCUPACION = {
    "Ingeniero/a": "técnico-profesional", "Tecnico/a": "técnico-profesional",
    "Disenador/a": "técnico-profesional", "Contador/a": "técnico-profesional",
    "Abogado/a": "técnico-profesional", "Administrador/a": "técnico-profesional",
    "Docente": "servicios", "Enfermero/a": "servicios",
    "Comerciante": "servicios", "Independiente": "servicios",
    "Estudiante": "sin actividad remunerada", "Pensionado/a": "sin actividad remunerada",
}
NIVELES_ESTRATO = {1: "bajo (1-2)", 2: "bajo (1-2)", 3: "medio (3-4)", 4: "medio (3-4)", 5: "alto (5-6)", 6: "alto (5-6)"}


def generalizar(datos, edad=10, sexo="agrupar", ciudad="region", ocupacion="grupo", estrato="exacto"):
    # edad: 0 (exacta), 5, 10 o 20 años  ·  sexo: "conservar" | "agrupar" | "suprimir"
    # ciudad: "ciudad" | "region" | "suprimir"  ·  ocupacion: "exacta" | "grupo" | "suprimir"
    # estrato: "exacto" | "nivel" (bajo/medio/alto) | "suprimir"
    d = datos.copy()
    if edad:
        ini = (d["edad"] // edad * edad).astype(int)
        d["edad"] = ini.astype(str) + "–" + (ini + edad - 1).astype(str)
    if sexo == "agrupar":
        d["sexo"] = d["sexo"].replace({"Otro": "Otro/NR", "Prefiere no responder": "Otro/NR"})
    elif sexo == "suprimir":
        d["sexo"] = "*"
    if ciudad == "region":
        d["ciudad"] = d["ciudad"].map(REGIONES)
    elif ciudad == "suprimir":
        d["ciudad"] = "*"
    if ocupacion == "grupo":
        d["ocupacion"] = d["ocupacion"].map(GRUPOS_OCUPACION)
    elif ocupacion == "suprimir":
        d["ocupacion"] = "*"
    if "estrato" in d.columns:
        if estrato == "nivel":
            d["estrato"] = d["estrato"].map(NIVELES_ESTRATO).fillna("sin dato")
        elif estrato == "suprimir":
            d["estrato"] = "*"
    return d


def ncp(version, original=None, cuasi=CUASI_AMPLIADO):
    # Pérdida de información (NCP, 0–100 %). Para cada registro y cuasi-identificador:
    #   (valores originales que caben en su clase − 1) / (valores posibles − 1)
    # 0 = dato exacto · 100 = dato suprimido. Un registro eliminado cuenta como 100.
    original = df if original is None else original
    perdidas = []
    for c in cuasi:
        o = original[c].astype(str)
        dominio = o.nunique()
        v = version[c].reindex(original.index).astype(str)
        clase = o.groupby(v).transform("nunique")
        p = (clase - 1) / (dominio - 1)
        p[~original.index.isin(version.index)] = 1.0
        perdidas.append(p)
    return round(float(pd.concat(perdidas, axis=1).mean().mean() * 100), 1)


def dif_tasas(version, var="categoria_top"):
    # Mayor diferencia (puntos porcentuales) en la tasa de abandono por categoría, versión vs. original.
    orig = df.groupby(var)["churn"].mean()
    nueva = version.groupby(var)["churn"].mean().reindex(orig.index)
    return round(float((nueva - orig).abs().max() * 100), 1)


def _matriz(d, columnas, ref=None):
    X = pd.get_dummies(d[columnas], dtype=float)
    return X if ref is None else X.reindex(columns=ref, fill_value=0)


def utilidad_cv(transformar=None, suprimir_en=None, sintetico=None, semilla=42):
    # AUC del modelo de abandono, comparable entre versiones y SIN fugas:
    #  · los mismos 5 pliegues para todas las versiones (comparación pareada);
    #  · la transformación, la supresión o el generador se ajustan SOLO con el entrenamiento;
    #  · se evalúa siempre en personas reales que no se usaron, transformadas con la misma regla.
    cv = StratifiedKFold(5, shuffle=True, random_state=semilla)
    aucs = []
    for i_tr, i_te in cv.split(df, df["churn"]):
        tr, te = df.iloc[i_tr], df.iloc[i_te]
        if sintetico is not None:
            tr_t, te_t = sintetico(tr), te
        else:
            tr_t = transformar(tr) if transformar else tr
            if suprimir_en:
                tr_t = tr_t[tam_grupo(tr_t, suprimir_en) >= K_OBJETIVO]
            te_t = transformar(te) if transformar else te
        if len(tr_t) < 50 or tr_t["churn"].nunique() < 2:
            aucs.append(np.nan)   # la supresión dejó muy pocos registros para entrenar
            continue
        Xtr = _matriz(tr_t, COLS_MODELO)
        mediana = Xtr.median()
        Xtr = Xtr.fillna(mediana)
        Xte = _matriz(te_t, COLS_MODELO, Xtr.columns).fillna(mediana)
        modelo = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=0.5))
        modelo.fit(Xtr, tr_t["churn"])
        aucs.append(roc_auc_score(te["churn"], modelo.predict_proba(Xte)[:, 1]))
    aucs = np.array(aucs)
    if np.isnan(aucs).any():
        print("⚠️  Con esta versión la supresión deja demasiados pocos registros para entrenar: AUC no disponible.")
    return aucs


BITACORA = []


def registrar(paso, datos, tecnica, nota=""):
    b = perfil_riesgo(datos, CUASI)
    a = perfil_riesgo(datos, CUASI_AMPLIADO) if "estrato" in datos.columns else {}
    fila = {"paso": paso, "técnica": tecnica, "registros": b["registros"],
            "k mín. (básico)": b["k mínimo"], "% k<5 (básico)": b["% k<5"],
            "% k<5 (+estrato)": a.get("% k<5", np.nan), "riesgo 1/k % (+estrato)": a.get("riesgo medio 1/k %", np.nan),
            "% homogéneos": b["% homogéneos (k≥2)"], "NCP %": ncp(datos), "nota": nota}
    BITACORA[:] = [x for x in BITACORA if x["paso"] != paso] + [fila]
    return pd.DataFrame(BITACORA).set_index("paso")


print("Caja de herramientas lista ✔")
""")

    # ------------------------------------------------------------ ATACAR
    c.md("""
---

# 1 · ATACAR

*Antes de proteger una base, intente romperla.*

### La versión «anonimizada» que casi todo el mundo entrega

Borramos nombre, correo, teléfono, documento y dirección. Es lo que se suele
llamar «anonimizar».
""")

    c.code(r"""
IDENTIFICADORES_DIRECTOS = ["nombre", "email", "telefono", "documento", "direccion"]

base_ingenua = df.drop(columns=IDENTIFICADORES_DIRECTOS).copy()
base_ingenua["_verdad"] = df["cliente_id"]   # solo para verificar el experimento

print(f"Quedan {base_ingenua.shape[1] - 1} variables. Ningún nombre a la vista.")
base_ingenua[CUASI + ["compras_farmacia_6m", "busquedas_maternidad", "categoria_top"]].head()
""")

    c.md("""
### El atacante

Alguien tiene una **fuente pública**: perfiles profesionales, una lista de
egresados, una publicación en redes. En ella aparecen 300 clientes con su
nombre, edad, sexo, ciudad y ocupación. Nada secreto. También anotó el
**estrato**, que se deduce de una dirección: lo usaremos más adelante.
""")

    c.code(r"""
rng = np.random.default_rng(2026)
muestra = rng.choice(len(df), size=300, replace=False)

fuente_publica = df.iloc[muestra][["nombre"] + CUASI + ["estrato"]].copy()
fuente_publica["_verdad"] = df.iloc[muestra]["cliente_id"].values   # el atacante no lo ve

fuente_publica.drop(columns="_verdad").head()
""")

    c.code(r"""
# El ataque completo es esta línea:
cruce = fuente_publica.merge(base_ingenua, on=CUASI)

res_ingenua, reidentificados = ataque_vinculacion(fuente_publica, base_ingenua, CUASI)

print("\nLo que ahora sabemos de cinco personas con nombre propio:")
reidentificados[["nombre", "edad", "ciudad", "categoria_top",
                 "compras_farmacia_6m", "busquedas_maternidad", "entrega_asistida"]].head()
""")

    pregunta_nb(
        c, "riesgo", next(n),
        "Con una sola línea de `merge`, ¿qué porcentaje de las 300 personas "
        "quedó reidentificado **con certeza**?\n\n"
        "Mire las columnas de la derecha: `busquedas_maternidad`, "
        "`compras_farmacia_6m`, `entrega_asistida`. ¿Qué podría inferir alguien "
        "sobre esas personas? ¿Seguiría llamando «anonimizada» a esta base?",
        "Cerca del 80 % de la fuente pública queda reidentificada con certeza "
        "(el número exacto aparece en la salida). Las columnas de la derecha "
        "permiten inferir embarazo, una condición de salud o una discapacidad: "
        "datos sensibles que nadie recogió como tales. La base **no** está "
        "anonimizada; solo está **desnominalizada**. Es el mismo mecanismo de "
        "los casos de Sweeney (1997), AOL (2006) y Netflix (2008).",
    )

    # ------------------------------------------------------------ MEDIR
    c.md("""
---

# 2 · MEDIR

*Anonimizar es un resultado que se mide, no una operación que se aplica.*

### Tres ideas en una tabla de ocho filas

Antes de mirar 1 512 registros, mire ocho. Los **cuasi-identificadores** son
edad y ciudad; el **atributo sensible** es la categoría que más compra.
""")

    c.code(r"""
juguete = pd.DataFrame({
    "edad":      ["30–39", "30–39", "30–39", "40–49", "40–49", "40–49", "50–59", "50–59"],
    "ciudad":    ["Caribe", "Caribe", "Caribe", "Centro", "Centro", "Centro", "Centro", "Pacífico"],
    "categoria": ["salud", "moda", "hogar", "maternidad", "maternidad", "maternidad", "libros", "salud"],
})
juguete["k (tamaño del grupo)"] = tam_grupo(juguete, ["edad", "ciudad"])
juguete["l (valores sensibles distintos)"] = (
    juguete.groupby(["edad", "ciudad"])["categoria"].transform("nunique"))
juguete
""")

    c.md("""
| Concepto | Pregunta que responde | En la tabla |
|:--|:--|:--|
| ***k*-anonimato** | ¿Con cuántas personas me confundo? | Las dos últimas filas tienen *k* = 1: están solas |
| ***l*-diversidad** | Aunque me confunda, ¿se sabe mi dato sensible? | El grupo 40–49 · Centro tiene *k* = 3 pero *l* = 1: las tres compran maternidad |
| **Riesgo 1/*k*** | Si el atacante busca a alguien y elige al azar dentro de su grupo, ¿cuánto acierta? | Un tercio en el grupo de tres; certeza en los de uno |

### Lo que estas métricas dicen y lo que no dicen

- **1/*k* es una probabilidad condicional, no universal.** Supone que el atacante
  **sabe que la persona está en la base** (el «modelo del fiscal») y que elige al
  azar dentro del grupo. Si no sabe si está, el riesgo es menor; si tiene
  información adicional, mayor.
- ***k* depende del escenario.** *k* se calcula para un conjunto declarado de
  cuasi-identificadores. Si el atacante conoce una variable más que viaja en la
  base, el *k* real puede ser mucho menor. Por eso este laboratorio mide **dos
  escenarios**.
- **Cumplir *k* ≥ 5 no es una garantía de anonimización.** No protege el
  atributo (homogeneidad), ni de la vinculación por otras columnas, ni de
  cruces futuros. Es un umbral de trabajo que hay que **declarar y justificar**.
- **La *l*-diversidad cuenta valores distintos, no su peso.** Un grupo con nueve
  «maternidad» y una «moda» tiene *l* = 2, pero revela el atributo con 90 % de
  confianza. Existen variantes (entrópica, *t*-cercanía) que miden la
  concentración; aquí basta con saber que *l* > 1 no es suficiente por sí sola.
""")

    c.code(r"""
linea_base = registrar("0 · sin identificadores directos", base_ingenua,
                       "supresión de 5 columnas",
                       nota="lo que casi todos entregan")
linea_base
""")

    c.code(r"""
grafico_grupos({"sin identificadores directos": base_ingenua},
               titulo="Línea base: la mayoría de las personas está sola en su grupo")
""")

    pregunta_nb(
        c, "decide", next(n),
        "La línea base da un *k* mínimo de 1 y un porcentaje alto en *k* = 1. "
        "Ahora mire la última columna: `% homogéneos (k≥2)`.\n\n"
        "Explique con sus palabras por qué una persona puede estar **protegida "
        "en su identidad** y **expuesta en su atributo sensible** al mismo tiempo.",
        "Si todos los miembros de un grupo comparten el valor sensible, el "
        "atacante no necesita saber cuál de ellos es la persona: le basta con "
        "saber que está en el grupo. Es el **ataque de homogeneidad**. Por eso "
        "*k*-anonimato no basta y se mide también *l*-diversidad.",
    )

    # ------------------------------------------------------------ TRANSFORMAR
    c.md("""
---

# 3 · TRANSFORMAR

*Ocho estaciones. En cada una: qué hace la técnica, qué protege, qué cuesta.*

| # | Estación | Familia |
|:--:|:--|:--|
| 1 | Supresión de identificadores indirectos | Eliminar |
| 2 | Seudonimización: *hash* ingenuo frente a HMAC con clave | Sustituir |
| 3 | Generalización con perillas | Reducir detalle |
| 4 | Supresión local de grupos pequeños | Eliminar |
| 5 | *Top/bottom coding* y microagregación | Reducir detalle |
| 6 | Perturbación: ruido y coordenadas | Alterar |
| 7 | Privacidad diferencial para tablas agregadas | Alterar con garantía |
| 8 | Datos sintéticos | Reemplazar |
""")

    # --- Estación 1
    c.md("""
## 🟢 🧰 Estación 1 · Supresión de identificadores indirectos

`ip`, `latitud`, `longitud` y `dispositivo` no tienen nombre, pero apuntan a
una persona o a una casa. Y el motor de recomendación no los necesita.
""")
    c.code(r"""
INDIRECTOS = ["ip", "latitud", "longitud", "dispositivo", "barrio", "fecha_nacimiento"]
# fecha_nacimiento es otra forma de la edad; barrio es ubicación fina.

e1 = base_ingenua.drop(columns=INDIRECTOS)
print("Columnas suprimidas:", ", ".join(INDIRECTOS))
print(f"Variables que quedan: {e1.shape[1] - 1}")

# ¿Qué habría pasado si el atacante también conociera el barrio?
for cols in [CUASI, CUASI + ["barrio"], CUASI + ["barrio", "estrato"]]:
    p = perfil_riesgo(df, cols, sensible=None)
    print(f"{' + '.join(cols):<52} -> {p['% k=1']:>5} % de personas solas")
""")

    pregunta_nb(
        c, "decide", next(n),
        "Suprimir estas columnas **no cambia** el riesgo medido con los cuatro "
        "cuasi-identificadores. Entonces, ¿para qué sirvió?",
        "Cierra otras puertas de ataque que la métrica con cuatro variables no "
        "ve: la IP y las coordenadas permiten vincular con registros de "
        "navegación o con un mapa; sumar `barrio` dispara la proporción de "
        "personas solas (vea la salida). La métrica mide un escenario de ataque, no todos. Por eso hay "
        "que **declarar el escenario** (qué sabe el atacante) en el informe.",
    )

    # --- Estación 2
    c.md("""
## 🟢 🧰 Estación 2 · Seudonimización: el *hash* no es un escudo

El proveedor necesita una clave para unir compras del mismo cliente. Tentación:
reemplazar el documento por su *hash* SHA-256. Veamos qué pasa si alguien
tiene **otra base con documentos** (una filtración, una base comprada).
""")
    c.code(r"""
def hash_ingenuo(valor):
    return hashlib.sha256(str(valor).encode("utf-8")).hexdigest()[:16]

# Lo que se entrega
entrega_hash = pd.DataFrame({"id_hash": df["documento"].map(hash_ingenuo),
                             "categoria_top": df["categoria_top"]})

# Lo que tiene el atacante: 400 documentos con nombre, de otra fuente
otra_base = df.sample(400, random_state=7)[["documento", "nombre"]]
otra_base["id_hash"] = otra_base["documento"].map(hash_ingenuo)   # ¡el algoritmo es público!

revertidos = otra_base.merge(entrega_hash, on="id_hash").drop_duplicates("documento")
print(f"Hash ingenuo: {len(revertidos)} de 400 personas reidentificadas")
revertidos[["nombre", "documento", "id_hash", "categoria_top"]].head(4)
""")
    c.code(r"""
# HMAC: hash con una CLAVE SECRETA que nunca sale de DataMarket.
CLAVE_SECRETA = secrets.token_bytes(32)   # en producción: gestor de secretos, rotación, acceso por rol

def seudonimo_hmac(valor, clave=CLAVE_SECRETA):
    return hmac.new(clave, str(valor).encode("utf-8"), hashlib.sha256).hexdigest()[:16]

entrega_hmac = pd.DataFrame({"id_seudo": df["documento"].map(seudonimo_hmac),
                             "categoria_top": df["categoria_top"]})
otra_base["id_seudo"] = otra_base["documento"].map(hash_ingenuo)  # el atacante no tiene la clave
print("HMAC sin la clave:", otra_base.merge(entrega_hmac, on="id_seudo")["documento"].nunique(),
      "de 400 personas reidentificadas")

# ¿Y si la clave se filtra? El HMAC es tan fuerte como la custodia de la clave.
otra_base["id_filtrado"] = otra_base["documento"].map(seudonimo_hmac)
print("HMAC con la clave filtrada:", otra_base.merge(entrega_hmac, left_on="id_filtrado",
      right_on="id_seudo")["documento"].nunique(), "de 400 personas reidentificadas")
""")
    pregunta_nb(
        c, "riesgo", next(n),
        "Con HMAC el cruce dio cero. ¿Significa que la base seudonimizada ya es "
        "**anónima**?\n\nPiense en dos cosas: quién tiene la clave y qué pasa "
        "con los cuasi-identificadores de la parte 1.",
        "No. Primero, DataMarket conserva la clave y la tabla de equivalencias: "
        "puede revertir el seudónimo, así que los datos siguen siendo personales "
        "(el GDPR lo dice expresamente en el considerando 26). Segundo, el "
        "seudónimo solo protege la columna del identificador: el ataque de "
        "vinculación por edad, sexo, ciudad y ocupación sigue funcionando igual. "
        "Tercero, el seudónimo es **determinista**: la misma persona tiene el "
        "mismo código en todas las entregas, así que dos entregas se pueden "
        "unir entre sí (vinculabilidad). "
        "En 2014 se publicaron 173 millones de viajes de taxi de Nueva York con "
        "las placas «protegidas» con MD5 sin clave; se revirtieron en horas.",
    )

    # --- Estación 3
    c.md("""
## 🟢 🧰 Estación 3 · Generalización con perillas 🎛️

Reducir el detalle de los cuasi-identificadores: edad exacta → rango; ciudad →
región; ocupación → grupo. **Mueva las perillas** y vuelva a ejecutar. Busque
la combinación más útil que deje menos del 5 % de los registros con *k* < 5.
""")
    c.code_var(
        r"""
# ===================== PERILLA =====================
NIVEL_EDAD     = 5           # 0 = exacta · 5 · 10 · 20 años
SEXO_COMO      = "conservar" # "conservar" · "agrupar" · "suprimir"
CIUDAD_COMO    = "ciudad"    # "ciudad" · "region" · "suprimir"
OCUPACION_COMO = "grupo"     # "exacta" · "grupo" · "suprimir"
ESTRATO_COMO   = "exacto"    # "exacto" · "nivel" (bajo/medio/alto) · "suprimir"
# ===================================================
# TODO: pruebe al menos tres combinaciones y anote cuál eligió y por qué.

e3 = generalizar(e1, NIVEL_EDAD, SEXO_COMO, CIUDAD_COMO, OCUPACION_COMO, ESTRATO_COMO)
registrar("3 · generalización (mía)", e3, "generalización",
          nota=f"edad {NIVEL_EDAD} · sexo {SEXO_COMO} · {CIUDAD_COMO} · ocupación {OCUPACION_COMO} · estrato {ESTRATO_COMO}")
""",
        r"""
# ===================== PERILLA =====================
NIVEL_EDAD     = 10          # 0 = exacta · 5 · 10 · 20 años
SEXO_COMO      = "agrupar"   # "conservar" · "agrupar" · "suprimir"
CIUDAD_COMO    = "region"    # "ciudad" · "region" · "suprimir"
OCUPACION_COMO = "suprimir"  # "exacta" · "grupo" · "suprimir"
ESTRATO_COMO   = "nivel"     # "exacto" · "nivel" (bajo/medio/alto) · "suprimir"
# ===================================================

e3 = generalizar(e1, NIVEL_EDAD, SEXO_COMO, CIUDAD_COMO, OCUPACION_COMO, ESTRATO_COMO)
registrar("3 · generalización (mía)", e3, "generalización",
          nota=f"edad {NIVEL_EDAD} · sexo {SEXO_COMO} · {CIUDAD_COMO} · ocupación {OCUPACION_COMO} · estrato {ESTRATO_COMO}")
""",
    )
    c.md("""
**Cómo leer la bitácora.** Hay dos columnas de riesgo porque hay dos
escenarios: el **básico** (el atacante conoce edad, sexo, ciudad y ocupación) y
el **ampliado** (además conoce el estrato, que se deduce de una dirección).
`NCP %` es la **pérdida de información**: 0 si el dato se entrega exacto, 100 si
se suprime. Una versión es mejor que otra solo si tiene **menos riesgo y menos
pérdida a la vez**.
""")
    c.code(r"""
grafico_grupos({"sin identificadores": base_ingenua, "generalizada": e3}, cuasi=CUASI_AMPLIADO,
               titulo="Antes y después de generalizar")
""")
    c.md("""
### Todas las combinaciones de una vez

En lugar de probar a mano, recorramos las **324 combinaciones** de perillas y
midamos cada una en el escenario ampliado. Cada punto es una versión posible de
la base. Los puntos unidos por la línea forman la **frontera de Pareto**: las
versiones que ninguna otra supera en riesgo **y** pérdida al mismo tiempo. Las
demás son decisiones dominadas: hay otra mejor en los dos ejes.
""")
    c.code(r"""
import itertools

filas = []
for ed, sx, ci, oc, es in itertools.product([0, 5, 10, 20], ["conservar", "agrupar", "suprimir"],
                                            ["ciudad", "region", "suprimir"], ["exacta", "grupo", "suprimir"],
                                            ["exacto", "nivel", "suprimir"]):
    g = generalizar(e1, ed, sx, ci, oc, es)
    filas.append({"edad": ed, "sexo": sx, "ciudad": ci, "ocupacion": oc, "estrato": es,
                  "% k<5": perfil_riesgo(g, CUASI_AMPLIADO, sensible=None)["% k<5"], "NCP %": ncp(g)})
mapa = pd.DataFrame(filas)

# Frontera de Pareto: nadie tiene a la vez menos riesgo y menos pérdida.
orden = mapa.sort_values(["NCP %", "% k<5"])
mapa["pareto"] = False
mejor = np.inf
for i, fila in orden.iterrows():
    if fila["% k<5"] < mejor:
        mapa.loc[i, "pareto"] = True
        mejor = fila["% k<5"]

fig, ax = plt.subplots(figsize=(9, 4.8))
ok = mapa["% k<5"] < 5
ax.scatter(mapa.loc[~ok, "NCP %"], mapa.loc[~ok, "% k<5"], color=COLOR["antes"], alpha=.5, s=18, label="no cumple (≥5 % en k<5)")
ax.scatter(mapa.loc[ok, "NCP %"], mapa.loc[ok, "% k<5"], color=COLOR["ok"], s=30, label="cumple (<5 % en k<5)")
fr = mapa[mapa["pareto"]].sort_values("NCP %")
ax.plot(fr["NCP %"], fr["% k<5"], "-", color=COLOR["acento"], lw=1.5, label="frontera de Pareto")
mia = mapa[(mapa.edad == NIVEL_EDAD) & (mapa.sexo == SEXO_COMO) & (mapa.ciudad == CIUDAD_COMO)
           & (mapa.ocupacion == OCUPACION_COMO) & (mapa.estrato == ESTRATO_COMO)]
ax.scatter(mia["NCP %"], mia["% k<5"], color=COLOR["acento"], s=220, marker="*", label="su elección", zorder=5)
ax.axhline(5, color=COLOR["alerta"], ls="--", lw=1)
ax.set_xlabel("Pérdida de información, NCP %  (← conserva más detalle)")
ax.set_ylabel("% registros con k<5  (↓ menos riesgo)")
ax.set_title("324 versiones posibles · escenario ampliado (con estrato)")
ax.legend(frameon=False, fontsize=8.5)
plt.show()

print("Las cinco versiones que cumplen con MENOS pérdida de información:")
mapa[ok].sort_values("NCP %").head(5)
""")
    c.md("""
#### 🎮 Panel interactivo (Colab o Jupyter)

Si está en Colab o Jupyter con `ipywidgets`, la celda siguiente crea un panel
con menús. Si no, muestra una tabla fija. Funciona igual en los dos casos.
""")
    c.code(r"""
def panel(edad=10, sexo="agrupar", ciudad="region", ocupacion="grupo", estrato="nivel"):
    g = generalizar(e1, edad, sexo, ciudad, ocupacion, estrato)
    b, a = perfil_riesgo(g, CUASI), perfil_riesgo(g, CUASI_AMPLIADO)
    semaforo = "🟢" if a["% k<5"] < 5 else ("🟡" if a["% k<5"] < 20 else "🔴")
    print(f"{semaforo}  k<5: {b['% k<5']} % (básico) · {a['% k<5']} % (+estrato)  ·  "
          f"homogéneos {a['% homogéneos (k≥2)']} %  ·  pérdida NCP {ncp(g)} %")

try:
    from ipywidgets import interact
    interact(panel, edad=[0, 5, 10, 20], sexo=["conservar", "agrupar", "suprimir"],
             ciudad=["ciudad", "region", "suprimir"], ocupacion=["exacta", "grupo", "suprimir"],
             estrato=["exacto", "nivel", "suprimir"])
except ImportError:
    for ed in [0, 5, 10, 20]:
        print(f"edad={ed:>2}", end="  ")
        panel(ed)
""")
    pregunta_nb(
        c, "decide", next(n),
        "Mire la frontera de Pareto. ¿Qué perillas aparecen en casi todas las "
        "versiones de la frontera? Si el proveedor necesita recomendar **por "
        "ciudad**, ¿qué tendría que sacrificar a cambio?",
        "En la frontera dominan la edad en rangos amplios y el estrato en "
        "niveles o suprimido: son las variables que más separan a las personas. "
        "Conservar la ciudad obliga a compensar con más generalización en edad, "
        "ocupación o estrato. La lección: **la finalidad decide qué variable se "
        "sacrifica**, y la frontera muestra el precio de cada elección. Elegir un "
        "punto fuera de la frontera es pagar pérdida o riesgo sin necesidad.",
    )

    # --- Estación 4
    c.md("""
## 🟢 🧰 Estación 4 · Supresión local: quitar a los que quedan solos

Después de generalizar suele quedar un puñado de personas en grupos pequeños.
Una salida es **suprimir esos registros**. Parece gratis. No lo es.

*La supresión se calcula en el escenario ampliado (con estrato): es el más
exigente de los dos que declaramos.*
""")
    c.code(r"""
tam = tam_grupo(e3, CUASI_AMPLIADO)
e4 = e3[tam >= K_OBJETIVO].copy()
suprimidos = e3[tam < K_OBJETIVO]

print(f"Registros suprimidos: {len(suprimidos)} ({len(suprimidos)/len(e3)*100:.1f} %)")
registrar("4 · + supresión local k<5", e4, "supresión de registros",
          nota=f"{len(suprimidos)} registros fuera")
""")
    c.code(r"""
# ¿Los suprimidos son una muestra al azar? Se comparan con sus datos ORIGINALES.
def rasgos(idx):
    o = df.loc[idx]
    return [o["churn"].mean(), o["sexo"].isin(["Otro", "Prefiere no responder"]).mean(),
            (o["pais_residencia"] != "Colombia").mean(), (o["edad"] >= 60).mean(),
            o["estrato"].isin([5, 6]).mean()]

comparacion = pd.DataFrame(
    {"se quedan": rasgos(e4.index), "se suprimen": rasgos(suprimidos.index)},
    index=["tasa de abandono", "sexo: otro / no responde", "residente fuera de Colombia",
           "60 años o más", "estratos 5 y 6"]) * 100
comparacion["diferencia (pp)"] = comparacion["se suprimen"] - comparacion["se quedan"]
print(f"La tasa de abandono por categoría cambia hasta {dif_tasas(e4)} puntos porcentuales "
      "respecto a la base completa.")
comparacion.round(1)
""")
    pregunta_nb(
        c, "riesgo", next(n),
        "¿A quién se lleva la supresión? Mire la columna `diferencia (pp)`. Si "
        "el proveedor entrena con la base sin esas personas, ¿para quién va a "
        "funcionar peor el recomendador? ¿Y qué le pasa a una estadística "
        "como la tasa de abandono?",
        "La supresión se lleva sobre todo a las minorías de la base: personas "
        "que no se identifican como F o M, mayores, residentes fuera del país, "
        "estratos poco frecuentes. Proteger su identidad borrándolas las vuelve "
        "**invisibles** para el modelo: es un sesgo de representación fabricado "
        "por la anonimización (enlace directo con el Encuentro 3). Además cambia "
        "las tasas que se calculen después. Alternativas: suprimir celdas "
        "(reemplazar por `*`) en lugar de filas, o generalizar más solo para "
        "esos grupos. Y siempre **reportar cuántos y quiénes** se suprimieron.",
    )

    # --- Estación 5
    c.md("""
## 🔵 🧰 Estación 5 · *Top coding* y microagregación

Los ingresos tienen una cola larga: una persona que gana 22 millones es casi
única aunque todo lo demás esté generalizado.

- ***Top/bottom coding***: todo lo que pase del percentil 95 se registra como el percentil 95.
- **Microagregación**: se ordena, se forman grupos de *k* personas y se reemplaza el valor por el promedio del grupo.
""")
    c.code(r"""
def top_bottom(s, inf=0.05, sup=0.95):
    return s.clip(s.quantile(inf), s.quantile(sup))

def microagregar(s, k=K_OBJETIVO):
    s = s.copy()
    validos = s.dropna().sort_values()
    grupo = np.arange(len(validos)) // k
    grupo[grupo == grupo.max()] = max(grupo.max() - 1, 0) if (grupo == grupo.max()).sum() < k else grupo.max()
    s.loc[validos.index] = validos.groupby(grupo).transform("mean").values
    return s

ingresos = e4["ingresos_mensuales"]
versiones_ing = pd.DataFrame({
    "original": ingresos,
    "top/bottom 5 %": top_bottom(ingresos),
    "microagregado k=5": microagregar(ingresos),
})

resumen = versiones_ing.agg(["mean", "median", "std", "max", "nunique"]).T
resumen.columns = ["media", "mediana", "desv. est.", "máximo", "valores distintos"]
resumen.style.format("{:,.0f}")
""")
    c.code(r"""
fig, ax = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
for a, (nombre, serie), col in zip(ax, versiones_ing.items(), [COLOR["antes"], COLOR["despues"], COLOR["acento"]]):
    a.hist(serie.dropna() / 1e6, bins=40, color=col)
    a.set_title(nombre)
    a.set_xlabel("millones de pesos")
plt.suptitle("Misma variable, tres niveles de protección", fontweight="bold")
plt.tight_layout()
plt.show()
""")
    pregunta_nb(
        c, "decide", next(n),
        "La microagregación conserva la media **exactamente**. ¿Qué no "
        "conserva? Y si el proveedor quisiera estudiar a los clientes de "
        "ingresos más altos, ¿cuál de las dos técnicas le haría más daño?",
        "Conserva la media pero reduce la varianza y la cantidad de valores "
        "distintos, y debilita correlaciones con otras variables. El *top "
        "coding* destruye la cola superior: si el interés está justamente en "
        "los clientes de mayores ingresos, es la técnica que más daño hace.",
    )

    # --- Estación 6
    c.md("""
## 🔵 🧰 Estación 6 · Perturbación: ruido y coordenadas

Alterar valores de forma controlada. Útil para variables continuas que el
proveedor necesita en escala numérica.
""")
    c.code(r"""
# ===================== PERILLA =====================
RUIDO_MONTO = 0.10      # DESVIACIÓN ESTÁNDAR relativa del ruido: 0.10 no significa «máximo ±10 %»
DECIMALES_COORD = 2     # 4 ≈ 11 m · 3 ≈ 110 m · 2 ≈ 1,1 km · 1 ≈ 11 km
# ===================================================
rng = np.random.default_rng(11)
monto_ruido = df["monto_compras"] * (1 + rng.normal(0, RUIDO_MONTO, len(df)))

cambio = (monto_ruido / df["monto_compras"] - 1).abs()
print(f"Registros con cambio mayor a ±{RUIDO_MONTO:.0%}: {(cambio > RUIDO_MONTO).mean():.0%}  ·  "
      f"mayor a ±{2*RUIDO_MONTO:.0%}: {(cambio > 2*RUIDO_MONTO).mean():.0%}  (normal: ≈32 % y ≈5 %)")
print(f"Media del monto   original: {df['monto_compras'].mean():>12,.0f}   con ruido: {monto_ruido.mean():>12,.0f}")
print(f"Desv. est. del monto original: {df['monto_compras'].std():>12,.0f}   con ruido: {monto_ruido.std():>12,.0f}")
print(f"Correlación monto-compras_6m original: {df['monto_compras'].corr(df['compras_6m']):.3f}"
      f"   con ruido: {monto_ruido.corr(df['compras_6m']):.3f}")

coords = df[["latitud", "longitud"]]
coords_r = coords.round(DECIMALES_COORD)
print(f"\nPuntos distintos con coordenadas originales: {len(coords.drop_duplicates()):,}")
print(f"Puntos distintos con {DECIMALES_COORD} decimales            : {len(coords_r.drop_duplicates()):,}")
k_coord = tam_grupo(coords_r.assign(barrio=df["barrio"]), ["latitud", "longitud", "barrio"])
print(f"Personas solas en su punto + barrio      : {(k_coord == 1).mean()*100:.1f} %")
""")
    pregunta_nb(
        c, "prueba", next(n),
        "Pruebe `DECIMALES_COORD = 1` y `= 3`. ¿Cuántos decimales necesita "
        "para que menos del 20 % quede solo en su punto? ¿Le sirve todavía al "
        "proveedor una coordenada así, o es mejor entregar solo la región?",
        "Con 3 decimales (≈ 110 m) y el barrio, el 97,6 % queda solo; con 2 "
        "(≈ 1 km), el 58,8 %; con 1 decimal (≈ 11 km), el 1,8 %, pero el punto "
        "ya equivale casi a la ciudad. A ese "
        "nivel la coordenada no aporta nada que la región no dé: es más "
        "honesto suprimirla. Además, el ruido de ±3 km que ya tenían los datos "
        "**no** las hacía anónimas, como advierte la Actividad 4.",
    )

    # --- Estación 7
    c.md("""
## 🔵 🧰 Estación 7 · Privacidad diferencial para tablas

Cuando lo que se publica son **conteos** (un tablero, un informe), se puede
sumar ruido calibrado con una garantía matemática. El parámetro **ε (épsilon)**
es el *presupuesto de privacidad*: menor ε, más ruido, más protección.

El mecanismo de Laplace: `conteo publicado = conteo real + Laplace(0, 1/ε)`.
Es la técnica que usó la Oficina del Censo de Estados Unidos para el censo de 2020.
""")
    c.code(r"""
# Pregunta que alguien quiere publicar: ¿cuántos clientes compran sobre todo salud o maternidad, por ciudad?
real = (df.assign(sensible=df["categoria_top"].isin(["salud_bienestar", "bebe_maternidad"]))
          .groupby("ciudad")["sensible"].sum().sort_values())

def laplace(conteos, epsilon, semilla=0):
    r = np.random.default_rng(semilla)
    return (conteos + r.laplace(0, 1 / epsilon, len(conteos))).round().clip(lower=0).astype(int)

tabla_dp = pd.DataFrame({"real": real})
for eps in [0.1, 0.5, 1, 5]:
    tabla_dp[f"ε = {eps}"] = laplace(real, eps).values
tabla_dp
""")
    c.code(r"""
# Error relativo promedio según ε, repitiendo 200 publicaciones.
eps_grid = [0.05, 0.1, 0.25, 0.5, 1, 2, 5]
errores = []
for eps in eps_grid:
    e = [np.mean(np.abs(laplace(real, eps, s) - real) / real) * 100 for s in range(200)]
    errores.append(np.mean(e))

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(eps_grid, errores, "o-", color=COLOR["acento"], lw=2)
ax.set_xscale("log")
ax.set_xlabel("ε  (← más privacidad · más exactitud →)")
ax.set_ylabel("error relativo medio %")
ax.set_title("El precio de la privacidad diferencial")
for x, y in zip(eps_grid, errores):
    ax.annotate(f"{y:.0f} %", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
plt.show()
""")
    c.md("""
### Tres ideas para no exagerar la garantía

- **Sensibilidad.** Un conteo cambia como máximo en 1 si se agrega o se quita
  una persona. Por eso la escala del ruido es 1/ε. Otras consultas (sumas de
  montos, promedios) tienen sensibilidad mayor y necesitan más ruido.
- **Composición en paralelo.** Cada persona está en una sola ciudad: publicar la
  tabla completa por ciudad gasta **ε una vez**, no doce.
- **Composición secuencial.** Publicar la **misma** tabla *m* veces gasta
  *m* × ε. Las 200 repeticiones del gráfico anterior son una **simulación** del
  error esperado, no publicaciones reales. Si se publicaran, el promedio
  revelaría el valor real, como muestra la celda siguiente.
""")
    c.code(r"""
# Ataque por promedio: publicar 50 veces con ε = 0,5 cada vez equivale a gastar ε = 25.
publicaciones = np.array([laplace(real, 0.5, s) for s in range(50)])
promedio = pd.Series(publicaciones.mean(axis=0), index=real.index).round(1)
pd.DataFrame({"real": real, "una publicación (ε = 0,5)": publicaciones[0],
              "promedio de 50 publicaciones": promedio}).tail(6)
""")
    pregunta_nb(
        c, "decide", next(n),
        "Para la ciudad más pequeña el error relativo es mucho mayor que para "
        "Bogotá con el mismo ε. ¿Por qué? ¿Qué le dice eso sobre publicar "
        "tablas muy desagregadas (por barrio, por vereda)?",
        "El ruido de Laplace tiene el mismo tamaño absoluto para todas las "
        "celdas; en una celda pequeña ese ruido pesa mucho más en términos "
        "relativos. Mientras más se desagrega, más ruido relativo, y cada "
        "consulta adicional consume presupuesto. Desagregar tiene un precio que "
        "se paga en exactitud o en privacidad, no hay tercera opción.",
    )

    # --- Estación 8
    c.md("""
## 🔵 🧰 Estación 8 · Datos sintéticos

Generar una base **nueva**, sin personas reales, que imite a la original.
Probamos dos generadores muy sencillos y los evaluamos con la prueba estándar
**TSTR**: *entrenar con sintético, evaluar con real*.

> ⚠️ **Regla para no hacer trampa.** Las personas reales con que se evalúa
> **no pueden** haber sido usadas para crear los sintéticos. Por eso partimos la
> base en dos: el 70 % alimenta al generador y el 30 % solo sirve para evaluar.
""")
    c.code(r"""
from sklearn.model_selection import train_test_split

def sintetico_independiente(datos, columnas=COLS_MODELO, n=None, semilla=1):
    # Cada columna se muestrea por separado: conserva marginales, rompe relaciones.
    r = np.random.default_rng(semilla)
    n = n or len(datos)
    return pd.DataFrame({c: r.choice(datos[c].values, n) for c in columnas + ["churn"]})

def sintetico_condicional(datos, columnas=COLS_MODELO, objetivo="churn", semilla=1):
    # Dentro de cada clase de abandono, cada columna se muestrea por separado.
    partes = []
    for valor, sub in datos.groupby(objetivo):
        s = sintetico_independiente(sub, columnas, len(sub), semilla + int(valor))
        s[objetivo] = valor
        partes.append(s)
    return pd.concat(partes, ignore_index=True).sample(frac=1, random_state=semilla)

def auc_holdout(entreno, prueba):
    Xtr = _matriz(entreno, COLS_MODELO); med = Xtr.median()
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000, C=0.5)).fit(Xtr.fillna(med), entreno["churn"])
    return round(roc_auc_score(prueba["churn"], m.predict_proba(_matriz(prueba, COLS_MODELO, Xtr.columns).fillna(med))[:, 1]), 3)

real_gen, real_eval = train_test_split(df, test_size=0.3, stratify=df["churn"], random_state=7)
s_ind = sintetico_independiente(real_gen)
s_con = sintetico_condicional(real_gen)

utilidad_sint = pd.DataFrame({"AUC en el 30 % real no visto": [
    auc_holdout(real_gen, real_eval), auc_holdout(s_ind, real_eval), auc_holdout(s_con, real_eval)]},
    index=["entrenado con el 70 % real (referencia)", "sintético independiente", "sintético condicional"])
utilidad_sint
""")
    c.md("""
### ¿El sintético protege? «Cero copias» no basta

Que ninguna fila sintética sea idéntica a una real es una condición mínima, no
una prueba. La pregunta útil es otra: **si un atacante busca en la base
sintética a una persona real que era única, ¿aprende algo sobre ella?**
Comparamos su acierto con el de alguien que simplemente adivina la categoría
más frecuente.
""")
    c.code(r"""
copias = s_con.merge(real_gen[COLS_MODELO + ["churn"]], on=COLS_MODELO + ["churn"]).shape[0]

unicos = real_gen[tam_grupo(real_gen, CUASI) == 1]          # personas reales solas en su grupo
coinc = unicos.merge(s_con, on=CUASI, suffixes=("_real", "_sint"))
acierto = (coinc[SENSIBLE + "_real"] == coinc[SENSIBLE + "_sint"]).mean() * 100
azar = real_gen[SENSIBLE].value_counts(normalize=True).iloc[0] * 100

print(f"Filas sintéticas idénticas a una persona real          : {copias}")
print(f"Personas únicas con al menos un «doble» sintético       : {coinc[CUASI].drop_duplicates().shape[0]} de {len(unicos)}")
print(f"Acierto del atacante sobre la categoría que más compra  : {acierto:.1f} %")
print(f"Acierto adivinando siempre la categoría más frecuente   : {azar:.1f} %")
""")
    pregunta_nb(
        c, "riesgo", next(n),
        "El sintético independiente pierde casi toda la señal; el condicional "
        "conserva parte. En la prueba de inferencia, el atacante acierta "
        "**menos** que adivinando. ¿Qué pasaría con esa prueba si usáramos un "
        "generador mucho más potente (redes neuronales, cópulas), que conserva "
        "más relaciones?",
        "Con un generador potente la utilidad sube, pero también el riesgo de "
        "que **memorice**: puede reproducir registros reales casi idénticos, "
        "sobre todo de personas atípicas, y entonces el acierto del atacante "
        "superaría al azar. Por eso un sintético no es anónimo por definición: "
        "hay que medir copias, inferencia de atributos y, en estudios serios, "
        "ataques de pertenencia. Nuestro generador es tan simple que no puede "
        "memorizar combinaciones; eso explica su baja utilidad y su bajo riesgo.",
    )

    # ------------------------------------------------------------ COMPARAR
    c.md("""
---

# 4 · COMPARAR

*Cinco bases candidatas, dos escenarios de atacante y una utilidad medida sin trampas.*

### Cómo se mide cada eje

| Eje | Medida | Cómo se lee |
|:--|:--|:--|
| Riesgo | % *k*<5 y riesgo 1/*k*, en el escenario **básico** y en el **ampliado** | El ampliado es el que decide: el estrato viaja en la base |
| Riesgo | % reidentificado por el **ataque** de vinculación | Personas de la fuente pública acertadas con certeza |
| Pérdida | **NCP %** | 0 = exacto · 100 = suprimido |
| Utilidad | **AUC** del modelo de abandono, 5 pliegues | Media ± desviación estándar entre pliegues |
| Utilidad | **ΔAUC** frente a V0, pareado (mismos pliegues) | Regla práctica, no una prueba formal: si ΔAUC, en valor absoluto, es menor que su desviación, **no hay diferencia demostrable** |
| Utilidad | **Δ tasa** de abandono por categoría | Cuánto se deforma una estadística descriptiva (pp) |

**Sin fugas:** en cada pliegue, la generalización, la supresión o el generador
sintético se aplican **solo** al 80 % de entrenamiento; el 20 % restante son
personas reales nuevas, a las que se aplica la misma regla de generalización
(sin suprimirlas, porque en la vida real siguen existiendo).
""")
    c.code(r"""
VERSIONES = {
    "V0 · sin identificadores":          dict(gen=None, sup=None),
    "V1 · generalización suave":         dict(gen=(5, "conservar", "ciudad", "grupo", "exacto"), sup=None),
    "V2 · fuerte + supresión (básico)":  dict(gen=(10, "agrupar", "region", "grupo", "exacto"), sup=CUASI),
    "V2b · fuerte + estrato en niveles": dict(gen=(10, "agrupar", "region", "suprimir", "nivel"), sup=CUASI_AMPLIADO),
    "V3 · sintética condicional":        dict(sint=True),
    "★ su versión (estaciones 3+4)":     dict(gen=(NIVEL_EDAD, SEXO_COMO, CIUDAD_COMO, OCUPACION_COMO, ESTRATO_COMO),
                                              sup=CUASI_AMPLIADO),
}

def construir(cfg, datos=e1):
    d = generalizar(datos, *cfg["gen"]) if cfg.get("gen") else datos
    return d[tam_grupo(d, cfg["sup"]) >= K_OBJETIVO] if cfg.get("sup") else d

candidatas, filas, aucs = {}, [], {}
for nombre, cfg in VERSIONES.items():
    if cfg.get("sint"):
        base = sintetico_condicional(df)
        aucs[nombre] = utilidad_cv(sintetico=lambda tr: sintetico_condicional(tr))
        fila = {"registros": len(base), "% k<5 básico": np.nan, "% k<5 ampliado": np.nan,
                "riesgo 1/k % ampliado": np.nan, "% reid. ataque básico": 0.0,
                "% reid. ataque ampliado": 0.0, "NCP %": np.nan}
    else:
        base = construir(cfg)
        pub = generalizar(fuente_publica, *cfg["gen"]) if cfg.get("gen") else fuente_publica
        trans = (lambda d, g=cfg.get("gen"): generalizar(d, *g)) if cfg.get("gen") else None
        aucs[nombre] = utilidad_cv(transformar=trans, suprimir_en=cfg.get("sup"))
        b, a = perfil_riesgo(base, CUASI), perfil_riesgo(base, CUASI_AMPLIADO)
        fila = {"registros": len(base), "% k<5 básico": b["% k<5"], "% k<5 ampliado": a["% k<5"],
                "riesgo 1/k % ampliado": a["riesgo medio 1/k %"],
                "% reid. ataque básico": ataque_vinculacion(pub, base, CUASI, mostrar=False)[0]["% reidentificadas"],
                "% reid. ataque ampliado": ataque_vinculacion(pub, base, CUASI_AMPLIADO, mostrar=False)[0]["% reidentificadas"],
                "NCP %": ncp(base)}
    candidatas[nombre] = base
    d = aucs[nombre] - aucs["V0 · sin identificadores"]
    fila.update({"Δ tasa abandono (pp)": dif_tasas(base),
                 "AUC": f"{aucs[nombre].mean():.3f} ± {aucs[nombre].std():.3f}",
                 "ΔAUC vs V0": f"{d.mean():+.3f} ± {d.std():.3f}" if nombre[:2] != "V0" else "—"})
    filas.append({"versión": nombre, **fila})

frontera = pd.DataFrame(filas).set_index("versión")
frontera
""")
    c.code(r"""
fig, ax = plt.subplots(figsize=(9.5, 5))
colores = [COLOR["alerta"], COLOR["ambar"], COLOR["despues"], COLOR["ok"], COLOR["acento"], "#0f172a"]
usados = {}
for (nombre, fila), col in zip(frontera.iterrows(), colores):
    d = aucs[nombre] - aucs["V0 · sin identificadores"]
    x, y, e = fila["% reid. ataque ampliado"], d.mean(), d.std()
    es_mia = nombre.startswith("★")
    ax.errorbar(x + (1.5 if es_mia else 0), y, yerr=e, fmt="*" if es_mia else "o", ms=16 if es_mia else 10,
                color=col, capsize=4, label=nombre, zorder=2 if es_mia else 3, alpha=.8 if es_mia else 1)
    k = round(x / 6)
    usados[k] = usados.get(k, -1) + 1
    corto = "★" if nombre.startswith("★") else nombre.split(" · ")[0]
    ax.annotate(corto, (x, y), textcoords="offset points", xytext=(10 + 22 * usados[k], 6),
                fontsize=10, fontweight="bold", color=col)
ax.axhline(0, color=COLOR["antes"], lw=1)
ax.text(60, 0.002, "misma utilidad que V0", fontsize=8, color=COLOR["antes"])
ax.axvspan(-3, 5, color=COLOR["ok"], alpha=.08)
ax.set_xlim(-3, 100)
ax.set_xlabel("% de la fuente pública reidentificado · escenario ampliado  (← más seguro)")
ax.set_ylabel("ΔAUC frente a V0 (pareado)\nmedia ± d.e. en 5 pliegues")
ax.set_title("¿Cuánta utilidad costó cada punto de riesgo que se quitó?")
ax.legend(frameon=False, loc="lower right", fontsize=8)
plt.show()
""")
    c.md("""
### ¿Qué técnicas llegaron a las versiones finales?

| Estación | ¿Está en V2 / V2b? | Por qué |
|:--|:--|:--|
| 1 · Supresión de indirectos | Sí | IP, coordenadas, barrio y fecha de nacimiento no viajan |
| 2 · Seudonimización | No en la base: se entrega un identificador aleatorio | El proveedor no necesita unir con otras tablas; si lo necesitara, HMAC |
| 3 · Generalización | Sí | Edad, sexo, ciudad, ocupación y (en V2b) estrato |
| 4 · Supresión local | Sí | Los grupos con *k* < 5 |
| 5 · *Top coding* / microagregación | No | `ingresos_mensuales` no se entrega: minimizar fue más barato |
| 6 · Perturbación | No | Las coordenadas no se entregan. **`monto_compras` sí, exacto**: riesgo residual que hay que declarar |
| 7 · Privacidad diferencial | No | Sirve para publicar tablas, no para entregar microdatos |
| 8 · Datos sintéticos | Es la versión V3 | Alternativa completa, no un paso |
""")
    pregunta_nb(
        c, "decision", next(n),
        "Compare V2 y V2b. V2 parece perfecta en el escenario básico. ¿Qué le "
        "pasa cuando el atacante también conoce el estrato? Luego mire la "
        "columna `ΔAUC vs V0`: ¿hay alguna versión con una pérdida de utilidad "
        "**demostrable**?\n\nLa pregunta central del encuentro: **¿cuánta "
        "utilidad estamos dispuestos a perder, y quién decide eso?**",
        "V2 cumple *k* ≥ 5 con cuatro cuasi-identificadores, pero entrega el "
        "estrato exacto: con él, la mayoría de los registros vuelve a quedar en "
        "grupos pequeños y el ataque ampliado reidentifica a muchas personas. "
        "**Una métrica sin escenario declarado no prueba nada.** V2b corrige "
        "eso generalizando el estrato y suprimiendo la ocupación, a cambio de más "
        "pérdida (NCP ≈ 44 %), unos 300 registros suprimidos y tasas "
        "descriptivas deformadas hasta unos 7 puntos. En utilidad predictiva, "
        "V1 y V2 pierden ≈ 0,005 de AUC, menos que su desviación: no es una "
        "diferencia demostrable. V2b pierde ≈ 0,016 ± 0,011 y el sintético "
        "≈ 0,027 ± 0,014: pérdidas **pequeñas pero consistentes**. Conclusión "
        "honesta: proteger de verdad sí cuesta, pero menos de lo que se teme, y "
        "solo se sabe midiendo. Quién decide: el responsable del tratamiento, "
        "con el umbral y el escenario escritos.",
    )

    # ------------------------------------------------------------ DECIDIR
    c.md("""
---

# 5 · DECIDIR Y ENTREGAR

*Una base concreta, un umbral escrito, un escenario declarado y un informe que
otra persona pueda auditar.*
""")
    c.code(r"""
pd.DataFrame(BITACORA).set_index("paso")
""")
    c.code_var(
        r"""
# ===================== PERILLA =====================
VERSION_ELEGIDA = "V2b · fuerte + estrato en niveles"   # una de las filas de `frontera`
SALIDA = "1 · base anonimizada con utilidad reducida"
# Las tres salidas defendibles (Actividad 4):
#   "1 · base anonimizada con utilidad reducida"
#   "2 · base seudonimizada bajo contrato"
#   "3 · no se entrega la base: alternativa"
FINALIDAD = "TODO: para qué usará el proveedor la base, en una frase"
POR_QUE_MICRODATOS = "TODO: por qué no basta con datos agregados o sintéticos"
UMBRAL = "TODO: por ejemplo, k ≥ 5 para el 100 % de los registros en el escenario ampliado"
JUSTIFICACION = "TODO: dos o tres frases con el porqué"
CONDICIONES = "TODO: condiciones contractuales y técnicas que acompañan la entrega"
EQUIPO = "TODO: nombres del grupo"
# ===================================================
""",
        r"""
# ===================== PERILLA =====================
VERSION_ELEGIDA = "V2b · fuerte + estrato en niveles"
SALIDA = "1 · base anonimizada con utilidad reducida"
FINALIDAD = "Entrenar y validar el motor de recomendación de DataMarket; ningún otro uso."
POR_QUE_MICRODATOS = ("El motor aprende de patrones individuales de compra; los agregados no sirven y "
                      "el sintético simple pierde parte de la señal.")
UMBRAL = "k ≥ 5 para el 100 % de los registros en el escenario ampliado y <5 % reidentificado en el ataque"
JUSTIFICACION = ("V2b es la única versión de microdatos que cumple en los dos escenarios declarados. "
                 "Cuesta una pérdida pequeña pero consistente de AUC (≈ 0,016), detalle demográfico y "
                 "unos 300 registros suprimidos, que se reportan con su perfil.")
CONDICIONES = ("Acuerdo de transmisión con prohibición de cruce y de reidentificación; uso exclusivo para la "
               "finalidad; ambiente controlado; destrucción a los 6 meses; auditoría.")
EQUIPO = "Docente · versión de referencia"
# ===================================================
""",
    )
    c.code(r"""
f = frontera.loc[VERSION_ELEGIDA]
v0 = frontera.iloc[0]

# ---- Verificación automática antes de exportar --------------------------------
es_sintetica = pd.isna(f["% k<5 ampliado"])
chequeos = {
    "k ≥ 5 para todos (escenario básico)": es_sintetica or f["% k<5 básico"] == 0,
    "k ≥ 5 para todos (escenario ampliado)": es_sintetica or f["% k<5 ampliado"] == 0,
    "ataque ampliado < 5 %": f["% reid. ataque ampliado"] < 5,
    "sin identificadores directos ni indirectos": not set(IDENTIFICADORES_DIRECTOS + INDIRECTOS) & set(candidatas[VERSION_ELEGIDA].columns),
}
cumple = all(chequeos.values())
for k_, v_ in chequeos.items():
    print(("✅ " if v_ else "❌ ") + k_)
if not cumple and SALIDA.startswith("1"):
    print("\n⚠️  La versión NO cumple el umbral para la salida 1. Cambie de versión o de salida "
          "(2: bajo contrato · 3: no entregar). El informe quedará marcado.")
dictamen = ("LIBERAR CON CONDICIONES" if cumple and SALIDA.startswith("1")
            else "NO LIBERAR COMO ANONIMIZADA" if SALIDA.startswith("1")
            else "ENTREGA BAJO CONTRATO (datos personales)" if SALIDA.startswith("2")
            else "NO SE ENTREGA LA BASE")

entregable = candidatas[VERSION_ELEGIDA][[c for c in COLS_MODELO + ["churn"] if c in candidatas[VERSION_ELEGIDA].columns]].copy()
entregable = entregable.loc[:, entregable.nunique() > 1]   # columnas suprimidas (todo «*») no viajan
entregable.insert(0, "id_entrega", [secrets.token_hex(6) for _ in range(len(entregable))])  # sin vínculo posible
entregable.to_csv("base_entregable_proveedor.csv", index=False, encoding="utf-8")

informe = f'''# Dictamen de liberación de datos · DataMarket → proveedor

**Equipo:** {EQUIPO}  ·  **Fecha:** {pd.Timestamp("today").date()}  ·  **Dictamen:** {dictamen}

## 1. Finalidad y necesidad
- Finalidad: {FINALIDAD}
- ¿Por qué microdatos?: {POR_QUE_MICRODATOS}

## 2. Qué se entrega
- Versión: **{VERSION_ELEGIDA}** · salida elegida: **{SALIDA}**
- {len(entregable)} registros de {len(df)} ({len(df) - len(entregable)} suprimidos) · {entregable.shape[1]} variables: {", ".join(entregable.columns)}

## 3. Qué se midió
Escenario básico: el atacante conoce edad, sexo, ciudad y ocupación. Escenario ampliado: además, el estrato.

| Métrica | Línea base (V0) | Entregable |
|:--|--:|--:|
| % registros con k<5 · básico | {v0["% k<5 básico"]} | {f["% k<5 básico"]} |
| % registros con k<5 · ampliado | {v0["% k<5 ampliado"]} | {f["% k<5 ampliado"]} |
| Riesgo medio 1/k % · ampliado | {v0["riesgo 1/k % ampliado"]} | {f["riesgo 1/k % ampliado"]} |
| % reidentificado en el ataque · ampliado | {v0["% reid. ataque ampliado"]} | {f["% reid. ataque ampliado"]} |
| Pérdida de información NCP % | {v0["NCP %"]} | {f["NCP %"]} |
| AUC del modelo de abandono (5 pliegues) | {v0["AUC"]} | {f["AUC"]} |
| ΔAUC frente a V0 (pareado) | — | {f["ΔAUC vs V0"]} |
| Máx. cambio en la tasa de abandono por categoría (pp) | 0 | {f["Δ tasa abandono (pp)"]} |

Verificación automática: {"; ".join(("cumple: " if v else "NO cumple: ") + k for k, v in chequeos.items())}.

## 4. Umbral aceptado y por qué
{UMBRAL}. {JUSTIFICACION}

## 5. Riesgo residual
Vale solo para los dos escenarios declarados. No cubre a un atacante que conozca montos o fechas de
compra exactos (`monto_compras` viaja sin perturbar) ni el cruce con otras bases del proveedor. El
riesgo 1/k supone que el atacante sabe que la persona está en la base.

## 6. Condiciones de la entrega
{CONDICIONES}
'''
with open("informe_anonimizacion.md", "w", encoding="utf-8") as fh:
    fh.write(informe)

from IPython.display import Markdown, display
display(Markdown(informe))
print("Archivos creados: base_entregable_proveedor.csv · informe_anonimizacion.md")
""")
    pregunta_nb(
        c, "decision", next(n),
        "El dictamen dice «riesgo residual: vale para los escenarios "
        "declarados». Nombre **un escenario de ataque** que su medición no "
        "cubre y diga qué condición contractual o técnica lo compensaría.",
        "Ejemplos: el proveedor tiene su propia base con montos y fechas de "
        "compra (puede vincular por comportamiento, no por demografía) → "
        "perturbar o redondear `monto_compras`, prohibición contractual de "
        "cruce, auditoría y ambiente controlado. O una filtración en el "
        "proveedor → cifrado, acceso por rol y plazo de destrucción. Lo que se "
        "busca es que el estudiante reconozca que **la métrica depende del "
        "escenario** y que el contrato cubre lo que la técnica no alcanza.",
    )

    # ------------------------------------------------------------ REFLEXIONAR
    c.md("""
---

# 6 · REFLEXIONAR

*Lo que cambia con el volumen y con los modelos.*

| Con Big Data… | Con IA… |
|:--|:--|
| Más variables = más cuasi-identificadores: la unicidad **crece**, no se diluye | El modelo entrenado puede **memorizar** y devolver datos personales |
| Las trazas (ubicación, compras, búsquedas) son únicas: 4 puntos de ubicación bastan para identificar al 95 % de las personas (de Montjoye, 2013) | Un **ataque de pertenencia** puede revelar si alguien estaba en el entrenamiento |
| Cada cruce nuevo es un ataque de vinculación potencial | El modelo pasa a ser un **activo que contiene datos** y hereda sus obligaciones |
""")
    pregunta_nb(
        c, "reflexiona", next(n),
        "El proveedor no quiere la base: quiere **entrenar un modelo** con ella. "
        "Si entrega V0 y él entrena un modelo muy grande, ¿la base deja de "
        "importar cuando se borra? ¿Qué pediría en el contrato sobre el "
        "**modelo**, no solo sobre los datos?",
        "No: el modelo puede conservar información de las personas y "
        "exponerla. En el contrato: uso exclusivo del modelo para la finalidad, "
        "prohibición de reutilizarlo o venderlo, destrucción o reentrenamiento "
        "si se revoca la autorización, pruebas de memorización antes del "
        "despliegue y la alternativa más fuerte: entrenar dentro del perímetro "
        "de DataMarket sin que los datos salgan.",
    )
    pregunta_nb(
        c, "reflexiona", next(n),
        "**Aporte al decálogo (Encuentro 5).** Escriba **una regla** para el "
        "decálogo del científico de datos que salga de este laboratorio.\n\n"
        "Formato: *verbo en imperativo + qué + evidencia que queda*. "
        "Ejemplo: «Mida el riesgo de reidentificación antes y después de "
        "transformar, y deje la bitácora con la entrega».",
        "Se busca una regla ejecutable y verificable. Otras buenas: «Ataque su "
        "base antes de entregarla»; «Nunca use un *hash* sin clave como "
        "seudónimo»; «Revise a quién se lleva la supresión».",
    )

    c.md("""
---

## Lo que queda del laboratorio

| Archivo | Para qué |
|:--|:--|
| `base_entregable_proveedor.csv` | La base que saldría hacia el proveedor |
| `informe_anonimizacion.md` | El dictamen de liberación: borrador del informe de la **Actividad 4** |
| La bitácora y la frontera riesgo-utilidad | La evidencia de que se midió |

### Las ocho técnicas en una línea

| Técnica | Protege | Cuesta |
|:--|:--|:--|
| Supresión de variables | Cierra puertas de vinculación | Todo el análisis que dependía de ellas |
| Seudonimización (HMAC) | El identificador | Nada… y **no anonimiza** |
| Generalización | Identidad (*k*) | Resolución analítica |
| Supresión local | Los casos raros | Sesgo: borra minorías |
| *Top coding* / microagregación | Valores extremos | Colas y varianza |
| Ruido | Valores exactos | Distribuciones y correlaciones |
| Privacidad diferencial | Tablas publicadas, con garantía | Exactitud en celdas pequeñas |
| Datos sintéticos | Todo, si no memoriza | Relaciones que el generador no captura |

**Siguiente paso:** Actividad 4 (en grupo, semana 8) y Encuentro 5 · el decálogo.

**Marco legal relacionado:** art. 10 de la Ley 1581 de 2012 (fines
estadísticos), considerando 26 del GDPR (datos anónimos frente a
seudonimizados), arts. 36 a 40 de la Ley 2335 de 2023 (reserva estadística).
""")
    return c


# ==========================================================================

def main() -> None:
    lab01().escribir("lab01")
    lab02().escribir("lab02")
    # Versión 2 revisada (10-nov-2026). La versión 1 se conserva en labs/lab03-*.ipynb.
    lab03().escribir("lab03-v2")


if __name__ == "__main__":
    main()
