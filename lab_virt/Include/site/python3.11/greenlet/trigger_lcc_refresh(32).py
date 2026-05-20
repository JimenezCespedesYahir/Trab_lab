# ================================================================
# trigger_lcc_refresh.py
# ================================================================
#
# OBJETIVO:
#
# Forzar refresh semántico territorial REAL
# en Power BI:
#
#     Unidad ejecutora
#         Todas
#             →
#     SALUD LUCIANO CASTILLO COLONNA
#
# y capturar:
#
# ✅ querydata BEFORE
# ✅ querydata AFTER
# ✅ WHERE territorial real
# ✅ literals territoriales
# ✅ propagación jurisdiccional
# ✅ payload refresh
#
# ================================================================
#
# DIFERENCIA CLAVE:
#
# Antes:
#   solo abríamos dashboard.
#
# Ahora:
#   provocaremos invalidación analítica REAL.
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

OUTPUT_DIR = "analytics/trigger_lcc_refresh"

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

TARGET_VALUE = (
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

def territorial_detected(payload):

    text = str(payload).lower()

    keys = [

        "luciano",
        "castillo",
        "sullana",
        "piura",
        "red",
        "micro",
        "codpre",
        "ipress",
        "unidad ejecutora"

    ]

    return any(
        k in text
        for k in keys
    )

# ================================================================
# DATASETS
# ================================================================

queries_before = []

queries_after = []

summary = {

    "dashboard_loaded": False,

    "filters_opened": False,

    "unidad_ejecutora_found": False,

    "target_found": False,

    "target_clicked": False,

    "refresh_triggered": False,

    "territorial_where_detected": False,

    "payload_after_detected": False,

    "payloads_before": 0,

    "payloads_after": 0
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
    # PHASE CONTROL
    # ============================================================

    phase = "BEFORE"

    # ============================================================
    # INTERCEPTOR
    # ============================================================

    def handle_request(request):

        global phase

        try:

            if "/querydata" not in request.url.lower():
                return

            payload = request.post_data

            where = extract_where(
                payload
            )

            row = {

                "timestamp":
                    now(),

                "phase":
                    phase,

                "where_count":
                    len(where),

                "territorial":
                    territorial_detected(
                        payload
                    ),

                "contains_lcc":
                    "LUCIANO"
                    in str(payload).upper(),

                "contains_sullana":
                    "SULLANA"
                    in str(payload).upper(),

                "contains_piura":
                    "PIURA"
                    in str(payload).upper(),

                "payload_preview":
                    str(payload)[:5000]
            }

            # ----------------------------------------------------
            # BEFORE
            # ----------------------------------------------------

            if phase == "BEFORE":

                queries_before.append(
                    row
                )

            # ----------------------------------------------------
            # AFTER
            # ----------------------------------------------------

            else:

                queries_after.append(
                    row
                )

                summary[
                    "payload_after_detected"
                ] = True

            # ----------------------------------------------------
            # SAVE RAW
            # ----------------------------------------------------

            save_json(

                {

                    "metadata":
                        row,

                    "payload":
                        payload

                },

                os.path.join(

                    PAYLOAD_DIR,

                    f"{phase.lower()}_{now()}.json"
                )
            )

            # ----------------------------------------------------
            # CONSOLE
            # ----------------------------------------------------

            print("=" * 70)
            print("QUERYDATA")
            print("=" * 70)

            print("PHASE:")
            print(phase)

            print("=" * 70)

            print("WHERE:")
            print(len(where))

            print("=" * 70)

            print("LCC:")
            print(row["contains_lcc"])

            print("=" * 70)

        except Exception as e:

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

    summary[
        "dashboard_loaded"
    ] = True

    time.sleep(25)

    # ============================================================
    # SCREENSHOT INITIAL
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "initial_dashboard.png"
        ),

        full_page=True
    )

    # ============================================================
    # CAPTURE BASELINE
    # ============================================================

    print("=" * 70)
    print("CAPTURANDO BASELINE")
    print("=" * 70)

    phase = "BEFORE"

    time.sleep(10)

    summary[
        "payloads_before"
    ] = len(queries_before)

    # ============================================================
    # OPEN FILTERS PANEL
    # ============================================================

    print("=" * 70)
    print("BUSCANDO FILTROS")
    print("=" * 70)

    filter_selectors = [

        "button",

        "[aria-label]",

        "[title]"

    ]

    opened = False

    for selector in filter_selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            count = min(
                els.count(),
                300
            )

            for i in range(count):

                try:

                    el = els.nth(i)

                    txt = safe_text(el)

                    aria = el.get_attribute(
                        "aria-label"
                    )

                    combined = (
                        f"{txt} {aria}"
                    ).lower()

                    if any(
                        k in combined
                        for k in [
                            "filtro",
                            "filter",
                            "unidad ejecutora"
                        ]
                    ):

                        print("=" * 70)
                        print("CONTROL DETECTADO")
                        print("=" * 70)

                        print(combined)

                        el.click()

                        summary[
                            "filters_opened"
                        ] = True

                        time.sleep(5)

                        opened = True

                        break

                except Exception:
                    pass

            if opened:
                break

        except Exception:
            pass

    # ============================================================
    # SCREENSHOT FILTERS
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "filters_opened.png"
        ),

        full_page=True
    )

    # ============================================================
    # FIND TARGET TEXT
    # ============================================================

    print("=" * 70)
    print("BUSCANDO TARGET")
    print("=" * 70)

    selectors = [

        "span",
        "div",
        "li",
        "[role='option']",
        "[role='treeitem']"

    ]

    clicked = False

    phase = "AFTER"

    for selector in selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                800
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el).strip()

                    if len(txt) == 0:
                        continue

                    if (
                        TARGET_VALUE.lower()
                        in txt.lower()
                    ):

                        summary[
                            "target_found"
                        ] = True

                        print("=" * 70)
                        print("TARGET DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        # ----------------------------
                        # FORCE REFRESH
                        # ----------------------------

                        try:

                            el.scroll_into_view_if_needed()

                            time.sleep(1)

                            el.click(
                                force=True,
                                timeout=5000
                            )

                            clicked = True

                            summary[
                                "target_clicked"
                            ] = True

                            summary[
                                "refresh_triggered"
                            ] = True

                            print("=" * 70)
                            print("CLICK EJECUTADO")
                            print("=" * 70)

                            # ------------------------
                            # WAIT RERENDER
                            # ------------------------

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

            "after_refresh.png"
        ),

        full_page=True
    )

    # ============================================================
    # ANALYSIS
    # ============================================================

    summary[
        "payloads_after"
    ] = len(queries_after)

    for q in queries_after:

        if (
            q["contains_lcc"]
            or q["contains_sullana"]
            or q["contains_piura"]
        ):

            summary[
                "territorial_where_detected"
            ] = True

    # ============================================================
    # EXPORT CSV
    # ============================================================

    pd.DataFrame(
        queries_before
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "queries_before.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        queries_after
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "queries_after.csv"
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
    print("SUMMARY")
    print("=" * 70)

    for k, v in summary.items():

        print(f"{k}: {v}")

    print("=" * 70)

    print("TRIGGER TERRITORIAL COMPLETADO")
    print("=" * 70)

    time.sleep(10)

    browser.close()