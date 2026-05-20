# ================================================================
# search_lcc_inside_combobox.py
# ================================================================
#
# OBJETIVO:
#
# Utilizar la búsqueda interna REAL del slicer Power BI
# para seleccionar:
#
#     SALUD LUCIANO CASTILLO COLONNA
#
# y capturar:
#
# ✅ propagación territorial
# ✅ payload AFTER
# ✅ WHERE real
# ✅ filtros jurisdiccionales
#
# ================================================================
#
# ESTRATEGIA:
#
# 1. Abrir slicer:
#       Establecimiento / Todas
#
# 2. Detectar:
#       .slicer-dropdown-menu
#
# 3. Encontrar:
#       input searchable REAL
#
# 4. Escribir:
#       SALUD LUCIANO CASTILLO COLONNA
#
# 5. Esperar filtrado dinámico
#
# 6. Detectar option renderizada
#
# 7. Click opción
#
# 8. Capturar querydata AFTER
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
    "analytics/search_lcc_inside_combobox"
)

PAYLOAD_DIR = os.path.join(
    OUTPUT_DIR,
    "payloads"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

HTML_DIR = os.path.join(
    OUTPUT_DIR,
    "html"
)

for d in [
    OUTPUT_DIR,
    PAYLOAD_DIR,
    SCREENSHOT_DIR,
    HTML_DIR
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

def save_html(content, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

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

def contains_territorial(payload):

    txt = str(payload).upper()

    keys = [

        "LUCIANO",
        "CASTILLO",
        "SULLANA",
        "PIURA",
        "ESTABLECIMIENTO",
        "UNIDAD EJECUTORA",
        "RED",
        "MICRO"
    ]

    return any(
        k in txt
        for k in keys
    )

# ================================================================
# DATASETS
# ================================================================

queries_before = []

queries_after = []

input_profiles = []

option_profiles = []

summary = {

    "dashboard_loaded": False,

    "filter_detected": False,

    "filter_clicked": False,

    "dropdown_detected": False,

    "searchable_input_detected": False,

    "search_text_written": False,

    "filtered_option_detected": False,

    "filtered_option_clicked": False,

    "rerender_detected": False,

    "payload_after_detected": False,

    "contains_lcc_after": False,

    "territorial_where_detected": False
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

                "contains_lcc":
                    "LUCIANO"
                    in str(payload).upper(),

                "contains_sullana":
                    "SULLANA"
                    in str(payload).upper(),

                "territorial":
                    contains_territorial(
                        payload
                    ),

                "payload_preview":
                    str(payload)[:7000]
            }

            if phase == "BEFORE":

                queries_before.append(
                    row
                )

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

    phase = "BEFORE"

    time.sleep(10)

    # ============================================================
    # FIND FILTER
    # ============================================================

    print("=" * 70)
    print("BUSCANDO FILTRO")
    print("=" * 70)

    target_filter = None

    selectors = [

        "div",
        "span",

        "[role='button']",

        "[role='combobox']"
    ]

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

                    txt = safe_text(el)

                    if (
                        "establecimiento"
                        in txt.lower()
                        and "todas"
                        in txt.lower()
                    ):

                        target_filter = el

                        summary[
                            "filter_detected"
                        ] = True

                        print("=" * 70)
                        print("FILTRO DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        break

                except Exception:
                    pass

            if target_filter is not None:
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
            print("FILTER CLICKED")
            print("=" * 70)

            time.sleep(5)

        except Exception as e:

            print(e)

    # ============================================================
    # SEARCH DROPDOWN
    # ============================================================

    print("=" * 70)
    print("SEARCHING DROPDOWN")
    print("=" * 70)

    dropdown = None

    dropdown_selectors = [

        ".slicer-dropdown-menu",

        "[role='listbox']"
    ]

    for selector in dropdown_selectors:

        try:

            els = page.locator(
                selector
            )

            count = els.count()

            print(f"{selector}: {count}")

            for i in range(count):

                try:

                    el = els.nth(i)

                    if not el.is_visible():
                        continue

                    dropdown = el

                    summary[
                        "dropdown_detected"
                    ] = True

                    txt = safe_text(el)

                    print("=" * 70)
                    print("DROPDOWN DETECTADO")
                    print("=" * 70)

                    print(txt[:3000])

                    print("=" * 70)

                    html = el.evaluate(
                        "e => e.outerHTML"
                    )

                    save_html(

                        html,

                        os.path.join(

                            HTML_DIR,

                            "dropdown.html"
                        )
                    )

                    break

                except Exception:
                    pass

            if dropdown is not None:
                break

        except Exception:
            pass

    # ============================================================
    # SEARCH INPUT
    # ============================================================

    print("=" * 70)
    print("SEARCHING INPUT")
    print("=" * 70)

    search_input = None

    input_selectors = [

        "input",

        "[role='textbox']",

        "[contenteditable='true']"
    ]

    for selector in input_selectors:

        try:

            els = page.locator(
                selector
            )

            count = min(
                els.count(),
                100
            )

            print(f"{selector}: {count}")

            for i in range(count):

                try:

                    el = els.nth(i)

                    visible = el.is_visible()

                    enabled = el.is_enabled()

                    editable = el.is_editable()

                    profile = {

                        "selector":
                            selector,

                        "visible":
                            visible,

                        "enabled":
                            enabled,

                        "editable":
                            editable,

                        "role":
                            safe_attr(
                                el,
                                "role"
                            ),

                        "aria_label":
                            safe_attr(
                                el,
                                "aria-label"
                            ),

                        "placeholder":
                            safe_attr(
                                el,
                                "placeholder"
                            ),

                        "class":
                            safe_attr(
                                el,
                                "class"
                            )
                    }

                    input_profiles.append(
                        profile
                    )

                    if (
                        visible
                        and enabled
                        and editable
                    ):

                        search_input = el

                        summary[
                            "searchable_input_detected"
                        ] = True

                        print("=" * 70)
                        print("SEARCHABLE INPUT")
                        print("=" * 70)

                        print(profile)

                        print("=" * 70)

                        break

                except Exception:
                    pass

            if search_input is not None:
                break

        except Exception:
            pass

    # ============================================================
    # WRITE SEARCH
    # ============================================================

    if search_input is not None:

        try:

            phase = "AFTER"

            search_input.click()

            time.sleep(1)

            search_input.fill(
                TARGET_TEXT
            )

            summary[
                "search_text_written"
            ] = True

            print("=" * 70)
            print("SEARCH TEXT WRITTEN")
            print("=" * 70)

            time.sleep(8)

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
    # SEARCH FILTERED OPTION
    # ============================================================

    print("=" * 70)
    print("SEARCHING FILTERED OPTION")
    print("=" * 70)

    clicked = False

    option_selectors = [

        "[role='option']",

        "label",

        "li",

        "div",

        "span"
    ]

    for selector in option_selectors:

        try:

            els = page.locator(
                f"{selector}:visible"
            )

            total = min(
                els.count(),
                1500
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = els.nth(i)

                    txt = safe_text(el)

                    if len(txt.strip()) == 0:
                        continue

                    option_profiles.append({

                        "selector":
                            selector,

                        "text":
                            txt,

                        "role":
                            safe_attr(
                                el,
                                "role"
                            ),

                        "aria_label":
                            safe_attr(
                                el,
                                "aria-label"
                            )
                    })

                    if (
                        TARGET_TEXT.lower()
                        in txt.lower()
                    ):

                        summary[
                            "filtered_option_detected"
                        ] = True

                        print("=" * 70)
                        print("OPTION DETECTADA")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        el.scroll_into_view_if_needed()

                        time.sleep(1)

                        el.click(
                            force=True
                        )

                        clicked = True

                        summary[
                            "filtered_option_clicked"
                        ] = True

                        summary[
                            "rerender_detected"
                        ] = True

                        print("=" * 70)
                        print("OPTION CLICKED")
                        print("=" * 70)

                        time.sleep(30)

                        break

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

    for q in queries_after:

        if q["territorial"]:

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

    pd.DataFrame(
        input_profiles
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "input_profiles.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        option_profiles
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "option_profiles.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    save_json(

        summary,

        os.path.join(
            OUTPUT_DIR,
            "summary.json"
        )
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for k, v in summary.items():

        print(f"{k}: {v}")

    print("=" * 70)

    print("SEARCH LCC COMPLETADO")
    print("=" * 70)

    time.sleep(10)

    browser.close()