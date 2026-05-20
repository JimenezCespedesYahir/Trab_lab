# ============================================================
# capture_payloads_v14.py
# ============================================================
#
# v14 FINAL STABLE PIPELINE
#
# RESUELVE:
#
# ✅ overlays
# ✅ rerender
# ✅ DOM recycling
# ✅ virtual scroll
# ✅ slicers
# ✅ territorial filters
# ✅ active overlay
# ✅ UE filtering
# ✅ optional searchbox
# ✅ payload interception
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

OUTPUT_DIR = Path(
    "capture_payloads_v14_outputs"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)

payload_counter = 0


# ============================================================
# UTIL
# ============================================================

def section(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# SAVE PAYLOAD
# ============================================================

def save_payload(text):

    global payload_counter

    payload_counter += 1

    filename = (
        OUTPUT_DIR /
        f"payload_{payload_counter:03d}.json"
    )

    filename.write_text(
        text,
        encoding="utf-8"
    )

    print(
        f"PAYLOAD SAVED: {filename.name}"
    )


# ============================================================
# RESPONSE HOOK
# ============================================================

def handle_response(response):

    try:

        url = response.url.lower()

        if "/querydata" in url:

            section(
                "QUERYDATA CAPTURADA"
            )

            print(
                f"STATUS: {response.status}"
            )

            text = response.text()

            save_payload(text)

    except Exception as e:

        print(e)


# ============================================================
# OPEN DASHBOARD
# ============================================================

def open_dashboard(page):

    section(
        "OPEN DASHBOARD"
    )

    page.goto(
        POWERBI_URL,
        wait_until="networkidle"
    )

    section(
        "WAIT FULL RENDER"
    )

    time.sleep(25)


# ============================================================
# OPEN FILTERS PANEL
# ============================================================

def open_filters_panel(page):

    section(
        "OPEN FILTERS PANEL"
    )

    containers = page.locator(
        ".visualContainer"
    )

    count = containers.count()

    print(
        f"CONTAINERS: {count}"
    )

    for i in range(count):

        container = containers.nth(i)

        try:

            txt = (
                container.inner_text()
                .strip()
            )

            if "Filtros" in txt:

                print(
                    f"FOUND FILTERS BUTTON: {i}"
                )

                container.click()

                time.sleep(5)

                return

        except:
            pass

    raise Exception(
        "Filters button not found"
    )


# ============================================================
# FIND FILTER
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

    count = containers.count()

    print(
        f"CONTAINERS: {count}"
    )

    for i in range(count):

        container = containers.nth(i)

        try:

            txt = (
                container.inner_text()
                .strip()
            )

            combo_count = (
                container.locator(
                    "[role='combobox']"
                ).count()
            )

            if (
                combo_count > 0
                and label.lower() in txt.lower()
            ):

                print(
                    f"\nFOUND INDEX: {i}"
                )

                print(
                    "\nTEXT:\n"
                )

                print(txt)

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

    section(
        "OPEN DROPDOWN"
    )

    box = container.bounding_box()

    if not box:

        raise Exception(
            "No bounding box"
        )

    x = (
        box["x"]
        + box["width"]
        - 25
    )

    y = (
        box["y"]
        + (box["height"] / 2)
    )

    print(
        f"CLICK X: {x}"
    )

    print(
        f"CLICK Y: {y}"
    )

    page.mouse.click(
        x,
        y
    )

    time.sleep(5)


# ============================================================
# FIND ACTIVE OVERLAY
# ============================================================

def find_active_overlay(page):

    section(
        "FIND ACTIVE OVERLAY"
    )

    trees = page.locator(
        "div[role='tree']"
    )

    count = trees.count()

    print(
        f"TREES: {count}"
    )

    best_overlay = None
    best_area = 0

    for i in range(count):

        tree = trees.nth(i)

        try:

            box = tree.bounding_box()

            if not box:
                continue

            area = (
                box["width"]
                * box["height"]
            )

            txt = (
                tree.inner_text()
                .strip()
            )

            print("\n----------------")
            print(f"INDEX: {i}")
            print(f"AREA: {area}")
            print(txt[:500])

            if area > best_area:

                best_area = area
                best_overlay = tree

        except:
            pass

    if not best_overlay:

        raise Exception(
            "No active overlay found"
        )

    print(
        f"\nACTIVE AREA: {best_area}"
    )

    return best_overlay


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

    count = searchboxes.count()

    print(
        f"SEARCHBOXES: {count}"
    )

    # ========================================================
    # SEARCHBOX OPTIONAL
    # ========================================================

    if count == 0:

        print(
            "NO SEARCHBOX -> SKIP SEARCH"
        )

        return

    searchbox = searchboxes.first

    searchbox.click()

    time.sleep(1)

    searchbox.fill("")

    time.sleep(1)

    searchbox.fill(value)

    time.sleep(5)

    current = searchbox.input_value()

    print(
        f"INPUT VALUE: {current}"
    )


# ============================================================
# CLICK OPTION
# ============================================================

def click_option(
    overlay,
    expected
):

    section(
        f"CLICK OPTION -> {expected}"
    )

    # ========================================================
    # RESET SCROLL TOP
    # ========================================================

    overlay.evaluate(
        "(el) => el.scrollTop = 0"
    )

    time.sleep(2)

    # ========================================================
    # ITERATIVE SEARCH
    # ========================================================

    for attempt in range(30):

        print(
            f"\nATTEMPT: {attempt + 1}"
        )

        options = overlay.locator(
            "[role='treeitem']"
        )

        count = options.count()

        print(
            f"OPTIONS: {count}"
        )

        for i in range(count):

            option = options.nth(i)

            try:

                txt = (
                    option.inner_text()
                    .strip()
                )

                print(
                    f"\nOPTION:\n{txt}"
                )

                if (
                    expected.upper()
                    in txt.upper()
                ):

                    print(
                        "\nMATCH FOUND"
                    )

                    option.click()

                    time.sleep(3)

                    return

            except:
                pass

        # ====================================================
        # SCROLL DOWN
        # ====================================================

        overlay.evaluate(
            "(el) => el.scrollTop += 400"
        )

        time.sleep(2)

    raise Exception(
        f"Option not found: {expected}"
    )


# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section(
        "WAIT RERENDER"
    )

    time.sleep(10)


