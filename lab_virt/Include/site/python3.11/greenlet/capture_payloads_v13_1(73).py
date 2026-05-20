# ============================================================
# capture_payloads_v13_1.py
# ============================================================
#
# BASE ESTABLE:
#   - capture_payloads_v13.py
#
# OBJETIVO:
#   Resolver ÚNICAMENTE el problema restante:
#
#       SALUD LUCIANO CASTILLO COLONNA
#
# CAUSA REAL:
#   Power BI virtualiza el scroll del slicer UE.
#
# SOLUCIÓN:
#   1. reset scroll top
#   2. reread dinámico opciones
#   3. scroll incremental robusto
#
# NO TOCAR:
#   - open_filters_panel()
#   - overlay architecture
#   - rerender logic
#   - searchbox logic
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

OUTPUT_DIR = Path("payloads_v13_1")
OUTPUT_DIR.mkdir(exist_ok=True)

payload_counter = 0


# ============================================================
# SECTION
# ============================================================

def section(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# SAVE PAYLOAD
# ============================================================

def save_payload(payload):

    global payload_counter

    payload_counter += 1

    path = OUTPUT_DIR / f"payload_{payload_counter:03}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)

    print(f"PAYLOAD SAVED: {path}")


# ============================================================
# OPEN DASHBOARD
# ============================================================

def open_dashboard(page):

    section("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="networkidle"
    )


# ============================================================
# WAIT FULL RENDER
# ============================================================

def wait_full_render():

    section("WAIT FULL RENDER")

    time.sleep(15)


# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section("WAIT RERENDER")

    time.sleep(10)


# ============================================================
# OPEN FILTERS PANEL
# ============================================================

def open_filters_panel(page):

    section("OPEN FILTERS PANEL")

    #
    # ESTA VERSIÓN ERA LA ESTABLE
    # NO CAMBIAR
    #

    page.locator("text=Filtros").first.click()

    time.sleep(5)


# ============================================================
# FIND FILTER CONTAINER STABLE
# ============================================================

def find_filter_container_stable(
    page,
    label
):

    section(f"FIND FILTER -> {label}")

    containers = page.locator(".visualContainer")

    count = containers.count()

    print(f"CONTAINERS: {count}")

    for i in range(count):

        try:

            container = containers.nth(i)

            text = container.inner_text(timeout=1000)

            combo_count = container.locator(
                "[role='combobox']"
            ).count()

            if combo_count <= 0:
                continue

            if label.lower() in text.lower():

                print(f"\nFOUND INDEX: {i}")

                print("\nTEXT:\n")
                print(text[:500])

                return container

        except:
            pass

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
        raise Exception("No bounding box")

    #
    # CLICK DERECHA SLICER
    #

    x = box["x"] + (box["width"] * 0.92)
    y = box["y"] + (box["height"] * 0.50)

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
        "div[class*='slicer']",
        "div[class*='dropdown']",
        "div[class*='popup']"

    ]

    best_overlay = None
    largest_area = 0

    for selector in selectors:

        print(f"\nTRY SELECTOR: {selector}")

        overlays = page.locator(selector)

        count = overlays.count()

        print(f"COUNT: {count}")

        for i in range(count):

            try:

                overlay = overlays.nth(i)

                if not overlay.is_visible():
                    continue

                box = overlay.bounding_box()

                if not box:
                    continue

                area = box["width"] * box["height"]

                text = overlay.inner_text()[:500]

                if len(text.strip()) <= 0:
                    continue

                print("\n----------------")
                print(f"INDEX: {i}")
                print(f"AREA: {area}")
                print(text)

                #
                # IMPORTANTE:
                # ignorar panel lateral filtros
                #

                if area < 20000:
                    continue

                if area > largest_area:

                    largest_area = area
                    best_overlay = overlay

            except:
                pass

    if not best_overlay:

        raise Exception(
            "No active overlay found"
        )

    print(f"\nACTIVE AREA: {largest_area}")

    return best_overlay

# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(
    overlay,
    value
):

    section(f"SEARCH -> {value}")

    searchboxes = overlay.locator("input")

    count = searchboxes.count()

    print(f"SEARCHBOXES: {count}")

    #
    # ALGUNOS OVERLAYS NO TIENEN SEARCHBOX
    #

    if count <= 0:

        print("NO SEARCHBOX -> SKIP")

        return

    searchbox = searchboxes.first

    searchbox.click()

    time.sleep(1)

    searchbox.fill(value)

    time.sleep(5)

    try:

        current = searchbox.input_value()

        print(f"INPUT VALUE: {current}")

    except:
        pass


# ============================================================
# CLICK OPTION v13.1
# ============================================================

def click_option(
    overlay,
    expected
):

    section(f"CLICK OPTION -> {expected}")

    #
    # SCROLLABLE
    #

    scrollable = overlay

    #
    # ==========================================
    # RESET SCROLL TOP
    # ==========================================
    #

    try:

        scrollable.evaluate(
            "(el) => el.scrollTop = 0"
        )

        print("SCROLL RESET TOP")

        time.sleep(2)

    except:
        pass

    #
    # ==========================================
    # ROBUST VIRTUAL SCROLL
    # ==========================================
    #

    for step in range(40):

        print(f"\nSCROLL STEP: {step}")

        options = overlay.locator(
            "[role='treeitem'], span, div"
        )

        count = options.count()

        print(f"OPTIONS: {count}")

        for i in range(count):

            try:

                option = options.nth(i)

                if not option.is_visible():
                    continue

                txt = option.inner_text().strip()

                if not txt:
                    continue

                print(f"\nOPTION:\n{txt}")

                #
                # FLEXIBLE MATCH
                #

                if expected.upper() in txt.upper():

                    print("\nMATCH FOUND")

                    option.click()

                    time.sleep(5)

                    return

            except:
                pass

        #
        # SCROLL DOWN
        #

        try:

            scrollable.evaluate(
                "(el) => el.scrollTop += 400"
            )

            print("SCROLL DOWN")

        except:
            pass

        time.sleep(1.5)

    raise Exception(
        f"Option not found: {expected}"
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
# APPLY FILTER FINAL
# ============================================================

def apply_filter(
    page,
    label,
    search_value_text,
    expected_option
):

    section(f"APPLY FILTER -> {label}")

    #
    # FIND FILTER
    #

    container = find_filter_container_stable(
        page,
        label
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

    overlay = find_active_overlay(page)

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


# ============================================================
# RESET GRUPO PRODUCTO
# ============================================================

def reset_grupo_producto(page):

    section("RESET GRUPO PRODUCTO")

    container = find_filter_container_stable(
        page,
        "Grupo Producto"
    )

    open_dropdown(
        page,
        container
    )

    overlay = find_active_overlay(page)

    click_option(
        overlay,
        "Seleccionar todo"
    )

    wait_rerender()

    close_overlay(page)

    open_filters_panel(page)


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    #
    # INTERCEPT PAYLOADS
    #

    def handle_response(response):

        try:

            if "querydata" in response.url.lower():

                section("QUERYDATA CAPTURADA")

                print(f"STATUS: {response.status}")

                payload = response.json()

                save_payload(payload)

        except:
            pass

    page.on(
        "response",
        handle_response
    )

    #
    # OPEN
    #

    open_dashboard(page)

    wait_full_render()

    open_filters_panel(page)

    #
    # MACROREGION
    #

    apply_filter(
        page,
        label="MACROREGION",
        search_value_text="NORTE",
        expected_option="NORTE"
    )

    #
    # INSTITUCION
    #

    apply_filter(
        page,
        label="Institución",
        search_value_text="GOBIERNO",
        expected_option="GOBIERNO REGIONAL"
    )

    #
    # UNIDAD EJECUTORA
    #

    apply_filter(
        page,
        label="Unidad ejecutora",
        search_value_text="CASTILLO",
        expected_option="SALUD LUCIANO CASTILLO COLONNA"
    )

    #
    # RESET PRODUCTO
    #

    reset_grupo_producto(page)

    print("\nDONE")

    time.sleep(999999)