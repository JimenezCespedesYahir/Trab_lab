# ================================================================
# extract_powerbi_semantic_model.py
# ================================================================
# OBJETIVO:
# Extraer y analizar el modelo semántico Power BI SISMED
#
# DASHBOARD:
# Consumo Histórico SISMED
#
# FUNCIONALIDADES:
# ✅ descarga conceptualschema
# ✅ guarda JSON crudo
# ✅ extrae tablas
# ✅ extrae columnas
# ✅ extrae medidas
# ✅ extrae relaciones
# ✅ detecta campos temporales
# ✅ detecta campos EE.SS
# ✅ detecta campos productos
# ✅ detecta campos consumo
# ✅ persistencia incremental
# ✅ auditoría científica
#
# ================================================================

from playwright.sync_api import sync_playwright
import requests
import pandas as pd
import json
import os
import re
import time
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

POWERBI_URL = (
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUt"
    "MGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVk"
    "YWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"
    "&pageName=ReportSection"
)

OUTPUT_DIR = "analytics/powerbi_semantic"

RAW_DIR = os.path.join(
    OUTPUT_DIR,
    "raw"
)

CSV_DIR = os.path.join(
    OUTPUT_DIR,
    "csv"
)

# ================================================================
# DIRECTORIOS
# ================================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().isoformat()

# ------------------------------------------------

