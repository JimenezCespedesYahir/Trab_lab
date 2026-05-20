# ================================================================
# inspect_slicer_dom.py
# ================================================================
# OBJETIVO:
#
# Ingeniería inversa profunda del slicer Power BI.
#
# Este script:
#
# ✅ detecta slicers REALES
# ✅ inspecciona DOM interno
# ✅ extrae aria-labels
# ✅ extrae data-testid
# ✅ detecta scroll virtual
# ✅ detecta opciones renderizadas
# ✅ detecta clickables reales
# ✅ detecta wrappers Power BI
# ✅ detecta jerarquía DOM
# ✅ exporta HTML estructurado
# ✅ captura screenshots
#
# OBJETIVO CIENTÍFICO:
#
# descubrir cómo Power BI renderiza:
#
# slicers territoriales
#
# para luego:
#
# controlar filtros jurisdiccionales.
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

OUTPUT_DIR = "analytics/slicer_dom_inspection"

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
# TARGET KEYWORDS
# ================================================================

TERRITORIAL_KEYWORDS = [

    "establecimiento",

    "disa",

    "diresa",

    "geresa",

    "red",

    "micro",

    "provincia",

    "distrito",

    "departamento",

    "ipress"
]

# ================================================================
# STRUCTURAL SELECTORS
# ================================================================

SELECTORS = [

    "[role='combobox']",

    "[role='listbox']",

    "button[aria-expanded]",

    ".slicerContainer",

    ".visualContainer"
]

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

# ------------------------------------------------

