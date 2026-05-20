# ============================================================
# full_filters_export_pipeline.py
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

OUTPUT_DIR = Path("full_filters_export_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADLESS = False


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


def save_payload(payloads):
    path = OUTPUT_DIR / "querydata_after_filters.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payloads, f, ensure_ascii=False, indent=2)

    print(f"\nPAYLOAD SAVED -> {path}")


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

    section("WAIT POWER BI RENDER")

    time.sleep(20)


# ============================================================
# CLICK FILTERS BUTTON
# ============================================================

def click_filters_button(page):

    section("CLICK FILTROS")

    filters_btn = page.locator(
        "text=Filtros"
    ).first

    filters_btn.click(force=True)

    time.sleep(6)


# ============================================================
# WAIT FILTERS PANEL
# ============================================================

def wait_filters_panel(page):

    section("WAIT FILTERS PANEL")

    combos = page.locator(
        "[role='combobox']"
    )

    total = combos.count()

    print(f"COMBOBOXES: {total}")

    if total < 5:
        raise Exception(
            "Panel filtros no renderizó correctamente"
        )

    time.sleep(5)


# ============================================================
# FIND FILTER CONTAINER
# ============================================================

def find_filter_container(page, label):

    section(f"FIND CONTAINER -> {label}")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"CONTAINERS: {total}")

    for i in range(total):

        container = containers.nth(i)

        try:

            text = container.inner_text(timeout=2000)

        except:
            continue

        if label.lower() in text.lower():

            print(f"FOUND CONTAINER INDEX: {i}")
            print(text[:300])

            return container

    raise Exception(
        f"No se encontró container: {label}"
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

    time.sleep(3)


# ============================================================
# DETECT ACTIVE OVERLAY
# ============================================================

def detect_active_overlay(page):

    section("DETECT ACTIVE OVERLAY")

    overlays = page.locator(
        "div[role='listbox'], div[role='tree']"
    )

    total = overlays.count()

    print(f"OVERLAYS: {total}")

    visible = []

    for i in range(total):

        overlay = overlays.nth(i)

        try:

            if overlay.is_visible():

                txt = overlay.inner_text(timeout=2000)

                if txt.strip():

                    visible.append(overlay)

        except:
            pass

    if not visible:

        raise Exception(
            "No visible overlay detected"
        )

    overlay = visible[-1]

    print("\nOVERLAY DETECTED\n")

    try:
        print(
            overlay.inner_text(timeout=2000)[:500]
        )
    except:
        pass

    return overlay


# ============================================================
# FIND REAL SEARCHBOX
# ============================================================

def find_real_searchbox(page):

    section("FIND REAL SEARCHBOX")

    searchboxes = page.locator(
        "input.searchInput"
    )

    total = searchboxes.count()

    print(f"SEARCHBOXES: {total}")

    if total == 0:

        raise Exception(
            "No searchInput found"
        )
    
    visible_searchboxes = []
    
    for i in range(total):
        
        sb = searchboxes.nth(i)
        
        try:
            
            if sb.is_visible():
                
                visible_searchboxes.append(sb)
                
        except:
            
            pass
        
    if not visible_searchboxes:
        
        raise Exception(
            "No visible searchbox found"
            )
        
    sb = visible_searchboxes[-1]
    
    print("\nSEARCHBOX FOUND")
    
    return sb


# ============================================================
# SEARCH FILTER VALUE
# ============================================================

def search_filter_value(page, value):

    section(f"TYPE FILTER -> {value}")

    sb = find_real_searchbox(page)

    sb.click(force=True)

    time.sleep(1)

    sb.press("Control+A")

    time.sleep(1)

    sb.press("Backspace")

    time.sleep(1)

    sb.fill(value)

    time.sleep(5)


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

    for i in range(total):

        option = options.nth(i)

        try:

            txt = option.inner_text(timeout=2000)

        except:
            continue

        print(f"\nOPTION:\n{txt}")

        if value.lower() in txt.lower():

            print("\nMATCH FOUND")

            option.click(force=True)

            time.sleep(8)

            return

    raise Exception(
        f"No match found -> {value}"
    )


# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(page, label, value):

    section(f"APPLY FILTER -> {label}")

    container = find_filter_container(
        page,
        label
    )

    open_dropdown(container)

    detect_active_overlay(page)

    search_filter_value(
        page,
        value
    )

    click_exact_option(
        page,
        value
    )


# ============================================================
# VERIFY CLEAN FILTERS
# ============================================================

def verify_clean_filters(page):

    section("VERIFY CLEAN FILTERS")

    checks = [
        "Grupo Producto",
        "ATC",
        "Forma Farmacéutica",
        "Listado de Productos"
    ]

    for item in checks:

        try:

            locator = page.locator(
                f"text={item}"
            ).first

            text = locator.inner_text()

            print(f"\nCHECK: {item}")
            print(text)

        except:

            print(f"\nWARNING: {item}")


# ============================================================
# WAIT RERENDER
# ============================================================

def wait_rerender():

    section("WAIT RERENDER")

    time.sleep(15)


# ============================================================
# CLICK DOWNLOAD
# ============================================================

def click_download(page):

    section("CLICK DOWNLOAD")

    btn = page.locator(
        "text=Descargar"
    ).first

    btn.click(force=True)

    time.sleep(5)


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=HEADLESS
    )

    context = browser.new_context()

    page = context.new_page()

    payloads = []

    # ========================================================
    # CAPTURE QUERYDATA
    # ========================================================

    def handle_response(response):

        try:

            if "/querydata" in response.url.lower():

                print("\n")
                print("=" * 80)
                print("QUERYDATA CAPTURADA")
                print("=" * 80)

                print(f"STATUS: {response.status}")

                try:

                    payloads.append({
                        "url": response.url,
                        "status": response.status,
                        "body": response.text()
                    })

                except:
                    pass

        except:
            pass

    page.on(
        "response",
        handle_response
    )

    # ========================================================
    # PIPELINE
    # ========================================================

    open_dashboard(page)

    click_filters_button(page)

    wait_filters_panel(page)

    # --------------------------------------------------------
    # 1. MACROREGION
    # --------------------------------------------------------

    apply_filter(
        page,
        "MACROREGION",
        "NORTE"
    )

    # --------------------------------------------------------
    # 2. INSTITUCION
    # --------------------------------------------------------

    apply_filter(
        page,
        "Institución",
        "GOBIERNO REGIONAL"
    )

    # --------------------------------------------------------
    # 3. UNIDAD EJECUTORA
    # --------------------------------------------------------

    apply_filter(
        page,
        "Unidad ejecutora",
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    verify_clean_filters(page)

    # --------------------------------------------------------
    # WAIT
    # --------------------------------------------------------

    wait_rerender()

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    click_download(page)

    # --------------------------------------------------------
    # SAVE PAYLOADS
    # --------------------------------------------------------

    save_payload(payloads)

    # ========================================================
    # SUMMARY
    # ========================================================

    section("SUMMARY")

    print(f"PAYLOADS: {len(payloads)}")
    print(f"OUTPUT: {OUTPUT_DIR}")

    section("FULL FILTERS EXPORT PIPELINE COMPLETED")

    input("\nENTER PARA CERRAR...")

    browser.close()