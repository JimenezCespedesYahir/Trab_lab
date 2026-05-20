# ================================================================
# inspect_slicer_options.py
# ================================================================
# OBJETIVO:
#
# Ingeniería inversa profunda del slicer territorial.
#
# Este script:
#
# ✅ encuentra slicer real
# ✅ aria-label = Establecimiento
# ✅ abre slicer
# ✅ detecta estructura interna
# ✅ imprime TODAS las opciones
# ✅ detecta checkbox
# ✅ detecta multiselect
# ✅ detecta búsqueda interna
# ✅ detecta jerarquía
# ✅ detecta virtualización
# ✅ detecta clickables reales
# ✅ exporta opciones
# ✅ screenshots
# ✅ html interno
#
# OBJETIVO CIENTÍFICO:
#
# dominar completamente:
#
# selección jurisdiccional
#
# dentro del dashboard Power BI.
#
# ================================================================

from playwright.sync_api import sync_playwright
import pandas as pd
import os
import json
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
    "analytics/slicer_options_inspection"
)

HTML_DIR = os.path.join(
    OUTPUT_DIR,
    "html"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [

    OUTPUT_DIR,
    HTML_DIR,
    SCREENSHOT_DIR

]:
    os.makedirs(
        d,
        exist_ok=True
    )

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

# ------------------------------------------------

def safe_attr(locator, attr):

    try:

        return locator.get_attribute(attr)

    except Exception:

        return None

# ------------------------------------------------

def safe_text(locator):

    try:

        return locator.inner_text(
            timeout=500
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

# ================================================================
# DATASETS
# ================================================================

option_rows = []

summary = {

    "slicer_found": False,

    "search_detected": False,

    "checkbox_detected": False,

    "multiselect_detected": False,

    "virtualization_detected": False,

    "hierarchical_detected": False,

    "sullana_detected": False,

    "luciano_detected": False
}

# ================================================================
# PLAYWRIGHT
# ================================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

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

            text = safe_text(g)

            if aria:

                if (
                    "establecimiento"
                    in aria.lower()
                ):

                    slicer = g

                    summary["slicer_found"] = True

                    print("=" * 70)
                    print("SLICER REAL DETECTADO")
                    print("=" * 70)

                    print("ARIA:")
                    print(aria)

                    print("=" * 70)

                    print("TEXT:")
                    print(text[:500])

                    print("=" * 70)

                    break

        except Exception:

            pass

    # ============================================================
    # VALIDATION
    # ============================================================

    if slicer is None:

        print("NO SE ENCONTRÓ SLICER")

        browser.close()

        exit()

    # ============================================================
    # SCREENSHOT BEFORE
    # ============================================================

    slicer.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "slicer_before_expand.png"
        )
    )

    # ============================================================
    # EXPAND
    # ============================================================

    print("=" * 70)
    print("EXPANDIENDO SLICER")
    print("=" * 70)

    expanded = False

    # ------------------------------------------------------------
    # TRY CLICK
    # ------------------------------------------------------------

    click_targets = slicer.locator(

        "button, div, span"

    )

    total_clicks = min(
        click_targets.count(),
        50
    )

    for i in range(total_clicks):

        try:

            t = click_targets.nth(i)

            txt = safe_text(t)

            if (
                "todas" in txt.lower()
                or
                "establecimiento" in txt.lower()
            ):

                t.click(
                    timeout=2000
                )

                expanded = True

                time.sleep(5)

                print("CLICK OK")

                break

        except Exception:

            pass

    # ------------------------------------------------------------
    # FALLBACK
    # ------------------------------------------------------------

    if not expanded:

        try:

            slicer.click()

            expanded = True

            time.sleep(5)

        except Exception:

            pass

    # ============================================================
    # SCREENSHOT AFTER
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_expand.png"
        ),

        full_page=True
    )

    # ============================================================
    # EXPORT HTML
    # ============================================================

    try:

        outer_html = slicer.evaluate(
            "(node) => node.outerHTML"
        )

    except Exception:

        outer_html = ""

    with open(

        os.path.join(

            HTML_DIR,

            "slicer_expanded.html"
        ),

        "w",

        encoding="utf-8"

    ) as f:

        f.write(outer_html)

    # ============================================================
    # DETECT SEARCH
    # ============================================================

    print("=" * 70)
    print("DETECTANDO SEARCH")
    print("=" * 70)

    search_boxes = page.locator(

        "input, textarea"

    )

    search_count = search_boxes.count()

    print(f"SEARCH INPUTS: {search_count}")

    if search_count > 0:

        summary["search_detected"] = True

    # ============================================================
    # DETECT OPTIONS
    # ============================================================

    print("=" * 70)
    print("INSPECCIONANDO OPCIONES")
    print("=" * 70)

    option_selectors = [

        "div",

        "span",

        "label",

        "li",

        "input",

        "[role='option']",

        "[role='treeitem']",

        "[role='checkbox']"
    ]

    option_id = 0

    detected_texts = set()

    for selector in option_selectors:

        try:

            elements = page.locator(
                selector
            )

            total = min(
                elements.count(),
                500
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = elements.nth(i)

                    text = safe_text(el).strip()

                    # --------------------------------------------
                    # FILTER EMPTY
                    # --------------------------------------------

                    if len(text) == 0:
                        continue

                    # --------------------------------------------
                    # DEDUP
                    # --------------------------------------------

                    if text in detected_texts:
                        continue

                    detected_texts.add(text)

                    option_id += 1

                    role = safe_attr(
                        el,
                        "role"
                    )

                    aria = safe_attr(
                        el,
                        "aria-label"
                    )

                    class_attr = safe_attr(
                        el,
                        "class"
                    )

                    checked = safe_attr(
                        el,
                        "aria-checked"
                    )

                    expanded_attr = safe_attr(
                        el,
                        "aria-expanded"
                    )

                    # --------------------------------------------
                    # CHECKBOX
                    # --------------------------------------------

                    is_checkbox = False

                    if (
                        role == "checkbox"
                        or checked is not None
                    ):
                        is_checkbox = True

                        summary[
                            "checkbox_detected"
                        ] = True

                    # --------------------------------------------
                    # HIERARCHY
                    # --------------------------------------------

                    is_tree = False

                    if (
                        role == "treeitem"
                        or expanded_attr is not None
                    ):
                        is_tree = True

                        summary[
                            "hierarchical_detected"
                        ] = True

                    # --------------------------------------------
                    # CLICKABLE
                    # --------------------------------------------

                    clickable = False

                    try:

                        el.click(
                            timeout=300
                        )

                        clickable = True

                    except Exception:

                        pass

                    # --------------------------------------------
                    # VIRTUALIZATION
                    # --------------------------------------------

                    virtual = False

                    html_fragment = ""

                    try:

                        html_fragment = el.evaluate(
                            "(node) => node.outerHTML"
                        )

                    except Exception:

                        pass

                    virtual_keywords = [

                        "scroll",

                        "virtual",

                        "viewport"
                    ]

                    for kw in virtual_keywords:

                        if kw in html_fragment.lower():

                            virtual = True

                            summary[
                                "virtualization_detected"
                            ] = True

                    # --------------------------------------------
                    # TARGETS
                    # --------------------------------------------

                    contains_sullana = (
                        "sullana"
                        in text.lower()
                    )

                    contains_luciano = (
                        "luciano"
                        in text.lower()
                    )

                    if contains_sullana:

                        summary[
                            "sullana_detected"
                        ] = True

                    if contains_luciano:

                        summary[
                            "luciano_detected"
                        ] = True

                    # --------------------------------------------
                    # MULTISELECT
                    # --------------------------------------------

                    if checked is not None:

                        summary[
                            "multiselect_detected"
                        ] = True

                    # --------------------------------------------
                    # RECORD
                    # --------------------------------------------

                    row = {

                        "option_id":
                            option_id,

                        "selector":
                            selector,

                        "text":
                            text,

                        "role":
                            role,

                        "aria_label":
                            aria,

                        "checked":
                            checked,

                        "expanded":
                            expanded_attr,

                        "checkbox":
                            is_checkbox,

                        "hierarchical":
                            is_tree,

                        "clickable":
                            clickable,

                        "virtualized":
                            virtual,

                        "contains_sullana":
                            contains_sullana,

                        "contains_luciano":
                            contains_luciano,

                        "class":
                            class_attr
                    }

                    option_rows.append(
                        row
                    )

                    # --------------------------------------------
                    # CONSOLE
                    # --------------------------------------------

                    print("=" * 70)

                    print(text[:200])

                    print("- ROLE:", role)

                    print("- CHECKBOX:", is_checkbox)

                    print("- CLICKABLE:", clickable)

                    print("- SULLANA:", contains_sullana)

                    print("- LUCIANO:", contains_luciano)

                except Exception:

                    pass

        except Exception:

            pass

    # ============================================================
    # EXPORT CSV
    # ============================================================

    print("=" * 70)
    print("EXPORTANDO RESULTADOS")
    print("=" * 70)

    df = pd.DataFrame(
        option_rows
    )

    csv_path = os.path.join(

        OUTPUT_DIR,

        "slicer_options.csv"
    )

    df.to_csv(

        csv_path,

        index=False,

        encoding="utf-8-sig"
    )

    # ============================================================
    # SUMMARY JSON
    # ============================================================

    save_json(

        summary,

        os.path.join(

            OUTPUT_DIR,

            "inspection_summary.json"
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

    print("TOTAL OPCIONES:")
    print(len(df))

    print("=" * 70)

    print("OUTPUT CSV:")
    print(csv_path)

    print("=" * 70)

    print("INSPECCIÓN OPCIONES COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()