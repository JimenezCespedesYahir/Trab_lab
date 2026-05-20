# OBJETIVO:
# Ingeniería inversa funcional de REUNIS / SISMED
#
# Explora dinámicamente:
# - tabs
# - botones
# - filtros
# - formularios
# - exportaciones
# - requests AJAX
# - requests POST
# - descargas Excel
# - datasets ocultos
#
# Además:
# - hace click automáticamente
# - captura network traffic
# - captura respuestas JSON
# - detecta endpoints exportables
# - detecta meses
# - detecta variables SISMED
#
# ============================================================

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import re
import time
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://www.minsa.gob.pe/reunis/?op=3&niv=5"

HEADLESS = False

WAIT_SHORT = 3
WAIT_MEDIUM = 7
WAIT_LONG = 15

OUTPUT_DIR = "analytics"

RAW_DIR = os.path.join(
    OUTPUT_DIR,
    "interaction_raw"
)

SCREENSHOT_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

DOWNLOAD_DIR = os.path.join(
    OUTPUT_DIR,
    "downloads"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ============================================================
# STORAGE
# ============================================================

network_requests = []

network_responses = []

detected_buttons = []

detected_forms = []

detected_selects = []

detected_inputs = []

detected_downloads = []

detected_tables = []

detected_tabs = []

possible_endpoints = []

# ============================================================
# HELPERS
# ============================================================

def safe_filename(text):

    text = re.sub(
        r'[^a-zA-Z0-9_\-]',
        '_',
        text
    )

    return text[:150]


def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def save_text(path, content):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

# ============================================================
# PLAYWRIGHT
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=HEADLESS
    )

    context = browser.new_context(
        accept_downloads=True
    )

    page = context.new_page()

    # ========================================================
    # NETWORK CAPTURE
    # ========================================================

    def handle_request(request):

        try:

            entry = {

                "timestamp":
                    datetime.utcnow().isoformat(),

                "method":
                    request.method,

                "url":
                    request.url,

                "resource_type":
                    request.resource_type,

                "headers":
                    json.dumps(request.headers),

                "post_data":
                    request.post_data
            }

            network_requests.append(entry)

            url = request.url.lower()

            keywords = [

                "json",
                "api",
                "excel",
                "xlsx",
                "csv",
                "download",
                "export",
                "sismed",
                "consumo",
                "producto",
                "establecimiento",
                "medicamento",
                "mensual"
            ]

            if any(k in url for k in keywords):

                possible_endpoints.append(entry)

        except Exception as e:

            print("REQUEST ERROR:", e)

    # ========================================================
    # RESPONSE CAPTURE
    # ========================================================

    def handle_response(response):

        try:

            content_type = response.headers.get(
                "content-type",
                ""
            )

            body = None

            if (
                "json" in content_type.lower()
                or "javascript" in content_type.lower()
                or "text" in content_type.lower()
            ):

                try:
                    body = response.text()[:2000]
                except:
                    body = None

            entry = {

                "timestamp":
                    datetime.utcnow().isoformat(),

                "url":
                    response.url,

                "status":
                    response.status,

                "content_type":
                    content_type,

                "body_preview":
                    body
            }

            network_responses.append(entry)

        except Exception as e:

            print("RESPONSE ERROR:", e)

    # ========================================================
    # DOWNLOAD CAPTURE
    # ========================================================

    def handle_download(download):

        try:

            filename = download.suggested_filename

            path = os.path.join(
                DOWNLOAD_DIR,
                filename
            )

            download.save_as(path)

            detected_downloads.append({

                "filename": filename,
                "path": path,
                "url": download.url
            })

            print("=" * 60)
            print("DOWNLOAD DETECTADO")
            print("=" * 60)

            print(filename)

        except Exception as e:

            print("DOWNLOAD ERROR:", e)

    # ========================================================
    # REGISTER EVENTS
    # ========================================================

    page.on("request", handle_request)

    page.on("response", handle_response)

    page.on("download", handle_download)

    # ========================================================
    # OPEN PAGE
    # ========================================================

    print("=" * 70)
    print("ABRIENDO REUNIS/SISMED")
    print("=" * 70)

    page.goto(
        BASE_URL,
        timeout=120000
    )

    time.sleep(WAIT_LONG)

    # ========================================================
    # SAVE INITIAL HTML
    # ========================================================

    html = page.content()

    save_text(

        os.path.join(
            RAW_DIR,
            "initial_page.html"
        ),

        html
    )

    # ========================================================
    # SCREENSHOT
    # ========================================================

    page.screenshot(

        path=os.path.join(
            SCREENSHOT_DIR,
            "initial_page.png"
        ),

        full_page=True
    )

    # ========================================================
    # DETECT TABS
    # ========================================================

    print("=" * 70)
    print("DETECTANDO TABS")
    print("=" * 70)

    tab_selectors = [

        "a",
        "button",
        "[role='tab']",
        ".nav-link",
        ".tab",
        ".menu",
        ".dropdown-item"
    ]

    for selector in tab_selectors:

        try:

            elements = page.query_selector_all(
                selector
            )

            for idx, el in enumerate(elements):

                try:

                    text = el.inner_text().strip()

                    href = el.get_attribute("href")

                    if len(text) > 0:

                        detected_tabs.append({

                            "selector":
                                selector,

                            "text":
                                text,

                            "href":
                                href
                        })

                except:
                    pass

        except:
            pass

    print("Tabs detectados:", len(detected_tabs))

    # ========================================================
    # DETECT FORMS
    # ========================================================

    print("=" * 70)
    print("DETECTANDO FORMULARIOS")
    print("=" * 70)

    forms = page.query_selector_all("form")

    print("Forms:", len(forms))

    for idx, form in enumerate(forms):

        try:

            action = form.get_attribute("action")

            method = form.get_attribute("method")

            detected_forms.append({

                "form_index": idx,
                "action": action,
                "method": method
            })

        except:
            pass

    # ========================================================
    # DETECT SELECTS
    # ========================================================

    print("=" * 70)
    print("DETECTANDO SELECTS")
    print("=" * 70)

    selects = page.query_selector_all("select")

    print("Selects:", len(selects))

    for idx, sel in enumerate(selects):

        try:

            name = sel.get_attribute("name")

            options = sel.query_selector_all("option")

            values = []

            for op in options[:20]:

                try:

                    values.append({

                        "text":
                            op.inner_text(),

                        "value":
                            op.get_attribute("value")
                    })

                except:
                    pass

            detected_selects.append({

                "select_index": idx,
                "name": name,
                "options": values
            })

        except:
            pass

    # ========================================================
    # DETECT INPUTS
    # ========================================================

    print("=" * 70)
    print("DETECTANDO INPUTS")
    print("=" * 70)

    inputs = page.query_selector_all("input")

    print("Inputs:", len(inputs))

    for idx, inp in enumerate(inputs):

        try:

            detected_inputs.append({

                "index": idx,

                "type":
                    inp.get_attribute("type"),

                "name":
                    inp.get_attribute("name"),

                "id":
                    inp.get_attribute("id"),

                "placeholder":
                    inp.get_attribute(
                        "placeholder"
                    )
            })

        except:
            pass

    # ========================================================
    # DETECT TABLES
    # ========================================================

    print("=" * 70)
    print("DETECTANDO TABLAS")
    print("=" * 70)

    tables = page.query_selector_all("table")

    print("Tables:", len(tables))

    for idx, table in enumerate(tables):

        try:

            text = table.inner_text()[:1000]

            detected_tables.append({

                "table_index": idx,
                "preview": text
            })

        except:
            pass

    # ========================================================
    # INTERACTIVE EXPLORATION
    # ========================================================

    print("=" * 70)
    print("EXPLORACIÓN INTERACTIVA")
    print("=" * 70)

    clickable_selectors = [

        "button",
        "a",
        ".btn",
        ".nav-link",
        ".dropdown-item",
        "[onclick]"
    ]

    clicked = 0

    for selector in clickable_selectors:

        try:

            elements = page.query_selector_all(
                selector
            )

            for idx, el in enumerate(elements[:20]):

                try:

                    text = el.inner_text().strip()

                    if len(text) == 0:
                        continue

                    print("\nCLICK:")
                    print(text)

                    el.click(timeout=3000)

                    clicked += 1

                    time.sleep(WAIT_SHORT)

                    # screenshot after click

                    page.screenshot(

                        path=os.path.join(

                            SCREENSHOT_DIR,

                            f"click_{clicked}.png"
                        ),

                        full_page=True
                    )

                except:
                    pass

        except:
            pass

    # ========================================================
    # SAVE FINAL HTML
    # ========================================================

    final_html = page.content()

    save_text(

        os.path.join(
            RAW_DIR,
            "final_page.html"
        ),

        final_html
    )

    # ========================================================
    # EXPORT CSV
    # ========================================================

    pd.DataFrame(
        network_requests
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "interaction_requests.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        network_responses
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "interaction_responses.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_tabs
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_tabs.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_forms
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_forms.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_selects
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_selects.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_inputs
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_inputs.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_tables
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_tables.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        detected_downloads
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "detected_downloads.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(
        possible_endpoints
    ).drop_duplicates().to_csv(

        os.path.join(
            OUTPUT_DIR,
            "possible_endpoints.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("Requests:", len(network_requests))

    print("Responses:", len(network_responses))

    print("Tabs:", len(detected_tabs))

    print("Forms:", len(detected_forms))

    print("Selects:", len(detected_selects))

    print("Inputs:", len(detected_inputs))

    print("Tables:", len(detected_tables))

    print("Downloads:", len(detected_downloads))

    print("Possible endpoints:", len(possible_endpoints))

    print("=" * 70)

    print("EXPLORACIÓN INTERACTIVA COMPLETADA")
    print("=" * 70)

    time.sleep(20)

    browser.close()