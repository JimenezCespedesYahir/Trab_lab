# ============================================================
# capture_payloads_v12.py
# ============================================================
#
# FINAL ESTABLE POWER BI PIPELINE
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

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# ============================================================
# URL POWER BI
# ============================================================

URL = (
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUt"
    "MGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVk"
    "YWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"
    "&pageName=ReportSection"
)

# ============================================================
# OUTPUT
# ============================================================

OUTPUT_DIR = Path(
    "capture_payloads_v12_outputs"
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
# SECTION
# ============================================================

def section(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

# ============================================================
# SAVE PAYLOADS
# ============================================================

def save_payloads():

    global payload_counter

    for payload in captured_payloads:

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

            json.dump(
                payload,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(
            f"PAYLOAD SAVED: {filename.name}"
        )

    captured_payloads.clear()

# ============================================================
# HANDLE RESPONSE
# ============================================================

def handle_response(response):

    try:

        if "/querydata" not in response.url:
            return

        section("QUERYDATA CAPTURADA")

        print(
            f"STATUS: {response.status}"
        )

        if response.status != 200:
            return

        data = response.json()

        captured_payloads.append(data)

    except Exception as e:

        print(
            f"ERROR PAYLOAD: {e}"
        )

# ============================================================
# WAITS
# ============================================================

def wait_full_render():

    section("WAIT FULL RENDER")

    time.sleep(30)

def wait_rerender():

    section("WAIT RERENDER")

    time.sleep(12)

# ============================================================
# OPEN DASHBOARD
# ============================================================

def open_dashboard(page):

    section("OPEN DASHBOARD")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=120000
    )

    wait_full_render()

# ============================================================
# OPEN FILTERS PANEL (ESTABLE)
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

            container.click(
                force=True
            )

            time.sleep(6)

            #
            # VALIDAR APERTURA
            #

            new_total = page.locator(
                ".visualContainer"
            ).count()

            print(
                f"NEW CONTAINERS: {new_total}"
            )

            if new_total < 30:

                raise Exception(
                    "Filters panel did not open"
                )

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

        combo_count = container.locator(
            "[role='combobox']"
        ).count()

        if combo_count <= 0:
            continue

        if label.lower() in txt.lower():

            print(
                f"\nFOUND INDEX: {i}"
            )

            print("\nTEXT:\n")

            print(txt[:500])

            return container

    raise Exception(
        f"Filter not found: {label}"
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
    # CLICK DERECHA
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

    page.mouse.click(x, y)

    time.sleep(5)

# ============================================================
# FIND ACTIVE OVERLAY
# ============================================================

def find_active_overlay(page):

    section("FIND ACTIVE OVERLAY")

    selectors = [

        "div[role='tree']",

        "div[role='listbox']",

        ".slicer-dropdown-menu"

    ]

    candidates = []

    for selector in selectors:

        loc = page.locator(selector)

        total = loc.count()

        print(f"{selector}: {total}")

        for i in range(total):

            try:

                overlay = loc.nth(i)

                if not overlay.is_visible():
                    continue

                box = overlay.bounding_box()

                if not box:
                    continue

                area = (
                    box["width"]
                    * box["height"]
                )

                txt = overlay.inner_text()

                print("\n----------------")

                print(f"INDEX: {i}")

                print(f"AREA: {area}")

                print(txt[:300])

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
    # MÁS GRANDE
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
    # Algunos slicers no tienen búsqueda
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

    time.sleep(10)

    print(
        searchbox.input_value()
    )

# ============================================================
# GET OPTIONS
# ============================================================

def get_options(overlay):

    options = overlay.locator(
        "[role='treeitem'], [role='option']"
    )

    results = []

    total = options.count()

    for i in range(total):

        try:

            opt = options.nth(i)

            if not opt.is_visible():
                continue

            txt = (
                opt.inner_text()
                .strip()
            )

            if txt:

                results.append(
                    (
                        txt,
                        opt
                    )
                )

        except:
            pass

    return results

# ============================================================
# CLICK OPTION WITH VIRTUAL SCROLL
# ============================================================

def click_option(
    page,
    overlay,
    expected_option,
    max_scrolls=40
):

    section(
        f"CLICK OPTION -> "
        f"{expected_option}"
    )

    seen = set()

    for scroll in range(max_scrolls):

        print(
            f"\nSCROLL ITERATION: {scroll}"
        )

        options = get_options(overlay)

        print(
            f"OPTIONS: {len(options)}"
        )

        new_found = False

        for txt, opt in options:

            print("\nOPTION:")
            print(txt)

            if txt not in seen:
                new_found = True

            seen.add(txt)

            #
            # MATCH FLEXIBLE
            #

            if (
                expected_option.upper()
                in txt.upper()
            ):

                print(
                    "\nMATCH FOUND"
                )

                opt.click(force=True)

                time.sleep(5)

                return

        #
        # SCROLL
        #

        print("\nSCROLL DOWN")

        try:

            overlay.hover()

            page.mouse.wheel(
                0,
                1200
            )

        except:
            pass

        time.sleep(3)

        #
        # SI YA NO HAY NUEVAS
        #

        if not new_found:

            print(
                "\nNO NEW OPTIONS"
            )

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

    page.mouse.click(10, 10)

    time.sleep(2)

# ============================================================
# VALIDATE FILTER
# ============================================================

def validate_filter(
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

    print("\nTEXT:\n")

    print(txt)

    if expected.upper() not in txt.upper():

        raise Exception(
            f"Validation failed: {label}"
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
    # OVERLAY
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
        page,
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
    # SAVE PAYLOADS
    #

    save_payloads()

    #
    # REOPEN FILTERS
    #

    open_filters_panel(page)

    time.sleep(5)

    #
    # VALIDATE
    #

    validate_filter(
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
        page,
        overlay,
        "Seleccionar todo"
    )

    wait_rerender()

    close_overlay(page)

    save_payloads()

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
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
    # SUMMARY
    # ========================================================

    section("SUMMARY")

    print(
        f"TOTAL PAYLOADS: "
        f"{payload_counter}"
    )

    print(
        f"OUTPUT: {OUTPUT_DIR}"
    )

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()