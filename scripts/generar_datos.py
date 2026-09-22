"""
generar_datos.py
================

Genera el dataset sintetico del caso transversal del curso:
DataMarket Analytics (empresa ficticia colombiana de comercio electronico).

NINGUN dato de este archivo corresponde a una persona real.
Todo se construye con un generador pseudoaleatorio de semilla fija,
por lo que el resultado es REPRODUCIBLE: ejecutar el script dos veces
produce exactamente el mismo CSV.

Uso
---
    python scripts/generar_datos.py
    python scripts/generar_datos.py --n 1500 --semilla 2026 --salida data/clientes_sinteticos.csv

Diseno pedagogico
-----------------
El dataset tiene 35 columnas y esta construido a proposito para que
aparezcan, de forma natural, las discusiones del curso:

1. Identificadores directos      -> nombre, email, telefono, documento, direccion
2. Cuasi-identificadores         -> edad, sexo, ciudad, barrio, ocupacion, estrato
3. Identificadores en linea      -> ip, dispositivo
4. Datos de comportamiento       -> visitas_web, productos_vistos, compras_6m
5. Datos inferidos por la empresa-> score_riesgo_interno, segmento
6. Proxies de datos sensibles    -> compras_farmacia_6m (salud),
                                    entrega_asistida (discapacidad),
                                    busquedas_maternidad (embarazo)
7. Trazabilidad del origen       -> origen_dato, fecha_autorizacion,
                                    consentimiento_marketing
8. Alcance territorial           -> pais_residencia (incluye residentes en la UE)

Ademas:
- La variable objetivo `churn` depende PARCIALMENTE de las variables
  proxy de datos sensibles. Eso es intencional: permite que en el
  Laboratorio 2 el "modelo B" tenga mejor AUC que el "modelo A" y que la
  decision no sea puramente tecnica.
- Hay valores faltantes deliberados en ingresos_mensuales, ocupacion,
  estrato y fecha_autorizacion.
- Hay duplicados y registros con formato inconsistente (correos en
  mayusculas, telefonos con separadores distintos) para el bloque de calidad.
"""

from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# 1. Vocabularios sinteticos
# --------------------------------------------------------------------------

NOMBRES = [
    "Ana", "Luis", "Camila", "Andres", "Valentina", "Juan", "Laura", "Carlos",
    "Daniela", "Santiago", "Paula", "Julian", "Natalia", "Felipe", "Diana",
    "Ricardo", "Sofia", "Mateo", "Carolina", "Sebastian", "Marcela", "Oscar",
    "Angela", "David", "Tatiana", "Nicolas", "Lorena", "Esteban", "Claudia",
    "Hernan", "Ximena", "Alvaro", "Liliana", "Mauricio", "Sandra", "Jorge",
]

APELLIDOS = [
    "Rojas", "Gomez", "Martinez", "Castro", "Vargas", "Moreno", "Ospina",
    "Quintero", "Salazar", "Beltran", "Cardenas", "Lozano", "Pineda",
    "Arango", "Zapata", "Mendoza", "Cifuentes", "Barrios", "Guerrero",
    "Naranjo", "Peralta", "Riveros", "Solano", "Trujillo", "Uribe", "Velez",
]

# ciudad -> (departamento_no_usado, lat, lon, barrios)
CIUDADES = {
    "Bogota":       (4.6486, -74.0819, ["Chapinero", "Suba", "Kennedy", "Usaquen", "Teusaquillo", "Engativa"]),
    "Medellin":     (6.2442, -75.5812, ["El Poblado", "Laureles", "Belen", "Robledo"]),
    "Cali":         (3.4516, -76.5320, ["Granada", "San Fernando", "Ciudad Jardin", "Aguablanca"]),
    "Barranquilla": (10.9685, -74.7813, ["El Prado", "Riomar", "Simon Bolivar"]),
    "Cartagena":    (10.3910, -75.4794, ["Bocagrande", "Manga", "El Pozon"]),
    "Bucaramanga":  (7.1193, -73.1227, ["Cabecera", "Provenza", "Real de Minas"]),
    "Pereira":      (4.8133, -75.6961, ["Alamos", "Cuba", "Centro"]),
    "Manizales":    (5.0703, -75.5138, ["Palermo", "Chipre", "La Enea"]),
    "Ibague":       (4.4389, -75.2322, ["Ambala", "Picalena", "Centro"]),
    "Villavicencio": (4.1420, -73.6266, ["Barzal", "Porfia", "Centro"]),
    "Pasto":        (1.2136, -77.2811, ["Centro", "Torobajo", "Aranda"]),
    "Santa Marta":  (11.2408, -74.1990, ["El Rodadero", "Gaira", "Centro"]),
}