# ============================================================
# CLOSE OVERLAY
# ============================================================

def close_overlay(page):

    section(
        "CLOSE OVERLAY"
    )

    page.keyboard.press(
        "Escape"
    )

    time.sleep(2)

    page.mouse.click(
        20,
        20
    )

    time.sleep(2)


# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(
    page,
    label,
    expected_option,
    use_search=False,
    search_text=None
):

    section(
        f"APPLY FILTER -> {label}"
    )

    container = (
        find_filter_container_stable(
            page,
            label
        )
    )

    open_dropdown(
        page,
        container
    )

    overlay = (
        find_active_overlay(page)
    )

    # ========================================================
    # OPTIONAL SEARCH
    # ========================================================

    if use_search and search_text:

        search_value(
            overlay,
            search_text
        )

    click_option(
        overlay,
        expected_option
    )

    wait_rerender()

    close_overlay(page)

    open_filters_panel(page)

    time.sleep(5)


# ============================================================
# RESET PRODUCTO
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


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.on(
        "response",
        handle_response
    )

    # ========================================================
    # OPEN
    # ========================================================

    open_dashboard(page)

    # ========================================================
    # OPEN FILTERS
    # ========================================================

    open_filters_panel(page)

    # ========================================================
    # MACROREGION
    # ========================================================

    apply_filter(
        page,
        label="MACROREGION",
        expected_option="NORTE",
        use_search=False
    )

    # ========================================================
    # INSTITUCION
    # ========================================================

    apply_filter(
        page,
        label="Institución",
        expected_option="GOBIERNO REGIONAL",
        use_search=False
    )

    # ========================================================
    # UE
    # ========================================================

    apply_filter(
        page,
        label="Unidad ejecutora",
        expected_option=(
            "SALUD LUCIANO CASTILLO COLONNA"
        ),
        use_search=True,
        search_text="CASTILLO"
    )

    # ========================================================
    # RESET PRODUCTO
    # ========================================================

    reset_grupo_producto(page)

    # ========================================================
    # FINAL WAIT
    # ========================================================

    section(
        "FINAL WAIT"
    )

    time.sleep(20)

    print("\nDONE")

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()