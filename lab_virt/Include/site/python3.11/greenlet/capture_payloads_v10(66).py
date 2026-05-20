# ============================================================
# capture_payloads_v10.py
# ============================================================
#
# PIPELINE FINAL ESTABLE POWER BI
#
# OBJETIVO:
# ----------
# 1. Abrir dashboard
# 2. Abrir panel filtros
# 3. Aplicar filtros territoriales
# 4. Capturar TODOS los /querydata
# 5. Guardar payloads JSON
#
# CAMBIO CRÍTICO V10
# ------------------
#
# open_dropdown()
#
# YA NO usa:
#
#   role="combobox"
#
# AHORA usa:
#
#   CLICK FÍSICO POR COORDENADAS
#
# Porque Power BI:
#
# - recicla DOM
# - reutiliza comboboxes
# - crea overlays ocultos
# - virtualiza slicers
#
# Entonces:
#
# click físico == estabilidad máxima
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
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUt"
    "MGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVk"
    "YWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"
    "&pageName=ReportSection"
)

OUTPUT_DIR = Path("payload_outputs_v10")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# UTIL
# ============================================================

def section(title):

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# WAIT
# ============================================================

def wait_rerender(seconds=10):

    section("WAIT RERENDER")

    time.sleep(seconds)


# ============================================================
# OPEN DASHBOARD
# ============================================================

def open_dashboard(page):

    section("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="domcontentloaded"
    )

    section("WAIT FULL RENDER")

    #
    # Power BI hydration
    #

    time.sleep(30)


# ============================================================
# OPEN FILTERS PANEL
# ============================================================

def open_filters_panel(page):

    section("OPEN FILTERS PANEL")

    buttons = page.locator(".visualContainer")

    count = buttons.count()

    print(f"CONTAINERS: {count}")

    for i in range(count):

        container = buttons.nth(i)

        try:

            txt = container.inner_text(timeout=1000)

        except:
            continue

        if "Filtros" in txt:

            print(f"FOUND FILTERS BUTTON: {i}")

            container.click()

            time.sleep(5)

            return

    raise Exception(
        "No se encontró botón filtros"
    )


# ============================================================
# FIND FILTER CONTAINER STABLE
# ============================================================

def find_filter_container_stable(
    page,
    label
):

    section(
        f"FIND FILTER -> {label}"
    )

    containers = page.locator(
        ".visualContainer"
    )

    count = containers.count()

    print(f"CONTAINERS: {count}")

    for i in range(count):

        container = containers.nth(i)

        try:

            txt = container.inner_text(
                timeout=1000
            )

        except:
            continue

        txt_low = txt.lower()

        combo_count = container.locator(
            "div[role='combobox']"
        ).count()

        if (
            label.lower() in txt_low
            and combo_count > 0
        ):

            print(f"\nFOUND INDEX: {i}")

            print("\nTEXT:\n")
            print(txt[:500])

            return container

    raise Exception(
        f"No se encontró filtro: {label}"
    )


# ============================================================
# OPEN DROPDOWN (V10 FINAL)
# ============================================================

def open_dropdown(
    page,
    container
):

    section("OPEN DROPDOWN")

    box = container.bounding_box()

    if not box:
        raise Exception(
            "No bounding box"
        )

    #
    # CLICK EN FLECHA DERECHA
    #

    x = box["x"] + box["width"] - 25
    y = box["y"] + (
        box["height"] / 2
    )

    print(f"CLICK X: {x}")
    print(f"CLICK Y: {y}")

    #
    # CLICK HUMANO REAL
    #

    page.mouse.click(x, y)

    time.sleep(5)


# ============================================================
# FIND ACTIVE OVERLAY
# ============================================================

def find_active_overlay(page):

    section("FIND ACTIVE OVERLAY")

    selectors = [

        ".slicer-dropdown-menu",

        "div[role='listbox']",

        "div[role='tree']"

    ]

    candidates = []

    for selector in selectors:

        loc = page.locator(selector)

        total = loc.count()

        print(
            f"{selector}: {total}"
        )

        for i in range(total):

            overlay = loc.nth(i)

            try:

                if not overlay.is_visible():
                    continue

                box = overlay.bounding_box()

                if not box:
                    continue

                width = box["width"]
                height = box["height"]

                area = width * height

                txt = overlay.inner_text()

                print("\n----------------")

                print(f"INDEX: {i}")

                print(f"AREA: {area}")

                print(
                    txt[:200]
                )

                #
                # SOLO overlays reales
                #

                if area > 50000:

                    candidates.append(
                        (
                            area,
                            overlay
                        )
                    )

            except:
                pass

    if len(candidates) == 0:

        raise Exception(
            "No active overlay found"
        )

    #
    # ELEGIR MÁS GRANDE
    #

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    chosen = candidates[0][1]

    print("\nACTIVE OVERLAY SELECTED")

    return chosen


# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(
    overlay,
    value
):

    section(
        f"SEARCH -> {value}"
    )

    searchboxes = overlay.locator(
        "input.searchInput"
    )

    count = searchboxes.count()

    print(f"SEARCHBOXES: {count}")

    if count == 0:

        raise Exception(
            "No searchbox found"
        )

    searchbox = searchboxes.first

    searchbox.fill("")

    time.sleep(1)

    searchbox.fill(value)

    time.sleep(10)

    print(
        "SEARCHBOX VALUE:",
        searchbox.input_value()
    )


# ============================================================
# CLICK OPTION
# ============================================================

def click_option(
    overlay,
    expected_option
):

    section(
        f"CLICK OPTION -> {expected_option}"
    )

    options = overlay.locator(
        ".slicerText"
    )

    count = options.count()

    print(f"OPTIONS: {count}")

    for i in range(count):

        option = options.nth(i)

        try:

            txt = option.inner_text()

        except:
            continue

        txt_clean = txt.strip()

        print("\nOPTION:")
        print(txt_clean)

        if (
            expected_option.upper()
            in txt_clean.upper()
        ):

            print("\nMATCH FOUND")

            option.click()

            time.sleep(5)

            return

    raise Exception(
        f"No se encontró opción: "
        f"{expected_option}"
    )


# ============================================================
# CLOSE OVERLAY
# ============================================================

def close_overlay(page):

    section("CLOSE OVERLAY")

    page.keyboard.press("Escape")

    time.sleep(2)

    page.mouse.click(20, 20)

    time.sleep(2)


# ============================================================
# APPLY FILTER FINAL
# ============================================================

def apply_filter(
    page,
    label,
    search_value_text,
    expected_option
):

    section(
        f"APPLY FILTER -> {label}"
    )

    #
    # FIND FILTER
    #

    container = find_filter_container_stable(
        page,
        label
    )

    #
    # OPEN DROPDOWN
    #

    open_dropdown(
        page,
        container
    )

    #
    # OVERLAY
    #

    overlay = find_active_overlay(
        page
    )

    #
    # SEARCH
    #

    search_value(
        overlay,
        search_value_text
    )

    #
    # CLICK OPTION
    #

    click_option(
        overlay,
        expected_option
    )

    #
    # WAIT RERENDER
    #

    wait_rerender()

    #
    # CLOSE OVERLAY
    #

    close_overlay(page)

    #
    # REOPEN FILTERS PANEL
    #

    open_filters_panel(page)

    time.sleep(5)


# ============================================================
# RESET GRUPO PRODUCTO
# ============================================================

def reset_grupo_producto(page):

    section(
        "RESET GRUPO PRODUCTO"
    )

    container = find_filter_container_stable(
        page,
        "Grupo Producto"
    )

    open_dropdown(
        page,
        container
    )

    overlay = find_active_overlay(
        page
    )

    options = overlay.locator(
        ".slicerText"
    )

    count = options.count()

    print(f"OPTIONS: {count}")

    for i in range(count):

        option = options.nth(i)

        try:

            txt = option.inner_text()

        except:
            continue

        print(txt)

        if (
            "Seleccionar todo".upper()
            in txt.upper()
        ):

            option.click()

            time.sleep(5)

            break

    wait_rerender()

    close_overlay(page)

    open_filters_panel(page)

    time.sleep(5)


# ============================================================
# CAPTURE QUERYDATA
# ============================================================

payload_counter = 0

def handle_response(response):

    global payload_counter

    if "/querydata" in response.url:

        section(
            "QUERYDATA CAPTURADA"
        )

        print(
            f"STATUS: {response.status}"
        )

        try:

            txt = response.text()

        except:
            return

        payload_counter += 1

        filename = (
            OUTPUT_DIR
            / f"payload_{payload_counter:03d}.json"
        )

        filename.write_text(
            txt,
            encoding="utf-8"
        )

        print(
            f"PAYLOAD SAVED: "
            f"{filename.name}"
        )


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    #
    # LISTENER
    #

    page.on(
        "response",
        handle_response
    )

    #
    # OPEN DASHBOARD
    #

    open_dashboard(page)

    #
    # OPEN FILTERS
    #

    open_filters_panel(page)

    #
    # MACROREGION
    #

    apply_filter(
        page,
        label="MACROREGION",
        search_value_text="NORTE",
        expected_option="NORTE"
    )

    #
    # INSTITUCION
    #

    apply_filter(
        page,
        label="Institución",
        search_value_text="GOBIERNO",
        expected_option="GOBIERNO REGIONAL"
    )

    #
    # UNIDAD EJECUTORA
    #

    apply_filter(
        page,
        label="Unidad ejecutora",
        search_value_text="LUCIANO",
        expected_option=(
            "SALUD LUCIANO "
            "CASTILLO COLONNA"
        )
    )

    #
    # RESET PRODUCTO
    #

    reset_grupo_producto(page)

    #
    # FINAL WAIT
    #

    section("FINAL WAIT")

    time.sleep(20)

    #
    # SUMMARY
    #

    section("SUMMARY")

    print(
        f"TOTAL PAYLOADS: "
        f"{payload_counter}"
    )

    print(
        f"OUTPUT DIR: "
        f"{OUTPUT_DIR}"
    )

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()