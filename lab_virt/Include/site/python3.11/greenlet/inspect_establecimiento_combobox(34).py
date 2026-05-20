# ================================================================
# inspect_establecimiento_combobox.py
# ================================================================
#
# OBJETIVO:
#
# Inspeccionar quirúrgicamente el controlador:
#
#     Establecimiento
#         Todas
#
# para descubrir:
#
# ✅ aria-expanded
# ✅ combobox interno
# ✅ overlay popup
# ✅ option nodes
# ✅ input searchable
# ✅ virtual scroll
# ✅ checkbox mode
# ✅ role hierarchy
# ✅ focus state
# ✅ popup renderizado
#
# ================================================================
#
# DIFERENCIA CLAVE:
#
# Antes:
#   buscábamos texto globalmente.
#
# Ahora:
#   inspeccionamos estructura DOM exacta
#   del combobox territorial.
#
# ================================================================

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
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
    "analytics/inspect_establecimiento_combobox"
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

def save_html(content, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

# ================================================================
# DATASETS
# ================================================================

combobox_profiles = []

option_profiles = []

overlay_profiles = []

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
    # SEARCH ESTABLECIMIENTO
    # ============================================================

    print("=" * 70)
    print("BUSCANDO ESTABLECIMIENTO")
    print("=" * 70)

    selectors = [

        "div",
        "span",

        "[role='combobox']",

        "[role='button']",

        "[aria-label]"
    ]

    target = None

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

                        target = el

                        print("=" * 70)
                        print("TARGET DETECTADO")
                        print("=" * 70)

                        print(txt)

                        print("=" * 70)

                        break

                except Exception:
                    pass

            if target is not None:
                break

        except Exception:
            pass

    # ============================================================
    # VALIDATION
    # ============================================================

    if target is None:

        print("NO TARGET")

        browser.close()

        exit()

    # ============================================================
    # PROFILE TARGET
    # ============================================================

    print("=" * 70)
    print("PROFILING COMBOBOX")
    print("=" * 70)

    attrs = [

        "role",

        "aria-label",

        "aria-expanded",

        "aria-haspopup",

        "aria-controls",

        "aria-owns",

        "aria-activedescendant",

        "tabindex",

        "class",

        "id"
    ]

    profile = {

        "text":
            safe_text(target)
    }

    for attr in attrs:

        profile[attr] = safe_attr(
            target,
            attr
        )

    combobox_profiles.append(
        profile
    )

    # ============================================================
    # SAVE OUTER HTML
    # ============================================================

    try:

        html = target.evaluate(
            "el => el.outerHTML"
        )

        save_html(

            html,

            os.path.join(

                HTML_DIR,

                "target_outerhtml.html"
            )
        )

    except Exception as e:

        print(e)

    # ============================================================
    # CLICK TARGET
    # ============================================================

    print("=" * 70)
    print("CLICK TARGET")
    print("=" * 70)

    try:

        target.scroll_into_view_if_needed()

        time.sleep(1)

        target.click(
            force=True
        )

        time.sleep(5)

    except Exception as e:

        print(e)

    # ============================================================
    # SCREENSHOT AFTER CLICK
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_click.png"
        ),

        full_page=True
    )

    # ============================================================
    # REPROFILE
    # ============================================================

    print("=" * 70)
    print("REPROFILING")
    print("=" * 70)

    repro_profile = {

        "phase":
            "after_click"
    }

    for attr in attrs:

        repro_profile[attr] = safe_attr(
            target,
            attr
        )

    combobox_profiles.append(
        repro_profile
    )

    # ============================================================
    # SEARCH OVERLAYS
    # ============================================================

    print("=" * 70)
    print("SEARCHING OVERLAYS")
    print("=" * 70)

    overlay_selectors = [

        "[role='listbox']",

        "[role='dialog']",

        "[role='menu']",

        ".popupContainer",

        ".slicer-dropdown-menu",

        ".dropdown-popup",

        ".overlay",

        ".popup"
    ]

    for selector in overlay_selectors:

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

                    txt = safe_text(el)

                    overlay_profiles.append({

                        "selector":
                            selector,

                        "text":
                            txt[:3000],

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

                        "class":
                            safe_attr(
                                el,
                                "class"
                            )
                    })

                    # ------------------------------------
                    # SAVE HTML
                    # ------------------------------------

                    try:

                        html = el.evaluate(
                            "e => e.outerHTML"
                        )

                        save_html(

                            html,

                            os.path.join(

                                HTML_DIR,

                                f"overlay_{selector.replace('[','').replace(']','').replace('/','_')}_{i}.html"
                            )
                        )

                    except Exception:
                        pass

                except Exception:
                    pass

        except Exception:
            pass

    # ============================================================
    # SEARCH OPTIONS
    # ============================================================

    print("=" * 70)
    print("SEARCHING OPTIONS")
    print("=" * 70)

    option_selectors = [

        "[role='option']",

        "[role='treeitem']",

        "li",

        "label",

        "input",

        ".slicerItemContainer",

        ".visibleGroup"
    ]

    for selector in option_selectors:

        try:

            els = page.locator(
                selector
            )

            count = min(
                els.count(),
                500
            )

            print(f"{selector}: {count}")

            for i in range(count):

                try:

                    el = els.nth(i)

                    visible = el.is_visible()

                    txt = safe_text(el)

                    option_profiles.append({

                        "selector":
                            selector,

                        "visible":
                            visible,

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
                            ),

                        "aria_checked":
                            safe_attr(
                                el,
                                "aria-checked"
                            ),

                        "aria_selected":
                            safe_attr(
                                el,
                                "aria-selected"
                            ),

                        "class":
                            safe_attr(
                                el,
                                "class"
                            ),

                        "tabindex":
                            safe_attr(
                                el,
                                "tabindex"
                            )
                    })

                except Exception:
                    pass

        except Exception:
            pass

    # ============================================================
    # EXPORT CSV
    # ============================================================

    pd.DataFrame(
        combobox_profiles
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "combobox_profiles.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        overlay_profiles
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "overlay_profiles.csv"
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

    # ============================================================
    # SUMMARY
    # ============================================================

    summary = {

        "combobox_profiles":
            len(combobox_profiles),

        "overlay_profiles":
            len(overlay_profiles),

        "option_profiles":
            len(option_profiles)
    }

    with open(

        os.path.join(
            OUTPUT_DIR,
            "summary.json"
        ),

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(
            summary,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ============================================================
    # CONSOLE
    # ============================================================

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for k, v in summary.items():

        print(f"{k}: {v}")

    print("=" * 70)

    print("INSPECCIÓN COMBOBOX COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()