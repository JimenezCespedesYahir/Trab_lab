# ============================================================
# inspect_overlay_buttons.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Inspeccionar específicamente el overlay del slicer:
#
#     Establecimiento
#
# para descubrir:
#
#   - botones ocultos
#   - iconos lupa
#   - triggers búsqueda
#   - aria-labels
#   - SVG search icons
#   - buttons interactivos
#   - textbox diferido
#
# ============================================================

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = (
    "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"
)

OUTPUT_DIR = Path(
    "inspect_overlay_buttons_outputs"
)

SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

OUTPUT_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

def banner(title):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)

# ------------------------------------------------------------

def screenshot(page, name):

    page.screenshot(
        path=str(
            SCREENSHOT_DIR / f"{name}.png"
        ),
        full_page=True
    )

# ------------------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    text = text.replace("\n", " ")

    text = text.replace("\t", " ")

    text = " ".join(text.split())

    return text.strip()

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=False,

        slow_mo=300

    )

    context = browser.new_context(

        ignore_https_errors=True,

        viewport={

            "width": 1700,
            "height": 1000

        }

    )

    page = context.new_page()

    page.set_default_timeout(60000)

    page.set_default_navigation_timeout(120000)

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    banner(
        "OPEN DASHBOARD"
    )

    page.goto(

        POWERBI_URL,

        wait_until="domcontentloaded",

        timeout=120000

    )

    # ========================================================
    # WAIT FULL RENDER
    # ========================================================

    banner(
        "WAITING POWER BI RENDER"
    )

    time.sleep(35)

    screenshot(
        page,
        "dashboard_loaded"
    )

    # ========================================================
    # GET CONTAINERS
    # ========================================================

    banner(
        "GET CONTAINERS"
    )

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    # ========================================================
    # CONTAINER 4
    # ========================================================

    banner(
        "TARGET CONTAINER 4"
    )

    container = containers.nth(4)

    text = clean_text(
        container.inner_text()
    )

    print(text)

    screenshot(
        page,
        "container_4"
    )

    # ========================================================
    # FIND COMBOBOX
    # ========================================================

    banner(
        "FIND COMBOBOX"
    )

    combos = container.locator(
        "[role='combobox']"
    )

    combo_total = combos.count()

    print(f"COMBOBOXES: {combo_total}")

    if combo_total == 0:

        browser.close()

        raise Exception(
            "No combobox"
        )

    combo = combos.first

    # ========================================================
    # OPEN DROPDOWN
    # ========================================================

    banner(
        "OPEN DROPDOWN"
    )

    combo.click(force=True)

    time.sleep(5)

    screenshot(
        page,
        "dropdown_opened"
    )

    # ========================================================
    # DETECT OVERLAYS
    # ========================================================

    banner(
        "DETECT OVERLAYS"
    )

    overlays = []

    selectors = [

        "div[role='listbox']",
        "div[role='tree']"

    ]

    for selector in selectors:

        loc = page.locator(selector)

        count = loc.count()

        print(f"{selector}: {count}")

        for i in range(count):

            try:

                overlay = loc.nth(i)

                if not overlay.is_visible():
                    continue

                bbox = overlay.bounding_box()

                if not bbox:
                    continue

                area = (
                    bbox["width"]
                    *
                    bbox["height"]
                )

                text = clean_text(
                    overlay.inner_text()
                )

                overlays.append({

                    "locator": overlay,
                    "area": area,
                    "text": text

                })

            except:
                pass

    if len(overlays) == 0:

        screenshot(
            page,
            "no_overlay"
        )

        browser.close()

        raise Exception(
            "No overlays detectados"
        )

    overlays = sorted(

        overlays,

        key=lambda x: x["area"],

        reverse=True

    )

    overlay = overlays[0]["locator"]

    print("\nOVERLAY:\n")

    print(overlays[0]["text"][:3000])

    screenshot(
        page,
        "overlay_detected"
    )

    # ========================================================
    # INSPECT BUTTONS
    # ========================================================

    banner(
        "INSPECT BUTTONS"
    )

    button_selectors = [

        "button",
        "[role='button']",
        "svg",
        "i",
        "[aria-label]",
        "[title]"

    ]

    total_found = 0

    for selector in button_selectors:

        print("\n")
        print("-" * 60)

        print(f"SELECTOR: {selector}")

        try:

            loc = overlay.locator(selector)

            count = loc.count()

            print(f"COUNT: {count}")

            for i in range(count):

                try:

                    item = loc.nth(i)

                    if not item.is_visible():
                        continue

                    total_found += 1

                    text = clean_text(
                        item.inner_text()
                    )

                    aria = (
                        item.get_attribute(
                            "aria-label"
                        ) or ""
                    )

                    title = (
                        item.get_attribute(
                            "title"
                        ) or ""
                    )

                    role = (
                        item.get_attribute(
                            "role"
                        ) or ""
                    )

                    cls = (
                        item.get_attribute(
                            "class"
                        ) or ""
                    )

                    data_testid = (
                        item.get_attribute(
                            "data-testid"
                        ) or ""
                    )

                    print("\nELEMENT")

                    print(f"INDEX: {i}")

                    print(f"TEXT: {text}")

                    print(f"ARIA: {aria}")

                    print(f"TITLE: {title}")

                    print(f"ROLE: {role}")

                    print(f"CLASS: {cls}")

                    print(f"DATA-TESTID: {data_testid}")

                    # =====================================
                    # SEARCH KEYWORDS
                    # =====================================

                    full = (

                        text
                        + " "
                        + aria
                        + " "
                        + title
                        + " "
                        + cls
                        + " "
                        + data_testid

                    ).lower()

                    keywords = [

                        "search",
                        "buscar",
                        "find",
                        "magnify",
                        "icon",
                        "filter"

                    ]

                    found = False

                    for kw in keywords:

                        if kw in full:

                            found = True

                    if found:

                        print("\nSEARCH RELATED ELEMENT")

                except Exception as e:

                    print(e)

        except Exception as e:

            print(e)

    # ========================================================
    # INSPECT INPUTS AGAIN
    # ========================================================

    banner(
        "INSPECT INPUTS AGAIN"
    )

    input_selectors = [

        "input",
        "textarea",
        "[contenteditable='true']"

    ]

    for selector in input_selectors:

        print("\n")
        print("-" * 60)

        print(f"SELECTOR: {selector}")

        try:

            loc = overlay.locator(selector)

            count = loc.count()

            print(f"COUNT: {count}")

            for i in range(count):

                try:

                    inp = loc.nth(i)

                    if not inp.is_visible():
                        continue

                    placeholder = (
                        inp.get_attribute(
                            "placeholder"
                        ) or ""
                    )

                    aria = (
                        inp.get_attribute(
                            "aria-label"
                        ) or ""
                    )

                    typ = (
                        inp.get_attribute(
                            "type"
                        ) or ""
                    )

                    cls = (
                        inp.get_attribute(
                            "class"
                        ) or ""
                    )

                    print("\nINPUT")

                    print(f"INDEX: {i}")

                    print(f"TYPE: {typ}")

                    print(f"PLACEHOLDER: {placeholder}")

                    print(f"ARIA: {aria}")

                    print(f"CLASS: {cls}")

                except:
                    pass

        except:
            pass

    # ========================================================
    # TRY CTRL+F
    # ========================================================

    banner(
        "TRY CTRL+F"
    )

    overlay.click(force=True)

    time.sleep(2)

    page.keyboard.press(
        "Control+F"
    )

    time.sleep(5)

    screenshot(
        page,
        "after_ctrl_f"
    )

    # ========================================================
    # INPUTS AFTER CTRL+F
    # ========================================================

    banner(
        "INPUTS AFTER CTRL+F"
    )

    inputs_after = overlay.locator(
        "input"
    )

    total_after = inputs_after.count()

    print(f"INPUTS AFTER: {total_after}")

    for i in range(total_after):

        try:

            inp = inputs_after.nth(i)

            if not inp.is_visible():
                continue

            placeholder = (
                inp.get_attribute(
                    "placeholder"
                ) or ""
            )

            aria = (
                inp.get_attribute(
                    "aria-label"
                ) or ""
            )

            typ = (
                inp.get_attribute(
                    "type"
                ) or ""
            )

            print("\nINPUT")

            print(f"INDEX: {i}")

            print(f"TYPE: {typ}")

            print(f"PLACEHOLDER: {placeholder}")

            print(f"ARIA: {aria}")

        except:
            pass

    # ========================================================
    # FINAL SCREENSHOT
    # ========================================================

    screenshot(
        page,
        "final_state"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    banner(
        "SUMMARY"
    )

    print(f"BUTTONS INSPECTED: {total_found}")

    print(f"OUTPUT: {OUTPUT_DIR}")

    print("\n")
    print("=" * 80)
    print("OVERLAY BUTTON INSPECTION COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()