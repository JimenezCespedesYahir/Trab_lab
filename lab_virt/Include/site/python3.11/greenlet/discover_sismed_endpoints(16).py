# OBJETIVO:
# Ingeniería inversa científica del ecosistema SISMED / REUNIS
#
# Detecta automáticamente:
# - endpoints AJAX
# - APIs ocultas
# - requests JSON
# - Power BI embeds
# - parámetros de filtros
# - datasets mensuales
# - consultas por establecimiento
# - consultas por producto
# - patrones SISMED
#
# SALIDAS:
# analytics/
# ├── discovered_requests.csv
# ├── discovered_json_urls.csv
# ├── discovered_powerbi.csv
# ├── discovered_ajax_payloads.csv
# ├── discovered_possible_datasets.csv
# ├── raw_html/
# └── raw_responses/
#
# ============================================================

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import re
import time
from urllib.parse import unquote

# ============================================================
# CONFIG
# ============================================================

BASE_URL = "https://www.minsa.gob.pe/reunis/?op=3&niv=5"

HEADLESS = False

WAIT_SECONDS = 15

OUTPUT_DIR = "analytics"

RAW_HTML_DIR = os.path.join(
    OUTPUT_DIR,
    "raw_html"
)

RAW_RESPONSES_DIR = os.path.join(
    OUTPUT_DIR,
    "raw_responses"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RAW_HTML_DIR, exist_ok=True)
os.makedirs(RAW_RESPONSES_DIR, exist_ok=True)

# ============================================================
# STORAGE
# ============================================================

requests_data = []

json_urls = []

powerbi_data = []

ajax_payloads = []

possible_datasets = []

# ============================================================
# HELPERS
# ============================================================

def detect_possible_dataset(url):

    keywords = [
        "json",
        "api",
        "dataset",
        "powerbi",
        "sismed",
        "consumo",
        "medic",
        "establecimiento",
        "producto",
        "mensual",
        "stock",
        "disponibilidad",
        "download",
        "csv",
        "excel",
        "xlsx",
        "pivot"
    ]

    for k in keywords:
        if k.lower() in url.lower():
            return True

    return False


