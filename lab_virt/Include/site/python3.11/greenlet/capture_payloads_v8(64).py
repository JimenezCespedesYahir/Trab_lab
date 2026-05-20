# ============================================================
# capture_payloads_v8.py
# ============================================================
#
# v8 — DUAL FILTER MODE STABLE
# ============================================================
#
# PROBLEMA FINAL RESUELTO
# -----------------------
#
# NO todos los filtros Power BI tienen:
#
#     input.searchInput
#
# Porque:
#
# - Macroregión = lista simple
# - Institución = lista simple
# - UE = searchable virtualized
#
# Entonces:
#
# apply_filter() ahora soporta:
#
#     use_searchbox=True/False
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
    "capture_payloads_v8_outputs"
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

        return None

    return searchboxes.first


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

    before_snapshot = (
        get_options_snapshot(
            overlay
        )
    )

    print("\nBEFORE SNAPSHOT:")
    print(before_snapshot[:8])

    searchbox = (
        find_searchbox_inside_overlay(
            overlay
        )
    )

    #
    # FILTRO SIN SEARCHBOX
    #

    if searchbox is None:

        print(
            "\nOVERLAY WITHOUT SEARCHBOX"
        )

        return

    #
    # SEARCHBOX REAL
    #

    searchbox.click(force=True)

    time.sleep(1)

    searchbox.press("Control+A")

    time.sleep(1)

    searchbox.press("Backspace")

    time.sleep(1)

    searchbox.fill(value)

    #
    # VERIFY REAL INPUT
    #

    real_value = (
        searchbox.input_value()
    )

    print("\nINPUT VALUE:")
    print(real_value)

    if value.upper() not in real_value.upper():

        raise Exception(
            "Texto NO ingresado en searchbox real"
        )

    #
    # WAIT REAL REFRESH
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
    # ACTIVE OVERLAY
    #

    overlay = (
        find_active_overlay(page)
    )

    #
    # SEARCH MODE
    #

    if use_searchbox:

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
    # CLOSE
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

    #
    # SEARCHBOX opcional
    #

    search_value_inside_overlay(
        overlay,
        ""
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
    # NETWORK
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