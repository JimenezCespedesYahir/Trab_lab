# ============================================================
# map_filters_panel.py
# ============================================================
#
# OBJETIVO
# --------
# 1. Abrir dashboard
# 2. Abrir panel "Filtros"
# 3. Esperar render lateral
# 4. Re-mapear visualContainers
# 5. Identificar índices REALES de:
#
#    - Macroregion
#    - Institucion
#    - Unidad ejecutora
#    - Grupo Producto
#
# IMPRIME:
# --------
# - INDEX
# - X
# - Y
# - WIDTH
# - HEIGHT
# - COMBOBOXES
# - TEXT PREVIEW
#
# RESULTADO ESPERADO
# ------------------
#
# FILTER_MAP = {
#     "macro": X,
#     "institucion": Y,
#     "ue": Z,
#     "grupo_producto": W,
# }
#
# ============================================================

import time
import pandas as pd

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
    "map_filters_panel_outputs"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# LOG
# ============================================================

def section(title):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)


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

                try:

                    if btn.is_visible():

                        txt = btn.inner_text()

                        print("\nBUTTON:")
                        print(txt)

                        btn.click(force=True)

                        clicked = True

                        break

                except:
                    pass

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
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=HEADLESS
    )

    page = browser.new_page()

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    section("OPEN DASHBOARD")

    page.goto(
        POWERBI_URL,
        wait_until="domcontentloaded",
        timeout=120000
    )

    # ========================================================
    # WAIT FULL RENDER
    # ========================================================

    section("WAIT FULL RENDER")

    #
    # MUY IMPORTANTE
    #
    # Power BI:
    # - hidrata React
    # - inicializa semantic model
    # - renderiza visuals
    # - prepara overlays
    #

    time.sleep(25)

    # ========================================================
    # OPEN FILTERS PANEL
    # ========================================================

    click_filters_button(page)

    # ========================================================
    # WAIT FILTERS PANEL RENDER
    # ========================================================

    section("WAIT FILTERS PANEL")

    #
    # MUY IMPORTANTE
    #
    # recién aquí aparecen:
    #
    # - Macroregion
    # - Institucion
    # - Unidad ejecutora
    # - Grupo Producto
    #

    time.sleep(8)

    # ========================================================
    # RE-MAP CONTAINERS
    # ========================================================

    section("RE-MAP VISUAL CONTAINERS")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    rows = []

    # ========================================================
    # ITERATE
    # ========================================================

    for i in range(total):

        print("\n")
        print("-" * 80)

        try:

            container = containers.nth(i)

            # ------------------------------------------------
            # BOX
            # ------------------------------------------------

            box = container.bounding_box()

            if box:

                x = round(box["x"], 2)
                y = round(box["y"], 2)
                width = round(box["width"], 2)
                height = round(box["height"], 2)

            else:

                x = None
                y = None
                width = None
                height = None

            # ------------------------------------------------
            # TEXT
            # ------------------------------------------------

            try:

                text = container.inner_text(
                    timeout=2000
                )

            except:

                text = ""

            text = text.strip()

            preview = text[:800]

            # ------------------------------------------------
            # COMBOBOXES
            # ------------------------------------------------

            try:

                combos = container.locator(
                    "[role='combobox']"
                )

                combo_count = combos.count()

            except:

                combo_count = 0

            # ------------------------------------------------
            # PRINT
            # ------------------------------------------------

            print(f"INDEX: {i}")
            print(f"X: {x}")
            print(f"Y: {y}")
            print(f"WIDTH: {width}")
            print(f"HEIGHT: {height}")
            print(f"COMBOBOXES: {combo_count}")

            print("\nTEXT PREVIEW:\n")

            print(preview)

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            rows.append({

                "index": i,

                "x": x,
                "y": y,

                "width": width,
                "height": height,

                "comboboxes": combo_count,

                "text_preview": preview

            })

        except Exception as e:

            print(f"ERROR INDEX {i}: {e}")

    # ========================================================
    # SAVE CSV
    # ========================================================

    section("SAVE CSV")

    df = pd.DataFrame(rows)

    csv_path = (
        OUTPUT_DIR /
        "filters_panel_map.csv"
    )

    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"CSV SAVED: {csv_path}")

    # ========================================================
    # KEEP OPEN
    # ========================================================

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()