def save_text_file(path, content):

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

    context = browser.new_context()

    page = context.new_page()

    # ========================================================
    # NETWORK LISTENERS
    # ========================================================

    def handle_request(request):

        try:

            url = request.url

            method = request.method

            headers = request.headers

            post_data = request.post_data

            resource_type = request.resource_type

            entry = {
                "url": url,
                "method": method,
                "resource_type": resource_type,
                "headers": json.dumps(headers),
                "post_data": post_data
            }

            requests_data.append(entry)

            # =================================================
            # DETECTAR JSON / APIs
            # =================================================

            if (
                "json" in url.lower()
                or "api" in url.lower()
                or "ajax" in url.lower()
            ):

                json_urls.append({
                    "url": url,
                    "method": method
                })

            # =================================================
            # DETECTAR POWER BI
            # =================================================

            if (
                "powerbi" in url.lower()
                or "power-bi" in url.lower()
                or "pbirs" in url.lower()
                or "reportembed" in url.lower()
            ):

                powerbi_data.append({
                    "url": url,
                    "method": method
                })

            # =================================================
            # DETECTAR AJAX PAYLOADS
            # =================================================

            if post_data:

                ajax_payloads.append({
                    "url": url,
                    "method": method,
                    "post_data": post_data
                })

            # =================================================
            # DETECTAR POSIBLES DATASETS
            # =================================================

            if detect_possible_dataset(url):

                possible_datasets.append({
                    "url": url,
                    "method": method
                })

        except Exception as e:

            print("ERROR REQUEST:", e)

    # ========================================================
    # RESPONSE CAPTURE
    # ========================================================

    def handle_response(response):

        try:

            url = response.url

            content_type = response.headers.get(
                "content-type",
                ""
            )

            # =================================================
            # GUARDAR RESPUESTAS JSON
            # =================================================

            if (
                "application/json" in content_type
                or "text/json" in content_type
            ):

                try:

                    body = response.text()

                    filename = re.sub(
                        r'[^a-zA-Z0-9]',
                        '_',
                        url
                    )[:150]

                    filepath = os.path.join(
                        RAW_RESPONSES_DIR,
                        f"{filename}.json"
                    )

                    save_text_file(
                        filepath,
                        body
                    )

                except:
                    pass

        except Exception as e:

            print("ERROR RESPONSE:", e)

    # ========================================================
    # REGISTER LISTENERS
    # ========================================================

    page.on("request", handle_request)

    page.on("response", handle_response)

    # ========================================================
    # OPEN PAGE
    # ========================================================

    print("=" * 70)
    print("ABRIENDO REUNIS / SISMED...")
    print("=" * 70)

    page.goto(
        BASE_URL,
        timeout=120000
    )

    time.sleep(WAIT_SECONDS)

    # ========================================================
    # SAVE HTML
    # ========================================================

    html = page.content()

    save_text_file(
        os.path.join(
            RAW_HTML_DIR,
            "reunis_main_page.html"
        ),
        html
    )

    print("=" * 70)
    print("HTML PRINCIPAL GUARDADO")
    print("=" * 70)

    # ========================================================
    # DETECTAR IFRAMES
    # ========================================================

    print("=" * 70)
    print("DETECTANDO IFRAMES")
    print("=" * 70)

    iframes = page.query_selector_all("iframe")

    print("TOTAL IFRAMES:", len(iframes))

    for i, iframe in enumerate(iframes):

        try:

            src = iframe.get_attribute("src")

            print(f"\nIFRAME {i}")
            print(src)

            if src:

                requests_data.append({
                    "url": src,
                    "method": "IFRAME",
                    "resource_type": "iframe",
                    "headers": "",
                    "post_data": ""
                })

        except:
            pass

    # ========================================================
    # DETECTAR SCRIPTS
    # ========================================================

    print("=" * 70)
    print("DETECTANDO SCRIPTS")
    print("=" * 70)

    scripts = page.query_selector_all("script")

    print("TOTAL SCRIPTS:", len(scripts))

    for idx, script in enumerate(scripts):

        try:

            src = script.get_attribute("src")

            if src:

                print(f"SCRIPT {idx}: {src}")

                requests_data.append({
                    "url": src,
                    "method": "SCRIPT",
                    "resource_type": "script",
                    "headers": "",
                    "post_data": ""
                })

        except:
            pass

    # ========================================================
    # DETECTAR LINKS
    # ========================================================

    print("=" * 70)
    print("DETECTANDO LINKS")
    print("=" * 70)

    links = page.query_selector_all("a")

    discovered_links = []

    for link in links:

        try:

            href = link.get_attribute("href")

            text = link.inner_text()

            if href:

                discovered_links.append({
                    "text": text,
                    "href": href
                })

        except:
            pass

    # ========================================================
    # EXPORT REQUESTS
    # ========================================================

    df_requests = pd.DataFrame(requests_data)

    df_requests.drop_duplicates(
        inplace=True
    )

    requests_path = os.path.join(
        OUTPUT_DIR,
        "discovered_requests.csv"
    )

    df_requests.to_csv(
        requests_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # EXPORT JSON URLS
    # ========================================================

    df_json = pd.DataFrame(json_urls)

    df_json.drop_duplicates(
        inplace=True
    )

    json_path = os.path.join(
        OUTPUT_DIR,
        "discovered_json_urls.csv"
    )

    df_json.to_csv(
        json_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # EXPORT POWER BI
    # ========================================================

    df_powerbi = pd.DataFrame(powerbi_data)

    df_powerbi.drop_duplicates(
        inplace=True
    )

    powerbi_path = os.path.join(
        OUTPUT_DIR,
        "discovered_powerbi.csv"
    )

    df_powerbi.to_csv(
        powerbi_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # EXPORT AJAX PAYLOADS
    # ========================================================

    df_ajax = pd.DataFrame(ajax_payloads)

    df_ajax.drop_duplicates(
        inplace=True
    )

    ajax_path = os.path.join(
        OUTPUT_DIR,
        "discovered_ajax_payloads.csv"
    )

    df_ajax.to_csv(
        ajax_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # EXPORT POSSIBLE DATASETS
    # ========================================================

    df_possible = pd.DataFrame(
        possible_datasets
    )

    df_possible.drop_duplicates(
        inplace=True
    )

    possible_path = os.path.join(
        OUTPUT_DIR,
        "discovered_possible_datasets.csv"
    )

    df_possible.to_csv(
        possible_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # EXPORT LINKS
    # ========================================================

    df_links = pd.DataFrame(
        discovered_links
    )

    links_path = os.path.join(
        OUTPUT_DIR,
        "discovered_links.csv"
    )

    df_links.to_csv(
        links_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("TOTAL REQUESTS:", len(df_requests))

    print("JSON URLS:", len(df_json))

    print("POWER BI:", len(df_powerbi))

    print("AJAX:", len(df_ajax))

    print("POSSIBLE DATASETS:", len(df_possible))

    print("LINKS:", len(df_links))

    print("\nARCHIVOS GENERADOS:")

    print(requests_path)

    print(json_path)

    print(powerbi_path)

    print(ajax_path)

    print(possible_path)

    print(links_path)

    print("\nDIRECTORIOS:")

    print(RAW_HTML_DIR)

    print(RAW_RESPONSES_DIR)

    print("=" * 70)

    print("EXPLORACIÓN SISMED COMPLETADA")
    print("=" * 70)

    time.sleep(20)

    browser.close()