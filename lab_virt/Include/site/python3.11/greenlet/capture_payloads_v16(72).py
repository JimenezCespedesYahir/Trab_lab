# ============================================================
# capture_payloads_v16.py
# ============================================================
#
# POWER BI AUTOMATION PIPELINE
# v16 FINAL STABILIZED
#
# MEJORAS v16
# ------------
#
# ✅ open_filters_panel robusto
# ✅ soporte div[role='button']
# ✅ soporte aria-label
# ✅ dropdown icon detection
# ✅ overlay tree detection
# ✅ virtual scrolling
# ✅ rerender stabilization
# ✅ dynamic semantic matching
# ✅ overlay scoped search
# ✅ payload interception
# ✅ Power BI DOM recycling resistant
#
# ============================================================

import os
import json
import time

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


OUTPUT_DIR = "payloads_v16"

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

def save_payload(payload):

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

        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"PAYLOAD SAVED: {filename}")

# ============================================================
# INTERCEPT QUERYDATA
# ============================================================

def intercept_requests(page):

    def handle_response(response):

        try:

            if "querydata" in response.url.lower():

                section("QUERYDATA CAPTURADA")

                print(f"STATUS: {response.status}")

                data = response.json()

                save_payload(data)

        except:
            pass

    page.on(
        "response",
        handle_response
    )

# ============================================================
# OPEN DASHBOARD
# ============================================================

def open_dashboard(page):

    section("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="networkidle",
        timeout=120000
    )

# ============================================================
# WAIT FULL RENDER
# ============================================================

def wait_full_render():

    section("WAIT FULL RENDER")

    time.sleep(15)

# ============================================================
# OPEN FILTERS PANEL v16
# ============================================================

def open_filters_panel(page):

    section("OPEN FILTERS PANEL")

    #
    # SOLO BOTONES REALES
    #

    selectors = [

        "button",
        "div[role='button']"

    ]

    keywords = [

        "filtros",
        "filters",
        "panel de filtros",
        "filter pane"

    ]

    for selector in selectors:

        print(f"\nTRY SELECTOR: {selector}")

        elements = page.locator(selector)

        count = elements.count()

        print(f"ELEMENTS: {count}")

        for i in range(count):

            try:

                el = elements.nth(i)

                if not el.is_visible():
                    continue

                txt = ""

                try:
                    txt = el.inner_text().strip()
                except:
                    pass

                aria = ""

                try:
                    aria = (
                        el.get_attribute("aria-label")
                        or ""
                    )
                except:
                    pass

                combined = f"{txt} {aria}"

                combined_lower = combined.lower()

                print("\n----------------")
                print(f"INDEX: {i}")
                print(combined[:200])

                #
                # MATCH ESTRICTO
                #

                matched = any(
                    kw == combined_lower.strip()
                    or kw in combined_lower
                    for kw in keywords
                )

                if not matched:
                    continue

                #
                # EVITAR CONTENEDORES GIGANTES
                #

                box = el.bounding_box()

                if not box:
                    continue

                area = (
                    box["width"] *
                    box["height"]
                )

                print(f"AREA: {area}")

                #
                # Si es enorme => probablemente
                # es el documento completo
                #

                if area > 50000:
                    print("SKIP HUGE CONTAINER")
                    continue

                #
                # CLICK
                #

                x = box["x"] + (
                    box["width"] / 2
                )

                y = box["y"] + (
                    box["height"] / 2
                )

                print("\nFILTER BUTTON FOUND")

                print(f"CLICK X: {x}")
                print(f"CLICK Y: {y}")

                page.mouse.click(x, y)

                time.sleep(5)

                #
                # VALIDAR APERTURA
                #

                trees = page.locator(
                    "div[role='tree']"
                )

                if trees.count() > 0:

                    print("FILTER PANEL OPENED")

                    return

            except Exception as e:

                print(e)

    raise Exception(
        "Filters panel not found"
    )

# ============================================================
# FIND FILTER CONTAINER STABLE
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

            text = container.inner_text()

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
# OPEN DROPDOWN v16
# ============================================================

