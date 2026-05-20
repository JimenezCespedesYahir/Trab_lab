# ============================================================
# capture_payloads_v6.py
# ============================================================
#
# MEJORA CRÍTICA v6
# -----------------
#
# Problema detectado:
#
# Unidad ejecutora:
#
# - renderiza async
# - virtualiza opciones
# - tarda más en refrescar
#
# Entonces:
#
# options = 8
#
# era cache viejo.
#
# SOLUCIÓN v6
# -----------
#
# ✅ wait_options_refresh()
# ✅ polling dinámico
# ✅ espera refresh REAL
# ✅ timing estable UE
# ✅ search CASTILLO
# ✅ matching flexible
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
    "capture_payloads_v6_outputs"
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

    clicked = False

    for i in range(total):

        btn = buttons.nth(i)

        try:

            if btn.is_visible():

                print("\nBUTTON:")
                print(btn.inner_text())

                btn.click(force=True)

                clicked = True

                break

        except:
            pass

    if not clicked:

        raise Exception(
            "No se pudo abrir panel filtros"
        )

    time.sleep(8)


# ============================================================
# FIND FILTER CONTAINER STABLE
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

            combos = container.locator(
                "[role='combobox']"
            )

            combo_count = combos.count()

            if combo_count == 0:
                continue

            text = container.inner_text()

            text = text.strip()

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

    time.sleep(4)


# ============================================================
# FIND SEARCHBOX
# ============================================================

def find_searchbox(page):

    section("FIND SEARCHBOX")

    searchboxes = page.locator(
        "input.searchInput"
    )

    total = searchboxes.count()

    print(f"SEARCHBOXES: {total}")

    visibles = []

    for i in range(total):

        sb = searchboxes.nth(i)

        try:

            if sb.is_visible():

                visibles.append(sb)

        except:
            pass

    print(
        f"VISIBLE SEARCHBOXES: {len(visibles)}"
    )

    if len(visibles) == 0:

        raise Exception(
            "No visible searchbox"
        )

    return visibles[-1]


# ============================================================
# GET OPTIONS SNAPSHOT
# ============================================================

def get_options_snapshot(page):

    options = page.locator(
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
    page,
    before_snapshot,
    timeout=20
):

    section("WAIT OPTIONS REFRESH")

    start = time.time()

    while True:

        current = get_options_snapshot(page)

        print("\nCURRENT OPTIONS:")
        print(current[:8])

        #
        # REFRESH DETECTADO
        #

        if current != before_snapshot:

            print("\nOPTIONS REFRESHED")

            return

        #
        # TIMEOUT
        #

        elapsed = time.time() - start

        if elapsed > timeout:

            print(
                "\nTIMEOUT WAITING OPTIONS REFRESH"
            )

            return

        time.sleep(1)


# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(
    page,
    value
):

    section(f"SEARCH -> {value}")

    #
    # Snapshot BEFORE
    #

    before_snapshot = get_options_snapshot(page)

    print("\nBEFORE SNAPSHOT:")
    print(before_snapshot[:8])

    #
    # SEARCHBOX
    #

    sb = find_searchbox(page)

    sb.click(force=True)

    time.sleep(1)

    sb.press("Control+A")

    time.sleep(1)

    sb.press("Backspace")

    time.sleep(1)

    #
    # TYPE
    #

    sb.fill(value)

    #
    # MUY IMPORTANTE
    #
    # Power BI:
    # - virtualiza
    # - lazy loading
    # - async semantic refresh
    #

    time.sleep(10)

    #
    # ESPERAR REFRESH REAL
    #

    wait_options_refresh(
        page,
        before_snapshot
    )


# ============================================================
# CLICK OPTION FLEXIBLE
# ============================================================

def click_option(
    page,
    expected_option
):

    section(
        f"CLICK OPTION -> {expected_option}"
    )

    options = page.locator(
        ".slicerText"
    )

    total = options.count()

    print(f"OPTIONS: {total}")

    found = False

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
        # MATCH FLEXIBLE
        #

        if expected_option.upper() in txt.upper():

            print("\nMATCH FOUND")

            option.click(force=True)

            found = True

            break

    if not found:

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

    container = find_filter_container_stable(
        page,
        label
    )

    open_dropdown(container)

    search_value(
        page,
        search_value_text
    )

    click_option(
        page,
        expected_option
    )

    wait_rerender()

    close_overlay(page)

    open_filters_panel(page)

    time.sleep(5)


# ============================================================
# RESET GRUPO PRODUCTO
# ============================================================

def reset_grupo_producto(page):

    section("RESET GRUPO PRODUCTO")

    container = find_filter_container_stable(
        page,
        "Grupo Producto"
    )

    open_dropdown(container)

    #
    # Esperar render completo
    #

    time.sleep(5)

    options = page.locator(
        ".slicerText"
    )

    total = options.count()

    print(f"OPTIONS: {total}")

    found = False

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

            print("\nRESET OPTION FOUND")

            option.click(force=True)

            found = True

            break

    if not found:

        raise Exception(
            "No reset option found"
        )

    wait_rerender()

    close_overlay(page)

    open_filters_panel(page)

    time.sleep(5)


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