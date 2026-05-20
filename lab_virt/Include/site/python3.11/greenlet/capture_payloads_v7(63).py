# ============================================================
# capture_payloads_v7.py
# ============================================================
#
# v7 — OVERLAY-SCOPED SEARCHBOX FIX
# ============================================================
#
# PROBLEMA REAL IDENTIFICADO
# --------------------------
#
# El searchbox global:
#
#     page.locator("input.searchInput")
#
# estaba capturando:
#
# - overlays viejos
# - inputs reciclados
# - DOM residual
# - searchbox incorrecto
#
# Entonces:
#
# - el texto NO llegaba al slicer UE
# - las opciones NO cambiaban
# - wait_options_refresh() timeout
#
# SOLUCIÓN DEFINITIVA
# -------------------
#
# 1. detectar overlay ACTIVO visible
# 2. buscar searchbox SOLO dentro overlay
# 3. escribir dentro overlay correcto
# 4. verificar input_value()
# 5. esperar refresh real
#
# ============================================================

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

HEADLESS = False

OUTPUT_DIR = Path(
    "capture_payloads_v7_outputs"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)

PAYLOAD_DIR = (
    OUTPUT_DIR / "payloads"
)

PAYLOAD_DIR.mkdir(
    exist_ok=True
)

# ============================================================
# GLOBALS
# ============================================================

payload_counter = 0

captured_payloads = []


# ============================================================
# LOG
# ============================================================

def section(title):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


# ============================================================
# SAVE PAYLOAD
# ============================================================