def open_dropdown(page, container):

    section("OPEN DROPDOWN")

    dropdown_icons = container.locator(
        "i, svg, button"
    )

    count = dropdown_icons.count()

    print(f"DROPDOWN ICONS: {count}")

    for i in range(count):

        try:

            icon = dropdown_icons.nth(i)

            if not icon.is_visible():
                continue

            box = icon.bounding_box()

            if not box:
                continue

            x = box["x"] + (
                box["width"] / 2
            )

            y = box["y"] + (
                box["height"] / 2
            )

            print(f"\nCLICK ICON: {i}")
            print(f"X: {x}")
            print(f"Y: {y}")

            page.mouse.click(x, y)

            time.sleep(3)

            trees = page.locator(
                "div[role='tree']"
            )

            if trees.count() > 0:

                print("OVERLAY OPENED")

                return

        except:
            pass

    print("\nFALLBACK CLICK")

    box = container.bounding_box()

    x = box["x"] + (
        box["width"] * 0.88
    )

    y = box["y"] + (
        box["height"] * 0.50
    )

    page.mouse.click(x, y)

    time.sleep(3)

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

    best = None
    best_area = 0

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

            if area > best_area:

                best_area = area
                best = tree

        except:
            pass

    if best:

        print(f"\nACTIVE AREA: {best_area}")

        return best

    raise Exception(
        "No active overlay found"
    )

# ============================================================
# SEARCH VALUE
# ============================================================

def search_value(
    overlay,
    text
):

    section(f"SEARCH -> {text}")

    selectors = [

        "input",
        "input[type='text']",
        ".searchInput",
        "[placeholder*='Buscar']",
        "[placeholder*='Search']"

    ]

    for selector in selectors:

        try:

            searchboxes = overlay.locator(
                selector
            )

            count = searchboxes.count()

            print(f"{selector}: {count}")

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

        except:
            pass

    print("NO SEARCHBOX FOUND -> CONTINUE")

# ============================================================
# CLICK OPTION v16
# ============================================================

def click_option(
    page,
    overlay,
    expected
):

    section(f"CLICK OPTION -> {expected}")

    scrollable = overlay

    try:

        scrollable.evaluate(
            "(el) => el.scrollTop = 0"
        )

        time.sleep(2)

    except:
        pass

    for attempt in range(30):

        print(f"\nSCROLL ITERATION: {attempt}")

        options = overlay.locator(
            "[role='treeitem'], li, div"
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

                print(txt)

                if expected.upper() in txt.upper():

                    print("\nMATCH FOUND")

                    option.click()

                    time.sleep(5)

                    return

            except:
                pass

        try:

            scrollable.evaluate(
                "(el) => el.scrollTop += 500"
            )

            time.sleep(2)

        except:
            pass

    raise Exception(
        f"Option not found: {expected}"
    )

# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section("WAIT RERENDER")

    time.sleep(10)

# ============================================================
# CLOSE OVERLAY
# ============================================================

def close_overlay(page):

    section("CLOSE OVERLAY")

    try:

        page.keyboard.press("Escape")

    except:
        pass

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

    container = find_filter_container_stable(
        page,
        label
    )

    open_dropdown(
        page,
        container
    )

    overlay = find_active_overlay(
        page
    )

    search_value(
        overlay,
        search_value_text
    )

    click_option(
        page,
        overlay,
        expected_option
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
        headless=False
    )

    page = browser.new_page()

    intercept_requests(page)

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    open_dashboard(page)

    # ========================================================
    # WAIT FULL RENDER
    # ========================================================

    wait_full_render()

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
        search_value_text="NORTE",
        expected_option="NORTE"
    )

    # ========================================================
    # INSTITUCION
    # ========================================================

    apply_filter(
        page,
        label="Institución",
        search_value_text="GOBIERNO",
        expected_option="GOBIERNO REGIONAL"
    )

    # ========================================================
    # UNIDAD EJECUTORA
    # ========================================================

    apply_filter(
        page,
        label="Unidad ejecutora",
        search_value_text="CASTILLO",
        expected_option="SALUD LUCIANO CASTILLO COLONNA"
    )

    print("\nDONE")

    time.sleep(999999)