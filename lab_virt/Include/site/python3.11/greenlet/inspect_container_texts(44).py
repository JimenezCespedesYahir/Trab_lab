# ============================================================
# inspect_container_texts.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Inspeccionar TODOS los visual containers Power BI
# e imprimir EXACTAMENTE:
#
#   - inner_text()
#   - aria labels
#   - roles
#   - cantidad de combobox
#   - cantidad de inputs
#   - cantidad de listbox
#
# Para descubrir:
#
#   - nombres reales slicers
#   - labels reales
#   - texto renderizado interno
#   - keywords territoriales
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

OUTPUT_DIR = Path("inspect_container_outputs")

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

# ============================================================
# CLEAN TEXT
# ============================================================

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

    banner("OPEN DASHBOARD")

    page.goto(

        POWERBI_URL,

        wait_until="domcontentloaded",

        timeout=120000

    )

    # ========================================================
    # WAIT FULL RENDER
    # ========================================================

    banner("WAITING POWER BI RENDER")

    time.sleep(35)

    screenshot(
        page,
        "dashboard_loaded"
    )

    # ========================================================
    # FIND CONTAINERS
    # ========================================================

    banner("DETECTING VISUAL CONTAINERS")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    # ========================================================
    # LOOP CONTAINERS
    # ========================================================

    for i in range(total):

        banner(
            f"CONTAINER {i}"
        )

        try:

            container = containers.nth(i)

            visible = container.is_visible()

            print(f"VISIBLE: {visible}")

            if not visible:
                continue

            # ------------------------------------------------
            # TEXT
            # ------------------------------------------------

            try:

                text = container.inner_text(
                    timeout=5000
                )

            except:

                text = ""

            text = clean_text(text)

            print("\nINNER_TEXT:\n")

            print(text[:3000])

            # ------------------------------------------------
            # ATTRIBUTES
            # ------------------------------------------------

            try:

                role = container.get_attribute(
                    "role"
                )

            except:

                role = None

            try:

                aria = container.get_attribute(
                    "aria-label"
                )

            except:

                aria = None

            print("\nROLE:")

            print(role)

            print("\nARIA LABEL:")

            print(aria)

            # ------------------------------------------------
            # COUNTS
            # ------------------------------------------------

            combos = container.locator(
                "[role='combobox']"
            ).count()

            listbox = container.locator(
                "[role='listbox']"
            ).count()

            inputs = container.locator(
                "input"
            ).count()

            buttons = container.locator(
                "button"
            ).count()

            checkboxes = container.locator(
                "input[type='checkbox']"
            ).count()

            print("\nCOMPONENTS:")

            print(f"COMBOBOXES: {combos}")

            print(f"LISTBOXES: {listbox}")

            print(f"INPUTS: {inputs}")

            print(f"BUTTONS: {buttons}")

            print(f"CHECKBOXES: {checkboxes}")

            # ------------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------------

            try:

                bbox = container.bounding_box()

            except:

                bbox = None

            print("\nBOUNDING BOX:")

            print(bbox)

            # ------------------------------------------------
            # KEYWORDS
            # ------------------------------------------------

            TERRITORIAL_KEYWORDS = [

                "macroregion",
                "diresa",
                "geresa",
                "diris",
                "red",
                "micro",
                "institución",
                "unidad",
                "ejecutora",
                "establecimiento",
                "sullana",
                "luciano",
                "castillo",
                "gobierno regional"

            ]

            found = []

            text_lower = text.lower()

            for keyword in TERRITORIAL_KEYWORDS:

                if keyword.lower() in text_lower:

                    found.append(keyword)

            print("\nTERRITORIAL KEYWORDS:")

            print(found)

            # ------------------------------------------------
            # SCREENSHOT
            # ------------------------------------------------

            screenshot(
                page,
                f"container_{i}"
            )

            print("\nSCREENSHOT SAVED")

        except Exception as e:

            print("\nERROR:")

            print(e)

    # ========================================================
    # SUMMARY
    # ========================================================

    banner("SUMMARY")

    print(f"TOTAL CONTAINERS: {total}")

    print(f"OUTPUT DIR: {OUTPUT_DIR}")

    print("\n")
    print("=" * 80)
    print("CONTAINER INSPECTION COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()