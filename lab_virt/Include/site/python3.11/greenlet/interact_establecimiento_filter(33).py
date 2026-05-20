# ================================================================
# interact_establecimiento_filter.py
# ================================================================
#
# OBJETIVO:
#
# Interactuar EXCLUSIVAMENTE con el filtro:
#
#     Establecimiento
#         Todas
#
# para seleccionar:
#
#     SALUD LUCIANO CASTILLO COLONNA
#
# y capturar:
#
# ✅ querydata BEFORE
# ✅ querydata AFTER
# ✅ WHERE territorial real
# ✅ propagación jurisdiccional
# ✅ payload diferencial
#
# ================================================================
#
# ESTRATEGIA:
#
# Ya NO interactuar con visuales analíticos.
#
# Ahora:
#   SOLO controlar el filtro territorial real.
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
    "analytics/interact_establecimiento_filter"
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
        "establecimiento",
        "unidad ejecutora",
        "codpre",
        "ipress",
        "red",
        "micro"

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

    "establecimiento_detected": False,

    "filter_clicked": False,

    "dropdown_opened": False,

    "target_found": False,

    "target_clicked": False,

    "rerender_triggered": False,

    "payload_after_detected": False,

    "territorial_where_detected": False,

    "contains_lcc_after": False,

    "contains_sullana_after": False,

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

    phase = "BEFORE"

    # ============================================================
    # REQUEST INTERCEPTION
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
                    str(payload)[:6000]
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

                if row["contains_lcc"]:

                    summary[
                        "contains_lcc_after"
                    ] = True

                if row["contains_sullana"]:

                    summary[
                        "contains_sullana_after"
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
    # BASELINE
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
    # FIND ESTABLECIMIENTO
    # ============================================================

    print("=" * 70)
    print("BUSCANDO FILTRO ESTABLECIMIENTO")
    print("=" * 70)

    filter_found = False

    selectors = [

        "div",
        "span",

        "[role='button']",

        "[role='combobox']",

        "[aria-label]"
    ]

    target_filter = None

    for selector in selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                1200
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el).strip()

                    if len(txt) == 0:
                        continue

                    combined = txt.lower()

                    if (
                        "establecimiento"
                        in combined
                        and "todas"
                        in combined
                    ):

                        target_filter = el

                        filter_found = True

                        summary[
                            "establecimiento_detected"
                        ] = True

                        print("=" * 70)
                        print("FILTRO DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        break

                except Exception:
                    pass

            if filter_found:
                break

        except Exception:
            pass

    # ============================================================
    # CLICK FILTER
    # ============================================================

    if target_filter is not None:

        try:

            target_filter.scroll_into_view_if_needed()

            time.sleep(1)

            target_filter.click(
                force=True
            )

            summary[
                "filter_clicked"
            ] = True

            print("=" * 70)
            print("FILTRO CLICKED")
            print("=" * 70)

            time.sleep(5)

        except Exception as e:

            print(e)

    # ============================================================
    # SCREENSHOT DROPDOWN
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "dropdown_attempt.png"
        ),

        full_page=True
    )

    # ============================================================
    # AFTER PHASE
    # ============================================================

    phase = "AFTER"

    # ============================================================
    # SEARCH OPTIONS
    # ============================================================

    print("=" * 70)
    print("BUSCANDO OPCIONES")
    print("=" * 70)

    clicked = False

    option_selectors = [

        "span",
        "div",
        "li",

        "[role='option']",

        "[role='treeitem']",

        "[role='listbox']",

        "[role='menuitem']"
    ]

    for selector in option_selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                2500
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el).strip()

                    if len(txt) == 0:
                        continue

                    if (
                        TARGET_TEXT.lower()
                        in txt.lower()
                    ):

                        summary[
                            "target_found"
                        ] = True

                        summary[
                            "dropdown_opened"
                        ] = True

                        print("=" * 70)
                        print("TARGET DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        # ----------------------------
                        # CLICK TARGET
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
                                "rerender_triggered"
                            ] = True

                            print("=" * 70)
                            print("TARGET CLICKED")
                            print("=" * 70)

                            # ------------------------
                            # WAIT RERENDER
                            # ------------------------

                            time.sleep(30)

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
    # FINAL SCREENSHOT
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_selection.png"
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
    # EXPORT
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

    print("INTERACCIÓN ESTABLECIMIENTO COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()