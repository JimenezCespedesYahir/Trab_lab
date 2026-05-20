# ================================================================
# detect_real_searchbox.py
# ================================================================
#
# OBJETIVO:
#
# Detectar el textbox REAL del slicer Power BI:
#
#     Establecimiento
#         Todas
#
# distinguiéndolo de:
#
# ❌ checkbox inputs
# ❌ hidden inputs
# ❌ focus proxies
# ❌ accessibility inputs
#
# ================================================================
#
# EL OBJETIVO REAL:
#
# Encontrar el searchbox auténtico:
#
# ✅ type="search"
# ✅ contenteditable
# ✅ aria-label
# ✅ placeholder
# ✅ dentro de .slicer-dropdown-menu
# ✅ overlay activo
# ✅ z-index superior
# ✅ bounding box visible
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
    "analytics/detect_real_searchbox"
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
    SCREENSHOT_DIR,
    HTML_DIR
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

def safe_bbox(locator):

    try:

        return locator.bounding_box()

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

input_profiles = []

candidate_profiles = []

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
    # FIND ESTABLECIMIENTO FILTER
    # ============================================================

    print("=" * 70)
    print("BUSCANDO FILTRO ESTABLECIMIENTO")
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

            print("=" * 70)
            print("FILTRO CLICKED")
            print("=" * 70)

            time.sleep(5)

        except Exception as e:

            print(e)

    # ============================================================
    # SCREENSHOT AFTER CLICK
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_filter_click.png"
        ),

        full_page=True
    )

    # ============================================================
    # DETECT OVERLAY
    # ============================================================

    print("=" * 70)
    print("BUSCANDO OVERLAYS")
    print("=" * 70)

    overlay_selectors = [

        ".slicer-dropdown-menu",

        "[role='listbox']",

        ".popupContainer",

        ".dropdown-popup",

        ".overlay"
    ]

    dropdown_overlay = None

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

                    dropdown_overlay = el

                    bbox = safe_bbox(el)

                    overlay_profiles.append({

                        "selector":
                            selector,

                        "visible":
                            el.is_visible(),

                        "text":
                            safe_text(el)[:1000],

                        "bbox":
                            str(bbox),

                        "class":
                            safe_attr(
                                el,
                                "class"
                            ),

                        "role":
                            safe_attr(
                                el,
                                "role"
                            )
                    })

                    print("=" * 70)
                    print("OVERLAY DETECTADO")
                    print("=" * 70)

                    print(safe_text(el)[:500])

                    print("=" * 70)

                    try:

                        html = el.evaluate(
                            "e => e.outerHTML"
                        )

                        save_html(

                            html,

                            os.path.join(

                                HTML_DIR,

                                f"overlay_{i}.html"
                            )
                        )

                    except Exception:
                        pass

                    break

                except Exception:
                    pass

            if dropdown_overlay is not None:
                break

        except Exception:
            pass

    # ============================================================
    # SEARCH REAL INPUTS
    # ============================================================

    print("=" * 70)
    print("INSPECCIONANDO INPUTS")
    print("=" * 70)

    input_selectors = [

        "input",

        "[role='textbox']",

        "[contenteditable='true']",

        "textarea"
    ]

    for selector in input_selectors:

        try:

            els = page.locator(
                selector
            )

            count = min(
                els.count(),
                200
            )

            print(f"{selector}: {count}")

            for i in range(count):

                try:

                    el = els.nth(i)

                    visible = el.is_visible()

                    enabled = False
                    editable = False

                    try:
                        enabled = el.is_enabled()
                    except:
                        pass

                    try:
                        editable = el.is_editable()
                    except:
                        pass

                    bbox = safe_bbox(el)

                    # ----------------------------------------
                    # JS COMPUTED STYLE
                    # ----------------------------------------

                    style = el.evaluate(
                        """
                        e => {

                            const s =
                                window.getComputedStyle(e);

                            return {

                                zIndex: s.zIndex,

                                display: s.display,

                                visibility: s.visibility,

                                opacity: s.opacity,

                                position: s.position
                            };
                        }
                        """
                    )

                    # ----------------------------------------
                    # PARENT CHECK
                    # ----------------------------------------

                    inside_dropdown = False

                    try:

                        inside_dropdown = el.evaluate(
                            """
                            e => {

                                return !!e.closest(
                                    '.slicer-dropdown-menu'
                                );
                            }
                            """
                        )

                    except:
                        pass

                    # ----------------------------------------
                    # PROFILE
                    # ----------------------------------------

                    profile = {

                        "selector":
                            selector,

                        "visible":
                            visible,

                        "enabled":
                            enabled,

                        "editable":
                            editable,

                        "inside_dropdown":
                            inside_dropdown,

                        "text":
                            safe_text(el),

                        "type":
                            safe_attr(
                                el,
                                "type"
                            ),

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
                            ),

                        "id":
                            safe_attr(
                                el,
                                "id"
                            ),

                        "tabindex":
                            safe_attr(
                                el,
                                "tabindex"
                            ),

                        "bbox":
                            str(bbox),

                        "zindex":
                            style["zIndex"],

                        "display":
                            style["display"],

                        "visibility":
                            style["visibility"],

                        "opacity":
                            style["opacity"],

                        "position":
                            style["position"]
                    }

                    input_profiles.append(
                        profile
                    )

                    # ----------------------------------------
                    # REAL SEARCHBOX HEURISTIC
                    # ----------------------------------------

                    candidate = False

                    if (
                        visible
                        and enabled
                        and inside_dropdown
                    ):

                        if (
                            profile["type"] == "search"
                            or profile["role"] == "textbox"
                            or editable
                            or profile["placeholder"] is not None
                            or profile["aria_label"] is not None
                        ):

                            candidate = True

                    if candidate:

                        candidate_profiles.append(
                            profile
                        )

                        print("=" * 70)
                        print("CANDIDATE SEARCHBOX")
                        print("=" * 70)

                        for k, v in profile.items():

                            print(f"{k}: {v}")

                        print("=" * 70)

                        try:

                            html = el.evaluate(
                                "e => e.outerHTML"
                            )

                            save_html(

                                html,

                                os.path.join(

                                    HTML_DIR,

                                    f"candidate_{i}.html"
                                )
                            )

                        except Exception:
                            pass

                except Exception:
                    pass

        except Exception:
            pass

    # ============================================================
    # SCREENSHOT FINAL
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "final_state.png"
        ),

        full_page=True
    )

    # ============================================================
    # EXPORT CSV
    # ============================================================

    pd.DataFrame(
        input_profiles
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "all_input_profiles.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        candidate_profiles
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "candidate_searchboxes.csv"
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

    # ============================================================
    # SUMMARY
    # ============================================================

    summary = {

        "inputs_detected":
            len(input_profiles),

        "candidate_searchboxes":
            len(candidate_profiles),

        "overlays_detected":
            len(overlay_profiles)
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

    print("DETECCIÓN SEARCHBOX COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()