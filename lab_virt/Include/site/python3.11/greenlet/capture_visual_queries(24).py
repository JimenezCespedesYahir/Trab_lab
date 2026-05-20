# ================================================================
# capture_visual_queries.py
# ================================================================
# OBJETIVO:
# Reverse engineering avanzado de visual queries Power BI
#
# Este script:
#
# ✅ intercepta querydata
# ✅ intercepta semanticQueryDataShapeCommand
# ✅ detecta DAX queries
# ✅ detecta drilldowns
# ✅ detecta slicers/filtros
# ✅ detecta filtros territoriales
# ✅ detecta granularidad EE.SS
# ✅ guarda payloads completos
# ✅ guarda responses completas
# ✅ persistencia incremental
# ✅ auditoría científica
#
# OBJETIVO CIENTÍFICO:
# Descubrir si Power BI permite:
#
# EE.SS × producto × tiempo
#
# mediante queries dinámicas.
#
# ================================================================

from playwright.sync_api import sync_playwright
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
    "analytics/powerbi_visual_queries"
)

RAW_REQUESTS_DIR = os.path.join(
    OUTPUT_DIR,
    "raw_requests"
)

RAW_RESPONSES_DIR = os.path.join(
    OUTPUT_DIR,
    "raw_responses"
)

SCREENSHOTS_DIR = os.path.join(
    OUTPUT_DIR,
    "screenshots"
)

for d in [

    OUTPUT_DIR,
    RAW_REQUESTS_DIR,
    RAW_RESPONSES_DIR,
    SCREENSHOTS_DIR

]:
    os.makedirs(d, exist_ok=True)

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

# ------------------------------------------------

def save_json(data, path):

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

def safe_filename(text):

    return (
        text.replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("?", "_")
        .replace("&", "_")
        .replace("=", "_")
    )

# ================================================================
# DATASETS
# ================================================================

captured_queries = []

captured_responses = []

# ================================================================
# KEYWORDS
# ================================================================

QUERY_KEYWORDS = [

    "querydata",

    "semanticquery",

    "semanticquerydatashapecommand",

    "executequeries",

    "dax",

    "visuals"
]

TERRITORIAL_KEYWORDS = [

    "disa",

    "red",

    "microred",

    "departamento",

    "provincia",

    "distrito",

    "ipress",

    "eess",

    "establecimiento",

    "ubigeo"
]

PRODUCT_KEYWORDS = [

    "codigo_med",

    "medicamento",

    "atc",

    "producto"
]

TEMPORAL_KEYWORDS = [

    "mesano",

    "mes",

    "fecha",

    "anno"
]

# ================================================================
# DETECTION HELPERS
# ================================================================

def detect_keywords(text, keywords):

    text = str(text).lower()

    return any(
        kw.lower() in text
        for kw in keywords
    )

