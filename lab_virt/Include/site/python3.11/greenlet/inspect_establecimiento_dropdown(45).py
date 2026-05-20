# ============================================================
# inspect_establecimiento_dropdown.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# 1. Abrir dashboard
# 2. Detectar CONTAINER 4
# 3. Abrir SOLO el slicer:
#
#       Establecimiento
#
# 4. Detectar overlay ACTIVO
# 5. Detectar searchbox REAL
# 6. Escribir:
#
#       SALUD LUCIANO CASTILLO COLONNA
#
# 7. Esperar rerender
# 8. Detectar opciones filtradas
# 9. Capturar querydata
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
    "inspect_establecimiento_dropdown_outputs"
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
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=False,

        slow_mo=400

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
        "GET VISUAL CONTAINERS"
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

        print("NO COMBOBOX")

        browser.close()

        raise Exception(
            "No se encontró combobox"
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

        total_overlay = loc.count()

        print(f"{selector}: {total_overlay}")

        for i in range(total_overlay):

            try:

                overlay = loc.nth(i)

                if not overlay.is_visible():
                    continue

                bbox = overlay.bounding_box()

                if not bbox:
                    continue

                text = clean_text(
                    overlay.inner_text()
                )

                overlays.append({

                    "locator": overlay,
                    "bbox": bbox,
                    "text": text

                })

            except:
                pass

    print(f"VISIBLE OVERLAYS: {len(overlays)}")

    if len(overlays) == 0:

        screenshot(
            page,
            "no_overlay"
        )

        browser.close()

        raise Exception(
            "No overlays detectados"
        )

    # ========================================================
    # PICK BIGGEST OVERLAY
    # ========================================================

    overlays = sorted(

        overlays,

        key=lambda x:
            x["bbox"]["width"]
            *
            x["bbox"]["height"],

        reverse=True

    )

    overlay = overlays[0]["locator"]

    print("\nOVERLAY TEXT:\n")

    print(overlays[0]["text"][:3000])

    screenshot(
        page,
        "overlay_detected"
    )

    # ========================================================
    # FIND SEARCHBOX
    # ========================================================

    banner(
        "FIND SEARCHBOX"
    )

    searchbox = None

    inputs = overlay.locator(
        "input"
    )

    input_total = inputs.count()

    print(f"INPUTS: {input_total}")

    for i in range(input_total):

        try:

            inp = inputs.nth(i)

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

            input_type = (
                inp.get_attribute(
                    "type"
                ) or ""
            )

            print("\nINPUT")

            print(f"INDEX: {i}")

            print(f"TYPE: {input_type}")

            print(f"PLACEHOLDER: {placeholder}")

            print(f"ARIA: {aria}")

            if (

                "buscar" in placeholder.lower()

                or

                "search" in placeholder.lower()

                or

                "buscar" in aria.lower()

            ):

                searchbox = inp

                print("\nSEARCHBOX REAL DETECTADO")

                break

        except:
            pass

    if not searchbox:

        screenshot(
            page,
            "searchbox_not_found"
        )

        browser.close()

        raise Exception(
            "No se detectó searchbox"
        )

    # ========================================================
    # TYPE LCC
    # ========================================================

    banner(
        "TYPE FILTER"
    )

    value = (
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    searchbox.click(force=True)

    time.sleep(1)

    searchbox.press(
        "Control+A"
    )

    time.sleep(1)

    searchbox.press(
        "Backspace"
    )

    time.sleep(1)

    searchbox.press_sequentially(

        value,

        delay=60

    )

    print(value)

    time.sleep(6)

    screenshot(
        page,
        "typed_lcc"
    )

    # ========================================================
    # DETECT FILTERED OPTIONS
    # ========================================================

    banner(
        "FILTERED OPTIONS"
    )

    option_candidates = overlay.locator(
        "text=SALUD"
    )

    total_options = option_candidates.count()

    print(f"OPTIONS: {total_options}")

    for i in range(total_options):

        try:

            opt = option_candidates.nth(i)

            if not opt.is_visible():
                continue

            text = clean_text(
                opt.inner_text()
            )

            print("\nOPTION")

            print(text)

        except:
            pass

    # ========================================================
    # WAIT RERENDER
    # ========================================================

    banner(
        "WAIT FINAL"
    )

    time.sleep(15)

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

    print(f"PAYLOADS: {len(captured)}")

    print(f"OUTPUT: {OUTPUT_DIR}")

    print("\n")
    print("=" * 80)
    print("INSPECTION COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()