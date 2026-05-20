# ============================================================
# capture_payloads_v11.py
# ============================================================
#
# FINAL STABLE POWER BI TERRITORIAL PIPELINE
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
# 4. Grupo Producto = Seleccionar todo
# 5. Capturar TODOS los /querydata
# 6. Guardar payloads JSON
#
# ============================================================
#
# MEJORAS V11
# -----------
#
# ✅ click físico por coordenadas
# ✅ overlay detection estable
# ✅ overlay más grande visible
# ✅ remap dinámico containers
# ✅ close overlay robusto
# ✅ reopen filters panel
# ✅ payload interception
# ✅ matching flexible
# ✅ searchbox scoped
# ✅ normalize_text integrado
# ✅ click_option corregido
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
    "capture_payloads_v11_outputs"
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


# ============================================================
# LOG
# ============================================================

def section(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    return (
        text
        .upper()
        .strip()
        .replace("\n", " ")
        .replace("  ", " ")
    )


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

        save_payload(text)

    except Exception as e:

        print(
            f"ERROR CAPTURANDO PAYLOAD: {e}"
        )


# ============================================================
# WAIT
# ============================================================

def wait_rerender(seconds=12):

    section("WAIT RERENDER")

    time.sleep(seconds)


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
    # Power BI hydration
    #

    time.sleep(30)


# ============================================================
# OPEN FILTERS PANEL
# ============================================================

def open_filters_panel(page):

    section("OPEN FILTERS PANEL")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

        container = containers.nth(i)

        try:

            txt = container.inner_text(
                timeout=1000
            )

        except:
            continue

        if "Filtros" in txt:

            print(
                f"FOUND FILTERS BUTTON: {i}"
            )

            container.click(force=True)

            time.sleep(6)

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

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

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

            print(
                f"\nFOUND INDEX: {i}"
            )

            print("\nTEXT:\n")

            print(txt[:500])

            return container

    raise Exception(
        f"No se encontró filtro: {label}"
    )


# ============================================================
# OPEN DROPDOWN
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

    x = (
        box["x"]
        + box["width"]
        - 25
    )

    y = (
        box["y"]
        + (box["height"] / 2)
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

        print(f"{selector}: {total}")

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

                print(txt[:200])

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
    # MÁS GRANDE = dropdown real
    #

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    chosen = candidates[0][1]

    print(
        "\nACTIVE OVERLAY SELECTED"
    )

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

    total = searchboxes.count()

    print(
        f"SEARCHBOXES: {total}"
    )

    #
    # SLICERS simples NO tienen searchbox
    #

    if total == 0:

        print(
            "\nNO SEARCHBOX PRESENT"
        )

        return

    searchbox = searchboxes.first

    searchbox.click(force=True)

    time.sleep(1)

    searchbox.press("Control+A")

    time.sleep(1)

    searchbox.press("Backspace")

    time.sleep(1)

    searchbox.fill(value)

    #
    # Esperar refresh incremental
    #

    time.sleep(10)

    print(
        "\nINPUT VALUE:"
    )

    print(
        searchbox.input_value()
    )


# ============================================================
# CLICK OPTION
# ============================================================

def click_option(overlay, text):

    section(f"CLICK OPTION -> {text}")

    normalized_target = normalize_text(text)

    previous_count = -1
    attempts = 0

    while attempts < 40:

        options = overlay.locator(
            "div[role='treeitem'], div[role='option']"
        )

        count = options.count()

        print(f"\nVISIBLE OPTIONS: {count}")

        #
        # evitar loop infinito
        #

        if count == previous_count:
            attempts += 1
        else:
            attempts = 0

        previous_count = count

        for i in range(count):

            try:

                option = options.nth(i)

                label = option.inner_text().strip()

                print(f"\nOPTION:\n{label}")

                normalized_label = normalize_text(label)

                if normalized_target in normalized_label:

                    print("\nMATCH FOUND")

                    option.scroll_into_view_if_needed()

                    time.sleep(0.3)

                    option.click()

                    return

            except:
                pass

        #
        # SCROLL DOWN
        #

        print("\nSCROLL DOWN")

        overlay.evaluate("""
            el => {
                el.scrollTop += 500;
            }
        """)

        time.sleep(0.7)

    raise Exception(
        f"No se encontró opción: {text}"
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

    open_dropdown(
        page,
        container
    )

    #
    # ACTIVE OVERLAY
    #

    overlay = (
        find_active_overlay(page)
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

    #
    # VALIDATE
    #

    validate_filter_selected(
        page,
        label,
        expected_option
    )


# ============================================================
# RESET GRUPO PRODUCTO
# ============================================================

def reset_grupo_producto(page):

    section(
        "RESET GRUPO PRODUCTO"
    )

    container = (
        find_filter_container_stable(
            page,
            "Grupo Producto"
        )
    )

    open_dropdown(
        page,
        container
    )

    overlay = (
        find_active_overlay(page)
    )

    click_option(
        overlay,
        "Seleccionar todo"
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

    page = browser.new_page()

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
        search_value_text="LUCIANO",
        expected_option=(
            "SALUD LUCIANO "
            "CASTILLO COLONNA"
        )
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