OCUPACIONES = [
    "Ingeniero/a", "Docente", "Comerciante", "Contador/a", "Disenador/a",
    "Enfermero/a", "Abogado/a", "Estudiante", "Administrador/a", "Tecnico/a",
    "Pensionado/a", "Independiente",
]

DISPOSITIVOS = ["Android", "iOS", "Windows", "macOS", "Linux"]

CANALES = [
    "busqueda_organica", "publicidad_pagada", "referido", "redes_sociales",
    "email_marketing", "marketplace",
]

# El origen del dato es la variable clave de la discusion sobre FINALIDAD.
ORIGENES = {
    "facturacion":            0.30,   # recolectado para emitir factura
    "entrega_domicilio":      0.22,   # recolectado para entregar el pedido
    "registro_cuenta":        0.20,   # el usuario creo una cuenta
    "programa_fidelizacion":  0.12,   # incluye autorizacion de marketing
    "lista_comprada_tercero": 0.09,   # <- origen problematico
    "enriquecimiento_web":    0.07,   # <- origen problematico (scraping)
}

CATEGORIAS = [
    "tecnologia", "hogar", "moda", "deportes", "mascotas",
    "salud_bienestar", "bebe_maternidad", "supermercado", "libros",
]

PAISES = {
    "Colombia": 0.90,
    "Espana": 0.025,
    "Mexico": 0.02,
    "Estados Unidos": 0.015,
    "Alemania": 0.015,
    "Francia": 0.010,
    "Ecuador": 0.010,
    "Italia": 0.005,
}

PAISES_UE = {"Espana", "Alemania", "Francia", "Italia"}

DOMINIOS = ["correo.com", "mail.co", "webmail.net", "datamail.co", "miemail.com"]


def _sin_tildes(texto: str) -> str:
    """Normaliza a ASCII para construir correos verosimiles."""
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .replace(" ", "")
        .replace("/", "")
    )


# --------------------------------------------------------------------------
# 2. Generacion
# --------------------------------------------------------------------------

