# ============================================================
# inspect_container_positions.py
# ============================================================
# OBJETIVO:
#
# Mapear TODOS los .visualContainer de Power BI
#
# Exportar:
#
# INDEX
# X
# Y
# WIDTH
# HEIGHT
# TEXT_PREVIEW
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
    "https://app.powerbi.com/view?r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUtMGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9&pageName=ReportSection"
)

OUTPUT_DIR = Path(
    "container_positions_output"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)

CSV_OUTPUT = OUTPUT_DIR / "visual_container_positions.csv"

# ============================================================
# HELPERS
# ============================================================

def banner(title):

    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)

# ------------------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    text = text.replace("\n", " ")

    text = text.replace("\t", " ")

    text = " ".join(text.split())

    return text.strip()

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=False,

        slow_mo=200

    )

    context = browser.new_context(

        viewport={
            "width": 1800,
            "height": 1100
        },

        ignore_https_errors=True

    )

    page = context.new_page()

    page.set_default_timeout(60000)

    # ========================================================
    # OPEN DASHBOARD
    # ========================================================

    banner(
        "OPEN DASHBOARD"
    )

    page.goto(

        POWERBI_URL,

        wait_until="domcontentloaded",

        timeout=120000

    )

    # ========================================================
    # WAIT POWER BI
    # ========================================================

    banner(
        "WAIT POWER BI RENDER"
    )

    time.sleep(35)

    # ========================================================
    # GET CONTAINERS
    # ========================================================

    banner(
        "GET VISUAL CONTAINERS"
    )

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

            if not container.is_visible():

                print(f"INDEX {i} -> NOT VISIBLE")

                continue

            bbox = container.bounding_box()

            if not bbox:

                print(f"INDEX {i} -> NO BBOX")

                continue

            text = clean_text(
                container.inner_text()
            )

            preview = text[:250]

            x = round(
                bbox["x"],
                2
            )

            y = round(
                bbox["y"],
                2
            )

            width = round(
                bbox["width"],
                2
            )

            height = round(
                bbox["height"],
                2
            )

            print(f"INDEX: {i}")

            print(f"X: {x}")

            print(f"Y: {y}")

            print(f"WIDTH: {width}")

            print(f"HEIGHT: {height}")

            print("\nTEXT PREVIEW:")

            print(preview)

            rows.append({

                "index": i,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "text_preview": preview

            })

        except Exception as e:

            print(f"ERROR INDEX {i}")

            print(e)

    # ========================================================
    # EXPORT CSV
    # ========================================================

    banner(
        "EXPORT CSV"
    )

    df = pd.DataFrame(rows)

    df.to_csv(

        CSV_OUTPUT,

        index=False,

        encoding="utf-8-sig"

    )

    print(CSV_OUTPUT)

    # ========================================================
    # FINAL
    # ========================================================

    banner(
        "INSPECTION COMPLETED"
    )

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()