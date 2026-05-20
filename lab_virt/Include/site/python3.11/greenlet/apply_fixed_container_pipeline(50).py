# ============================================================
# apply_fixed_container_pipeline.py
# ============================================================
# PIPELINE FINAL ESTABLE
# ------------------------------------------------------------
# Usa:
#
#   containers.nth(...)
#
# DIRECTAMENTE.
#
# SIN:
#   - matching textual
#   - heurísticas DOM
#   - aria-labels
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
    "fixed_container_pipeline_outputs"
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

    print(overlays[0]["text"][:1000])

    return overlay

# ============================================================
# APPLY FILTER USING FIXED CONTAINER
# ============================================================

def apply_filter(

    page,

    containers,

    container_index,

    search_text,

    target_text

):

    banner(
        f"APPLY FILTER CONTAINER {container_index}"
    )

    container = containers.nth(
        container_index
    )

    text = clean_text(
        container.inner_text()
    )

    print("\nCONTAINER TEXT\n")

    print(text[:1000])

    screenshot(
        page,
        f"container_{container_index}"
    )

    # ========================================================
    # COMBOBOX
    # ========================================================

    combos = container.locator(
        "[role='combobox']"
    )

    combo_total = combos.count()

    print(f"\nCOMBOBOXES: {combo_total}")

    if combo_total == 0:

        print("NO COMBOBOX")

        return False

    combo = combos.first

    # ========================================================
    # OPEN
    # ========================================================

    banner(
        "OPEN DROPDOWN"
    )

    combo.click(force=True)

    time.sleep(5)

    screenshot(
        page,
        f"dropdown_{container_index}"
    )

    # ========================================================
    # OVERLAY
    # ========================================================

    overlay = get_active_overlay(
        page
    )

    if not overlay:

        print("NO OVERLAY")

        return False

    # ========================================================
    # ACTIVATE SEARCH MODE
    # ========================================================

    banner(
        "ACTIVATE SEARCH"
    )

    overlay.click(force=True)

    time.sleep(2)

    # ========================================================
    # TYPE
    # ========================================================

    banner(
        f"TYPE: {search_text}"
    )

    page.keyboard.type(

        search_text,

        delay=90

    )

    time.sleep(8)

    screenshot(
        page,
        f"typed_{container_index}"
    )

    # ========================================================
    # OPTIONS
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

            if target_text.lower() in text.lower():

                selected = option

                print("\nMATCH FOUND")

                break

        except:
            pass

    if not selected:

        print("\nNO MATCH")

        screenshot(
            page,
            f"no_match_{container_index}"
        )

        return False

    # ========================================================
    # CLICK
    # ========================================================

    banner(
        "CLICK OPTION"
    )

    selected.click(force=True)

    print("\nOPTION SELECTED")

    time.sleep(15)

    screenshot(
        page,
        f"selected_{container_index}"
    )

    return True

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
    # GET CONTAINERS
    # ========================================================

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    banner(
        "TOTAL CONTAINERS"
    )

    print(total)

    # ========================================================
    # APPLY ESTABLECIMIENTO
    # CONTAINER 4
    # ========================================================

    apply_filter(

        page,

        containers,

        4,

        "LUCIANO",

        "SALUD LUCIANO CASTILLO COLONNA"

    )

    # ========================================================
    # WAIT FINAL
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
    # DOWNLOAD BUTTON
    # CONTAINER 16
    # ========================================================

    banner(
        "DOWNLOAD CONTAINER"
    )

    download_container = containers.nth(16)

    print(

        clean_text(
            download_container.inner_text()
        )

    )

    screenshot(
        page,
        "download_container"
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
    print("FIXED CONTAINER PIPELINE COMPLETED")
    print("=" * 80)

    input("\nENTER PARA CERRAR...")

    browser.close()