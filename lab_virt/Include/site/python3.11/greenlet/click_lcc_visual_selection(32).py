# ================================================================
# click_lcc_visual_selection.py
# ================================================================
#
# OBJETIVO:
#
# Interactuar directamente con el visual:
#
#     "tabla det. 4 (ue)"
#
# para seleccionar:
#
#     "SALUD LUCIANO CASTILLO COLONNA"
#
# y capturar:
#
# ✅ querydata AFTER
# ✅ WHERE territorial real
# ✅ propagación jurisdiccional
# ✅ payload territorial
# ✅ crossfilter refresh
#
# ================================================================
#
# DIFERENCIA CRÍTICA:
#
# Antes:
#   buscábamos slicers.
#
# Ahora:
#   interactuamos directamente con
#   visual crossfilter territorial.
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
    "analytics/click_lcc_visual"
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

VISUAL_NAME = (
    "tabla det. 4 (ue)"
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

    "visual_detected": False,

    "visual_clicked": False,

    "target_detected": False,

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
    # INTERCEPT REQUESTS
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

            "initial.png"
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
    # SEARCH VISUAL
    # ============================================================

    print("=" * 70)
    print("BUSCANDO VISUAL UE")
    print("=" * 70)

    visual_found = False

    selectors = [

        "div",
        "span",

        "[role='grid']",

        "[role='table']",

        "[role='row']",

        "[role='cell']"
    ]

    target_visual = None

    for selector in selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                1000
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el).strip()

                    if len(txt) == 0:
                        continue

                    if (
                        VISUAL_NAME.lower()
                        in txt.lower()
                    ):

                        target_visual = el

                        visual_found = True

                        summary[
                            "visual_detected"
                        ] = True

                        print("=" * 70)
                        print("VISUAL DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        break

                except Exception:
                    pass

            if visual_found:
                break

        except Exception:
            pass

    # ============================================================
    # CLICK VISUAL
    # ============================================================

    if target_visual is not None:

        try:

            target_visual.scroll_into_view_if_needed()

            time.sleep(1)

            target_visual.click(
                force=True
            )

            summary[
                "visual_clicked"
            ] = True

            print("=" * 70)
            print("VISUAL CLICKED")
            print("=" * 70)

            time.sleep(5)

        except Exception as e:

            print(e)

    # ============================================================
    # AFTER PHASE
    # ============================================================

    phase = "AFTER"

    # ============================================================
    # FIND TARGET
    # ============================================================

    print("=" * 70)
    print("BUSCANDO LCC")
    print("=" * 70)

    clicked = False

    target_selectors = [

        "span",

        "div",

        "td",

        "[role='cell']",

        "[role='row']"
    ]

    for selector in target_selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                2000
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
                            "target_detected"
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

                            time.sleep(25)

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

            "after_click.png"
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

    print("CLICK VISUAL COMPLETADO")
    print("=" * 70)

    time.sleep(10)

    browser.close()