# ============================================================
# capture_payloads_v15.py
# ============================================================

from playwright.sync_api import sync_playwright
import time
import json
import os

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

OUTPUT_DIR = "payloads_v15"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

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

def save_payload(payload_text):

    global payload_counter

    payload_counter += 1

    filename = os.path.join(
        OUTPUT_DIR,
        f"payload_{payload_counter:03d}.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(payload_text)

    print(f"PAYLOAD SAVED: {filename}")


# ============================================================
# HANDLE RESPONSE
# ============================================================

def handle_response(response):

    try:

        url = response.url.lower()

        if "querydata" not in url:
            return

        section("QUERYDATA CAPTURADA")

        print(f"STATUS: {response.status}")

        payload = response.text()

        save_payload(payload)

    except Exception as e:

        print(f"RESPONSE ERROR: {e}")


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

    buttons = page.locator(
        "button"
    )

    count = buttons.count()

    print(f"BUTTONS: {count}")

    for i in range(count):

        try:

            btn = buttons.nth(i)

            txt = btn.inner_text().strip()

            print(f"\nBUTTON {i}:")
            print(txt)

            txt_lower = txt.lower()

            if any(
                k in txt_lower
                for k in [
                    "filtro",
                    "filtros",
                    "filter"
                ]
            ):

                print(f"\nFOUND FILTERS BUTTON: {i}")

                btn.click()

                time.sleep(5)

                return

        except Exception as e:

            print(f"BUTTON ERROR: {e}")

    raise Exception(
        "Filters button not found"
    )


# ============================================================
# FIND FILTER CONTAINER
# ============================================================

def find_filter_container_stable(
    page,
    label
):

    section(f"FIND FILTER -> {label}")

    containers = page.locator(
        ".visualContainer"
    )

    count = containers.count()

    print(f"CONTAINERS: {count}")

    for i in range(count):

        try:

            container = containers.nth(i)

            combo_count = container.locator(
                "[role='combobox']"
            ).count()

            if combo_count <= 0:
                continue

            text = container.inner_text()

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
# OPEN DROPDOWN v15
# ============================================================

def open_dropdown(page, container):

    section("OPEN DROPDOWN")

    selectors = [

        "div[role='button']",
        "button",
        "svg",
        "i",
        ".dropdown",
        ".caret",
        ".chevron"

    ]

    # ========================================================
    # STRATEGY 1
    # INTERACTIVE ELEMENTS
    # ========================================================

    for selector in selectors:

        try:

            print(f"\nTRY SELECTOR: {selector}")

            elements = container.locator(
                selector
            )

            count = elements.count()

            print(f"ELEMENTS: {count}")

            for i in range(count):

                try:

                    el = elements.nth(i)

                    if not el.is_visible():
                        continue

                    box = el.bounding_box()

                    if not box:
                        continue

                    x = box["x"] + (
                        box["width"] / 2
                    )

                    y = box["y"] + (
                        box["height"] / 2
                    )

                    print(f"\nCLICK ELEMENT: {i}")
                    print(f"X: {x}")
                    print(f"Y: {y}")

                    page.mouse.click(x, y)

                    time.sleep(2)

                    trees = page.locator(
                        "div[role='tree']"
                    )

                    tree_count = trees.count()

                    print(f"TREES: {tree_count}")

                    if tree_count > 0:

                        print("\nOVERLAY OPENED")

                        return

                except Exception as e:

                    print(f"INNER ERROR: {e}")

        except Exception as e:

            print(f"SELECTOR ERROR: {e}")

    # ========================================================
    # STRATEGY 2
    # MULTI HOTSPOT FALLBACK
    # ========================================================

    print("\nMULTI HOTSPOT FALLBACK")

    box = container.bounding_box()

    if not box:
        raise Exception(
            "No bounding box"
        )

    hotspot_ratios = [

        0.95,
        0.92,
        0.88,
        0.85,
        0.82

    ]

    for ratio in hotspot_ratios:

        try:

            x = box["x"] + (
                box["width"] * ratio
            )

            y = box["y"] + (
                box["height"] / 2
            )

            print(f"\nHOTSPOT RATIO: {ratio}")
            print(f"CLICK X: {x}")
            print(f"CLICK Y: {y}")

            page.mouse.click(x, y)

            time.sleep(2)

            trees = page.locator(
                "div[role='tree']"
            )

            tree_count = trees.count()

            print(f"TREES: {tree_count}")

            if tree_count > 0:

                print("\nOVERLAY OPENED VIA HOTSPOT")

                return

        except Exception as e:

            print(f"HOTSPOT ERROR: {e}")

    raise Exception(
        "Could not open dropdown"
    )


# ============================================================
# FIND ACTIVE OVERLAY
# ============================================================

def find_active_overlay(page):

    section("FIND ACTIVE OVERLAY")

    trees = page.locator(
        "div[role='tree']"
    )

    count = trees.count()

    print(f"TREES: {count}")

    if count <= 0:

        raise Exception(
            "No active overlay found"
        )

    max_area = -1
    active = None

    for i in range(count):

        try:

            tree = trees.nth(i)

            if not tree.is_visible():
                continue

            box = tree.bounding_box()

            if not box:
                continue

            area = (
                box["width"] *
                box["height"]
            )

            txt = tree.inner_text()

            print("\n----------------")
            print(f"INDEX: {i}")
            print(f"AREA: {area}")
            print(txt[:300])

            if area > max_area:

                max_area = area
                active = tree

        except:
            pass

    if active is None:

        raise Exception(
            "No active overlay found"
        )

    print(f"\nACTIVE AREA: {max_area}")

    return active


# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(
    overlay,
    text
):

    section(f"SEARCH -> {text}")

    searchboxes = overlay.locator(
        "input"
    )

    count = searchboxes.count()

    print(f"SEARCHBOXES: {count}")

    if count <= 0:

        print("NO SEARCHBOX")
        return

    for i in range(count):

        try:

            sb = searchboxes.nth(i)

            if not sb.is_visible():
                continue

            sb.click()

            time.sleep(1)

            sb.fill(text)

            time.sleep(5)

            print("SEARCH APPLIED")

            return

        except:
            pass


