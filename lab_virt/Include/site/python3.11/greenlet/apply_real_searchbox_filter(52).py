# ============================================================
# apply_real_searchbox_filter.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Usar el searchbox REAL detectado:
#
#     input.searchInput
#
# para:
#
# 1. Abrir slicer Establecimiento
# 2. Activar textbox REAL
# 3. Escribir:
#
#       LUCIANO
#
# 4. Esperar rerender
# 5. Detectar opciones filtradas
# 6. Click:
#
#       SALUD LUCIANO CASTILLO COLONNA
#
# 7. Capturar querydata AFTER
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
    "real_searchbox_filter_outputs"
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

        total = loc.count()

        for i in range(total):

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

    overlay = overlays[0]["locator"]

    print("\nOVERLAY DETECTADO\n")

    print(overlays[0]["text"][:2000])

    return overlay

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=False,

        slow_mo=350

    )

    context = browser.new_context(

        viewport={
            "width": 1800,
            "height": 1100
        },

        ignore_https_errors=True

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
    # WAIT POWER BI
    # ========================================================

    banner(
        "WAIT POWER BI RENDER"
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

    print(

        clean_text(
            container.inner_text()
        )

    )

    screenshot(
        page,
        "container_4"
    )

    # ========================================================
    # OPEN COMBOBOX
    # ========================================================

    banner(
        "OPEN COMBOBOX"
    )

    combo = container.locator(
        "[role='combobox']"
    ).first

    combo.click(force=True)

    time.sleep(5)

    screenshot(
        page,
        "dropdown_opened"
    )

    # ========================================================
    # GET OVERLAY
    # ========================================================

    banner(
        "GET ACTIVE OVERLAY"
    )

    overlay = get_active_overlay(
        page
    )

    if not overlay:

        raise Exception(
            "NO OVERLAY"
        )

    # ========================================================
    # REAL SEARCHBOX
    # ========================================================

    banner(
        "DETECT REAL SEARCHBOX"
    )

    searchboxes = page.locator(
        "input.searchInput"
    )

    total_searchboxes = searchboxes.count()

    print(f"SEARCHBOXES: {total_searchboxes}")

    if total_searchboxes == 0:

        screenshot(
            page,
            "no_searchbox"
        )

        raise Exception(
            "NO SEARCHBOX"
        )

    searchbox = searchboxes.last

    print("\nSEARCHBOX FOUND")

    print(searchbox)

    screenshot(
        page,
        "searchbox_detected"
    )

    # ========================================================
    # CLICK SEARCHBOX
    # ========================================================

    banner(
        "CLICK SEARCHBOX"
    )

    searchbox.click(force=True)

    time.sleep(2)

    # ========================================================
    # CLEAR
    # ========================================================

    banner(
        "CLEAR SEARCHBOX"
    )

    searchbox.fill("")

    time.sleep(1)

    # ========================================================
    # TYPE LUCIANO
    # ========================================================

    banner(
        "TYPE: LUCIANO"
    )

    searchbox.fill(
        "LUCIANO"
    )

    time.sleep(8)

    screenshot(
        page,
        "typed_luciano"
    )

    # ========================================================
    # INSPECT OVERLAY AFTER FILTER
    # ========================================================

    banner(
        "OVERLAY AFTER FILTER"
    )

    overlay_text = clean_text(
        overlay.inner_text()
    )

    print("\n")

    print(overlay_text[:4000])

    # ========================================================
    # SEARCH OPTIONS
    # ========================================================

    banner(
        "SEARCH OPTIONS"
    )

    options = overlay.locator(
        ".slicerItemContainer"
    )

    total_options = options.count()

    print(f"OPTIONS: {total_options}")

    selected = None

    for i in range(total_options):

        try:

            option = options.nth(i)

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

                selected = option

                print("\nMATCH FOUND")

                break

        except Exception as e:

            print(e)

    # ========================================================
    # CLICK OPTION
    # ========================================================

    if selected:

        banner(
            "CLICK OPTION"
        )

        selected.click(force=True)

        print("\nOPTION SELECTED")

        time.sleep(20)

        screenshot(
            page,
            "option_selected"
        )

    else:

        print("\nNO MATCH FOUND")

        screenshot(
            page,
            "no_match"
        )

    # ========================================================
    # FINAL WAIT
    # ========================================================

    banner(
        "FINAL WAIT"
    )

    time.sleep(15)

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
    print("REAL SEARCHBOX FILTER COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()