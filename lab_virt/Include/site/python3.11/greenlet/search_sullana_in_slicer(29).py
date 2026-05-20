# ================================================================
# search_sullana_in_slicer.py
# ================================================================
# OBJETIVO:
#
# Interacción semántica territorial Power BI.
#
# Este script:
#
# ✅ encuentra slicer real
# ✅ detecta input búsqueda
# ✅ escribe "SULLANA"
# ✅ espera rerender dinámico
# ✅ captura nuevas opciones
# ✅ detecta:
#       - SULLANA
#       - LUCIANO
#       - CASTILLO
#       - DSRSLCC
# ✅ intenta click selección
# ✅ intercepta querydata BEFORE
# ✅ intercepta querydata AFTER
# ✅ compara payloads
# ✅ detecta WHERE clauses
# ✅ detecta filtros territoriales
# ✅ exporta replayables
#
# OBJETIVO CIENTÍFICO:
#
# descubrir:
#
# cómo Power BI segmenta territorialmente
# el consumo farmacéutico.
#
# ================================================================

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import time
import re
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
    "analytics/sullana_search"
)

PAYLOAD_BEFORE_DIR = os.path.join(
    OUTPUT_DIR,
    "before"
)

PAYLOAD_AFTER_DIR = os.path.join(
    OUTPUT_DIR,
    "after"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [

    OUTPUT_DIR,
    PAYLOAD_BEFORE_DIR,
    PAYLOAD_AFTER_DIR,
    SCREENSHOT_DIR

]:
    os.makedirs(
        d,
        exist_ok=True
    )

# ================================================================
# TARGETS
# ================================================================

SEARCH_TERMS = [

    "SULLANA",

    "LUCIANO",

    "CASTILLO",

    "DSRSLCC"
]

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

# ------------------------------------------------

def safe_text(locator):

    try:

        return locator.inner_text(
            timeout=500
        )

    except Exception:

        return ""

# ------------------------------------------------

def safe_attr(locator, attr):

    try:

        return locator.get_attribute(attr)

    except Exception:

        return None

# ------------------------------------------------

def contains_targets(text):

    if text is None:
        return False

    text = str(text).lower()

    targets = [

        "sullana",

        "luciano",

        "castillo",

        "dsrslcc"
    ]

    return any(
        t in text
        for t in targets
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

# ================================================================
# DATASETS
# ================================================================

before_queries = []

after_queries = []

detected_options = []

interaction_summary = {

    "slicer_found": False,

    "search_input_found": False,

    "search_executed": False,

    "target_detected": False,

    "target_clicked": False,

    "query_changed": False,

    "where_after": 0,

    "sullana_in_payload": False
}

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

    phase = "BEFORE"

    def handle_request(request):

        try:

            url = request.url.lower()

            if "/querydata" not in url:
                return

            post_data = request.post_data

            record = {

                "timestamp":
                    now(),

                "phase":
                    phase,

                "url":
                    request.url,

                "where_count":
                    len(
                        extract_where(
                            post_data
                        )
                    ),

                "contains_sullana":
                    "SULLANA"
                    in str(post_data),

                "contains_luciano":
                    "LUCIANO"
                    in str(post_data),

                "contains_castillo":
                    "CASTILLO"
                    in str(post_data),

                "contains_dsrslcc":
                    "DSRSLCC"
                    in str(post_data),

                "preview":
                    str(post_data)[:4000]
            }

            # ----------------------------------------------------
            # SAVE
            # ----------------------------------------------------

            if phase == "BEFORE":

                before_queries.append(
                    record
                )

                save_json(

                    record,

                    os.path.join(

                        PAYLOAD_BEFORE_DIR,

                        f"before_{now()}.json"
                    )
                )

            else:

                after_queries.append(
                    record
                )

                save_json(

                    record,

                    os.path.join(

                        PAYLOAD_AFTER_DIR,

                        f"after_{now()}.json"
                    )
                )

            # ----------------------------------------------------
            # CONSOLE
            # ----------------------------------------------------

            print("=" * 70)
            print("QUERYDATA DETECTADA")
            print("=" * 70)

            print("PHASE:")
            print(phase)

            print("=" * 70)

            print("WHERE:")
            print(record["where_count"])

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
    # OPEN
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
    # BEFORE BASELINE
    # ============================================================

    phase = "BEFORE"

    print("=" * 70)
    print("CAPTURANDO BASELINE")
    print("=" * 70)

    time.sleep(10)

    # ============================================================
    # FIND SLICER
    # ============================================================

    print("=" * 70)
    print("BUSCANDO SLICER")
    print("=" * 70)

    slicer = None

    groups = page.locator(
        "[role='group']"
    )

    total_groups = groups.count()

    print(f"GROUPS: {total_groups}")

    for i in range(total_groups):

        try:

            g = groups.nth(i)

            aria = safe_attr(
                g,
                "aria-label"
            )

            if aria:

                if (
                    "establecimiento"
                    in aria.lower()
                ):

                    slicer = g

                    interaction_summary[
                        "slicer_found"
                    ] = True

                    print("=" * 70)
                    print("SLICER ENCONTRADO")
                    print("=" * 70)

                    print(aria)

                    print("=" * 70)

                    break

        except Exception:

            pass

    # ============================================================
    # VALIDATION
    # ============================================================

    if slicer is None:

        print("NO SLICER")

        browser.close()

        exit()

    # ============================================================
    # OPEN SLICER
    # ============================================================

    print("=" * 70)
    print("ABRIENDO SLICER")
    print("=" * 70)

    try:

        slicer.click()

        time.sleep(5)

    except Exception as e:

        print(e)

    # ============================================================
    # SCREENSHOT
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "slicer_open.png"
        ),

        full_page=True
    )

    # ============================================================
    # SEARCH INPUT
    # ============================================================

    print("=" * 70)
    print("BUSCANDO INPUT")
    print("=" * 70)

    inputs = page.locator(
        "input"
    )

    total_inputs = inputs.count()

    print(f"INPUTS: {total_inputs}")

    target_input = None

    for i in range(total_inputs):

        try:

            inp = inputs.nth(i)

            placeholder = safe_attr(
                inp,
                "placeholder"
            )

            aria = safe_attr(
                inp,
                "aria-label"
            )

            print("=" * 70)
            print(f"INPUT {i}")

            print("PLACEHOLDER:")
            print(placeholder)

            print("ARIA:")
            print(aria)

            # ----------------------------------------------------
            # SELECT INPUT
            # ----------------------------------------------------

            target_input = inp

            interaction_summary[
                "search_input_found"
            ] = True

            break

        except Exception:

            pass

    # ============================================================
    # SEARCH
    # ============================================================

    if target_input is not None:

        print("=" * 70)
        print("ESCRIBIENDO SULLANA")
        print("=" * 70)

        phase = "AFTER"

        try:

            target_input.fill(
                "SULLANA"
            )

            interaction_summary[
                "search_executed"
            ] = True

            time.sleep(10)

        except Exception as e:

            print(e)

    # ============================================================
    # SCREENSHOT SEARCH
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_search.png"
        ),

        full_page=True
    )

    # ============================================================
    # DETECT NEW OPTIONS
    # ============================================================

    print("=" * 70)
    print("BUSCANDO OPCIONES NUEVAS")
    print("=" * 70)

    selectors = [

        "[role='option']",

        "span",

        "div",

        "li"
    ]

    for selector in selectors:

        try:

            els = page.locator(
                selector
            )

            total = min(
                els.count(),
                300
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el).strip()

                    if len(txt) == 0:
                        continue

                    contains = contains_targets(
                        txt
                    )

                    row = {

                        "selector":
                            selector,

                        "text":
                            txt,

                        "contains_target":
                            contains
                    }

                    detected_options.append(
                        row
                    )

                    # ------------------------------------------------
                    # TARGET DETECTED
                    # ------------------------------------------------

                    if contains:

                        interaction_summary[
                            "target_detected"
                        ] = True

                        print("=" * 70)
                        print("TARGET DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        # --------------------------------------------
                        # TRY CLICK
                        # --------------------------------------------

                        try:

                            el.click(
                                timeout=2000
                            )

                            interaction_summary[
                                "target_clicked"
                            ] = True

                            time.sleep(10)

                            page.screenshot(

                                path=os.path.join(

                                    SCREENSHOT_DIR,

                                    "after_click.png"
                                ),

                                full_page=True
                            )

                            break

                        except Exception:

                            pass

                except Exception:

                    pass

        except Exception:

            pass

    # ============================================================
    # EXPORT OPTIONS
    # ============================================================

    df_options = pd.DataFrame(
        detected_options
    )

    df_options.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_options.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # QUERY COMPARISON
    # ============================================================

    df_before = pd.DataFrame(
        before_queries
    )

    df_after = pd.DataFrame(
        after_queries
    )

    df_before.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "queries_before.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    df_after.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "queries_after.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # ANALYSIS
    # ============================================================

    if len(df_after) > 0:

        interaction_summary[
            "query_changed"
        ] = True

        interaction_summary[
            "where_after"
        ] = int(
            df_after["where_count"].max()
        )

        interaction_summary[
            "sullana_in_payload"
        ] = bool(
            df_after[
                "contains_sullana"
            ].sum()
        )

    # ============================================================
    # SAVE SUMMARY
    # ============================================================

    save_json(

        interaction_summary,

        os.path.join(
            OUTPUT_DIR,
            "interaction_summary.json"
        )
    )

    # ============================================================
    # FINAL SUMMARY
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    for k, v in interaction_summary.items():

        print(f"{k}: {v}")

    print("=" * 70)

    print("QUERIES BEFORE:")
    print(len(df_before))

    print("=" * 70)

    print("QUERIES AFTER:")
    print(len(df_after))

    print("=" * 70)

    print("OPCIONES:")
    print(len(df_options))

    print("=" * 70)

    print("BÚSQUEDA TERRITORIAL COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()