def generar(n: int = 1500, semilla: int = 2026) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)

    # --- identidad sintetica -------------------------------------------------
    nombres = rng.choice(NOMBRES, n)
    apellidos = rng.choice(APELLIDOS, n)
    nombre_completo = np.array([f"{a} {b}" for a, b in zip(nombres, apellidos)])

    cliente_id = np.array([f"DM-{i:05d}" for i in range(1, n + 1)])

    # Documento CLARAMENTE sintetico: prefijo SYN para que nadie lo confunda
    # con un numero de identificacion real.
    documento = np.array([f"SYN-{rng.integers(10_000_000, 99_999_999)}" for _ in range(n)])

    email = np.array([
        f"{_sin_tildes(a)}.{_sin_tildes(b)}{rng.integers(1, 999)}@{rng.choice(DOMINIOS)}"
        for a, b in zip(nombres, apellidos)
    ])

    telefono = np.array([f"3{rng.integers(0, 10)}{rng.integers(10_000_000, 99_999_999)}" for _ in range(n)])

    # --- demografia ----------------------------------------------------------
    edad = np.clip(rng.normal(38, 13, n).round().astype(int), 18, 82)
    fecha_nacimiento = pd.to_datetime("2026-01-01") - pd.to_timedelta(edad * 365.25, unit="D")
    fecha_nacimiento = fecha_nacimiento.normalize()

    sexo = rng.choice(["F", "M", "Otro", "Prefiere no responder"], n, p=[0.48, 0.47, 0.03, 0.02])

    ciudades = list(CIUDADES.keys())
    pesos_ciudad = np.array([0.28, 0.16, 0.12, 0.09, 0.07, 0.06, 0.05, 0.04, 0.04, 0.035, 0.03, 0.025])
    pesos_ciudad = pesos_ciudad / pesos_ciudad.sum()
    ciudad = rng.choice(ciudades, n, p=pesos_ciudad)

    barrio, lat, lon = [], [], []
    for c in ciudad:
        base_lat, base_lon, barrios = CIUDADES[c]
        barrio.append(rng.choice(barrios))
        # Ruido geografico de ~ +/- 3 km. Suficiente para que el punto
        # caiga en la ciudad, y suficiente para discutir reidentificacion.
        lat.append(round(base_lat + rng.normal(0, 0.025), 5))
        lon.append(round(base_lon + rng.normal(0, 0.025), 5))
    barrio = np.array(barrio)
    latitud = np.array(lat)
    longitud = np.array(lon)

    direccion = np.array([
        f"{rng.choice(['Calle', 'Carrera', 'Transversal', 'Diagonal'])} "
        f"{rng.integers(1, 180)} # {rng.integers(1, 99)}-{rng.integers(1, 99)}"
        for _ in range(n)
    ])

    estrato = rng.choice([1, 2, 3, 4, 5, 6], n, p=[0.07, 0.20, 0.31, 0.22, 0.13, 0.07])
    ocupacion = rng.choice(OCUPACIONES, n)

    # Ingresos correlacionados con estrato (log-normal) -> proxy socioeconomico.
    base_ingreso = np.array([1.3, 1.7, 2.4, 3.6, 5.6, 8.4])[estrato - 1]
    ingresos_mensuales = np.round(
        rng.lognormal(mean=np.log(base_ingreso * 1_000_000), sigma=0.32, size=n), -4
    )

    pais_residencia = rng.choice(list(PAISES.keys()), n, p=list(PAISES.values()))
    dispositivo = rng.choice(DISPOSITIVOS, n, p=[0.46, 0.23, 0.21, 0.07, 0.03])
    ip = np.array([
        f"{rng.integers(10, 224)}.{rng.integers(0, 256)}.{rng.integers(0, 256)}.{rng.integers(1, 255)}"
        for _ in range(n)
    ])

    canal_adquisicion = rng.choice(CANALES, n, p=[0.26, 0.22, 0.14, 0.18, 0.10, 0.10])
    origen_dato = rng.choice(list(ORIGENES.keys()), n, p=list(ORIGENES.values()))

    # --- comportamiento ------------------------------------------------------
    visitas_web = rng.poisson(14, n) + rng.integers(0, 6, n)
    productos_vistos = (visitas_web * rng.uniform(0.8, 3.4, n)).round().astype(int)
    compras_6m = rng.poisson(np.clip(visitas_web / 6, 0.2, 6))
    ticket = rng.lognormal(mean=np.log(120_000), sigma=0.55, size=n)
    monto_compras = np.round(compras_6m * ticket, -3)

    dias_desde_ultima = np.where(
        compras_6m > 0,
        rng.integers(1, 190, n),
        rng.integers(150, 420, n),
    )
    fecha_ultima_compra = pd.to_datetime("2026-08-31") - pd.to_timedelta(dias_desde_ultima, unit="D")

    categoria_top = rng.choice(CATEGORIAS, n, p=[0.17, 0.15, 0.16, 0.10, 0.08, 0.11, 0.07, 0.11, 0.05])

    # --- variables "incomodas" ----------------------------------------------
    # Ninguna de estas es, formalmente, un dato sensible.
    # Todas permiten INFERIR uno. Ese es el punto del Caso D.
    compras_farmacia_6m = rng.poisson(
        np.where(categoria_top == "salud_bienestar", 3.2, 0.5) + edad / 45
    )
    entrega_asistida = rng.binomial(
        1, np.clip(0.04 + (edad > 65) * 0.22 + (edad > 75) * 0.15, 0, 0.6)
    )
    busquedas_maternidad = rng.poisson(
        np.where(categoria_top == "bebe_maternidad", 6.0, 0.25)
        * np.where((sexo == "F") & (edad.astype(float) < 42), 1.8, 0.5)
    )

    # --- variable objetivo ---------------------------------------------------
    # El churn depende de comportamiento (legitimo) Y de variables proxy de
    # datos sensibles (problematico). Asi, el "modelo B" gana AUC a costa de
    # usar variables que no deberia usar sin justificacion.
    z = (
        -0.35
        # --- bloque de comportamiento: el "modelo A" del Laboratorio 2 ------
        + 0.0120 * dias_desde_ultima
        - 0.38 * compras_6m
        - 0.020 * visitas_web
        - 0.0000016 * monto_compras
        + 0.30 * (canal_adquisicion == "publicidad_pagada")
        - 0.28 * (canal_adquisicion == "referido")
        # --- bloque "sensible": aqui esta el dilema del Laboratorio 2 -------
        - 0.34 * estrato
        + 0.034 * (edad - 38)
        + 0.95 * entrega_asistida
        + 0.20 * compras_farmacia_6m
        - 0.20 * busquedas_maternidad
        + 0.45 * (sexo == "M")
    )
    z = z + rng.normal(0, 0.60, n)
    p_churn = 1 / (1 + np.exp(-z))
    churn = rng.binomial(1, p_churn)

    # Score interno: dato INFERIDO por la empresa, no declarado por la persona.
    # Se construye a partir de un modelo anterior y desactualizado, con ruido:
    # es informativo, pero NO es una copia de la variable objetivo.
    score_riesgo_interno = np.clip(
        np.round(100 * (0.30 + 0.45 * p_churn + rng.normal(0, 0.16, n))).astype(int), 0, 100
    )

    segmento = pd.cut(
        score_riesgo_interno,
        bins=[-1, 35, 55, 75, 101],
        labels=["fiel", "estable", "en_riesgo", "critico"],
    ).astype(str)

    # --- consentimiento ------------------------------------------------------
    # Solo el programa de fidelizacion y el registro de cuenta tienen una
    # autorizacion de marketing mayoritaria. Los demas origenes, no.
    p_consent = np.select(
        [
            origen_dato == "programa_fidelizacion",
            origen_dato == "registro_cuenta",
            origen_dato == "facturacion",
            origen_dato == "entrega_domicilio",
        ],
        [0.93, 0.55, 0.18, 0.12],
        default=0.02,  # listas compradas y enriquecimiento web
    )
    consentimiento_marketing = rng.binomial(1, p_consent)

    fecha_autorizacion = pd.to_datetime("2026-08-31") - pd.to_timedelta(
        rng.integers(30, 1500, n), unit="D"
    )
    # Los origenes problematicos no tienen fecha de autorizacion: no existe
    # evidencia de que la persona haya autorizado nada.
    sin_evidencia = np.isin(origen_dato, ["lista_comprada_tercero", "enriquecimiento_web"])
    fecha_autorizacion = pd.Series(fecha_autorizacion).mask(sin_evidencia)

    # --- ensamblaje ----------------------------------------------------------
    df = pd.DataFrame({
        "cliente_id": cliente_id,
        "nombre": nombre_completo,
        "email": email,
        "telefono": telefono,
        "documento": documento,
        "fecha_nacimiento": fecha_nacimiento.date if hasattr(fecha_nacimiento, "date") else fecha_nacimiento,
        "edad": edad,
        "sexo": sexo,
        "ciudad": ciudad,
        "barrio": barrio,
        "direccion": direccion,
        "latitud": latitud,
        "longitud": longitud,
        "estrato": estrato,
        "ocupacion": ocupacion,
        "ingresos_mensuales": ingresos_mensuales,
        "dispositivo": dispositivo,
        "ip": ip,
        "pais_residencia": pais_residencia,
        "canal_adquisicion": canal_adquisicion,
        "origen_dato": origen_dato,
        "fecha_autorizacion": fecha_autorizacion,
        "consentimiento_marketing": consentimiento_marketing,
        "visitas_web": visitas_web,
        "productos_vistos": productos_vistos,
        "categoria_top": categoria_top,
        "compras_6m": compras_6m,
        "monto_compras": monto_compras,
        "fecha_ultima_compra": fecha_ultima_compra,
        # Nota: `dias_desde_ultima_compra` NO se exporta a proposito.
        # Es una variable derivada y los estudiantes la construyen en el
        # Laboratorio 2, en el bloque de feature engineering, para discutir
        # que inferencias nuevas estamos creando sobre las personas.
        "compras_farmacia_6m": compras_farmacia_6m,
        "entrega_asistida": entrega_asistida,
        "busquedas_maternidad": busquedas_maternidad,
        "score_riesgo_interno": score_riesgo_interno,
        "segmento": segmento,
        "churn": churn,
    })

    df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"]).dt.strftime("%Y-%m-%d")
    df["fecha_ultima_compra"] = pd.to_datetime(df["fecha_ultima_compra"]).dt.strftime("%Y-%m-%d")
    df["fecha_autorizacion"] = pd.to_datetime(df["fecha_autorizacion"]).dt.strftime("%Y-%m-%d")

    # --- imperfecciones deliberadas -----------------------------------------
    # (a) valores faltantes
    idx = rng.choice(n, size=int(0.09 * n), replace=False)
    df.loc[idx, "ingresos_mensuales"] = np.nan
    idx = rng.choice(n, size=int(0.05 * n), replace=False)
    df.loc[idx, "ocupacion"] = np.nan
    idx = rng.choice(n, size=int(0.04 * n), replace=False)
    df.loc[idx, "estrato"] = np.nan

    # (b) formato inconsistente en correos y telefonos (bloque de CALIDAD)
    idx = rng.choice(n, size=int(0.06 * n), replace=False)
    df.loc[idx, "email"] = df.loc[idx, "email"].str.upper()
    idx = rng.choice(n, size=int(0.05 * n), replace=False)
    df.loc[idx, "telefono"] = df.loc[idx, "telefono"].str.replace(
        r"^(\d{3})(\d{3})(\d{4})$", r"\1-\2-\3", regex=True
    )

    # (c) 12 duplicados exactos de cliente (mismo correo, cliente_id distinto)
    dup = df.sample(12, random_state=semilla).copy()
    dup["cliente_id"] = [f"DM-9{i:04d}" for i in range(1, 13)]
    df = pd.concat([df, dup], ignore_index=True)

    df = df.sample(frac=1, random_state=semilla).reset_index(drop=True)
    return df


# --------------------------------------------------------------------------
# 3. CLI
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Genera el dataset sintetico de DataMarket Analytics.")
    parser.add_argument("--n", type=int, default=1500, help="numero de clientes base (default: 1500)")
    parser.add_argument("--semilla", type=int, default=2026, help="semilla pseudoaleatoria (default: 2026)")
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "clientes_sinteticos.csv",
        help="ruta del CSV de salida",
    )
    args = parser.parse_args()

    df = generar(n=args.n, semilla=args.semilla)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.salida, index=False, encoding="utf-8")

    print(f"Archivo generado: {args.salida}")
    print(f"Filas: {len(df)}   Columnas: {df.shape[1]}")
    print(f"Tasa de churn: {df['churn'].mean():.3f}")
    print(f"Residentes en la UE: {df['pais_residencia'].isin(PAISES_UE).sum()}")
    print(f"Sin evidencia de autorizacion: {df['fecha_autorizacion'].isna().sum()}")


if __name__ == "__main__":
    main()
