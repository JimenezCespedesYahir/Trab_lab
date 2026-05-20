# ============================================================
# apply_semantic_filters.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Aplicar filtros territoriales robustos en Power BI:
#
#   Unidad ejecutora  -> SALUD LUCIANO CASTILLO COLONNA
#   Macroregion       -> NORTE
#   Institucion       -> GOBIERNO REGIONAL
#
# SIN:
#   - nth(index) global
#   - text global
#   - overlays ambiguos
#
# CON:
#   - containers semánticos
#   - combobox contextual
#   - overlays locales
#   - captura querydata
#
# ============================================================

import json
import time
from pathlib import Path

from playwright.sync_api import (
    sync_playwright,
    TimeoutError
)

# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"

OUTPUT_DIR = Path("semantic_filter_outputs")

PAYLOAD_DIR = OUTPUT_DIR / "payloads"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

OUTPUT_DIR.mkdir(exist_ok=True)
PAYLOAD_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

payload_counter = 0


# ============================================================
# BANNER
# ============================================================

def banner(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# QUERYDATA CAPTURE
# ============================================================

def setup_query_capture(page):

    captured = []

    def handle_response(response):

        global payload_counter

        try:

            if "/querydata" not in response.url:
                return

            request = response.request

            payload_counter += 1

            post_data = request.post_data

            parsed_body = {}

            if post_data:

                try:
                    parsed_body = json.loads(post_data)

                except:
                    parsed_body = {
                        "raw": post_data
                    }

            result = {
                "url": response.url,
                "status": response.status,
                "method": request.method,
                "body": parsed_body
            }

            out_file = (
                PAYLOAD_DIR /
                f"query_{payload_counter}.json"
            )

            with open(
                out_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    result,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            captured.append(result)

            print("\n")
            print("=" * 70)
            print("QUERYDATA CAPTURADA")
            print("=" * 70)

            print(f"STATUS: {response.status}")

        except Exception as e:

            print(f"ERROR CAPTURE: {e}")

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
    label_text
):

    banner(
        f"BUSCANDO CONTAINER: {label_text}"
    )

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(
        f"TOTAL VISUAL CONTAINERS: {total}"
    )

    for i in range(total):

        try:

            container = containers.nth(i)

            if not container.is_visible():
                continue

            text = container.inner_text(
                timeout=3000
            )

            if not text:
                continue

            text = text.strip().upper()

            if label_text.upper() not in text:
                continue

            combos = container.locator(
                "[role='combobox']"
            )

            if combos.count() == 0:
                continue

            print(
                f"CONTAINER ENCONTRADO: {i}"
            )

            print(text[:500])

            return container

        except Exception:
            pass

    print("NO ENCONTRADO")

    return None


# ============================================================
# FIND COMBOBOX
# ============================================================

def find_combobox_inside_container(
    container
):

    try:

        combos = container.locator(
            "[role='combobox']"
        )

        total = combos.count()

        print(
            f"COMBOBOXES INTERNOS: {total}"
        )

        for i in range(total):

            combo = combos.nth(i)

            if combo.is_visible():

                print(
                    f"COMBOBOX VISIBLE: {i}"
                )

                return combo

    except Exception as e:

        print(f"ERROR COMBO: {e}")

    return None


# ============================================================
# OPEN DROPDOWN
# ============================================================

def open_dropdown(combo):

    combo.click(force=True)

    time.sleep(3)


# ============================================================
# CLEAR COMBOBOX
# ============================================================

def clear_combobox(combo):

    combo.click(force=True)

    time.sleep(1)

    combo.press("Control+A")

    time.sleep(1)

    combo.press("Backspace")

    time.sleep(1)


# ============================================================
# TYPE FILTER
# ============================================================

def type_filter(
    combo,
    value
):

    combo.press_sequentially(
        value,
        delay=40
    )

    time.sleep(4)


# ============================================================
# CLICK OPTION INSIDE CONTAINER
# ============================================================

def click_option_inside_container(
    container,
    value
):

    banner(
        f"BUSCANDO OPCION: {value}"
    )

    option_candidates = [

        container.locator(
            f"text={value}"
        ),

        container.locator(
            f"span:has-text('{value}')"
        ),

        container.locator(
            f"div:has-text('{value}')"
        ),

        container.locator(
            f"label:has-text('{value}')"
        ),
    ]

    for locator in option_candidates:

        try:

            total = locator.count()

            print(
                f"CANDIDATOS: {total}"
            )

            for i in range(total):

                item = locator.nth(i)

                if not item.is_visible():
                    continue

                text = item.inner_text().strip()

                if value.upper() in text.upper():

                    print(
                        f"CLICK OPTION: {text}"
                    )

                    item.click(force=True)

                    time.sleep(6)

                    return True

        except Exception:
            pass

    print("NO OPTION FOUND")

    return False


# ============================================================
# APPLY FILTER INSIDE CONTAINER
# ============================================================

def apply_filter_inside_container(
    page,
    slicer_name,
    value
):

    banner(
        f"APLICANDO FILTRO: {slicer_name}"
    )

    container = find_slicer_container(
        page,
        slicer_name
    )

    if not container:

        print("NO CONTAINER")

        return False

    combo = find_combobox_inside_container(
        container
    )

    if not combo:

        print("NO COMBO")

        return False

    open_dropdown(combo)

    clear_combobox(combo)

    type_filter(
        combo,
        value
    )

    success = click_option_inside_container(
        container,
        value
    )

    if success:

        print(
            f"FILTRO OK: {value}"
        )

        time.sleep(10)

    return success


# ============================================================
# VERIFY CLEAN STATE
# ============================================================

def verify_clean_state(page):

    banner("VERIFICANDO ESTADO")

    checks = [
        "Grupo Producto",
        "ATC",
        "Forma Farmacéutica"
    ]

    for check in checks:

        try:

            container = find_slicer_container(
                page,
                check
            )

            if not container:
                continue

            text = container.inner_text()

            print("\n")
            print(check)

            if "Todas" in text:

                print("OK -> Todas")

            else:

                print(
                    "WARNING -> ALTERADO"
                )

        except:
            pass


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=400
    )

    context = browser.new_context()

    page = context.new_page()

    # ========================================================
    # QUERY CAPTURE
    # ========================================================

    captured = setup_query_capture(page)

    # ========================================================
    # RESET VISUAL STATE
    # ========================================================

    banner("RESET VISUAL STATE")

    page.goto(
        POWERBI_URL,
        wait_until="networkidle"
    )

    time.sleep(15)

    # HARD RESET
    page.reload(
        wait_until="networkidle"
    )

    time.sleep(10)

    page.screenshot(
        path=str(
            SCREENSHOT_DIR /
            "initial_state.png"
        )
    )

    # ========================================================
    # OPEN FILTERS
    # ========================================================

    banner("ABRIENDO FILTROS")

    try:

        filtros = page.locator(
            "text=Filtros"
        )

        if filtros.count() > 0:

            filtros.first.click(
                force=True
            )

            time.sleep(5)

    except:
        pass

    # ========================================================
    # APPLY FILTERS
    # ========================================================

    apply_filter_inside_container(
        page,
        "Unidad ejecutora",
        "SALUD LUCIANO CASTILLO COLONNA"
    )

    apply_filter_inside_container(
        page,
        "MACROREGION",
        "NORTE"
    )

    apply_filter_inside_container(
        page,
        "Institución",
        "GOBIERNO REGIONAL"
    )

    # ========================================================
    # VERIFY CLEAN STATE
    # ========================================================

    verify_clean_state(page)

    # ========================================================
    # WAIT FINAL RENDER
    # ========================================================

    banner("WAIT FINAL RENDER")

    time.sleep(20)

    # ========================================================
    # FINAL SCREENSHOT
    # ========================================================

    page.screenshot(
        path=str(
            SCREENSHOT_DIR /
            "final_state.png"
        ),
        full_page=True
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    banner("SUMMARY")

    print(
        f"PAYLOADS CAPTURADOS: {len(captured)}"
    )

    print(
        f"PAYLOAD DIR: {PAYLOAD_DIR}"
    )

    print(
        f"SCREENSHOTS DIR: {SCREENSHOT_DIR}"
    )

    print("\n")
    print("=" * 70)
    print("PIPELINE SEMANTIC FILTER COMPLETADO")
    print("=" * 70)

    input("\nENTER PARA CERRAR...")

    browser.close()