# ============================================================
# apply_lcc_territorial_filters.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Aplicar territorialidad REAL:
#
#   1. MACROREGION = NORTE
#   2. Institución = GOBIERNO REGIONAL
#   3. Unidad ejecutora =
#      SALUD LUCIANO CASTILLO COLONNA
#
# Y asegurar:
#
#   Grupo Producto       -> Todas
#   Listado Productos    -> Todas
#   Forma Farmacéutica   -> Todas
#   ATC                  -> Todas
#   Tipo de Suministro   -> Todas
#   EE.SS. Ejecutoras    -> Todas
#   Petitorio            -> Todas
#   Periodo              -> Todas
#   Tipo EE.SS.          -> Todas
#
# ============================================================

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"

OUTPUT_DIR = Path("territorial_filter_outputs")

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
    print("=" * 70)
    print(title)
    print("=" * 70)

# ------------------------------------------------------------

def screenshot(page, name):

    page.screenshot(
        path=str(
            SCREENSHOT_DIR / f"{name}.png"
        ),
        full_page=True
    )

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

            out = {
                "url": response.url,
                "status": response.status,
                "method": request.method,
                "body": request.post_data
            }

            with open(
                PAYLOAD_DIR / f"query_{payload_counter}.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    out,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            captured.append(out)

            print("\n")
            print("=" * 70)
            print("QUERYDATA CAPTURADA")
            print("=" * 70)

            print(f"STATUS: {response.status}")

        except Exception as e:

            print(e)

    page.on(
        "response",
        handle_response
    )

    return captured

# ============================================================
# FIND SLICER CONTAINER
# ============================================================

def find_slicer_container(
    page,
    slicer_name
):

    banner(
        f"BUSCANDO SLICER: {slicer_name}"
    )

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

        try:

            container = containers.nth(i)

            if not container.is_visible():
                continue

            text = container.inner_text(
                timeout=3000
            )

            if not text:
                continue

            text = text.strip().upper()

            if slicer_name.upper() not in text:
                continue

            combos = container.locator(
                "[role='combobox']"
            )

            if combos.count() == 0:
                continue

            print(f"SLICER ENCONTRADO: {i}")

            print(text[:400])

            return container

        except:
            pass

    print("NO SLICER")

    return None

# ============================================================
# FIND COMBOBOX
# ============================================================

def find_combobox_inside_container(
    container
):

    combos = container.locator(
        "[role='combobox']"
    )

    total = combos.count()

    print(f"COMBOBOXES: {total}")

    for i in range(total):

        try:

            combo = combos.nth(i)

            if combo.is_visible():

                print(f"VISIBLE COMBO: {i}")

                return combo

        except:
            pass

    return None

# ============================================================
# GET OVERLAYS
# ============================================================

def get_overlay_snapshot(page):

    snapshot = []

    selectors = [

        "div[role='listbox']",
        "div[role='tree']",
        "div[aria-label]"
    ]

    for selector in selectors:

        try:

            loc = page.locator(selector)

            total = loc.count()

            for i in range(total):

                try:

                    item = loc.nth(i)

                    if not item.is_visible():
                        continue

                    text = item.inner_text()

                    if not text:
                        continue

                    text = text.strip()

                    if len(text) < 3:
                        continue

                    bbox = item.bounding_box()

                    entry = {

                        "selector": selector,
                        "index": i,
                        "text": text[:500],
                        "x": bbox["x"] if bbox else None,
                        "y": bbox["y"] if bbox else None,
                        "width": bbox["width"] if bbox else None,
                        "height": bbox["height"] if bbox else None,
                    }

                    snapshot.append(entry)

                except:
                    pass

        except:
            pass

    return snapshot

# ============================================================
# DETECT FRESH OVERLAYS
# ============================================================

def detect_fresh_overlays(
    before,
    after
):

    fresh = []

    before_keys = set()

    for item in before:

        key = (
            item["selector"],
            item["x"],
            item["y"],
            item["width"],
            item["height"]
        )

        before_keys.add(key)

    for item in after:

        key = (
            item["selector"],
            item["x"],
            item["y"],
            item["width"],
            item["height"]
        )

        if key not in before_keys:

            fresh.append(item)

    return fresh

# ============================================================
# FIND FRESH OVERLAY LOCATOR
# ============================================================

def find_fresh_overlay_locator(
    page,
    fresh
):

    selectors = [

        "div[role='listbox']",
        "div[role='tree']",
        "div[aria-label]"
    ]

    for selector in selectors:

        loc = page.locator(selector)

        total = loc.count()

        for i in range(total):

            try:

                item = loc.nth(i)

                if not item.is_visible():
                    continue

                bbox = item.bounding_box()

                if not bbox:
                    continue

                for fresh_item in fresh:

                    if (
                        abs(bbox["x"] - fresh_item["x"]) < 5
                        and
                        abs(bbox["y"] - fresh_item["y"]) < 5
                    ):

                        return item

            except:
                pass

    return None

# ============================================================
# OPEN DROPDOWN
# ============================================================

def open_dropdown(
    page,
    combo
):

    before = get_overlay_snapshot(page)

    combo.click(force=True)

    time.sleep(4)

    after = get_overlay_snapshot(page)

    fresh = detect_fresh_overlays(
        before,
        after
    )

    print(f"FRESH OVERLAYS: {len(fresh)}")

    overlay = find_fresh_overlay_locator(
        page,
        fresh
    )

    return overlay

# ============================================================
# SEARCH INSIDE OVERLAY
# ============================================================

def search_option_inside_overlay(
    overlay,
    text
):

    banner(
        f"BUSCANDO OPCION: {text}"
    )

    candidates = [

        overlay.locator(
            f"text={text}"
        ),

        overlay.locator(
            f"span:has-text('{text}')"
        ),

        overlay.locator(
            f"div:has-text('{text}')"
        ),

        overlay.locator(
            f"label:has-text('{text}')"
        )
    ]

    for locator in candidates:

        try:

            total = locator.count()

            print(f"CANDIDATOS: {total}")

            for i in range(total):

                item = locator.nth(i)

                if not item.is_visible():
                    continue

                value = item.inner_text()

                if text.upper() in value.upper():

                    print(f"OPTION FOUND: {value}")

                    return item

        except:
            pass

    print("NO OPTION")

    return None

# ============================================================
# CLICK OPTION
# ============================================================

def click_overlay_option(option):

    option.click(force=True)

    time.sleep(10)

# ============================================================
# RESET TO TODAS
# ============================================================

def reset_slicer_to_all(
    page,
    slicer_name
):

    banner(
        f"RESET: {slicer_name}"
    )

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:
        return False

    combo = find_combobox_inside_container(
        container
    )

    if not combo:
        return False

    overlay = open_dropdown(
        page,
        combo
    )

    if not overlay:
        return False

    option = search_option_inside_overlay(
        overlay,
        "Todas"
    )

    if not option:
        return False

    click_overlay_option(option)

    print(f"{slicer_name} -> TODAS")

    return True

# ============================================================
# APPLY TERRITORIAL FILTER
# ============================================================

def apply_filter(
    page,
    slicer_name,
    value
):

    banner(
        f"APLICANDO {slicer_name} = {value}"
    )

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:
        return False

    combo = find_combobox_inside_container(
        container
    )

    if not combo:
        return False

    overlay = open_dropdown(
        page,
        combo
    )

    if not overlay:
        return False

    # ========================================================
    # SEARCHBOX
    # ========================================================

    searchboxes = overlay.locator(
        "input"
    )

    if searchboxes.count() > 0:

        try:

            sb = searchboxes.first

            sb.click(force=True)

            time.sleep(1)

            sb.press("Control+A")

            sb.press("Backspace")

            time.sleep(1)

            sb.press_sequentially(
                value,
                delay=40
            )

            time.sleep(4)

        except:
            pass

    option = search_option_inside_overlay(
        overlay,
        value
    )

    if not option:
        return False

    click_overlay_option(option)

    print(f"FILTER OK: {value}")

    return True

# ============================================================
# VERIFY
# ============================================================

def verify_filter(
    page,
    slicer_name,
    expected
):

    banner(
        f"VERIFY: {slicer_name}"
    )

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:
        return

    text = container.inner_text()

    print(text)

    if expected.upper() in text.upper():

        print("OK")

    else:

        print("WARNING")

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    context = browser.new_context(
        ignore_https_errors=True
    )

    page = context.new_page()

    page.set_default_timeout(60000)

    captured = setup_capture(page)

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    banner("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="domcontentloaded"
    )

    time.sleep(25)

    screenshot(
        page,
        "01_dashboard"
    )

    # ========================================================
    # OPEN FILTERS
    # ========================================================

    banner("OPEN FILTERS")

    try:

        filtros = page.locator(
            "text=Filtros"
        )

        if filtros.count() > 0:

            filtros.first.click(
                force=True
            )

            time.sleep(5)

    except:
        pass

    screenshot(
        page,
        "02_filters"
    )

    # ========================================================
    # RESET NON TERRITORIAL
    # ========================================================

    NON_TERRITORIAL = [

        "Grupo Producto",
        "Listado",
        "Forma Farmacéutica",
        "ATC",
        "Tipo de Suministro",
        "EE.SS. Ejecutoras",
        "Petitorio",
        "Periodo",
        "Tipo EE.SS."
    ]

    for slicer in NON_TERRITORIAL:

        try:

            reset_slicer_to_all(
                page,
                slicer
            )

        except Exception as e:

            print(e)

    # ========================================================
    # TERRITORIAL FILTERS
    # ========================================================

    apply_filter(
        page,
        "MACROREGION",
        "NORTE"
    )

    apply_filter(
        page,
        "Institución",
        "GOBIERNO REGIONAL"
    )

    apply_filter(
        page,
        "Unidad ejecutora",
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    # ========================================================
    # VERIFY
    # ========================================================

    verify_filter(
        page,
        "MACROREGION",
        "NORTE"
    )

    verify_filter(
        page,
        "Institución",
        "GOBIERNO REGIONAL"
    )

    verify_filter(
        page,
        "Unidad ejecutora",
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    # ========================================================
    # FINAL WAIT
    # ========================================================

    banner("WAIT FINAL")

    time.sleep(20)

    screenshot(
        page,
        "99_final"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    banner("SUMMARY")

    print(
        f"PAYLOADS: {len(captured)}"
    )

    print(
        f"OUTPUT: {OUTPUT_DIR}"
    )

    print("\n")
    print("=" * 70)
    print("TERRITORIAL FILTERING COMPLETADO")
    print("=" * 70)

    input("\nENTER PARA CERRAR...")

    browser.close()