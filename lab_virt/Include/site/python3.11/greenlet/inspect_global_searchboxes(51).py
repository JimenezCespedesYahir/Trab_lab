# ============================================================
# inspect_global_searchboxes.py
# ============================================================
# OBJETIVO
# ------------------------------------------------------------
# Detectar TODOS los:
#
#   - input
#   - textarea
#   - contenteditable
#
# visibles:
#
#   BEFORE dropdown
#   AFTER dropdown
#
# para descubrir:
#
#   - searchbox global Power BI
#   - textbox diferido
#   - overlay externalizado
#   - portal React
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
    "inspect_global_searchboxes_outputs"
)

SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"

OUTPUT_DIR.mkdir(
    exist_ok=True
)

SCREENSHOT_DIR.mkdir(
    exist_ok=True
)

CSV_BEFORE = (
    OUTPUT_DIR /
    "searchboxes_before.csv"
)

CSV_AFTER = (
    OUTPUT_DIR /
    "searchboxes_after.csv"
)

CSV_DIFF = (
    OUTPUT_DIR /
    "searchboxes_diff.csv"
)

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

# ------------------------------------------------------------

def screenshot(page, name):

    page.screenshot(
        path=str(
            SCREENSHOT_DIR / f"{name}.png"
        ),
        full_page=True
    )

# ============================================================
# INSPECT SEARCHBOXES
# ============================================================

def inspect_searchboxes(
    page,
    stage_name
):

    banner(
        f"INSPECT SEARCHBOXES -> {stage_name}"
    )

    selectors = [

        "input",
        "textarea",
        "[contenteditable='true']"

    ]

    rows = []

    uid = 0

    for selector in selectors:

        print("\n")
        print("-" * 70)

        print(f"SELECTOR: {selector}")

        loc = page.locator(selector)

        total = loc.count()

        print(f"TOTAL: {total}")

        for i in range(total):

            try:

                el = loc.nth(i)

                visible = el.is_visible()

                if not visible:
                    continue

                uid += 1

                bbox = el.bounding_box()

                if not bbox:
                    continue

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

                text = clean_text(
                    el.inner_text()
                )

                placeholder = (
                    el.get_attribute(
                        "placeholder"
                    ) or ""
                )

                aria = (
                    el.get_attribute(
                        "aria-label"
                    ) or ""
                )

                role = (
                    el.get_attribute(
                        "role"
                    ) or ""
                )

                typ = (
                    el.get_attribute(
                        "type"
                    ) or ""
                )

                cls = (
                    el.get_attribute(
                        "class"
                    ) or ""
                )

                title = (
                    el.get_attribute(
                        "title"
                    ) or ""
                )

                value = (
                    el.input_value()
                    if selector in ["input", "textarea"]
                    else ""
                )

                print("\nELEMENT")

                print(f"UID: {uid}")

                print(f"INDEX: {i}")

                print(f"VISIBLE: {visible}")

                print(f"X: {x}")

                print(f"Y: {y}")

                print(f"WIDTH: {width}")

                print(f"HEIGHT: {height}")

                print(f"TYPE: {typ}")

                print(f"ROLE: {role}")

                print(f"PLACEHOLDER: {placeholder}")

                print(f"ARIA: {aria}")

                print(f"TITLE: {title}")

                print(f"VALUE: {value}")

                print(f"TEXT: {text}")

                print(f"CLASS: {cls[:200]}")

                rows.append({

                    "stage": stage_name,
                    "uid": uid,
                    "selector": selector,
                    "index": i,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "type": typ,
                    "role": role,
                    "placeholder": placeholder,
                    "aria": aria,
                    "title": title,
                    "value": value,
                    "text": text,
                    "class": cls

                })

            except Exception as e:

                print(e)

    return rows

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(

        headless=False,

        slow_mo=250

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

    page.set_default_navigation_timeout(120000)

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
        "WAIT POWER BI"
    )

    time.sleep(35)

    screenshot(
        page,
        "dashboard_loaded"
    )

    # ========================================================
    # BEFORE
    # ========================================================

    before_rows = inspect_searchboxes(

        page,

        "BEFORE"

    )

    # ========================================================
    # GET CONTAINER 4
    # ========================================================

    banner(
        "GET CONTAINER 4"
    )

    containers = page.locator(
        ".visualContainer"
    )

    container = containers.nth(4)

    print(

        clean_text(
            container.inner_text()
        )

    )

    # ========================================================
    # OPEN COMBOBOX
    # ========================================================

    banner(
        "OPEN COMBOBOX"
    )

    combo = container.locator(
        "[role='combobox']"
    ).first

    combo.click(force=True)

    time.sleep(5)

    screenshot(
        page,
        "dropdown_opened"
    )

    # ========================================================
    # AFTER
    # ========================================================

    after_rows = inspect_searchboxes(

        page,

        "AFTER"

    )

    # ========================================================
    # EXPORT BEFORE
    # ========================================================

    banner(
        "EXPORT BEFORE"
    )

    df_before = pd.DataFrame(
        before_rows
    )

    df_before.to_csv(

        CSV_BEFORE,

        index=False,

        encoding="utf-8-sig"

    )

    print(CSV_BEFORE)

    # ========================================================
    # EXPORT AFTER
    # ========================================================

    banner(
        "EXPORT AFTER"
    )

    df_after = pd.DataFrame(
        after_rows
    )

    df_after.to_csv(

        CSV_AFTER,

        index=False,

        encoding="utf-8-sig"

    )

    print(CSV_AFTER)

    # ========================================================
    # DIFF
    # ========================================================

    banner(
        "BUILD DIFF"
    )

    before_keys = set(

        zip(
            df_before["x"],
            df_before["y"],
            df_before["width"],
            df_before["height"]
        )

    ) if len(df_before) > 0 else set()

    diff_rows = []

    for _, row in df_after.iterrows():

        key = (

            row["x"],
            row["y"],
            row["width"],
            row["height"]

        )

        if key not in before_keys:

            diff_rows.append(row)

    df_diff = pd.DataFrame(
        diff_rows
    )

    df_diff.to_csv(

        CSV_DIFF,

        index=False,

        encoding="utf-8-sig"

    )

    print(CSV_DIFF)

    # ========================================================
    # SUMMARY
    # ========================================================

    banner(
        "SUMMARY"
    )

    print(f"BEFORE: {len(df_before)}")

    print(f"AFTER: {len(df_after)}")

    print(f"DIFF: {len(df_diff)}")

    print("\n")
    print("=" * 80)
    print("GLOBAL SEARCHBOX INSPECTION COMPLETED")
    print("=" * 80)

    input(
        "\nENTER PARA CERRAR..."
    )

    browser.close()