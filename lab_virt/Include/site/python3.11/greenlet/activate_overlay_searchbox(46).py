# ============================================================
# activate_overlay_searchbox.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# 1. Abrir dashboard
# 2. Ir SOLO a:
#
#       CONTAINER 4
#       Establecimiento
#
# 3. Abrir dropdown
# 4. Detectar overlay
# 5. ACTIVAR búsqueda incremental
# 6. Escribir:
#
#       SALUD LUCIANO
#
# 7. Esperar rerender
# 8. Reinspeccionar overlay
# 9. Detectar opciones filtradas
# 10. Click exacto
# 11. Capturar querydata AFTER
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
    "activate_overlay_searchbox_outputs"
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

        slow_mo=350

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

    print("\nOVERLAY DETECTADO:\n")

    print(overlays[0]["text"][:3000])

    screenshot(
        page,
        "overlay_detected"
    )

    # ========================================================
    # ACTIVATE SEARCH MODE
    # ========================================================

    banner(
        "ACTIVATE SEARCH MODE"
    )

    overlay.click(force=True)

    time.sleep(2)

    screenshot(
        page,
        "overlay_clicked"
    )

    # ========================================================
    # TYPE DIRECTLY
    # ========================================================

    banner(
        "TYPE DIRECTLY"
    )

    search_value = (
        "SALUD LUCIANO"
    )

    page.keyboard.type(

        search_value,

        delay=90

    )

    print(search_value)

    # ========================================================
    # WAIT RERENDER
    # ========================================================

    banner(
        "WAIT RERENDER"
    )

    time.sleep(8)

    screenshot(
        page,
        "after_typing"
    )

    # ========================================================
    # INSPECT OVERLAY AGAIN
    # ========================================================

    banner(
        "REINSPECT OVERLAY"
    )

    overlay_text = clean_text(
        overlay.inner_text()
    )

    print("\nOVERLAY AFTER:\n")

    print(overlay_text[:4000])

    # ========================================================
    # DETECT FILTERED OPTIONS
    # ========================================================

    banner(
        "FILTERED OPTIONS"
    )

    option_candidates = overlay.locator(
        "text=SALUD"
    )

    option_total = option_candidates.count()

    print(f"OPTIONS: {option_total}")

    selected_option = None

    for i in range(option_total):

        try:

            option = option_candidates.nth(i)

            if not option.is_visible():
                continue

            text = clean_text(
                option.inner_text()
            )

            print("\nOPTION")

            print(text)

            if (

                "LUCIANO" in text.upper()

                or

                "CASTILLO" in text.upper()

                or

                "SALUD" in text.upper()

            ):

                selected_option = option

        except:
            pass

    # ========================================================
    # CLICK OPTION
    # ========================================================

    if selected_option:

        banner(
            "CLICK OPTION"
        )

        selected_option.click(
            force=True
        )

        print("\nOPTION CLICKED")

        time.sleep(15)

        screenshot(
            page,
            "option_selected"
        )

    else:

        print("\nNO MATCHING OPTION")

    # ========================================================
    # FINAL WAIT
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
    print("SEARCH ACTIVATION COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()