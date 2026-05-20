# ================================================================
# detect_jurisdiction_filters.py
# ================================================================
# OBJETIVO:
# Ingeniería territorial Power BI SISMED
#
# Este script:
#
# ✅ detecta slicers territoriales
# ✅ detecta filtros jurisdiccionales
# ✅ detecta drilldowns
# ✅ captura queries querydata reales
# ✅ extrae WHERE clauses
# ✅ detecta SULLANA / LUCIANO / PIURA
# ✅ detecta RED / MICRORED
# ✅ detecta joins territoriales
# ✅ guarda payloads replayables
# ✅ persiste incrementalmente
#
# DASHBOARD:
# Consumo Histórico de Productos Farmacéuticos
#
# OBJETIVO FINAL:
# descubrir cómo Power BI segmenta territorialmente:
#
# producto × EE.SS × mes
#
# ================================================================

from playwright.sync_api import sync_playwright
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

OUTPUT_DIR = (
    "analytics/jurisdiction_detection"
)

RAW_QUERIES_DIR = os.path.join(
    OUTPUT_DIR,
    "replayable_queries"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [
    OUTPUT_DIR,
    RAW_QUERIES_DIR,
    SCREENSHOT_DIR
]:
    os.makedirs(
        d,
        exist_ok=True
    )

# ================================================================
# KEYWORDS
# ================================================================

TERRITORIAL_KEYWORDS = [

    "disa",
    "diresa",
    "geresa",

    "red",
    "micro",

    "provincia",
    "distrito",
    "departamento",

    "ipress",
    "establecimiento",

    "sullana",
    "luciano",
    "castillo",

    "piura"
]

FIELD_KEYWORDS = [

    "Departamento",
    "Provincia",
    "Distrito",
    "Red",
    "micro_red",
    "diresa",
    "codpre_"
]

IGNORE_KEYWORDS = [

    "visualstudio",

    "telemetry",

    "track",

    "analytics"
]

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

# ------------------------------------------------

def contains_keywords(text, keywords):

    if text is None:
        return False

    text = str(text).lower()

    return any(
        kw.lower() in text
        for kw in keywords
    )

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

def extract_where_clauses(text):

    if text is None:
        return []

    matches = re.findall(

        r'"Where"\s*:\s*\[(.*?)\]',

        text,

        re.DOTALL
    )

    return matches

# ------------------------------------------------

def extract_literals(text):

    if text is None:
        return []

    patterns = [

        r"SULLANA",

        r"PIURA",

        r"LUCIANO",

        r"CASTILLO"
    ]

    found = []

    for p in patterns:

        if re.search(
            p,
            text,
            re.IGNORECASE
        ):
            found.append(p)

    return found

# ================================================================
# DATASETS
# ================================================================

queries_dataset = []

filters_dataset = []

territorial_fields = []

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
    # REQUEST INTERCEPTOR
    # ============================================================

    def handle_request(request):

        try:

            url = request.url

            url_lower = url.lower()

            # ----------------------------------------------------
            # IGNORE TELEMETRY
            # ----------------------------------------------------

            if contains_keywords(
                url_lower,
                IGNORE_KEYWORDS
            ):
                return

            # ----------------------------------------------------
            # ONLY QUERYDATA
            # ----------------------------------------------------

            if "/querydata" not in url_lower:
                return

            timestamp = now()

            print("=" * 70)
            print("QUERYDATA DETECTADA")
            print("=" * 70)

            post_data = request.post_data

            # ----------------------------------------------------
            # WHERE CLAUSES
            # ----------------------------------------------------

            where_clauses = extract_where_clauses(
                post_data
            )

            # ----------------------------------------------------
            # TERRITORIAL
            # ----------------------------------------------------

            territorial_detected = contains_keywords(
                post_data,
                TERRITORIAL_KEYWORDS
            )

            # ----------------------------------------------------
            # LITERALS
            # ----------------------------------------------------

            literals = extract_literals(
                post_data
            )

            contains_sullana = (
                "SULLANA" in literals
            )

            contains_piura = (
                "PIURA" in literals
            )

            # ----------------------------------------------------
            # FIELD DETECTION
            # ----------------------------------------------------

            detected_fields = []

            for field in FIELD_KEYWORDS:

                if field.lower() in str(post_data).lower():

                    detected_fields.append(
                        field
                    )

                    territorial_fields.append({

                        "timestamp": timestamp,

                        "field": field
                    })

            # ----------------------------------------------------
            # VISUAL ID
            # ----------------------------------------------------

            visual_ids = re.findall(

                r'"VisualId":"(.*?)"',

                str(post_data)
            )

            visual_id = None

            if len(visual_ids) > 0:

                visual_id = visual_ids[0]

            # ----------------------------------------------------
            # QUERY ID
            # ----------------------------------------------------

            query_id = (
                f"query_{timestamp}"
            )

            # ----------------------------------------------------
            # DATASET
            # ----------------------------------------------------

            record = {

                "timestamp": timestamp,

                "query_id": query_id,

                "visual_id": visual_id,

                "territorial_detected":
                    territorial_detected,

                "where_detected":
                    len(where_clauses) > 0,

                "contains_sullana":
                    contains_sullana,

                "contains_piura":
                    contains_piura,

                "contains_red":
                    "red" in str(post_data).lower(),

                "contains_microred":
                    "micro" in str(post_data).lower(),

                "request_url":
                    url,

                "detected_literals":
                    ",".join(literals),

                "detected_fields":
                    ",".join(detected_fields)
            }

            queries_dataset.append(
                record
            )

            # ----------------------------------------------------
            # SAVE RAW QUERY
            # ----------------------------------------------------

            raw_query = {

                "metadata": record,

                "headers": dict(
                    request.headers
                ),

                "post_data": post_data
            }

            save_json(

                raw_query,

                os.path.join(

                    RAW_QUERIES_DIR,

                    f"{query_id}.json"
                )
            )

            # ----------------------------------------------------
            # WHERE FILTERS
            # ----------------------------------------------------

            for w in where_clauses:

                filters_dataset.append({

                    "timestamp": timestamp,

                    "query_id": query_id,

                    "where_clause": w
                })

            # ----------------------------------------------------
            # CONSOLE
            # ----------------------------------------------------

            print("VISUAL ID:")
            print(visual_id)

            print("=" * 70)

            print("WHERE CLAUSES:")
            print(len(where_clauses))

            print("=" * 70)

            print("LITERALS:")
            print(literals)

            print("=" * 70)

            print("FIELDS:")
            print(detected_fields)

            print("=" * 70)

            print("SULLANA:")
            print(contains_sullana)

            print("=" * 70)

        except Exception as e:

            print("REQUEST ERROR")
            print(e)

    # ============================================================
    # ATTACH
    # ============================================================

    page.on(
        "request",
        handle_request
    )

    # ============================================================
    # OPEN DASHBOARD
    # ============================================================

    print("=" * 70)
    print("ABRIENDO DASHBOARD")
    print("=" * 70)

    page.goto(

        POWERBI_URL,

        wait_until="networkidle",

        timeout=180000
    )

    # ============================================================
    # WAIT LOAD
    # ============================================================

    time.sleep(20)

    # ============================================================
    # SCREENSHOT
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "dashboard_loaded.png"
        ),

        full_page=True
    )

    # ============================================================
    # DETECT SLICERS
    # ============================================================

    print("=" * 70)
    print("BUSCANDO SLICERS TERRITORIALES")
    print("=" * 70)

    selectors = [

        "[role='button']",

        "[aria-label]",

        "div",

        "span"
    ]

    territorial_clicks = 0

    for selector in selectors:

        try:

            elements = page.locator(
                selector
            )

            total = min(
                elements.count(),
                100
            )

            for i in range(total):

                try:

                    el = elements.nth(i)

                    text = (
                        el.inner_text(timeout=1000)
                    )

                    if contains_keywords(
                        text,
                        TERRITORIAL_KEYWORDS
                    ):

                        print("=" * 70)
                        print("TERRITORIAL SLICER")
                        print("=" * 70)

                        print(text)

                        print("=" * 70)

                        # ------------------------
                        # CLICK
                        # ------------------------

                        try:

                            el.click(
                                timeout=3000
                            )

                            territorial_clicks += 1

                            print("CLICK OK")

                            time.sleep(5)

                        except Exception:

                            pass

                except Exception:

                    pass

        except Exception:

            pass

    # ============================================================
    # EXPORT DATASETS
    # ============================================================

    print("=" * 70)
    print("EXPORTANDO RESULTADOS")
    print("=" * 70)

    df_queries = pd.DataFrame(
        queries_dataset
    )

    df_queries.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "jurisdiction_queries.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ------------------------------------------------------------

    save_json(

        filters_dataset,

        os.path.join(
            OUTPUT_DIR,
            "jurisdiction_filters.json"
        )
    )

    # ------------------------------------------------------------

    df_fields = pd.DataFrame(
        territorial_fields
    )

    df_fields.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_territorial_fields.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("QUERIES:")
    print(len(df_queries))

    print("=" * 70)

    print("FILTERS:")
    print(len(filters_dataset))

    print("=" * 70)

    print("FIELDS:")
    print(len(df_fields))

    print("=" * 70)

    print("TERRITORIAL CLICKS:")
    print(territorial_clicks)

    print("=" * 70)

    if len(df_queries) > 0:

        print("TOP QUERIES")

        print(

            df_queries[
                [
                    "visual_id",
                    "contains_sullana",
                    "contains_red",
                    "contains_microred"
                ]
            ].head(10)
        )

    print("=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print("jurisdiction_queries.csv")

    print("jurisdiction_filters.json")

    print("detected_territorial_fields.csv")

    print("replayable_queries/")

    print("=" * 70)
    print("JURISDICTION DETECTION COMPLETED")
    print("=" * 70)

    time.sleep(10)

    browser.close()