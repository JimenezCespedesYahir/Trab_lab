# ============================================================
# capture_payloads.py
# ============================================================
#
# OBJETIVO
# --------
# 1. Abrir dashboard Power BI
# 2. Aplicar territorialidad estable
# 3. Esperar rerender semántico
# 4. Interceptar TODOS los /querydata
# 5. Guardar payloads JSON crudos
#
# ESTRATEGIA FINAL
# ----------------
# - NO scraping visual
# - NO export button
# - NO copiar tablas
#
# Fuente real:
#   /querydata
#
# PIPELINE ESTABLE
# ----------------
# 1. Cachear containers iniciales
# 2. Usar índices fijos
# 3. Abrir dropdown
# 4. Buscar texto
# 5. Click exact option
# 6. Esperar rerender
# 7. Cerrar overlay
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

OUTPUT_DIR = Path("payload_capture_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

PAYLOAD_DIR = OUTPUT_DIR / "payloads"
PAYLOAD_DIR.mkdir(exist_ok=True)

HEADLESS = False

# ============================================================
# FILTER MAP
# ============================================================
#
# ESTOS ÍNDICES DEBEN AJUSTARSE
# SEGÚN TU INSPECCIÓN FINAL.
#
# LOS MÁS IMPORTANTES:
#
# Macroregion
# Institucion
# Unidad ejecutora
# Grupo Producto
#
# ============================================================

FILTER_MAP = {
    "macro": 6,
    "institucion": 7,
    "ue": 4,
    "grupo_producto": 8,
}

# ============================================================
# PAYLOAD STORAGE
# ============================================================

captured_payloads = []
payload_counter = 0


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

    global captured_payloads

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

        print(f"ERROR CAPTURANDO PAYLOAD: {e}")


# ============================================================
# GET FILTER CONTAINER
# ============================================================

def get_filter_container(
    containers,
    filter_key
):

    idx = FILTER_MAP[filter_key]

    container = containers.nth(idx)

    return container


# ============================================================
# OPEN DROPDOWN
# ============================================================

def open_dropdown(container):

    section("OPEN DROPDOWN")

    combos = container.locator(
        "[role='combobox']"
    )

    count = combos.count()

    if count == 0:

        raise Exception(
            "No combobox found"
        )

    combo = combos.first

    combo.click(force=True)

    time.sleep(3)


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

    visible = []

    for i in range(total):

        sb = searchboxes.nth(i)

        try:

            if sb.is_visible():
                visible.append(sb)

        except:
            pass

    print(
        f"VISIBLE SEARCHBOXES: {len(visible)}"
    )

    if len(visible) == 0:

        raise Exception(
            "No visible searchbox"
        )

    return visible[-1]


# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(
    page,
    value
):

    section(f"SEARCH -> {value}")

    searchbox = find_searchbox(page)

    searchbox.click(force=True)

    time.sleep(1)

    searchbox.press("Control+A")

    time.sleep(1)

    searchbox.press("Backspace")

    time.sleep(1)

    searchbox.fill(value)

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

        try:

            option = options.nth(i)

            if not option.is_visible():
                continue

            txt = option.inner_text().strip()

            print("\nOPTION:")
            print(txt)

            if txt.upper() == value.upper():

                print("\nMATCH FOUND")

                option.click(force=True)

                found = True

                break

        except:
            pass

    if not found:

        raise Exception(
            f"Option not found: {value}"
        )


# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section("WAIT RERENDER")

    #
    # MUY IMPORTANTE
    #
    # Power BI:
    # - recalcula semantic model
    # - rehace joins
    # - reprocesa slicers
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
    # - overlay persistente
    # - foco incorrecto
    # - búsqueda cruzada
    # - DOM reciclado
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

    preview = container.inner_text()

    print("\nCONTAINER PREVIEW:\n")
    print(preview[:400])

    open_dropdown(container)

    search_value(page, value)

    click_option(page, value)

    wait_rerender()

    close_overlay(page)


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=HEADLESS
    )

    page = browser.new_page()

    #
    # INTERCEPTAR NETWORK
    #

    page.on(
        "response",
        handle_response
    )

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    section("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="domcontentloaded"
    )

    # ========================================================
    # WAIT FULL RENDER
    # ========================================================

    section("WAIT FULL RENDER")

    #
    # MUY IMPORTANTE
    #
    # Power BI:
    # - hidrata React
    # - reconstruye semantic model
    # - inicializa slicers
    # - prepara overlays
    #

    time.sleep(25)

    # ========================================================
    # CACHE CONTAINERS
    # ========================================================

    section("CACHE CONTAINERS")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    # ========================================================
    # APPLY TERRITORIAL FILTERS
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
    # RESET PRODUCT FILTER
    # ========================================================

    #
    # IMPORTANTE:
    #
    # evitar contaminación ETL
    # productos persistentes
    #

    apply_filter(
        page,
        containers,
        "grupo_producto",
        "Todas"
    )

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
        f"OUTPUT: {OUTPUT_DIR}"
    )

    print(
        f"PAYLOAD DIR: {PAYLOAD_DIR}"
    )

    # ========================================================
    # KEEP OPEN
    # ========================================================

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()