def save_json(data, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# ------------------------------------------------

def save_text(data, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(data)

# ------------------------------------------------

def contains_keywords(text, keywords):

    if text is None:
        return False

    text = str(text).lower()

    return any(
        kw.lower() in text
        for kw in keywords
    )

# ================================================================
# VARIABLES
# ================================================================

conceptualschema_url = None

all_requests = []

all_tables = []
all_columns = []
all_measures = []
all_relationships = []

temporal_fields = []
eess_fields = []
product_fields = []
consumption_fields = []

# ================================================================
# KEYWORDS
# ================================================================

TEMPORAL_KEYWORDS = [
    "fecha",
    "mes",
    "anio",
    "año",
    "periodo",
    "year",
    "month",
    "date"
]

EESS_KEYWORDS = [
    "eess",
    "establecimiento",
    "ipress",
    "codigounico",
    "red",
    "microred",
    "institucion",
    "disa",
    "diris",
    "geresa"
]

PRODUCT_KEYWORDS = [
    "producto",
    "medicamento",
    "codigo_med",
    "codigo",
    "farmaceutico",
    "dispositivo",
    "sanitario"
]

CONSUMPTION_KEYWORDS = [
    "consumo",
    "cpma",
    "stock",
    "precio",
    "ventas",
    "intersan",
    "sis"
]

# ================================================================
# PLAYWRIGHT
# ================================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    # ============================================================
    # INTERCEPTAR REQUESTS
    # ============================================================

    def handle_request(request):

        global conceptualschema_url

        try:

            request_info = {
                "timestamp": now(),
                "method": request.method,
                "url": request.url
            }

            all_requests.append(request_info)

            if "conceptualschema" in request.url.lower():

                conceptualschema_url = request.url

                print("=" * 70)
                print("CONCEPTUAL SCHEMA DETECTADO")
                print("=" * 70)
                print(request.url)

        except Exception as e:

            print("ERROR REQUEST:", e)

    # ============================================================
    # EVENTO
    # ============================================================

    page.on(
        "request",
        handle_request
    )

    # ============================================================
    # ABRIR DASHBOARD
    # ============================================================

    print("=" * 70)
    print("ABRIENDO POWER BI")
    print("=" * 70)

    page.goto(
        POWERBI_URL,
        wait_until="networkidle",
        timeout=180000
    )

    time.sleep(25)

    # ============================================================
    # EXTRAER COOKIES
    # ============================================================

    cookies = context.cookies()

    session = requests.Session()

    for c in cookies:

        session.cookies.set(
            c["name"],
            c["value"]
        )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    # ============================================================
    # VALIDAR URL
    # ============================================================

    if conceptualschema_url is None:

        print("=" * 70)
        print("NO SE DETECTÓ conceptualschema")
        print("=" * 70)

        browser.close()
        exit()

    # ============================================================
    # DESCARGAR CONCEPTUAL SCHEMA
    # ============================================================

    print("=" * 70)
    print("DESCARGANDO CONCEPTUAL SCHEMA")
    print("=" * 70)

    response = session.get(
        conceptualschema_url,
        headers=headers,
        timeout=180
    )

    print("STATUS:", response.status_code)

    raw_schema_path = os.path.join(
        RAW_DIR,
        "raw_conceptualschema.json"
    )

    save_text(
        response.text,
        raw_schema_path
    )

    print("RAW JSON GUARDADO")

    # ============================================================
    # PARSE JSON
    # ============================================================

    try:

        schema = response.json()

    except Exception as e:

        print("ERROR JSON:", e)

        browser.close()
        exit()

    # ============================================================
    # EXPORT RAW
    # ============================================================

    parsed_schema_path = os.path.join(
        RAW_DIR,
        "parsed_conceptualschema.json"
    )

    save_json(
        schema,
        parsed_schema_path
    )

    # ============================================================
    # EXPLORACIÓN RECURSIVA
    # ============================================================

    def recursive_scan(obj, parent=""):

        if isinstance(obj, dict):

            for key, value in obj.items():

                full_key = f"{parent}.{key}"

                # --------------------------------------------
                # TABLAS
                # --------------------------------------------

                if key.lower() == "tables":

                    if isinstance(value, list):

                        for table in value:

                            table_name = table.get(
                                "name",
                                None
                            )

                            all_tables.append({
                                "table_name": table_name
                            })

                # --------------------------------------------
                # COLUMNAS
                # --------------------------------------------

                if key.lower() == "columns":

                    if isinstance(value, list):

                        for col in value:

                            col_name = col.get(
                                "name",
                                None
                            )

                            data_type = col.get(
                                "dataType",
                                None
                            )

                            all_columns.append({
                                "column_name": col_name,
                                "data_type": data_type,
                                "parent": parent
                            })

                            # ----------------------------
                            # TEMPORAL
                            # ----------------------------

                            if contains_keywords(
                                col_name,
                                TEMPORAL_KEYWORDS
                            ):

                                temporal_fields.append({
                                    "column_name": col_name,
                                    "parent": parent
                                })

                            # ----------------------------
                            # EE.SS
                            # ----------------------------

                            if contains_keywords(
                                col_name,
                                EESS_KEYWORDS
                            ):

                                eess_fields.append({
                                    "column_name": col_name,
                                    "parent": parent
                                })

                            # ----------------------------
                            # PRODUCTO
                            # ----------------------------

                            if contains_keywords(
                                col_name,
                                PRODUCT_KEYWORDS
                            ):

                                product_fields.append({
                                    "column_name": col_name,
                                    "parent": parent
                                })

                            # ----------------------------
                            # CONSUMO
                            # ----------------------------

                            if contains_keywords(
                                col_name,
                                CONSUMPTION_KEYWORDS
                            ):

                                consumption_fields.append({
                                    "column_name": col_name,
                                    "parent": parent
                                })

                # --------------------------------------------
                # MEDIDAS
                # --------------------------------------------

                if key.lower() == "measures":

                    if isinstance(value, list):

                        for measure in value:

                            measure_name = measure.get(
                                "name",
                                None
                            )

                            expression = measure.get(
                                "expression",
                                None
                            )

                            all_measures.append({
                                "measure_name": measure_name,
                                "expression": str(expression)
                            })

                # --------------------------------------------
                # RELACIONES
                # --------------------------------------------

                if key.lower() == "relationships":

                    if isinstance(value, list):

                        for rel in value:

                            all_relationships.append(rel)

                recursive_scan(
                    value,
                    full_key
                )

        elif isinstance(obj, list):

            for item in obj:

                recursive_scan(
                    item,
                    parent
                )

    # ============================================================
    # EJECUTAR SCAN
    # ============================================================

    print("=" * 70)
    print("ANALIZANDO MODELO SEMÁNTICO")
    print("=" * 70)

    recursive_scan(schema)

    # ============================================================
    # EXPORT CSV
    # ============================================================

    pd.DataFrame(all_tables).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "semantic_tables.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(all_columns).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "semantic_columns.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(all_measures).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "semantic_measures.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(all_relationships).to_csv(
        os.path.join(
            CSV_DIR,
            "semantic_relationships.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(temporal_fields).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "temporal_fields.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(eess_fields).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "eess_fields.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(product_fields).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "product_fields.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(consumption_fields).drop_duplicates().to_csv(
        os.path.join(
            CSV_DIR,
            "consumption_fields.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # RESUMEN FINAL
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("TABLAS:", len(all_tables))
    print("COLUMNAS:", len(all_columns))
    print("MEASURES:", len(all_measures))
    print("RELACIONES:", len(all_relationships))

    print("=" * 70)
    print("TEMPORAL FIELDS:", len(temporal_fields))
    print("EESS FIELDS:", len(eess_fields))
    print("PRODUCT FIELDS:", len(product_fields))
    print("CONSUMPTION FIELDS:", len(consumption_fields))

    print("=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print("raw_conceptualschema.json")
    print("parsed_conceptualschema.json")
    print("semantic_tables.csv")
    print("semantic_columns.csv")
    print("semantic_measures.csv")
    print("semantic_relationships.csv")
    print("temporal_fields.csv")
    print("eess_fields.csv")
    print("product_fields.csv")
    print("consumption_fields.csv")

    print("=" * 70)
    print("ANÁLISIS SEMÁNTICO COMPLETADO")
    print("=" * 70)

    time.sleep(10)

    browser.close()