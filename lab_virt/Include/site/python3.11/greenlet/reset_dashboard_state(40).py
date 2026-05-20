# ============================================================
# reset_dashboard_state.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Limpiar completamente el estado persistente Power BI:
#
#   Grupo Producto       -> Todas
#   ATC                  -> Todas
#   Forma Farmacéutica   -> Todas
#   Listado Productos    -> Todas
#
# ANTES de aplicar:
#
#   Unidad ejecutora
#   Macroregion
#   Institucion
#
# ============================================================
# PIPELINE NUEVO
# ------------------------------------------------------------
#
# open_dropdown()
# detect_overlay()
# search_inside_overlay()
# click_overlay_option()
#
# ============================================================

import json
import time
from pathlib import Path

from playwright.sync_api import (
    sync_playwright
)

# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"

OUTPUT_DIR = Path("reset_dashboard_outputs")

PAYLOAD_DIR = OUTPUT_DIR / "payloads"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

OUTPUT_DIR.mkdir(exist_ok=True)
PAYLOAD_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

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

            body = request.post_data

            out = {
                "url": response.url,
                "status": response.status,
                "body": body
            }

            out_file = (
                PAYLOAD_DIR /
                f"query_{payload_counter}.json"
            )

            with open(
                out_file,
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
            print("QUERYDATA")
            print("=" * 70)

            print(
                f"STATUS: {response.status}"
            )

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
# OPEN DROPDOWN
# ============================================================

def open_dropdown(combo):

    banner("OPEN DROPDOWN")

    combo.click(force=True)

    time.sleep(5)

# ============================================================
# FIND ACTIVE OVERLAY
# ============================================================

def find_active_overlay(page):

    banner("BUSCANDO OVERLAY ACTIVO")

    selectors = [

        "div[role='listbox']",
        "div[role='tree']",
        "div[aria-label]"
    ]

    for selector in selectors:

        try:

            overlays = page.locator(selector)

            total = overlays.count()

            print(
                f"{selector}: {total}"
            )

            for i in range(total):

                overlay = overlays.nth(i)

                if not overlay.is_visible():
                    continue

                text = overlay.inner_text()

                if not text:
                    continue

                if len(text.strip()) < 3:
                    continue

                print("\n")
                print("OVERLAY DETECTADO")
                print(text[:1000])

                return overlay

        except:
            pass

    print("NO OVERLAY")

    return None

# ============================================================
# SEARCH INSIDE OVERLAY
# ============================================================

def search_inside_overlay(
    overlay,
    option_text
):

    banner(
        f"BUSCANDO OPCION: {option_text}"
    )

    candidates = [

        overlay.locator(
            f"text={option_text}"
        ),

        overlay.locator(
            f"span:has-text('{option_text}')"
        ),

        overlay.locator(
            f"div:has-text('{option_text}')"
        ),

        overlay.locator(
            f"label:has-text('{option_text}')"
        )
    ]

    for locator in candidates:

        try:

            total = locator.count()

            print(
                f"CANDIDATOS: {total}"
            )

            for i in range(total):

                item = locator.nth(i)

                if not item.is_visible():
                    continue

                text = item.inner_text()

                if option_text.upper() in text.upper():

                    print(
                        f"OPCION: {text}"
                    )

                    return item

        except:
            pass

    print("NO OPTION")

    return None

# ============================================================
# CLICK OPTION
# ============================================================

def click_overlay_option(option):

    banner("CLICK OPTION")

    option.click(force=True)

    time.sleep(8)

# ============================================================
# RESET SLICER TO TODAS
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

    open_dropdown(combo)

    overlay = find_active_overlay(page)

    if not overlay:
        return False

    option = search_inside_overlay(
        overlay,
        "Todas"
    )

    if not option:
        return False

    click_overlay_option(option)

    print(
        f"{slicer_name} -> TODAS"
    )

    return True

# ============================================================
# VERIFY STATE
# ============================================================

def verify_state(
    page,
    slicer_name
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

    if "TODAS" in text.upper():

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

    context = browser.new_context()

    page = context.new_page()

    captured = setup_capture(page)

    # ========================================================
    # RESET VISUAL STATE
    # ========================================================

    banner("RESET VISUAL STATE")

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
        "01_initial"
    )

    # ========================================================
    # OPEN FILTER PANEL
    # ========================================================

    banner("ABRIENDO FILTROS")

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
    # RESET SLICERS
    # ========================================================

    reset_slicer_to_all(
        page,
        "Grupo Producto"
    )

    reset_slicer_to_all(
        page,
        "ATC"
    )

    reset_slicer_to_all(
        page,
        "Forma Farmacéutica"
    )

    reset_slicer_to_all(
        page,
        "Listado"
    )

    # ========================================================
    # VERIFY
    # ========================================================

    verify_state(
        page,
        "Grupo Producto"
    )

    verify_state(
        page,
        "ATC"
    )

    verify_state(
        page,
        "Forma Farmacéutica"
    )

    verify_state(
        page,
        "Listado"
    )

    # ========================================================
    # WAIT FINAL
    # ========================================================

    banner("WAIT FINAL RENDER")

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
    print("RESET DASHBOARD COMPLETADO")
    print("=" * 70)

    input("\nENTER PARA CERRAR...")

    browser.close()