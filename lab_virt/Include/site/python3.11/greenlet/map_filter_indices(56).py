# ============================================================
# map_filter_indices.py
# ============================================================
#
# OBJETIVO
# --------
# Mapear TODOS los visualContainers
# para estabilizar índices reales.
#
# IMPRIME:
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
# Identificar:
#
# Macroregion
# Institucion
# Unidad ejecutora
# Grupo Producto
#
# y construir:
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
    "map_filter_indices_outputs"
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
        wait_until="domcontentloaded"
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
    # - carga semantic model
    # - renderiza visuals
    # - inicializa slicers
    #

    time.sleep(25)

    # ========================================================
    # GET CONTAINERS
    # ========================================================

    section("GET VISUAL CONTAINERS")

    containers = page.locator(
        ".visualContainer"
    )

    total = containers.count()

    print(f"TOTAL CONTAINERS: {total}")

    rows = []

    # ========================================================
    # ITERATE CONTAINERS
    # ========================================================

    for i in range(total):

        print("\n")
        print("-" * 80)

        try:

            container = containers.nth(i)

            # ------------------------------------------------
            # BOUNDING BOX
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

                text = container.inner_text()

            except:

                text = ""

            text = text.strip()

            preview = text[:500]

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
            # SAVE ROW
            # ------------------------------------------------

            rows.append({
                "index": i,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "comboboxes": combo_count,
                "text_preview": preview,
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
        "container_map.csv"
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