def contains_keywords(text):

    if text is None:
        return False

    text = str(text).lower()

    return any(
        kw in text
        for kw in TERRITORIAL_KEYWORDS
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

inspection_rows = []

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
    # SCREENSHOT FULL
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "dashboard_full.png"
        ),

        full_page=True
    )

    # ============================================================
    # INSPECTION
    # ============================================================

    slicer_counter = 0

    print("=" * 70)
    print("INSPECCIONANDO SLICERS")
    print("=" * 70)

    for selector in SELECTORS:

        try:

            elements = page.locator(
                selector
            )

            total = min(
                elements.count(),
                50
            )

            print(f"{selector}: {total}")

            for i in range(total):

                try:

                    el = elements.nth(i)

                    # ------------------------------------------------
                    # BASIC TEXT
                    # ------------------------------------------------

                    try:

                        text = el.inner_text(
                            timeout=1000
                        )

                    except Exception:

                        text = ""

                    # ------------------------------------------------
                    # FILTER
                    # ------------------------------------------------

                    if not contains_keywords(text):
                        continue

                    slicer_counter += 1

                    print("=" * 70)
                    print(f"SLICER {slicer_counter}")
                    print("=" * 70)

                    print(text[:500])

                    # ------------------------------------------------
                    # ATTRIBUTES
                    # ------------------------------------------------

                    role = el.get_attribute("role")

                    aria_label = el.get_attribute(
                        "aria-label"
                    )

                    aria_expanded = el.get_attribute(
                        "aria-expanded"
                    )

                    data_testid = el.get_attribute(
                        "data-testid"
                    )

                    class_attr = el.get_attribute(
                        "class"
                    )

                    # ------------------------------------------------
                    # OUTER HTML
                    # ------------------------------------------------

                    try:

                        outer_html = el.evaluate(
                            "(node) => node.outerHTML"
                        )

                    except Exception:

                        outer_html = ""

                    # ------------------------------------------------
                    # CHILDREN COUNT
                    # ------------------------------------------------

                    try:

                        child_count = el.evaluate(
                            "(node) => node.children.length"
                        )

                    except Exception:

                        child_count = None

                    # ------------------------------------------------
                    # CLICKABLES
                    # ------------------------------------------------

                    try:

                        clickable_count = el.locator(

                            "button, div, span, li"

                        ).count()

                    except Exception:

                        clickable_count = 0

                    # ------------------------------------------------
                    # OPTIONS
                    # ------------------------------------------------

                    option_texts = []

                    # TRY OPEN
                    try:

                        el.click(
                            timeout=3000
                        )

                        time.sleep(3)

                    except Exception:

                        pass

                    # READ OPTIONS
                    try:

                        options = page.locator(

                            "[role='option'], "
                            "li, "
                            "span"

                        )

                        max_options = min(
                            options.count(),
                            100
                        )

                        for j in range(max_options):

                            try:

                                op = options.nth(j)

                                op_text = op.inner_text(
                                    timeout=300
                                )

                                if (
                                    op_text
                                    and
                                    len(op_text.strip()) > 0
                                ):

                                    option_texts.append(
                                        op_text.strip()
                                    )

                            except Exception:

                                pass

                    except Exception:

                        pass

                    # ------------------------------------------------
                    # VIRTUAL SCROLL DETECTION
                    # ------------------------------------------------

                    virtual_scroll = False

                    if (
                        "scroll"
                        in str(outer_html).lower()
                    ):
                        virtual_scroll = True

                    # ------------------------------------------------
                    # REACT DETECTION
                    # ------------------------------------------------

                    react_detected = False

                    react_keywords = [

                        "__react",

                        "react",

                        "fiber"
                    ]

                    for kw in react_keywords:

                        if kw.lower() in str(outer_html).lower():

                            react_detected = True

                    # ------------------------------------------------
                    # SAVE HTML
                    # ------------------------------------------------

                    html_path = os.path.join(

                        HTML_DIR,

                        f"slicer_{slicer_counter}.html"
                    )

                    with open(

                        html_path,

                        "w",

                        encoding="utf-8"

                    ) as f:

                        f.write(outer_html)

                    # ------------------------------------------------
                    # SCREENSHOT
                    # ------------------------------------------------

                    screenshot_path = os.path.join(

                        SCREENSHOT_DIR,

                        f"slicer_{slicer_counter}.png"
                    )

                    try:

                        el.screenshot(
                            path=screenshot_path
                        )

                    except Exception:

                        pass

                    # ------------------------------------------------
                    # RECORD
                    # ------------------------------------------------

                    row = {

                        "slicer_id":
                            slicer_counter,

                        "selector":
                            selector,

                        "text_preview":
                            text[:1000],

                        "role":
                            role,

                        "aria_label":
                            aria_label,

                        "aria_expanded":
                            aria_expanded,

                        "data_testid":
                            data_testid,

                        "class":
                            class_attr,

                        "children":
                            child_count,

                        "clickables":
                            clickable_count,

                        "virtual_scroll":
                            virtual_scroll,

                        "react_detected":
                            react_detected,

                        "options_detected":
                            len(option_texts),

                        "sample_options":
                            " | ".join(
                                option_texts[:20]
                            ),

                        "html_file":
                            html_path,

                        "screenshot_file":
                            screenshot_path
                    }

                    inspection_rows.append(
                        row
                    )

                    # ------------------------------------------------
                    # CONSOLE
                    # ------------------------------------------------

                    print("=" * 70)
                    print("ROLE:")
                    print(role)

                    print("=" * 70)
                    print("ARIA LABEL:")
                    print(aria_label)

                    print("=" * 70)
                    print("DATA TESTID:")
                    print(data_testid)

                    print("=" * 70)
                    print("OPTIONS:")
                    print(len(option_texts))

                    print("=" * 70)
                    print("VIRTUAL SCROLL:")
                    print(virtual_scroll)

                    print("=" * 70)
                    print("REACT:")
                    print(react_detected)

                    print("=" * 70)

                except Exception as e:

                    print("ELEMENT ERROR")
                    print(e)

        except Exception as e:

            print("SELECTOR ERROR")
            print(e)

    # ============================================================
    # EXPORT
    # ============================================================

    print("=" * 70)
    print("EXPORTANDO RESULTADOS")
    print("=" * 70)

    df = pd.DataFrame(
        inspection_rows
    )

    output_csv = os.path.join(

        OUTPUT_DIR,

        "slicer_dom_profiles.csv"
    )

    df.to_csv(

        output_csv,

        index=False,

        encoding="utf-8-sig"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("SLICERS INSPECTED:")
    print(len(df))

    print("=" * 70)

    print("OUTPUT:")
    print(output_csv)

    print("=" * 70)

    print("HTML FILES:")
    print(len(os.listdir(HTML_DIR)))

    print("=" * 70)

    print("SCREENSHOTS:")
    print(len(os.listdir(SCREENSHOT_DIR)))

    print("=" * 70)
    print("INSPECCIÓN DOM COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()