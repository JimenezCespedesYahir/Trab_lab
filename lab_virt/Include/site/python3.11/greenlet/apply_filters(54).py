# ============================================================
# apply_filters.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# 1. Abrir dashboard Power BI
# 2. Abrir panel "Filtros"
# 3. Aplicar:
#
#    - MACROREGION = NORTE
#    - Institución = GOBIERNO REGIONAL
#    - Unidad ejecutora =
#      SALUD LUCIANO CASTILLO COLONNA
#    - Grupo Producto = Todo
#
# 4. Esperar rerender completo
#
# ESTE SCRIPT:
#   - NO exporta
#   - NO parsea payloads
#   - NO descarga archivos
#
# SOLO:
#   inducir el query territorial correcto.
#
# ============================================================

import time

from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = (
    "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"
)

HEADLESS = False


# ============================================================
# HELPERS
# ============================================================

def section(title):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


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

    # React + semantic model + slicers
    time.sleep(30)


# ============================================================
# CLICK FILTERS BUTTON
# ============================================================

def click_filters_button(page):

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

                if btn.is_visible():

                    btn.click(force=True)

                    clicked = True

                    break

            if clicked:
                break

        except:
            pass

    if not clicked:

        raise Exception(
            "No se pudo abrir panel filtros"
        )

    time.sleep(6)


# ============================================================
# FIND FILTER CONTAINER
# ============================================================

def find_filter_container(page, label):

    section(f"FIND FILTER -> {label}")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

        container = containers.nth(i)

        try:

            text = container.inner_text(
                timeout=2000
            )

        except:
            continue

        if label.lower() in text.lower():

            print(f"\nFOUND INDEX: {i}")

            print("\nTEXT PREVIEW:\n")

            print(text[:500])

            return container

    raise Exception(
        f"No se encontró filtro: {label}"
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

    if len(visibles) == 0:

        raise Exception(
            "No visible searchbox found"
        )

    print(f"VISIBLE SEARCHBOXES: {len(visibles)}")

    return visibles[-1]


# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(page, value):

    section(f"SEARCH -> {value}")

    sb = find_searchbox(page)

    sb.click(force=True)

    time.sleep(1)

    sb.press("Control+A")

    time.sleep(1)

    sb.press("Backspace")

    time.sleep(1)

    sb.fill(value)

    time.sleep(6)


# ============================================================
# CLICK EXACT OPTION
# ============================================================

def click_exact_option(page, value):

    section(f"CLICK OPTION -> {value}")

    options = page.locator(
        ".slicerItemContainer"
    )

    total = options.count()

    print(f"OPTIONS: {total}")

    found = False

    for i in range(total):

        option = options.nth(i)

        try:

            if not option.is_visible():
                continue

            txt = option.inner_text(
                timeout=2000
            )

        except:
            continue

        txt_clean = txt.strip()

        print("\nOPTION:\n")

        print(txt_clean)

        if value.lower() in txt_clean.lower():

            print("\nMATCH FOUND")

            option.click(force=True)

            found = True

            break

    if not found:

        raise Exception(
            f"No se encontró opción: {value}"
        )

    # Esperar rerender Power BI
    section("WAIT RERENDER")

    time.sleep(10)


# ============================================================
# CLOSE OVERLAY
# ============================================================

def close_overlay(page):

    section("CLOSE OVERLAY")

    # crítico para evitar reutilización DOM
    page.keyboard.press("Escape")

    time.sleep(3)

    # click externo adicional
    page.mouse.click(20, 20)

    time.sleep(2)


# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(
    page,
    label,
    value
):

    section(f"APPLY FILTER -> {label}")

    container = find_filter_container(
        page,
        label
    )

    open_dropdown(container)

    search_value(
        page,
        value
    )

    click_exact_option(
        page,
        value
    )

    close_overlay(page)


# ============================================================
# VERIFY FILTERS
# ============================================================

def verify_filters(page):

    section("VERIFY FILTERS")

    expected = {

        "MACROREGION": "NORTE",

        "Institución": "GOBIERNO REGIONAL",

        "Unidad ejecutora":
            "SALUD LUCIANO CASTILLO COLONNA",

        "Grupo Producto": "Todo"

    }

    full_text = page.locator("body").inner_text()

    for k, v in expected.items():

        print("\n")
        print("-" * 60)

        print(f"FILTER: {k}")

        if v.lower() in full_text.lower():

            print(f"OK -> {v}")

        else:

            raise Exception(
                f"Filtro no aplicado: {k} -> {v}"
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
        },
        ignore_https_errors=True
    )

    page = context.new_page()

    page.set_default_timeout(60000)

    page.set_default_navigation_timeout(
        120000
    )

    # ========================================================
    # 1. OPEN DASHBOARD
    # ========================================================

    open_dashboard(page)

    # ========================================================
    # 2. OPEN FILTERS PANEL
    # ========================================================

    click_filters_button(page)

    # ========================================================
    # 3. APPLY TERRITORIALITY
    # ========================================================

    # --------------------------------------------------------
    # MACROREGION
    # --------------------------------------------------------

    apply_filter(
        page,
        "MACROREGION",
        "NORTE"
    )

    # --------------------------------------------------------
    # INSTITUCION
    # --------------------------------------------------------

    apply_filter(
        page,
        "Institución",
        "GOBIERNO REGIONAL"
    )

    # --------------------------------------------------------
    # UNIDAD EJECUTORA
    # --------------------------------------------------------

    apply_filter(
        page,
        "Unidad ejecutora",
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    # --------------------------------------------------------
    # GRUPO PRODUCTO
    # --------------------------------------------------------

    apply_filter(
        page,
        "Grupo Producto",
        "Todo"
    )

    # ========================================================
    # 4. VERIFY
    # ========================================================

    verify_filters(page)

    # ========================================================
    # 5. FINAL WAIT
    # ========================================================

    section("FINAL TERRITORIAL RERENDER")

    time.sleep(20)

    # ========================================================
    # DONE
    # ========================================================

    section("FILTER PIPELINE COMPLETED")

    print("\n")
    print("DSRSLCC territorialidad aplicada.")
    print("Dashboard listo para capture_payloads.py")

    input("\nENTER PARA CERRAR...")

    browser.close()