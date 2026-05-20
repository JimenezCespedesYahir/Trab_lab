# ================================================================
# apply_lcc_filters_and_export.py
# ================================================================
#
# OBJETIVO:
#
# Automatizar completamente:
#
# 1. Abrir dashboard Power BI
# 2. Abrir panel filtros
# 3. Aplicar:
#
#    Unidad ejecutora:
#       SALUD LUCIANO CASTILLO COLONNA
#
#    Macroregion:
#       NORTE
#
#    Institucion:
#       GOBIERNO REGIONAL
#
# 4. Esperar rerender
# 5. Capturar querydata AFTER filtering
# 6. Detectar WHERE territorial real
# 7. Exportar payloads
# 8. Descargar dataset automáticamente
#
# ================================================================
#
# OUTPUTS:
#
# analytics/lcc_export_pipeline/
#
#   ├── screenshots/
#   ├── payloads/
#   ├── responses/
#   ├── exports/
#   ├── querydata_after_filters.csv
#   ├── territorial_where_clauses.csv
#   ├── detected_literals.csv
#   ├── replayable_payloads.csv
#   └── execution_summary.json
#
# ================================================================

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import time
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

POWERBI_URL = (
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUt"
    "MGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVk"
    "YWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"
    "&pageName=ReportSection"
)

OUTPUT_DIR = (
    "analytics/lcc_export_pipeline"
)

PAYLOAD_DIR = os.path.join(
    OUTPUT_DIR,
    "payloads"
)

RESPONSES_DIR = os.path.join(
    OUTPUT_DIR,
    "responses"
)