# ================================================================
# PLAYWRIGHT
# ================================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    # ============================================================
    # REQUEST INTERCEPTOR
    # ============================================================

    def handle_request(request):

        try:

            url = request.url.lower()

            if detect_keywords(
                url,
                QUERY_KEYWORDS
            ):

                timestamp = now()

                print("=" * 70)
                print("VISUAL QUERY DETECTADA")
                print("=" * 70)

                print("METHOD:")
                print(request.method)

                print("=" * 70)

                print("URL:")
                print(request.url)

                print("=" * 70)

                headers = dict(
                    request.headers
                )

                post_data = request.post_data

                detected = {

                    "timestamp": timestamp,

                    "method": request.method,

                    "url": request.url,

                    "headers": headers,

                    "post_data": post_data,

                    "territorial_detected":
                        detect_keywords(
                            post_data,
                            TERRITORIAL_KEYWORDS
                        ),

                    "product_detected":
                        detect_keywords(
                            post_data,
                            PRODUCT_KEYWORDS
                        ),

                    "temporal_detected":
                        detect_keywords(
                            post_data,
                            TEMPORAL_KEYWORDS
                        )
                }

                captured_queries.append(
                    detected
                )

                # ------------------------------------------------
                # SAVE REQUEST
                # ------------------------------------------------

                request_file = os.path.join(

                    RAW_REQUESTS_DIR,

                    f"request_{timestamp}.json"
                )

                save_json(
                    detected,
                    request_file
                )

                print("REQUEST SAVED")

                print("=" * 70)

                print("TERRITORIAL:",
                      detected[
                          "territorial_detected"
                      ])

                print("PRODUCT:",
                      detected[
                          "product_detected"
                      ])

                print("TEMPORAL:",
                      detected[
                          "temporal_detected"
                      ])

                print("=" * 70)

                # ------------------------------------------------
                # PREVIEW
                # ------------------------------------------------

                if post_data:

                    print("POST DATA PREVIEW:")
                    print(post_data[:1500])

                    print("=" * 70)

        except Exception as e:

            print("REQUEST ERROR:")
            print(e)

    # ============================================================
    # RESPONSE INTERCEPTOR
    # ============================================================

    def handle_response(response):

        try:

            url = response.url.lower()

            if detect_keywords(
                url,
                QUERY_KEYWORDS
            ):

                timestamp = now()

                print("=" * 70)
                print("VISUAL RESPONSE DETECTADA")
                print("=" * 70)

                print("STATUS:")
                print(response.status)

                print("=" * 70)

                body = ""

                try:

                    body = response.text()

                except Exception:

                    pass

                detected = {

                    "timestamp": timestamp,

                    "url": response.url,

                    "status": response.status,

                    "body_preview": body[:5000],

                    "territorial_detected":
                        detect_keywords(
                            body,
                            TERRITORIAL_KEYWORDS
                        ),

                    "product_detected":
                        detect_keywords(
                            body,
                            PRODUCT_KEYWORDS
                        ),

                    "temporal_detected":
                        detect_keywords(
                            body,
                            TEMPORAL_KEYWORDS
                        )
                }

                captured_responses.append(
                    detected
                )

                # ------------------------------------------------
                # SAVE RESPONSE
                # ------------------------------------------------

                response_file = os.path.join(

                    RAW_RESPONSES_DIR,

                    f"response_{timestamp}.txt"
                )

                with open(
                    response_file,
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(body)

                print("RESPONSE SAVED")

                print("=" * 70)

                print("BODY PREVIEW:")
                print(body[:1500])

                print("=" * 70)

        except Exception as e:

            print("RESPONSE ERROR:")
            print(e)

    # ============================================================
    # ATTACH EVENTS
    # ============================================================

    page.on(
        "request",
        handle_request
    )

    page.on(
        "response",
        handle_response
    )

    # ============================================================
    # OPEN DASHBOARD
    # ============================================================

    print("=" * 70)
    print("ABRIENDO POWER BI")
    print("=" * 70)

    page.goto(
        POWERBI_URL,
        wait_until="networkidle",
        timeout=180000
    )

    # ============================================================
    # SCREENSHOT INITIAL
    # ============================================================

    page.screenshot(

        path=os.path.join(
            SCREENSHOTS_DIR,
            "initial_dashboard.png"
        ),

        full_page=True
    )

    # ============================================================
    # WAIT LOAD
    # ============================================================

    print("=" * 70)
    print("ESPERANDO CARGA")
    print("=" * 70)

    time.sleep(20)

    # ============================================================
    # INTERACTIVE EXPLORATION
    # ============================================================

    print("=" * 70)
    print("EXPLORACIÓN INTERACTIVA")
    print("=" * 70)

    # ------------------------------------------------------------
    # CLICK VISUALS
    # ------------------------------------------------------------

    selectors = [

        "div[role='button']",

        "svg",

        "canvas"
    ]

    click_counter = 0

    for selector in selectors:

        try:

            elements = page.locator(selector)

            count = min(
                elements.count(),
                15
            )

            print(f"{selector}: {count}")

            for i in range(count):

                try:

                    el = elements.nth(i)

                    el.click(
                        timeout=3000
                    )

                    click_counter += 1

                    print(
                        f"CLICK {click_counter}"
                    )

                    time.sleep(2)

                except Exception:

                    pass

        except Exception:

            pass

    # ============================================================
    # FINAL SCREENSHOT
    # ============================================================

    page.screenshot(

        path=os.path.join(
            SCREENSHOTS_DIR,
            "final_dashboard.png"
        ),

        full_page=True
    )

    # ============================================================
    # EXPORT SUMMARY
    # ============================================================

    df_requests = []

    for r in captured_queries:

        df_requests.append({

            "timestamp": r["timestamp"],

            "method": r["method"],

            "url": r["url"],

            "territorial_detected":
                r["territorial_detected"],

            "product_detected":
                r["product_detected"],

            "temporal_detected":
                r["temporal_detected"]
        })

    import pandas as pd

    df_requests = pd.DataFrame(
        df_requests
    )

    df_requests.to_csv(

        os.path.join(
            OUTPUT_DIR,
            "captured_visual_queries.csv"
        ),

        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("QUERIES:", len(captured_queries))

    print("RESPONSES:", len(captured_responses))

    print("CLICKS:", click_counter)

    print("=" * 70)

    territorial_count = sum(
        r["territorial_detected"]
        for r in captured_queries
    )

    product_count = sum(
        r["product_detected"]
        for r in captured_queries
    )

    temporal_count = sum(
        r["temporal_detected"]
        for r in captured_queries
    )

    print("TERRITORIAL QUERIES:",
          territorial_count)

    print("PRODUCT QUERIES:",
          product_count)

    print("TEMPORAL QUERIES:",
          temporal_count)

    print("=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print("captured_visual_queries.csv")
    print("raw_requests/")
    print("raw_responses/")
    print("screenshots/")

    print("=" * 70)
    print("VISUAL QUERY CAPTURE COMPLETED")
    print("=" * 70)

    time.sleep(10)

    browser.close()