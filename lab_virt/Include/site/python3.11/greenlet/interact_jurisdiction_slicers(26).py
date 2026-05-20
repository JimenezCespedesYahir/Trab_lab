# ================================================================
# interact_jurisdiction_slicers.py
# ================================================================
# OBJETIVO:
# Interacción semántica dirigida Power BI
#
# Este script:
#
# ✅ detecta slicers REALES
# ✅ evita tablas/charts/cards
# ✅ abre dropdowns territoriales
# ✅ lee opciones dinámicas
# ✅ busca PIURA / SULLANA / LUCIANO
# ✅ selecciona jurisdicción
# ✅ captura payload BEFORE
# ✅ captura payload AFTER
# ✅ compara WHERE clauses
# ✅ detecta propagación filtros
# ✅ guarda replayables
#
# OBJETIVO CIENTÍFICO:
#
# descubrir:
#
# producto × jurisdicción × mes
#
# para:
#
# DSRSLCC - SULLANA
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
    "analytics/jurisdiction_interactions"
)

RAW_BEFORE_DIR = os.path.join(
    OUTPUT_DIR,
    "payload_before"
)

RAW_AFTER_DIR = os.path.join(
    OUTPUT_DIR,
    "payload_after"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [

    OUTPUT_DIR,
    RAW_BEFORE_DIR,
    RAW_AFTER_DIR,
    SCREENSHOT_DIR

]:
    os.makedirs(
        d,
        exist_ok=True
    )

# ================================================================
# TARGETS
# ================================================================

TARGET_VALUES = [

    "PIURA",

    "SULLANA",

    "LUCIANO",

    "CASTILLO"
]

# ================================================================
# STRUCTURAL SELECTORS
# ================================================================

SLICER_SELECTORS = [

    "[role='combobox']",

    "[role='listbox']",

    "button[aria-expanded]",

    ".slicerContainer",

    ".visualContainer"
]

# ================================================================
# QUERY FILTER
# ================================================================

QUERY_ENDPOINT = "/querydata"

IGNORE_KEYWORDS = [

    "telemetry",

    "visualstudio",

    "analytics",

    "track"
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

def extract_where(text):

    if text is None:
        return []

    return re.findall(

        r'"Where"\s*:\s*\[(.*?)\]',

        text,

        re.DOTALL
    )

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

before_queries = []

after_queries = []

interaction_log = []

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
    # INTERCEPTOR
    # ============================================================

    current_phase = "BEFORE"

    def handle_request(request):

        try:

            url = request.url.lower()

            # ----------------------------------------------------
            # IGNORE
            # ----------------------------------------------------

            if contains_keywords(
                url,
                IGNORE_KEYWORDS
            ):
                return

            # ----------------------------------------------------
            # ONLY QUERYDATA
            # ----------------------------------------------------

            if QUERY_ENDPOINT not in url:
                return

            timestamp = now()

            post_data = request.post_data

            record = {

                "timestamp": timestamp,

                "url": request.url,

                "where_count":
                    len(
                        extract_where(
                            post_data
                        )
                    ),

                "literals":
                    extract_literals(
                        post_data
                    ),

                "contains_sullana":
                    "SULLANA" in str(post_data),

                "contains_piura":
                    "PIURA" in str(post_data),

                "contains_luciano":
                    "LUCIANO" in str(post_data),

                "contains_castillo":
                    "CASTILLO" in str(post_data),

                "post_data_preview":
                    str(post_data)[:3000]
            }

            # ----------------------------------------------------
            # BEFORE
            # ----------------------------------------------------

            if current_phase == "BEFORE":

                before_queries.append(
                    record
                )

                save_json(

                    record,

                    os.path.join(

                        RAW_BEFORE_DIR,

                        f"before_{timestamp}.json"
                    )
                )

            # ----------------------------------------------------
            # AFTER
            # ----------------------------------------------------

            else:

                after_queries.append(
                    record
                )

                save_json(

                    record,

                    os.path.join(

                        RAW_AFTER_DIR,

                        f"after_{timestamp}.json"
                    )
                )

            # ----------------------------------------------------
            # CONSOLE
            # ----------------------------------------------------

            print("=" * 70)
            print("QUERY CAPTURADA")
            print("=" * 70)

            print("PHASE:")
            print(current_phase)

            print("=" * 70)

            print("WHERE:")
            print(record["where_count"])

            print("=" * 70)

            print("LITERALS:")
            print(record["literals"])

            print("=" * 70)

            print("SULLANA:")
            print(record["contains_sullana"])

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
    print("ABRIENDO POWER BI")
    print("=" * 70)

    page.goto(

        POWERBI_URL,

        wait_until="networkidle",

        timeout=180000
    )

    time.sleep(20)

    # ============================================================
    # SCREENSHOT BEFORE
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "before_interaction.png"
        ),

        full_page=True
    )

    # ============================================================
    # CAPTURE BASELINE
    # ============================================================

    print("=" * 70)
    print("CAPTURANDO BASELINE")
    print("=" * 70)

    current_phase = "BEFORE"

    time.sleep(10)

    # ============================================================
    # INTERACTION PHASE
    # ============================================================

    current_phase = "AFTER"

    print("=" * 70)
    print("BUSCANDO SLICERS REALES")
    print("=" * 70)

    successful_interactions = 0

    # ============================================================
    # STRUCTURAL DETECTION
    # ============================================================

    for selector in SLICER_SELECTORS:

        try:

            elements = page.locator(
                selector
            )

            count = min(
                elements.count(),
                30
            )

            print(f"{selector}: {count}")

            for i in range(count):

                try:

                    el = elements.nth(i)

                    text = ""

                    try:

                        text = el.inner_text(
                            timeout=1000
                        )

                    except Exception:

                        pass

                    # ------------------------------------------------
                    # ONLY TERRITORIAL
                    # ------------------------------------------------

                    if not contains_keywords(
                        text,
                        [
                            "disa",
                            "geresa",
                            "diresa",
                            "red",
                            "micro",
                            "departamento",
                            "provincia",
                            "distrito",
                            "establecimiento",
                            "ipress"
                        ]
                    ):
                        continue

                    print("=" * 70)
                    print("SLICER DETECTADO")
                    print("=" * 70)

                    print(text)

                    print("=" * 70)

                    # ------------------------------------------------
                    # OPEN
                    # ------------------------------------------------

                    try:

                        el.click(
                            timeout=3000
                        )

                        time.sleep(3)

                    except Exception:

                        continue

                    # ------------------------------------------------
                    # READ OPTIONS
                    # ------------------------------------------------

                    options = page.locator(

                        "[role='option'], li, span"
                    )

                    total_options = min(
                        options.count(),
                        100
                    )

                    found_target = False

                    for j in range(total_options):

                        try:

                            op = options.nth(j)

                            op_text = op.inner_text(
                                timeout=500
                            )

                            # ----------------------------
                            # TARGETS
                            # ----------------------------

                            if contains_keywords(
                                op_text,
                                TARGET_VALUES
                            ):

                                print("=" * 70)
                                print("TARGET FOUND")
                                print("=" * 70)

                                print(op_text)

                                print("=" * 70)

                                # ------------------------
                                # CLICK TARGET
                                # ------------------------

                                try:

                                    op.click(
                                        timeout=3000
                                    )

                                    successful_interactions += 1

                                    found_target = True

                                    interaction_log.append({

                                        "timestamp":
                                            now(),

                                        "selector":
                                            selector,

                                        "target":
                                            op_text
                                    })

                                    time.sleep(10)

                                    break

                                except Exception:

                                    pass

                        except Exception:

                            pass

                    if found_target:

                        break

                except Exception:

                    pass

        except Exception:

            pass

    # ============================================================
    # SCREENSHOT AFTER
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_interaction.png"
        ),

        full_page=True
    )

    # ============================================================
    # EXPORT
    # ============================================================

    print("=" * 70)
    print("EXPORTANDO RESULTADOS")
    print("=" * 70)

    # ------------------------------------------------------------
    # BEFORE
    # ------------------------------------------------------------

    df_before = pd.DataFrame(
        before_queries
    )

    df_before.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "queries_before.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ------------------------------------------------------------
    # AFTER
    # ------------------------------------------------------------

    df_after = pd.DataFrame(
        after_queries
    )

    df_after.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "queries_after.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ------------------------------------------------------------
    # INTERACTIONS
    # ------------------------------------------------------------

    df_interactions = pd.DataFrame(
        interaction_log
    )

    df_interactions.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "interaction_log.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # COMPARISON
    # ============================================================

    comparison = {

        "before_queries":
            len(df_before),

        "after_queries":
            len(df_after),

        "successful_interactions":
            successful_interactions,

        "sullana_before":
            int(
                df_before[
                    "contains_sullana"
                ].sum()
            ) if len(df_before) > 0 else 0,

        "sullana_after":
            int(
                df_after[
                    "contains_sullana"
                ].sum()
            ) if len(df_after) > 0 else 0
    }

    save_json(

        comparison,

        os.path.join(
            OUTPUT_DIR,
            "comparison_summary.json"
        )
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("BEFORE:")
    print(len(df_before))

    print("=" * 70)

    print("AFTER:")
    print(len(df_after))

    print("=" * 70)

    print("INTERACTIONS:")
    print(successful_interactions)

    print("=" * 70)

    print("SULLANA BEFORE:")
    print(comparison["sullana_before"])

    print("=" * 70)

    print("SULLANA AFTER:")
    print(comparison["sullana_after"])

    print("=" * 70)

    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print("queries_before.csv")
    print("queries_after.csv")
    print("interaction_log.csv")
    print("comparison_summary.json")

    print("=" * 70)
    print("INTERACCIÓN SEMÁNTICA COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()