# ============================================================
# apply_filters_with_searchbox.py
# ============================================================
# PIPELINE ROBUSTO POWER BI
#
# 1. Abrir dashboard
# 2. Abrir dropdown territorial
# 3. Detectar overlay ACTIVO
# 4. Encontrar searchbox REAL
# 5. Escribir valor exacto
# 6. Esperar rerender
# 7. Buscar opción filtrada
# 8. Click exacto
# 9. Capturar querydata
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
    "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"
)

OUTPUT_DIR = Path("territorial_outputs")

PAYLOAD_DIR = OUTPUT_DIR / "payloads"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

OUTPUT_DIR.mkdir(exist_ok=True)
PAYLOAD_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

payload_counter = 0

# ============================================================
# HELPERS
# ============================================================

def banner(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

# ------------------------------------------------------------

def screenshot(page, name):

    page.screenshot(
        path=str(
            SCREENSHOT_DIR / f"{name}.png"
        ),
        full_page=True
    )

# ============================================================
# QUERY CAPTURE
# ============================================================

def setup_capture(page):

    captured = []

    def handle_response(response):

        global payload_counter

        try:

            if "/querydata" not in response.url:
                return

            payload_counter += 1

            request = response.request

            data = {

                "url": response.url,
                "status": response.status,
                "method": request.method,
                "post_data": request.post_data

            }

            with open(
                PAYLOAD_DIR / f"query_{payload_counter}.json",
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            captured.append(data)

            print("\n")
            print("=" * 70)
            print("QUERYDATA CAPTURADA")
            print("=" * 70)

            print(f"STATUS: {response.status}")

        except Exception as e:

            print(e)

    page.on(
        "response",
        handle_response
    )

    return captured

# ============================================================
# FIND SLICER CONTAINER
# ============================================================

def find_slicer_container(
    page,
    slicer_name
):

    banner(
        f"BUSCANDO SLICER: {slicer_name}"
    )

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

        try:

            container = containers.nth(i)

            if not container.is_visible():
                continue

            text = container.inner_text()

            if not text:
                continue

            text_upper = text.upper()

            if slicer_name.upper() in text_upper:

                combos = container.locator(
                    "[role='combobox']"
                )

                if combos.count() > 0:

                    print(f"SLICER ENCONTRADO: {i}")

                    print(text[:300])

                    return container

        except:
            pass

    return None

# ============================================================
# FIND COMBOBOX
# ============================================================

def find_combobox_inside_container(
    container
):

    combos = container.locator(
        "[role='combobox']"
    )

    total = combos.count()

    print(f"COMBOBOXES: {total}")

    for i in range(total):

        try:

            combo = combos.nth(i)

            if combo.is_visible():

                return combo

        except:
            pass

    return None

# ============================================================
# DETECT ACTIVE OVERLAY
# ============================================================

def detect_active_overlay(page):

    banner(
        "DETECTANDO OVERLAY ACTIVO"
    )

    selectors = [

        "div[role='listbox']",
        "div[role='tree']"

    ]

    candidates = []

    for selector in selectors:

        loc = page.locator(selector)

        total = loc.count()

        print(f"{selector}: {total}")

        for i in range(total):

            try:

                item = loc.nth(i)

                if not item.is_visible():
                    continue

                bbox = item.bounding_box()

                if not bbox:
                    continue

                area = (
                    bbox["width"]
                    *
                    bbox["height"]
                )

                text = item.inner_text()

                if len(text.strip()) < 3:
                    continue

                candidates.append({

                    "locator": item,
                    "area": area,
                    "text": text[:200]

                })

            except:
                pass

    if not candidates:

        print("NO OVERLAY")

        return None

    candidates = sorted(
        candidates,
        key=lambda x: x["area"],
        reverse=True
    )

    overlay = candidates[0]["locator"]

    print("OVERLAY DETECTADO")

    print(candidates[0]["text"])

    return overlay

# ============================================================
# FIND SEARCHBOX
# ============================================================

def find_searchbox_inside_overlay(
    overlay
):

    banner(
        "BUSCANDO SEARCHBOX"
    )

    selectors = [

        "input",
        "input[type='text']",
        "input[placeholder]"

    ]

    for selector in selectors:

        loc = overlay.locator(selector)

        total = loc.count()

        print(f"{selector}: {total}")

        for i in range(total):

            try:

                inp = loc.nth(i)

                if not inp.is_visible():
                    continue

                placeholder = (
                    inp.get_attribute(
                        "placeholder"
                    ) or ""
                )

                aria = (
                    inp.get_attribute(
                        "aria-label"
                    ) or ""
                )

                print("\nINPUT DETECTADO")

                print(f"placeholder: {placeholder}")

                print(f"aria: {aria}")

                if (

                    "buscar" in placeholder.lower()

                    or

                    "search" in placeholder.lower()

                    or

                    "buscar" in aria.lower()

                ):

                    print("SEARCHBOX REAL")

                    return inp

            except:
                pass

    print("NO SEARCHBOX")

    return None

# ============================================================
# TYPE FILTER
# ============================================================

def type_filter(
    searchbox,
    value
):

    banner(
        f"ESCRIBIENDO: {value}"
    )

    searchbox.click(force=True)

    time.sleep(1)

    searchbox.press(
        "Control+A"
    )

    time.sleep(1)

    searchbox.press(
        "Backspace"
    )

    time.sleep(1)

    searchbox.press_sequentially(
        value,
        delay=60
    )

    time.sleep(5)

# ============================================================
# SEARCH FILTERED OPTION
# ============================================================

def search_filtered_option(
    overlay,
    value
):

    banner(
        f"BUSCANDO OPCION FILTRADA: {value}"
    )

    candidates = overlay.locator(
        f"text={value}"
    )

    total = candidates.count()

    print(f"CANDIDATOS: {total}")

    for i in range(total):

        try:

            item = candidates.nth(i)

            if not item.is_visible():
                continue

            text = item.inner_text()

            print(text)

            if value.upper() in text.upper():

                print("OPTION FOUND")

                return item

        except:
            pass

    print("NO OPTION")

    return None

# ============================================================
# CLICK OPTION
# ============================================================

def click_option(option):

    banner(
        "CLICK OPTION"
    )

    option.click(force=True)

    time.sleep(12)

# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter_with_searchbox(
    page,
    slicer_name,
    value
):

    banner(
        f"APLICANDO FILTRO: {slicer_name}"
    )

    # --------------------------------------------------------
    # FIND SLICER
    # --------------------------------------------------------

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:

        print("NO CONTAINER")

        return False

    # --------------------------------------------------------
    # FIND COMBO
    # --------------------------------------------------------

    combo = find_combobox_inside_container(
        container
    )

    if not combo:

        print("NO COMBO")

        return False

    # --------------------------------------------------------
    # OPEN DROPDOWN
    # --------------------------------------------------------

    combo.click(force=True)

    time.sleep(4)

    screenshot(
        page,
        f"dropdown_{slicer_name}"
    )

    # --------------------------------------------------------
    # DETECT OVERLAY
    # --------------------------------------------------------

    overlay = detect_active_overlay(
        page
    )

    if not overlay:

        return False

    # --------------------------------------------------------
    # SEARCHBOX
    # --------------------------------------------------------

    searchbox = find_searchbox_inside_overlay(
        overlay
    )

    if not searchbox:

        return False

    # --------------------------------------------------------
    # TYPE
    # --------------------------------------------------------

    type_filter(
        searchbox,
        value
    )

    screenshot(
        page,
        f"typed_{slicer_name}"
    )

    # --------------------------------------------------------
    # SEARCH OPTION
    # --------------------------------------------------------

    option = search_filtered_option(
        overlay,
        value
    )

    if not option:

        return False

    # --------------------------------------------------------
    # CLICK
    # --------------------------------------------------------

    click_option(
        option
    )

    screenshot(
        page,
        f"selected_{slicer_name}"
    )

    print("\n")
    print("=" * 70)
    print("FILTRO APLICADO")
    print("=" * 70)

    print(f"{slicer_name} -> {value}")

    return True

# ============================================================
# VERIFY
# ============================================================

def verify_filter(
    page,
    slicer_name,
    expected
):

    banner(
        f"VERIFY: {slicer_name}"
    )

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:

        print("NO CONTAINER")

        return

    text = container.inner_text()

    print(text)

    if expected.upper() in text.upper():

        print("OK")

    else:

        print("WARNING")

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=False,

        slow_mo=400

    )

    context = browser.new_context(

        ignore_https_errors=True,

        viewport={

            "width": 1600,
            "height": 1000

        }

    )

    page = context.new_page()

    page.set_default_timeout(60000)

    page.set_default_navigation_timeout(120000)

    captured = setup_capture(page)

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    banner(
        "OPEN DASHBOARD"
    )

    try:

        page.goto(

            POWERBI_URL,

            wait_until="domcontentloaded",

            timeout=120000

        )

    except Exception as e:

        print("\n")
        print("=" * 70)
        print("ERROR OPENING DASHBOARD")
        print("=" * 70)

        print(e)

        browser.close()

        raise

    # ========================================================
    # WAIT POWER BI FULL RENDER
    # ========================================================

    banner(
        "WAITING POWER BI RENDER"
    )

    time.sleep(30)

    screenshot(
        page,
        "dashboard_loaded"
    )

    print("\n")
    print("=" * 70)
    print("DASHBOARD READY")
    print("=" * 70)

    # ========================================================
    # APPLY FILTERS
    # ========================================================

    apply_filter_with_searchbox(

        page,

        "MACROREGION",

        "NORTE"

    )

    apply_filter_with_searchbox(

        page,

        "Institución",

        "GOBIERNO REGIONAL"

    )

    apply_filter_with_searchbox(

        page,

        "Unidad ejecutora",

        "SALUD LUCIANO CASTILLO COLONNA"

    )

    # ========================================================
    # VERIFY
    # ========================================================

    verify_filter(

        page,

        "MACROREGION",

        "NORTE"

    )

    verify_filter(

        page,

        "Institución",

        "GOBIERNO REGIONAL"

    )

    verify_filter(

        page,

        "Unidad ejecutora",

        "SALUD LUCIANO CASTILLO COLONNA"

    )

    # ========================================================
    # WAIT FINAL
    # ========================================================

    banner(
        "WAIT FINAL"
    )

    time.sleep(20)

    screenshot(
        page,
        "final_state"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    banner(
        "SUMMARY"
    )

    print(
        f"PAYLOADS: {len(captured)}"
    )

    print(
        f"OUTPUT: {OUTPUT_DIR}"
    )

    print("\n")
    print("=" * 70)
    print("PIPELINE COMPLETADO")
    print("=" * 70)

    input("\nENTER PARA CERRAR...")

    browser.close()