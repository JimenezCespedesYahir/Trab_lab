# ============================================================
# capture_payloads_v5.py
# ============================================================
#
# PIPELINE FINAL ESTABLE
# ============================================================
#
# OBJETIVO
# --------
#
# 1. Abrir dashboard Power BI
# 2. Abrir panel filtros
# 3. Aplicar territorialidad:
#
#    - MACROREGION = NORTE
#    - Institución = GOBIERNO REGIONAL
#    - Unidad ejecutora =
#      SALUD LUCIANO CASTILLO COLONNA
#
# 4. Resetear:
#
#    - Grupo Producto = Seleccionar todo
#
# 5. Esperar rerender final
# 6. Capturar TODOS los /querydata
# 7. Guardar payloads JSON crudos
#
# ============================================================
#
# MEJORAS v5
# ----------
#
# ✅ Matching flexible contains()
# ✅ Search text separado de expected option
# ✅ Reopen filters después rerender
# ✅ Overlay lifecycle estable
# ✅ DOM recycling resuelto
# ✅ Searchbox estable
# ✅ Payload interception estable
# ✅ Panel collapse resuelto
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
    "capture_payloads_v5_outputs"
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

    #
    # CRÍTICO
    #
    # Power BI:
    # - React hydration
    # - semantic model
    # - slicers
    # - visuals
    # - overlays
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

    candidates = []

    for i in range(total):

        try:

            container = containers.nth(i)

            combos = container.locator(
                "[role='combobox']"
            )

            combo_count = combos.count()

            if combo_count == 0:
                continue

            try:

                text = container.inner_text(
                    timeout=2000
                )

            except:
                continue

            text = text.strip()

            print("\n")
            print("-" * 60)

            print(f"INDEX: {i}")

            print(f"COMBOBOXES: {combo_count}")

            print("\nTEXT:\n")

            print(text[:400])

            if label.lower() in text.lower():

                print("\nMATCH FOUND")

                candidates.append({

                    "index": i,
                    "container": container,
                    "text": text

                })

        except Exception as e:

            print(f"ERROR INDEX {i}: {e}")

    if len(candidates) == 0:

        raise Exception(
            f"No filter found: {label}"
        )

    target = candidates[0]

    print("\n")
    print("=" * 80)

    print("FINAL FILTER SELECTED")

    print("=" * 80)

    print(f"INDEX: {target['index']}")

    print("\nTEXT:\n")

    print(target["text"][:500])

    return target["container"]


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

    #
    # Esperar filtering incremental
    #

    time.sleep(5)


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
        # MUY IMPORTANTE
        #
        # Power BI:
        # - agrega prefijos
        # - concatena textos
        # - añade códigos
        # - añade regiones
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

    #
    # CRÍTICO
    #
    # Power BI:
    # - recalcula visuals
    # - rehace joins
    # - semantic model
    # - query propagation
    #

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

    # ========================================================
    # FIND FILTER STABLE
    # ========================================================

    container = find_filter_container_stable(
        page,
        label
    )

    # ========================================================
    # OPEN DROPDOWN
    # ========================================================

    open_dropdown(container)

    # ========================================================
    # SEARCH
    # ========================================================

    search_value(
        page,
        search_value_text
    )

    # ========================================================
    # CLICK FLEXIBLE OPTION
    # ========================================================

    click_option(
        page,
        expected_option
    )

    # ========================================================
    # WAIT RERENDER
    # ========================================================

    wait_rerender()

    # ========================================================
    # CLOSE OVERLAY
    # ========================================================

    close_overlay(page)

    # ========================================================
    # REOPEN FILTERS PANEL
    # ========================================================

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
        # RESET FLEXIBLE
        #

        valid = [

            "SELECCIONAR TODO",

            "TODAS",

            "TODO",

            "ALL"

        ]

        txt_upper = txt.upper()

        for v in valid:

            if v in txt_upper:

                print("\nRESET OPTION FOUND")

                option.click(force=True)

                found = True

                break

        if found:
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
    # 1. OPEN DASHBOARD
    # ========================================================

    open_dashboard(page)

    # ========================================================
    # 2. OPEN FILTERS PANEL
    # ========================================================

    open_filters_panel(page)

    # ========================================================
    # 3. MACROREGION
    # ========================================================

    apply_filter(
        page=page,
        label="MACROREGION",
        search_value_text="NORTE",
        expected_option="NORTE"
    )

    # ========================================================
    # 4. INSTITUCION
    # ========================================================

    apply_filter(
        page=page,
        label="Institución",
        search_value_text="GOBIERNO",
        expected_option="GOBIERNO REGIONAL"
    )

    # ========================================================
    # 5. UNIDAD EJECUTORA
    # ========================================================

    apply_filter(
        page=page,
        label="Unidad ejecutora",
        search_value_text="LUCIANO",
        expected_option="SALUD LUCIANO CASTILLO COLONNA"
    )

    # ========================================================
    # 6. RESET PRODUCTO
    # ========================================================

    reset_grupo_producto(page)

    # ========================================================
    # 7. FINAL WAIT
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

    # ========================================================
    # KEEP OPEN
    # ========================================================

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()