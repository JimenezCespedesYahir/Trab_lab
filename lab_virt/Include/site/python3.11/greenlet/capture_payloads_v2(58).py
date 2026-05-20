# ============================================================
# capture_payloads_v2.py
# ============================================================
#
# OBJETIVO FINAL
# ---------------
# 1. Abrir dashboard Power BI
# 2. Abrir panel filtros
# 3. Aplicar territorialidad:
#
#    - MACROREGION = NORTE
#    - Institucion = GOBIERNO REGIONAL
#    - Unidad ejecutora =
#      SALUD LUCIANO CASTILLO COLONNA
#
# 4. Resetear:
#
#    - Grupo Producto = Todas
#
# 5. Esperar rerender completo
# 6. Capturar TODOS los /querydata
# 7. Guardar payloads JSON crudos
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
    "capture_payloads_v2_outputs"
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
# FILTER MAP ESTABLE
# ============================================================

FILTER_MAP = {

    "macro": 6,

    "institucion": 7,

    "ue": 8,

    "grupo_producto": 9,

}

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

    #
    # CRÍTICO
    #
    # React
    # semantic model
    # slicers
    # overlays
    #

    time.sleep(25)


# ============================================================
# OPEN FILTERS PANEL
# ============================================================

def open_filters_panel(page):

    section("OPEN FILTERS PANEL")

    candidates = [

        page.locator("text=Filtros"),

        page.locator("[aria-label*='Filtro']"),

        page.locator("[title*='Filtro']")

    ]

    clicked = False

    for candidate in candidates:

        try:

            total = candidate.count()

            for i in range(total):

                btn = candidate.nth(i)

                try:

                    if btn.is_visible():

                        txt = btn.inner_text()

                        print("\nBUTTON:")
                        print(txt)

                        btn.click(force=True)

                        clicked = True

                        break

                except:
                    pass

            if clicked:
                break

        except:
            pass

    if not clicked:

        raise Exception(
            "No se pudo abrir panel filtros"
        )

    time.sleep(8)


# ============================================================
# CACHE CONTAINERS
# ============================================================

def cache_containers(page):

    section("CACHE FILTER CONTAINERS")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    return containers


# ============================================================
# GET FILTER CONTAINER
# ============================================================

def get_filter_container(
    containers,
    filter_key
):

    idx = FILTER_MAP[filter_key]

    container = containers.nth(idx)

    print(f"\nFILTER INDEX: {idx}")

    preview = container.inner_text()

    print("\nCONTAINER PREVIEW:\n")

    print(preview[:500])

    return container


# ============================================================
# OPEN DROPDOWN
# ============================================================

def open_dropdown(container):

    section("OPEN DROPDOWN")

    combos = container.locator(
        "[role='combobox']"
    )

    total = combos.count()

    print(f"COMBOBOXES: {total}")

    if total == 0:

        raise Exception(
            "No combobox found"
        )

    combo = combos.first

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
# SEARCH VALUE
# ============================================================

def search_value(
    page,
    value
):

    section(f"SEARCH -> {value}")

    sb = find_searchbox(page)

    sb.click(force=True)

    time.sleep(1)

    sb.press("Control+A")

    time.sleep(1)

    sb.press("Backspace")

    time.sleep(1)

    sb.fill(value)

    time.sleep(5)


# ============================================================
# CLICK OPTION
# ============================================================

def click_option(
    page,
    value
):

    section(f"CLICK OPTION -> {value}")

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

        if txt.upper() == value.upper():

            print("\nMATCH FOUND")

            option.click(force=True)

            found = True

            break

    if not found:

        raise Exception(
            f"No se encontró opción: {value}"
        )


# ============================================================
# RESET PRODUCT FILTER
# ============================================================

def reset_grupo_producto(
    page,
    containers
):

    section("RESET GRUPO PRODUCTO")

    container = get_filter_container(
        containers,
        "grupo_producto"
    )

    open_dropdown(container)

    #
    # NO buscar texto.
    #
    # Buscar:
    # Seleccionar todo
    # Todas
    #

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

        valid = [

            "Seleccionar todo",

            "Todas",

            "Todo",

            "All"

        ]

        if txt in valid:

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


# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section("WAIT RERENDER")

    #
    # CRÍTICO
    #
    # Power BI:
    # - recalcula visuals
    # - rehace joins
    # - reprocesa semantic model
    # - genera nuevos querydata
    #

    time.sleep(12)


# ============================================================
# CLOSE OVERLAY
# ============================================================

def close_overlay(page):

    section("CLOSE OVERLAY")

    #
    # CRÍTICO
    #
    # evita:
    # - overlays persistentes
    # - DOM reciclado
    # - foco incorrecto
    #

    page.keyboard.press("Escape")

    time.sleep(2)

    page.mouse.click(20, 20)

    time.sleep(2)


# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(
    page,
    containers,
    filter_key,
    value
):

    section(
        f"APPLY FILTER -> {filter_key}"
    )

    container = get_filter_container(
        containers,
        filter_key
    )

    open_dropdown(container)

    search_value(
        page,
        value
    )

    click_option(
        page,
        value
    )

    wait_rerender()

    close_overlay(page)


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

    page.on(
        "response",
        handle_response
    )

    # ========================================================
    # 1. OPEN DASHBOARD
    # ========================================================

    open_dashboard(page)

    # ========================================================
    # 2. OPEN FILTERS PANEL
    # ========================================================

    open_filters_panel(page)

    # ========================================================
    # 3. CACHE CONTAINERS
    # ========================================================

    containers = cache_containers(page)

    # ========================================================
    # 4. TERRITORIALITY
    # ========================================================

    apply_filter(
        page,
        containers,
        "macro",
        "NORTE"
    )

    apply_filter(
        page,
        containers,
        "institucion",
        "GOBIERNO REGIONAL"
    )

    apply_filter(
        page,
        containers,
        "ue",
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    # ========================================================
    # 5. RESET PRODUCT FILTER
    # ========================================================

    reset_grupo_producto(
        page,
        containers
    )

    # ========================================================
    # 6. FINAL WAIT
    # ========================================================

    section("FINAL TERRITORIAL WAIT")

    #
    # Esperar consolidación final
    #

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

    # ========================================================
    # KEEP OPEN
    # ========================================================

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()