# ============================================================
# detect_fresh_overlay.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Detectar EXCLUSIVAMENTE el overlay nuevo generado
# DESPUÉS de abrir un slicer Power BI.
#
# Esto resuelve:
#
#   - overlays persistentes
#   - overlays reciclados
#   - listbox viejos
#   - dropdowns residuales
#
# ============================================================
# PIPELINE
# ------------------------------------------------------------
#
# 1. detectar overlays BEFORE
# 2. abrir dropdown
# 3. detectar overlays AFTER
# 4. aislar overlays nuevos
# 5. inspeccionar overlay fresco
#
# ============================================================

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"

OUTPUT_DIR = Path("fresh_overlay_outputs")

SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

OUTPUT_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

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

    print(
        f"CONTAINERS: {total}"
    )

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

            print(
                f"SLICER ENCONTRADO: {i}"
            )

            print(text[:500])

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

    print(
        f"COMBOBOXES: {total}"
    )

    for i in range(total):

        try:

            combo = combos.nth(i)

            if combo.is_visible():

                print(
                    f"VISIBLE COMBO: {i}"
                )

                return combo

        except:
            pass

    return None

# ============================================================
# GET OVERLAY SNAPSHOT
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
                        "height": bbox["height"] if bbox else None
                    }

                    snapshot.append(entry)

                except:
                    pass

        except:
            pass

    return snapshot

# ============================================================
# PRINT SNAPSHOT
# ============================================================

def print_snapshot(
    title,
    snapshot
):

    banner(title)

    print(
        f"OVERLAYS: {len(snapshot)}"
    )

    for i, item in enumerate(snapshot):

        print("\n")
        print("-" * 50)

        print(
            f"OVERLAY {i}"
        )

        print(
            f"SELECTOR: {item['selector']}"
        )

        print(
            f"INDEX: {item['index']}"
        )

        print(
            f"POSITION: "
            f"{item['x']}, "
            f"{item['y']}"
        )

        print(
            f"SIZE: "
            f"{item['width']} x "
            f"{item['height']}"
        )

        print(
            item["text"][:300]
        )

# ============================================================
# FIND FRESH OVERLAYS
# ============================================================

def detect_fresh_overlays(
    before,
    after
):

    banner(
        "DETECTANDO OVERLAYS NUEVOS"
    )

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

    print(
        f"FRESH OVERLAYS: {len(fresh)}"
    )

    return fresh

# ============================================================
# OPEN DROPDOWN
# ============================================================

def open_dropdown(combo):

    banner("OPEN DROPDOWN")

    combo.click(force=True)

    time.sleep(4)

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    context = browser.new_context()

    page = context.new_page()

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    banner("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="networkidle"
    )

    time.sleep(15)

    page.reload(
        wait_until="networkidle"
    )

    time.sleep(10)

    screenshot(
        page,
        "01_dashboard_loaded"
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
        "02_filters_opened"
    )

    # ========================================================
    # TARGET SLICER
    # ========================================================

    container = find_slicer_container(
        page,
        "Grupo Producto"
    )

    if not container:

        print("NO CONTAINER")

        input()

        browser.close()

        raise Exception(
            "NO CONTAINER"
        )

    combo = find_combobox_inside_container(
        container
    )

    if not combo:

        print("NO COMBO")

        input()

        browser.close()

        raise Exception(
            "NO COMBO"
        )

    # ========================================================
    # BEFORE SNAPSHOT
    # ========================================================

    before = get_overlay_snapshot(
        page
    )

    print_snapshot(
        "OVERLAYS BEFORE",
        before
    )

    # ========================================================
    # OPEN DROPDOWN
    # ========================================================

    open_dropdown(combo)

    screenshot(
        page,
        "03_dropdown_opened"
    )

    # ========================================================
    # AFTER SNAPSHOT
    # ========================================================

    after = get_overlay_snapshot(
        page
    )

    print_snapshot(
        "OVERLAYS AFTER",
        after
    )

    # ========================================================
    # DETECT FRESH
    # ========================================================

    fresh = detect_fresh_overlays(
        before,
        after
    )

    # ========================================================
    # PRINT FRESH
    # ========================================================

    print_snapshot(
        "FRESH OVERLAYS",
        fresh
    )

    # ========================================================
    # INSPECT FRESH
    # ========================================================

    banner(
        "INSPECCIONANDO OVERLAYS NUEVOS"
    )

    for i, item in enumerate(fresh):

        print("\n")
        print("=" * 50)

        print(
            f"FRESH OVERLAY {i}"
        )

        print(
            f"SELECTOR: "
            f"{item['selector']}"
        )

        print(
            f"POSITION: "
            f"{item['x']}, "
            f"{item['y']}"
        )

        print(
            f"SIZE: "
            f"{item['width']} x "
            f"{item['height']}"
        )

        print("\nTEXT:\n")

        print(item["text"][:2000])

    # ========================================================
    # FINAL SCREENSHOT
    # ========================================================

    screenshot(
        page,
        "99_final"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    banner("SUMMARY")

    print(
        f"OVERLAYS BEFORE: {len(before)}"
    )

    print(
        f"OVERLAYS AFTER: {len(after)}"
    )

    print(
        f"FRESH OVERLAYS: {len(fresh)}"
    )

    print("\n")
    print("=" * 70)
    print("FRESH OVERLAY DETECTION COMPLETADA")
    print("=" * 70)

    input("\nENTER PARA CERRAR...")

    browser.close()