# ============================================================
# CLICK OPTION
# ============================================================

def click_option(
    overlay,
    expected
):

    section(f"CLICK OPTION -> {expected}")

    #
    # RESET SCROLL TOP
    #

    overlay.evaluate(
        "(el) => el.scrollTop = 0"
    )

    time.sleep(2)

    max_scrolls = 30

    for attempt in range(max_scrolls):

        print(f"\nATTEMPT: {attempt + 1}")

        options = overlay.locator(
            "div[role='treeitem'], span, label"
        )

        count = options.count()

        print(f"OPTIONS: {count}")

        for i in range(count):

            try:

                option = options.nth(i)

                txt = option.inner_text().strip()

                if not txt:
                    continue

                print(f"\nOPTION:\n{txt}")

                if expected.upper() in txt.upper():

                    print("\nMATCH FOUND")

                    option.click()

                    time.sleep(3)

                    return

            except:
                pass

        #
        # SCROLL DOWN
        #

        print("\nSCROLL DOWN")

        overlay.evaluate(
            "(el) => el.scrollTop += 400"
        )

        time.sleep(2)

    raise Exception(
        f"Option not found: {expected}"
    )


# ============================================================
# CLOSE OVERLAY
# ============================================================

def close_overlay(page):

    section("CLOSE OVERLAY")

    try:

        page.keyboard.press("Escape")

        time.sleep(2)

    except:
        pass


# ============================================================
# APPLY FILTER FINAL
# ============================================================

def apply_filter(
    page,
    label,
    search_text,
    expected_option
):

    section(f"APPLY FILTER -> {label}")

    # ========================================================
    # FIND FILTER
    # ========================================================

    container = find_filter_container_stable(
        page,
        label
    )

    # ========================================================
    # OPEN DROPDOWN
    # ========================================================

    open_dropdown(
        page,
        container
    )

    # ========================================================
    # FIND ACTIVE OVERLAY
    # ========================================================

    overlay = find_active_overlay(
        page
    )

    # ========================================================
    # SEARCH VALUE
    # ========================================================

    search_value(
        overlay,
        search_text
    )

    # ========================================================
    # CLICK OPTION
    # ========================================================

    click_option(
        overlay,
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

    apply_filter(
        page,
        label="Grupo Producto",
        search_text="Seleccionar",
        expected_option="Seleccionar todo"
    )


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    #
    # RESPONSE LISTENER
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
    # WAIT FULL RENDER
    # ========================================================

    wait_full_render()

    # ========================================================
    # OPEN FILTERS PANEL
    # ========================================================

    open_filters_panel(page)

    # ========================================================
    # MACROREGION
    # ========================================================

    apply_filter(
        page,
        label="MACROREGION",
        search_text="NORTE",
        expected_option="NORTE"
    )

    # ========================================================
    # INSTITUCION
    # ========================================================

    apply_filter(
        page,
        label="Institución",
        search_text="GOBIERNO",
        expected_option="GOBIERNO REGIONAL"
    )

    # ========================================================
    # UNIDAD EJECUTORA
    # ========================================================

    apply_filter(
        page,
        label="Unidad ejecutora",
        search_text="CASTILLO",
        expected_option="SALUD LUCIANO CASTILLO COLONNA"
    )

    # ========================================================
    # RESET PRODUCTO
    # ========================================================

    reset_grupo_producto(page)

    print("\nDONE")

    time.sleep(999999)