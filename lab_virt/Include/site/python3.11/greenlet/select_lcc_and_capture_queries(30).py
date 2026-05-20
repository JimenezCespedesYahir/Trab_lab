# ================================================================
# select_lcc_and_capture_queries.py
# ================================================================
#
# OBJETIVO:
#
# Seleccionar automáticamente:
#
# "SALUD LUCIANO CASTILLO COLONNA"
#
# dentro del slicer:
#
# "Unidad ejecutora"
#
# y capturar:
#
# ✅ querydata BEFORE
# ✅ querydata AFTER
# ✅ WHERE clauses
# ✅ payloads replayables
# ✅ filtros territoriales
# ✅ columnas jurisdiccionales
# ✅ literals territoriales
#
# ================================================================
#
# PIPELINE CIENTÍFICO:
#
# Power BI
# → filtro territorial
# → propagación semántica
# → querydata
# → fact table
# → ETL territorial
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
    "analytics/lcc_capture"
)

PAYLOAD_DIR = os.path.join(
    OUTPUT_DIR,
    "payloads"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [

    OUTPUT_DIR,
    PAYLOAD_DIR,
    SCREENSHOT_DIR

]:
    os.makedirs(
        d,
        exist_ok=True
    )

TARGET_TEXT = (
    "SALUD LUCIANO CASTILLO COLONNA"
)

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
            timeout=1000
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

def extract_where(payload):

    if payload is None:
        return []

    return re.findall(

        r'"Where"\s*:\s*\[(.*?)\]',

        str(payload),

        re.DOTALL
    )

# ------------------------------------------------

def detect_territorial_terms(text):

    if text is None:
        return False

    text = str(text).lower()

    keywords = [

        "luciano",

        "castillo",

        "sullana",

        "piura",

        "unidad ejecutora",

        "red",

        "micro",

        "disa",

        "diresa"
    ]

    return any(
        k in text
        for k in keywords
    )

# ================================================================
# DATASETS
# ================================================================

captured_queries = []

detected_filters = []

summary = {

    "unidad_ejecutora_found": False,

    "dropdown_opened": False,

    "target_found": False,

    "target_clicked": False,

    "querydata_detected": False,

    "territorial_payload_detected": False,

    "where_detected": False,

    "payloads_captured": 0
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
    # REQUEST INTERCEPTION
    # ============================================================

    def handle_request(request):

        try:

            if "/querydata" not in request.url.lower():
                return

            payload = request.post_data

            where = extract_where(
                payload
            )

            territorial = detect_territorial_terms(
                payload
            )

            record = {

                "timestamp":
                    now(),

                "url":
                    request.url,

                "where_detected":
                    len(where) > 0,

                "where_count":
                    len(where),

                "territorial_detected":
                    territorial,

                "contains_lcc":
                    "LUCIANO"
                    in str(payload),

                "contains_sullana":
                    "SULLANA"
                    in str(payload),

                "contains_piura":
                    "PIURA"
                    in str(payload),

                "payload_preview":
                    str(payload)[:5000]
            }

            captured_queries.append(
                record
            )

            # ----------------------------------------------------
            # SAVE RAW
            # ----------------------------------------------------

            save_json(

                {

                    "metadata":
                        record,

                    "payload":
                        payload

                },

                os.path.join(

                    PAYLOAD_DIR,

                    f"query_{now()}.json"
                )
            )

            # ----------------------------------------------------
            # UPDATE SUMMARY
            # ----------------------------------------------------

            summary[
                "querydata_detected"
            ] = True

            summary[
                "payloads_captured"
            ] += 1

            if territorial:

                summary[
                    "territorial_payload_detected"
                ] = True

            if len(where) > 0:

                summary[
                    "where_detected"
                ] = True

            # ----------------------------------------------------
            # CONSOLE
            # ----------------------------------------------------

            print("=" * 70)
            print("QUERYDATA DETECTADA")
            print("=" * 70)

            print("WHERE:")
            print(len(where))

            print("=" * 70)

            print("TERRITORIAL:")
            print(territorial)

            print("=" * 70)

            print("LCC:")
            print(record["contains_lcc"])

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
    # OPEN POWER BI
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
    # SCREENSHOT INITIAL
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "initial.png"
        ),

        full_page=True
    )

    # ============================================================
    # FIND "UNIDAD EJECUTORA"
    # ============================================================

    print("=" * 70)
    print("BUSCANDO SLICER")
    print("=" * 70)

    slicers = page.locator(
        "[role='group']"
    )

    total_slicers = slicers.count()

    print(f"SLICERS: {total_slicers}")

    target_slicer = None

    for i in range(total_slicers):

        try:

            sl = slicers.nth(i)

            txt = safe_text(sl)

            aria = safe_attr(
                sl,
                "aria-label"
            )

            combined = f"{txt} {aria}"

            if (
                "unidad ejecutora"
                in combined.lower()
            ):

                target_slicer = sl

                summary[
                    "unidad_ejecutora_found"
                ] = True

                print("=" * 70)
                print("SLICER ENCONTRADO")
                print("=" * 70)

                print(combined)

                print("=" * 70)

                break

        except Exception:

            pass

    # ============================================================
    # VALIDATION
    # ============================================================

    if target_slicer is None:

        print("NO SLICER")

        browser.close()

        exit()

    # ============================================================
    # OPEN DROPDOWN
    # ============================================================

    print("=" * 70)
    print("ABRIENDO DROPDOWN")
    print("=" * 70)

    opened = False

    dropdown_selectors = [

        "button",

        "[aria-expanded]",

        "svg",

        "i"
    ]

    for selector in dropdown_selectors:

        try:

            els = target_slicer.locator(
                selector
            )

            count = els.count()

            for j in range(count):

                try:

                    el = els.nth(j)

                    if el.is_visible():

                        el.click()

                        opened = True

                        summary[
                            "dropdown_opened"
                        ] = True

                        time.sleep(5)

                        break

                except Exception:

                    pass

            if opened:
                break

        except Exception:

            pass

    # ============================================================
    # FALLBACK CLICK
    # ============================================================

    if not opened:

        try:

            target_slicer.click()

            summary[
                "dropdown_opened"
            ] = True

            time.sleep(5)

        except Exception as e:

            print(e)

    # ============================================================
    # SCREENSHOT OPEN
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "dropdown_opened.png"
        ),

        full_page=True
    )

    # ============================================================
    # FIND OPTIONS
    # ============================================================

    print("=" * 70)
    print("BUSCANDO OPCIONES")
    print("=" * 70)

    selectors = [

        "[role='option']",

        "span",

        "div",

        "li"
    ]

    clicked = False

    for selector in selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                400
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el).strip()

                    if len(txt) == 0:
                        continue

                    if TARGET_TEXT.lower() in txt.lower():

                        summary[
                            "target_found"
                        ] = True

                        print("=" * 70)
                        print("TARGET ENCONTRADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        detected_filters.append({

                            "selector":
                                selector,

                            "text":
                                txt
                        })

                        try:

                            el.click(
                                timeout=3000
                            )

                            clicked = True

                            summary[
                                "target_clicked"
                            ] = True

                            print("=" * 70)
                            print("TARGET CLICKED")
                            print("=" * 70)

                            time.sleep(20)

                            break

                        except Exception as e:

                            print(e)

                except Exception:

                    pass

            if clicked:
                break

        except Exception:

            pass

    # ============================================================
    # SCREENSHOT FINAL
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_selection.png"
        ),

        full_page=True
    )

    # ============================================================
    # EXPORT CSV
    # ============================================================

    pd.DataFrame(
        captured_queries
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "captured_queries.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_filters
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_filters.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # SAVE SUMMARY
    # ============================================================

    save_json(

        summary,

        os.path.join(
            OUTPUT_DIR,
            "summary.json"
        )
    )

    # ============================================================
    # FINAL SUMMARY
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    for k, v in summary.items():

        print(f"{k}: {v}")

    print("=" * 70)

    print("QUERIES:")
    print(len(captured_queries))

    print("=" * 70)

    print("FILTROS:")
    print(len(detected_filters))

    print("=" * 70)

    print("CAPTURA TERRITORIAL COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()