# ============================================================
# capture_payloads_v9.py
# ============================================================
#
# v9 — FINAL STABLE TERRITORIAL PIPELINE
# ============================================================
#
# OBJETIVO
# --------
#
# 1. Abrir dashboard
# 2. Abrir panel filtros
# 3. Aplicar:
#
#    - MACROREGION = NORTE
#    - Institución = GOBIERNO REGIONAL
#    - Unidad ejecutora =
#      SALUD LUCIANO CASTILLO COLONNA
#
# 4. Reset Grupo Producto
# 5. Capturar TODOS los /querydata
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

HEADLESS = False

OUTPUT_DIR = Path(
    "capture_payloads_v9_outputs"
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

                btn.click(force=True)

                time.sleep(6)

                return

        except:
            pass

    raise Exception(
        "No se pudo abrir panel filtros"
    )


# ============================================================
# FIND FILTER STABLE
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

            text = (
                container.inner_text()
                .strip()
            )

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

        for i in range(total):

            item = loc.nth(i)

            try:

                if item.is_visible():

                    visibles.append(item)

            except:
                pass

    if len(visibles) == 0:

        raise Exception(
            "No active overlay found"
        )

    overlay = visibles[-1]

    print("\nACTIVE OVERLAY DETECTED")

    return overlay


# ============================================================
# SEARCHBOX INSIDE OVERLAY
# ============================================================

def find_searchbox_inside_overlay(
    overlay
):

    searchboxes = overlay.locator(
        "input.searchInput"
    )

    total = searchboxes.count()

    print(f"\nSEARCHBOXES INSIDE: {total}")

    if total == 0:

        return None

    return searchboxes.first


# ============================================================
# SEARCH VALUE
# ============================================================

def search_value_inside_overlay(
    overlay,
    value
):

    section(f"SEARCH -> {value}")

    searchbox = (
        find_searchbox_inside_overlay(
            overlay
        )
    )

    #
    # SI NO EXISTE SEARCHBOX
    #

    if searchbox is None:

        print(
            "\nNO SEARCHBOX INSIDE OVERLAY"
        )

        return

    searchbox.click(force=True)

    time.sleep(1)

    searchbox.press("Control+A")

    time.sleep(1)

    searchbox.press("Backspace")

    time.sleep(1)

    searchbox.fill(value)

    time.sleep(8)

    real = searchbox.input_value()

    print("\nREAL INPUT:")
    print(real)


# ============================================================
# GET OPTIONS
# ============================================================

def get_options(
    overlay
):

    options = overlay.locator(
        ".slicerText"
    )

    total = options.count()

    print(f"\nOPTIONS: {total}")

    results = []

    for i in range(total):

        option = options.nth(i)

        try:

            if option.is_visible():

                txt = (
                    option.inner_text()
                    .strip()
                )

                print("\nOPTION:")
                print(txt)

                results.append(
                    (option, txt)
                )

        except:
            pass

    return results


# ============================================================
# SCROLL OVERLAY
# ============================================================

def scroll_overlay_until_option(
    overlay,
    expected_option,
    max_scrolls=40
):

    section(
        f"SCROLL SEARCH -> {expected_option}"
    )

    previous_snapshot = set()

    for scroll_idx in range(max_scrolls):

        print("\n")
        print("-" * 60)

        print(
            f"SCROLL ITERATION: {scroll_idx + 1}"
        )

        current = get_options(
            overlay
        )

        texts = []

        for option, txt in current:

            texts.append(txt)

            #
            # FLEXIBLE MATCH
            #

            if (
                expected_option.upper()
                in txt.upper()
            ):

                print("\nMATCH FOUND")

                option.click(force=True)

                return

        snapshot = set(texts)

        #
        # NO NUEVAS OPCIONES
        #

        if (
            snapshot == previous_snapshot
            and scroll_idx > 5
        ):

            print(
                "\nNO NEW OPTIONS DETECTED"
            )

        previous_snapshot = snapshot

        #
        # SCROLL REAL
        #

        overlay.evaluate(
            """
            el => {
                el.scrollTop += 500;
            }
            """
        )

        time.sleep(2)

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
# VALIDATE FILTER
# ============================================================

def validate_filter_selected(
    page,
    label,
    expected
):

    section(
        f"VALIDATE -> {label}"
    )

    container = (
        find_filter_container_stable(
            page,
            label
        )
    )

    txt = (
        container.inner_text()
        .strip()
    )

    print("\nCONTAINER TEXT:\n")

    print(txt)

    if expected.upper() not in txt.upper():

        raise Exception(
            f"Filtro inválido: {label}"
        )

    print("\nVALIDATION OK")


# ============================================================
# APPLY FILTER FINAL
# ============================================================

def apply_filter(
    page,
    label,
    expected_option,
    use_searchbox=False,
    search_value_text=None
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
    # OPEN
    #

    open_dropdown(container)

    #
    # OVERLAY
    #

    overlay = (
        find_active_overlay(page)
    )

    #
    # SEARCHBOX opcional
    #

    if use_searchbox:

        search_value_inside_overlay(
            overlay,
            search_value_text
        )

    #
    # SCROLL + CLICK
    #

    scroll_overlay_until_option(
        overlay,
        expected_option
    )

    #
    # WAIT
    #

    wait_rerender()

    #
    # CLOSE
    #

    close_overlay(page)

    #
    # REOPEN FILTERS
    #

    open_filters_panel(page)

    time.sleep(5)

    #
    # VALIDATE
    #

    validate_filter_selected(
        page,
        label,
        expected_option
    )


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

    scroll_overlay_until_option(
        overlay,
        "Seleccionar todo"
    )

    wait_rerender()

    close_overlay(page)

    open_filters_panel(page)

    time.sleep(5)

    validate_filter_selected(
        page,
        "Grupo Producto",
        "Todas"
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
    # NETWORK LISTENER
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
        expected_option="NORTE",
        use_searchbox=False
    )

    # ========================================================
    # INSTITUCION
    # ========================================================

    apply_filter(
        page=page,
        label="Institución",
        expected_option="GOBIERNO REGIONAL",
        use_searchbox=False
    )

    # ========================================================
    # UNIDAD EJECUTORA
    # ========================================================

    apply_filter(
        page=page,
        label="Unidad ejecutora",
        expected_option="SALUD LUCIANO CASTILLO COLONNA",
        use_searchbox=True,
        search_value_text="CASTILLO"
    )

    # ========================================================
    # RESET PRODUCTO
    # ========================================================

    reset_grupo_producto(page)

    # ========================================================
    # FINAL WAIT
    # ========================================================

    section("FINAL WAIT")

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
        "\nTERRITORIAL PAYLOAD CAPTURE COMPLETED"
    )

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()