def save_payload(text):

    global payload_counter

    payload_counter += 1

    filename = (
        PAYLOAD_DIR /
        f"payload_{payload_counter:03d}.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)

    print(
        f"PAYLOAD SAVED: {filename.name}"
    )


# ============================================================
# RESPONSE HANDLER
# ============================================================

def handle_response(response):

    try:

        url = response.url.lower()

        if "/querydata" not in url:
            return

        section("QUERYDATA CAPTURADA")

        print(f"STATUS: {response.status}")

        text = response.text()

        captured_payloads.append(text)

        save_payload(text)

    except Exception as e:

        print(
            f"ERROR CAPTURANDO PAYLOAD: {e}"
        )


# ============================================================
# OPEN DASHBOARD
# ============================================================

def open_dashboard(page):

    section("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="domcontentloaded",
        timeout=120000
    )

    section("WAIT FULL RENDER")

    time.sleep(25)


# ============================================================
# OPEN FILTERS PANEL
# ============================================================

def open_filters_panel(page):

    section("OPEN FILTERS PANEL")

    buttons = page.locator("text=Filtros")

    total = buttons.count()

    for i in range(total):

        btn = buttons.nth(i)

        try:

            if btn.is_visible():

                print("\nBUTTON:")
                print(btn.inner_text())

                btn.click(force=True)

                time.sleep(8)

                return

        except:
            pass

    raise Exception(
        "No se pudo abrir panel filtros"
    )


# ============================================================
# FIND FILTER CONTAINER
# ============================================================

def find_filter_container_stable(
    page,
    label
):

    section(
        f"FIND FILTER STABLE -> {label}"
    )

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    for i in range(total):

        try:

            container = containers.nth(i)

            combo_count = container.locator(
                "[role='combobox']"
            ).count()

            if combo_count == 0:
                continue

            text = container.inner_text().strip()

            print("\n")
            print("-" * 60)

            print(f"INDEX: {i}")

            print(f"COMBOBOXES: {combo_count}")

            print("\nTEXT:\n")

            print(text[:300])

            if label.lower() in text.lower():

                print("\nMATCH FOUND")

                return container

        except:
            pass

    raise Exception(
        f"No filter found: {label}"
    )


# ============================================================
# OPEN DROPDOWN
# ============================================================

def open_dropdown(container):

    section("OPEN DROPDOWN")

    combo = container.locator(
        "[role='combobox']"
    ).first

    combo.click(force=True)

    time.sleep(5)


# ============================================================
# FIND ACTIVE OVERLAY
# ============================================================

def find_active_overlay(page):

    section("FIND ACTIVE OVERLAY")

    selectors = [

        "div[role='listbox']",

        "div[role='tree']"

    ]

    visibles = []

    for selector in selectors:

        loc = page.locator(selector)

        total = loc.count()

        print(f"\nSELECTOR: {selector}")
        print(f"TOTAL: {total}")

        for i in range(total):

            item = loc.nth(i)

            try:

                if item.is_visible():

                    txt = item.inner_text()

                    visibles.append(item)

                    print("\nVISIBLE OVERLAY:")
                    print(txt[:300])

            except:
                pass

    if len(visibles) == 0:

        raise Exception(
            "No active overlay found"
        )

    #
    # EL MÁS RECIENTE
    #

    overlay = visibles[-1]

    print("\nACTIVE OVERLAY SELECTED")

    return overlay


# ============================================================
# FIND SEARCHBOX INSIDE OVERLAY
# ============================================================

def find_searchbox_inside_overlay(
    overlay
):

    section(
        "FIND SEARCHBOX INSIDE OVERLAY"
    )

    searchboxes = overlay.locator(
        "input.searchInput"
    )

    total = searchboxes.count()

    print(f"SEARCHBOXES INSIDE: {total}")

    if total == 0:

        raise Exception(
            "No overlay searchbox found"
        )

    sb = searchboxes.first

    return sb


# ============================================================
# OPTIONS SNAPSHOT
# ============================================================

def get_options_snapshot(
    overlay
):

    options = overlay.locator(
        ".slicerText"
    )

    total = options.count()

    texts = []

    for i in range(total):

        option = options.nth(i)

        try:

            if option.is_visible():

                txt = option.inner_text().strip()

                texts.append(txt)

        except:
            pass

    return texts


# ============================================================
# WAIT OPTIONS REFRESH
# ============================================================

def wait_options_refresh(
    overlay,
    before_snapshot,
    timeout=20
):

    section("WAIT OPTIONS REFRESH")

    start = time.time()

    while True:

        current = get_options_snapshot(
            overlay
        )

        print("\nCURRENT OPTIONS:")
        print(current[:8])

        #
        # CAMBIO DETECTADO
        #

        if current != before_snapshot:

            print("\nOPTIONS REFRESHED")

            return

        elapsed = (
            time.time() - start
        )

        if elapsed > timeout:

            print(
                "\nTIMEOUT WAITING OPTIONS REFRESH"
            )

            return

        time.sleep(1)


# ============================================================
# SEARCH VALUE INSIDE OVERLAY
# ============================================================

def search_value_inside_overlay(
    overlay,
    value
):

    section(f"SEARCH -> {value}")

    #
    # SNAPSHOT BEFORE
    #

    before_snapshot = (
        get_options_snapshot(
            overlay
        )
    )

    print("\nBEFORE SNAPSHOT:")
    print(before_snapshot[:8])

    #
    # SEARCHBOX REAL
    #

    searchbox = (
        find_searchbox_inside_overlay(
            overlay
        )
    )

    #
    # CLICK
    #

    searchbox.click(force=True)

    time.sleep(1)

    #
    # CLEAR
    #

    searchbox.press("Control+A")

    time.sleep(1)

    searchbox.press("Backspace")

    time.sleep(1)

    #
    # TYPE
    #

    searchbox.fill(value)

    #
    # VERIFY REAL INPUT
    #

    real_value = (
        searchbox.input_value()
    )

    print("\nINPUT VALUE:")
    print(real_value)

    #
    # MUY IMPORTANTE
    #

    if value.upper() not in real_value.upper():

        raise Exception(
            "Texto NO ingresado en searchbox real"
        )

    #
    # ESPERAR REFRESH
    #

    time.sleep(5)

    wait_options_refresh(
        overlay,
        before_snapshot
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

    total = options.count()

    print(f"OPTIONS: {total}")

    for i in range(total):

        option = options.nth(i)

        try:

            if not option.is_visible():
                continue

            txt = option.inner_text().strip()

        except:
            continue

        print("\nOPTION:")
        print(txt)

        #
        # FLEXIBLE MATCH
        #

        if expected_option.upper() in txt.upper():

            print("\nMATCH FOUND")

            option.click(force=True)

            return

    raise Exception(
        f"No se encontró opción: {expected_option}"
    )


# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section("WAIT RERENDER")

    time.sleep(12)


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
# APPLY FILTER
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

    container = (
        find_filter_container_stable(
            page,
            label
        )
    )

    #
    # OPEN DROPDOWN
    #

    open_dropdown(container)

    #
    # ACTIVE OVERLAY
    #

    overlay = (
        find_active_overlay(page)
    )

    #
    # SEARCH REAL
    #

    search_value_inside_overlay(
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
    # REOPEN FILTERS
    #

    open_filters_panel(page)

    time.sleep(5)


# ============================================================
# RESET PRODUCTO
# ============================================================

def reset_grupo_producto(page):

    section("RESET GRUPO PRODUCTO")

    container = find_filter_container_stable(
        page,
        "Grupo Producto"
    )

    open_dropdown(container)

    overlay = find_active_overlay(page)

    options = overlay.locator(
        ".slicerText"
    )

    total = options.count()

    print(f"OPTIONS: {total}")

    for i in range(total):

        option = options.nth(i)

        try:

            if not option.is_visible():
                continue

            txt = option.inner_text().strip()

        except:
            continue

        print("\nOPTION:")
        print(txt)

        txt_upper = txt.upper()

        if (
            "SELECCIONAR TODO" in txt_upper
            or "TODAS" in txt_upper
            or "TODO" in txt_upper
        ):

            print("\nRESET FOUND")

            option.click(force=True)

            wait_rerender()

            close_overlay(page)

            open_filters_panel(page)

            time.sleep(5)

            return

    raise Exception(
        "No se encontró reset producto"
    )


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=HEADLESS,
        slow_mo=250
    )

    context = browser.new_context(
        viewport={
            "width": 1800,
            "height": 1100
        }
    )

    page = context.new_page()

    page.set_default_timeout(60000)

    #
    # NETWORK INTERCEPTION
    #

    page.on(
        "response",
        handle_response
    )

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    open_dashboard(page)

    # ========================================================
    # OPEN FILTERS PANEL
    # ========================================================

    open_filters_panel(page)

    # ========================================================
    # MACROREGION
    # ========================================================

    apply_filter(
        page=page,
        label="MACROREGION",
        search_value_text="NORTE",
        expected_option="NORTE"
    )

    # ========================================================
    # INSTITUCION
    # ========================================================

    apply_filter(
        page=page,
        label="Institución",
        search_value_text="GOBIERNO",
        expected_option="GOBIERNO REGIONAL"
    )

    # ========================================================
    # UNIDAD EJECUTORA
    # ========================================================

    apply_filter(
        page=page,
        label="Unidad ejecutora",
        search_value_text="CASTILLO",
        expected_option="SALUD LUCIANO CASTILLO COLONNA"
    )

    # ========================================================
    # RESET PRODUCTO
    # ========================================================

    reset_grupo_producto(page)

    # ========================================================
    # FINAL WAIT
    # ========================================================

    section("FINAL TERRITORIAL WAIT")

    time.sleep(20)

    # ========================================================
    # SUMMARY
    # ========================================================

    section("SUMMARY")

    print(
        f"TOTAL PAYLOADS: {len(captured_payloads)}"
    )

    print(
        f"PAYLOAD DIR: {PAYLOAD_DIR}"
    )

    print(
        "\nTerritorial payload capture completed."
    )

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()