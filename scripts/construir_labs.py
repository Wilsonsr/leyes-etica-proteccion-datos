"""
construir_labs.py
=================

Genera los cuatro cuadernos del curso a partir de una sola fuente:

    labs/lab01-estudiante.ipynb    labs/lab01-solucion.ipynb
    labs/lab02-estudiante.ipynb    labs/lab02-solucion.ipynb

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

def main() -> None:
    lab01().escribir("lab01")
    lab02().escribir("lab02")


if __name__ == "__main__":
    main()
