# ============================================================
# apply_territorial_pipeline.py
# ============================================================
# PIPELINE TERRITORIAL FINAL
# ------------------------------------------------------------
# 1. Abrir dashboard
# 2. Reset visual state
# 3. Aplicar:
#
#       MACROREGION = NORTE
#       INSTITUCION = GOBIERNO REGIONAL
#
# 4. Abrir:
#
#       Unidad ejecutora
#
# 5. Buscar:
#
#       SALUD LUCIANO CASTILLO COLONNA
#
# 6. Seleccionar opción exacta
# 7. Esperar rerender
# 8. Capturar querydata
# 9. Guardar payloads
#
# ============================================================

import json
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
    "territorial_pipeline_outputs"
)

SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

PAYLOAD_DIR = OUTPUT_DIR / "payloads"

OUTPUT_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)
PAYLOAD_DIR.mkdir(exist_ok=True)

payload_counter = 0

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
# QUERY CAPTURE
# ============================================================

def setup_capture(page):

    captured = []

    def handle_response(response):

        global payload_counter

        try:

            if "/querydata" not in response.url:
                return

            payload_counter += 1

            request = response.request

            data = {

                "url": response.url,
                "status": response.status,
                "method": request.method,
                "post_data": request.post_data

            }

            with open(
                PAYLOAD_DIR / f"query_{payload_counter}.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            captured.append(data)

            print("\n")
            print("=" * 80)
            print("QUERYDATA CAPTURADA")
            print("=" * 80)

            print(f"STATUS: {response.status}")

        except Exception as e:

            print(e)

    page.on(
        "response",
        handle_response
    )

    return captured

# ============================================================
# GET ACTIVE OVERLAY
# ============================================================

def get_active_overlay(page):

    overlays = []

    selectors = [

        "div[role='listbox']",
        "div[role='tree']"

    ]

    for selector in selectors:

        loc = page.locator(selector)

        count = loc.count()

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
        return None

    overlays = sorted(

        overlays,

        key=lambda x: x["area"],

        reverse=True

    )

    return overlays[0]["locator"]

# ============================================================
# FIND SLICER CONTAINER
# ============================================================

def find_slicer_container(page, label):

    banner(
        f"SEARCH CONTAINER -> {label}"
    )

    texts = page.locator(

        f"text={label}"

    )

    total = texts.count()

    print(f"MATCHES: {total}")

    for i in range(total):

        try:

            t = texts.nth(i)

            if not t.is_visible():
                continue

            print("\nVISIBLE LABEL FOUND")

            parent = t.locator(
                "xpath=ancestor::*[contains(@class,'visualContainer')]"
            ).first

            if parent.count() > 0:

                txt = clean_text(
                    parent.inner_text()
                )

                print(txt[:500])

                return parent

        except Exception as e:

            print(e)

    return None

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

        try:

            c = containers.nth(i)

            text = clean_text(
                c.inner_text()
            )

            if label.lower() in text.lower():

                print("\nCONTAINER FOUND")

                print(text[:500])

                return c

        except:
            pass

    return None

# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(

    page,

    slicer_name,

    value,

    search_value=None

):

    banner(
        f"APPLY FILTER -> {slicer_name}"
    )

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:

        print("NO CONTAINER")

        return False

    combos = container.locator(
        "[role='combobox']"
    )

    if combos.count() == 0:

        print("NO COMBOBOX")

        return False

    combo = combos.first

    combo.click(force=True)

    time.sleep(5)

    screenshot(
        page,
        f"{slicer_name}_dropdown"
    )

    overlay = get_active_overlay(page)

    if not overlay:

        print("NO OVERLAY")

        return False

    # ========================================================
    # CLICK OVERLAY
    # ========================================================

    overlay.click(force=True)

    time.sleep(2)

    # ========================================================
    # TYPE SEARCH
    # ========================================================

    if search_value:

        banner(
            f"TYPING: {search_value}"
        )

        page.keyboard.type(

            search_value,

            delay=80

        )

        time.sleep(6)

        screenshot(
            page,
            f"{slicer_name}_typed"
        )

    # ========================================================
    # FIND OPTIONS
    # ========================================================

    banner(
        "SEARCH OPTIONS"
    )

    options = overlay.locator(
        ".slicerItemContainer"
    )

    total = options.count()

    print(f"OPTIONS: {total}")

    selected = None

    for i in range(total):

        try:

            option = options.nth(i)

            if not option.is_visible():
                continue

            text = clean_text(
                option.inner_text()
            )

            print("\nOPTION")

            print(text)

            if value.lower() in text.lower():

                selected = option

                print("\nMATCH FOUND")

                break

        except:
            pass

    if not selected:

        print("\nNO MATCH")

        screenshot(
            page,
            f"{slicer_name}_no_match"
        )

        return False

    # ========================================================
    # CLICK OPTION
    # ========================================================

    banner(
        "CLICK OPTION"
    )

    selected.click(force=True)

    print("\nOPTION SELECTED")

    time.sleep(15)

    screenshot(
        page,
        f"{slicer_name}_selected"
    )

    return True

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

    captured = setup_capture(page)

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
    # WAIT RENDER
    # ========================================================

    banner(
        "WAIT POWER BI"
    )

    time.sleep(35)

    screenshot(
        page,
        "dashboard_loaded"
    )

    # ========================================================
    # FILTER 1
    # ========================================================

    apply_filter(

        page,

        "MACROREGION",

        "NORTE",

        search_value="NORTE"

    )

    # ========================================================
    # FILTER 2
    # ========================================================

    apply_filter(

        page,

        "Institución",

        "GOBIERNO REGIONAL",

        search_value="GOBIERNO"

    )

    # ========================================================
    # FILTER 3
    # ========================================================

    apply_filter(

        page,

        "Unidad ejecutora",

        "SALUD LUCIANO CASTILLO COLONNA",

        search_value="LUCIANO"

    )

    # ========================================================
    # FINAL WAIT
    # ========================================================

    banner(
        "WAIT FINAL"
    )

    time.sleep(20)

    screenshot(
        page,
        "final_dashboard"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    banner(
        "SUMMARY"
    )

    print(f"PAYLOADS: {len(captured)}")

    print(f"OUTPUT: {OUTPUT_DIR}")

    print("\n")
    print("=" * 80)
    print("TERRITORIAL PIPELINE COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()