EXPORTS_DIR = os.path.join(
    OUTPUT_DIR,
    "exports"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [
    OUTPUT_DIR,
    PAYLOAD_DIR,
    RESPONSES_DIR,
    EXPORTS_DIR,
    SCREENSHOT_DIR
]:
    os.makedirs(
        d,
        exist_ok=True
    )

# ================================================================
# FILTERS
# ================================================================

TARGET_FILTERS = {

    "Unidad ejecutora":
        "SALUD LUCIANO CASTILLO COLONNA",

    "MACROREGION":
        "NORTE",

    "Institución":
        "GOBIERNO REGIONAL"
}

# ================================================================
# DATASETS
# ================================================================

query_logs = []

where_logs = []

literal_logs = []

replay_logs = []

download_logs = []

# ================================================================
# HELPERS
# ================================================================

def ts():

    return datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

# ------------------------------------------------

def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# ------------------------------------------------

def contains_territorial(text):

    if text is None:
        return False

    t = str(text).lower()

    keys = [

        "sullana",
        "luciano",
        "castillo",
        "piura",
        "norte",
        "gobierno regional",
        "red",
        "micro",
        "unidad ejecutora",
        "diresa",
        "geresa"
    ]

    return any(
        k in t
        for k in keys
    )

# ------------------------------------------------

def recursive_extract(
    obj,
    found_literals,
    found_where
):

    if isinstance(obj, dict):

        for k, v in obj.items():

            if str(k).lower() == "where":

                found_where.append(v)

            recursive_extract(
                v,
                found_literals,
                found_where
            )

    elif isinstance(obj, list):

        for item in obj:

            recursive_extract(
                item,
                found_literals,
                found_where
            )

    else:

        try:

            s = str(obj)

            if contains_territorial(s):

                found_literals.append(s)

        except:
            pass

# ================================================================
# PLAYWRIGHT
# ================================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        accept_downloads=True
    )

    page = context.new_page()

    # ============================================================
    # NETWORK INTERCEPTION
    # ============================================================

    def handle_response(response):

        try:

            url = response.url

            if "/querydata" not in url:
                return

            body = response.request.post_data

            text = response.text()

            timestamp = ts()

            payload_file = os.path.join(

                PAYLOAD_DIR,

                f"query_{timestamp}.json"
            )

            response_file = os.path.join(

                RESPONSES_DIR,

                f"response_{timestamp}.json"
            )

            # ----------------------------------------------------
            # SAVE RAW
            # ----------------------------------------------------

            with open(
                payload_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    body if body else ""
                )

            with open(
                response_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(text)

            # ----------------------------------------------------
            # PARSE
            # ----------------------------------------------------

            found_literals = []

            found_where = []

            try:

                if body:

                    parsed = json.loads(body)

                    recursive_extract(
                        parsed,
                        found_literals,
                        found_where
                    )

            except:
                pass

            territorial = any(
                contains_territorial(x)
                for x in found_literals
            )

            # ----------------------------------------------------
            # QUERY LOG
            # ----------------------------------------------------

            query_logs.append({

                "timestamp":
                    timestamp,

                "url":
                    url,

                "territorial":
                    territorial,

                "where_count":
                    len(found_where),

                "literal_count":
                    len(found_literals),

                "payload_file":
                    payload_file,

                "response_file":
                    response_file
            })

            # ----------------------------------------------------
            # WHERE LOGS
            # ----------------------------------------------------

            for w in found_where:

                where_logs.append({

                    "timestamp":
                        timestamp,

                    "where":
                        str(w)[:5000]
                })

            # ----------------------------------------------------
            # LITERALS
            # ----------------------------------------------------

            for lit in found_literals:

                literal_logs.append({

                    "timestamp":
                        timestamp,

                    "literal":
                        lit
                })

            # ----------------------------------------------------
            # REPLAY
            # ----------------------------------------------------

            replay_logs.append({

                "timestamp":
                    timestamp,

                "request_url":
                    url,

                "payload_file":
                    payload_file
            })

            # ----------------------------------------------------
            # CONSOLE
            # ----------------------------------------------------

            print("=" * 70)
            print("QUERYDATA CAPTURADA")
            print("=" * 70)

            print(f"WHERE: {len(found_where)}")
            print(f"LITERALS: {len(found_literals)}")
            print(f"TERRITORIAL: {territorial}")

            if territorial:

                print("=" * 70)
                print("TERRITORIAL LITERALS")
                print("=" * 70)

                for lit in found_literals[:20]:

                    print(lit)

        except Exception as e:

            print(e)

    page.on(
        "response",
        handle_response
    )

    # ============================================================
    # OPEN DASHBOARD
    # ============================================================

    print("=" * 70)
    print("ABRIENDO DASHBOARD")
    print("=" * 70)

    page.goto(

        POWERBI_URL,

        wait_until="networkidle",

        timeout=180000
    )

    time.sleep(30)

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "dashboard_loaded.png"
        ),

        full_page=True
    )

    # ============================================================
    # OPEN FILTER PANEL
    # ============================================================

    print("=" * 70)
    print("ABRIENDO PANEL FILTROS")
    print("=" * 70)

    opened_filters = False

    filter_keywords = [

        "Filtros",
        "filtros"
    ]

    all_clickables = page.locator(

        "button, div, span"

    )

    total = min(
        all_clickables.count(),
        2000
    )

    for i in range(total):

        try:

            el = all_clickables.nth(i)

            txt = el.inner_text().strip()

            if txt in filter_keywords:

                el.click(force=True)

                opened_filters = True

                print(f"FILTROS OPENED: {txt}")

                time.sleep(5)

                break

        except:
            pass

    # ============================================================
    # SCREENSHOT FILTERS
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "filters_opened.png"
        ),

        full_page=True
    )

    # ============================================================
    # APPLY FILTERS
    # ============================================================

    print("=" * 70)
    print("APLICANDO FILTROS")
    print("=" * 70)

    combos = page.locator(

        "[role='combobox'], select"

    )

    combo_count = min(
        combos.count(),
        50
    )

    print(f"COMBOBOXES: {combo_count}")

    for i in range(combo_count):

        try:

            combo = combos.nth(i)

            txt = combo.inner_text().strip()

            aria = combo.get_attribute(
                "aria-label"
            )

            combined = (
                str(txt)
                + " "
                + str(aria)
            ).lower()

            print("=" * 70)
            print(f"COMBO {i}")
            print(combined)

            # ----------------------------------------------------
            # UNIDAD EJECUTORA
            # ----------------------------------------------------

            if (
                "unidad ejecutora"
                in combined
            ):

                print("MATCH: UNIDAD EJECUTORA")

                combo.click(force=True)

                time.sleep(3)

                page.keyboard.press("Control+A")

                page.keyboard.type(
                    "SALUD LUCIANO CASTILLO COLONNA"
                )

                time.sleep(2)

                page.keyboard.press("Enter")

                time.sleep(10)

            # ----------------------------------------------------
            # MACROREGION
            # ----------------------------------------------------

            if (
                "macroregion"
                in combined
                or "macroregión"
                in combined
            ):

                print("MATCH: MACROREGION")

                combo.click(force=True)

                time.sleep(2)

                page.keyboard.press("Control+A")

                page.keyboard.type(
                    "NORTE"
                )

                time.sleep(2)

                page.keyboard.press("Enter")

                time.sleep(10)

            # ----------------------------------------------------
            # INSTITUCION
            # ----------------------------------------------------

            if (
                "institución"
                in combined
                or "institucion"
                in combined
            ):

                print("MATCH: INSTITUCION")

                combo.click(force=True)

                time.sleep(2)

                page.keyboard.press("Control+A")

                page.keyboard.type(
                    "GOBIERNO REGIONAL"
                )

                time.sleep(2)

                page.keyboard.press("Enter")

                time.sleep(10)

        except Exception as e:

            print(e)

    # ============================================================
    # WAIT RERENDER
    # ============================================================

    print("=" * 70)
    print("WAITING RERENDER")
    print("=" * 70)

    time.sleep(20)

    # ============================================================
    # SCREENSHOT AFTER FILTERS
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "after_filters.png"
        ),

        full_page=True
    )

    # ============================================================
    # EXPORT / DOWNLOAD
    # ============================================================

    print("=" * 70)
    print("BUSCANDO DESCARGA")
    print("=" * 70)

    buttons = page.locator(
        "button, div, span"
    )

    total = min(
        buttons.count(),
        2500
    )

    for i in range(total):

        try:

            el = buttons.nth(i)

            txt = el.inner_text().strip().lower()

            if any(

                k in txt

                for k in [

                    "descargar",
                    "export",
                    "csv",
                    "xlsx"
                ]
            ):

                print("=" * 70)
                print("DOWNLOAD BUTTON")
                print("=" * 70)

                print(txt)

                try:

                    with page.expect_download(
                        timeout=15000
                    ) as download_info:

                        el.click(force=True)

                    download = download_info.value

                    save_path = os.path.join(

                        EXPORTS_DIR,

                        download.suggested_filename
                    )

                    download.save_as(
                        save_path
                    )

                    download_logs.append({

                        "file":
                            save_path
                    })

                    print(f"DOWNLOADED: {save_path}")

                except Exception as e:

                    print(e)

        except:
            pass

    # ============================================================
    # EXPORT CSV
    # ============================================================

    pd.DataFrame(
        query_logs
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "querydata_after_filters.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        where_logs
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "territorial_where_clauses.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        literal_logs
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_literals.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        replay_logs
    ).to_csv(

        os.path.join(
            OUTPUT_DIR,
            "replayable_payloads.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    summary = {

        "querydata_detected":
            len(query_logs),

        "where_detected":
            len(where_logs),

        "territorial_literals":
            len(literal_logs),

        "downloads":
            len(download_logs),

        "payloads_saved":
            len(os.listdir(PAYLOAD_DIR)),

        "responses_saved":
            len(os.listdir(RESPONSES_DIR))
    }

    save_json(

        os.path.join(
            OUTPUT_DIR,
            "execution_summary.json"
        ),

        summary
    )

    # ============================================================
    # FINAL SCREENSHOT
    # ============================================================

    page.screenshot(

        path=os.path.join(

            SCREENSHOT_DIR,

            "final_state.png"
        ),

        full_page=True
    )

    # ============================================================
    # CONSOLE
    # ============================================================

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for k, v in summary.items():

        print(f"{k}: {v}")

    print("=" * 70)

    print("PIPELINE LCC COMPLETADO")
    print("=" * 70)

    time.sleep(15)

    browser.close()