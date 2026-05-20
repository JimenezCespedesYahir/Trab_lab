# OBJETIVO:
# Ingeniería inversa profesional del dashboard Power BI
# "Consumo Histórico SISMED"
#
# FUNCIONALIDADES:
# ✅ Playwright
# ✅ Network interception
# ✅ Request logging
# ✅ Response logging
# ✅ Retry automático
# ✅ Persistencia incremental
# ✅ Raw JSON storage
# ✅ Metadata extraction
# ✅ Visual detection
# ✅ PowerBI query detection
#
# AUTOR:
# Proyecto HVRPTW Farmacéutico DSRSLCC - Sullana
# ================================================================

from playwright.sync_api import sync_playwright
import json
import pandas as pd
import os
import time
from datetime import datetime
from urllib.parse import urlparse

# ================================================================
# CONFIGURACIÓN
# ================================================================

POWERBI_URL = (
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUt"
    "MGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVk"
    "YWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"
    "&pageName=ReportSection"
)

OUTPUT_DIR = "analytics/powerbi_consumption"

RAW_REQUESTS_DIR = os.path.join(
    OUTPUT_DIR,
    "raw_requests"
)

RAW_RESPONSES_DIR = os.path.join(
    OUTPUT_DIR,
    "raw_responses"
)

JSON_RESPONSES_DIR = os.path.join(
    OUTPUT_DIR,
    "json_responses"
)

METADATA_DIR = os.path.join(
    OUTPUT_DIR,
    "metadata"
)

# ================================================================
# CREAR DIRECTORIOS
# ================================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RAW_REQUESTS_DIR, exist_ok=True)
os.makedirs(RAW_RESPONSES_DIR, exist_ok=True)
os.makedirs(JSON_RESPONSES_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# ================================================================
# VARIABLES GLOBALES
# ================================================================

all_requests = []
all_responses = []
visual_candidates = []
powerbi_queries = []
json_urls = []

request_counter = 0
response_counter = 0

# ================================================================
# HELPERS
# ================================================================

def timestamp():
    return datetime.utcnow().isoformat()

# ------------------------------------------------

def save_json(data, filepath):

    with open(
        filepath,
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

def save_text(text, filepath):

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(text)

# ------------------------------------------------

def safe_filename(text):

    invalid = [
        "/",
        "\\",
        ":",
        "?",
        "&",
        "=",
        "%",
        "*",
        '"',
        "<",
        ">",
        "|"
    ]

    for ch in invalid:
        text = text.replace(ch, "_")

    return text[:200]

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
    # REQUEST INTERCEPTION
    # ============================================================

    def handle_request(request):

        global request_counter

        request_counter += 1

        try:

            request_data = {
                "timestamp": timestamp(),
                "method": request.method,
                "url": request.url,
                "resource_type": request.resource_type,
                "headers": dict(request.headers),
                "post_data": request.post_data
            }

            all_requests.append(request_data)

            filename = (
                f"request_{request_counter}_"
                f"{safe_filename(request.url)}.json"
            )

            filepath = os.path.join(
                RAW_REQUESTS_DIR,
                filename
            )

            save_json(request_data, filepath)

            # ----------------------------------------------------
            # DETECCIÓN POWER BI
            # ----------------------------------------------------

            lower_url = request.url.lower()

            keywords = [
                "querydata",
                "metadata",
                "visuals",
                "explore",
                "semantic",
                "query",
                "dataset",
                "model",
                "reportsession",
                "bootstrapconfig"
            ]

            if any(k in lower_url for k in keywords):

                powerbi_queries.append({
                    "timestamp": timestamp(),
                    "url": request.url,
                    "method": request.method
                })

                print("=" * 70)
                print("POWER BI QUERY DETECTADA")
                print("=" * 70)
                print(request.method)
                print(request.url)

        except Exception as e:

            print("ERROR REQUEST:", e)

    # ============================================================
    # RESPONSE INTERCEPTION
    # ============================================================

    def handle_response(response):

        global response_counter

        response_counter += 1

        try:

            response_data = {
                "timestamp": timestamp(),
                "url": response.url,
                "status": response.status,
                "headers": dict(response.headers)
            }

            all_responses.append(response_data)

            # ----------------------------------------------------
            # RAW RESPONSE
            # ----------------------------------------------------

            try:

                body = response.text()

            except Exception:

                body = ""

            filename = (
                f"response_{response_counter}_"
                f"{safe_filename(response.url)}.txt"
            )

            filepath = os.path.join(
                RAW_RESPONSES_DIR,
                filename
            )

            save_text(body, filepath)

            # ----------------------------------------------------
            # DETECTAR JSON
            # ----------------------------------------------------

            content_type = (
                response.headers.get(
                    "content-type",
                    ""
                ).lower()
            )

            if (
                "application/json" in content_type
                or body.startswith("{")
                or body.startswith("[")
            ):

                json_urls.append(response.url)

                try:

                    parsed_json = json.loads(body)

                    json_filename = (
                        f"json_{response_counter}_"
                        f"{safe_filename(response.url)}.json"
                    )

                    json_filepath = os.path.join(
                        JSON_RESPONSES_DIR,
                        json_filename
                    )

                    save_json(
                        parsed_json,
                        json_filepath
                    )

                    # --------------------------------------------
                    # DETECTAR VISUALES
                    # --------------------------------------------

                    body_lower = body.lower()

                    visual_keywords = [
                        "visualcontainer",
                        "semanticquery",
                        "prototypequery",
                        "singlevisual",
                        "visual",
                        "querydata"
                    ]

                    if any(
                        k in body_lower
                        for k in visual_keywords
                    ):

                        visual_candidates.append({
                            "url": response.url,
                            "status": response.status
                        })

                        print("=" * 70)
                        print("VISUAL / QUERY DETECTADO")
                        print("=" * 70)
                        print(response.url)

                except Exception:
                    pass

        except Exception as e:

            print("ERROR RESPONSE:", e)

    # ============================================================
    # EVENTOS
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
    # NAVEGACIÓN
    # ============================================================

    print("=" * 70)
    print("ABRIENDO POWER BI...")
    print("=" * 70)

    max_retries = 3

    for attempt in range(max_retries):

        try:

            page.goto(
                POWERBI_URL,
                timeout=180000,
                wait_until="networkidle"
            )

            break

        except Exception as e:

            print(f"RETRY {attempt+1}: {e}")

            time.sleep(5)

    # ============================================================
    # ESPERAR CARGA
    # ============================================================

    print("=" * 70)
    print("ESPERANDO CARGA COMPLETA...")
    print("=" * 70)

    time.sleep(25)

    # ============================================================
    # DETECTAR IFRAMES
    # ============================================================

    print("=" * 70)
    print("DETECTANDO IFRAMES")
    print("=" * 70)

    frames = page.frames

    print("TOTAL FRAMES:", len(frames))

    frame_metadata = []

    for i, frame in enumerate(frames):

        try:

            frame_info = {
                "index": i,
                "name": frame.name,
                "url": frame.url
            }

            frame_metadata.append(frame_info)

            print(i, frame.url)

        except Exception:
            pass

    # ============================================================
    # DETECTAR ELEMENTOS VISUALES
    # ============================================================

    print("=" * 70)
    print("DETECTANDO ELEMENTOS VISUALES")
    print("=" * 70)

    try:

        visuals = page.locator(
            "div"
        ).all()

        print("DIVS DETECTADOS:", len(visuals))

    except Exception as e:

        print("ERROR VISUALES:", e)

    # ============================================================
    # SCREENSHOT
    # ============================================================

    screenshot_path = os.path.join(
        OUTPUT_DIR,
        "dashboard_capture.png"
    )

    page.screenshot(
        path=screenshot_path,
        full_page=True
    )

    # ============================================================
    # EXPORTAR METADATA
    # ============================================================

    requests_df = pd.DataFrame(all_requests)
    responses_df = pd.DataFrame(all_responses)

    requests_df.to_csv(
        os.path.join(
            METADATA_DIR,
            "requests_log.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    responses_df.to_csv(
        os.path.join(
            METADATA_DIR,
            "responses_log.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(powerbi_queries).to_csv(
        os.path.join(
            METADATA_DIR,
            "powerbi_queries.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(visual_candidates).to_csv(
        os.path.join(
            METADATA_DIR,
            "visual_candidates.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame(frame_metadata).to_csv(
        os.path.join(
            METADATA_DIR,
            "frames_metadata.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    # ============================================================
    # RESUMEN FINAL
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("REQUESTS:", len(all_requests))
    print("RESPONSES:", len(all_responses))
    print("JSON URLS:", len(json_urls))
    print("POWER BI QUERIES:", len(powerbi_queries))
    print("VISUAL CANDIDATES:", len(visual_candidates))
    print("FRAMES:", len(frame_metadata))

    print("=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print(RAW_REQUESTS_DIR)
    print(RAW_RESPONSES_DIR)
    print(JSON_RESPONSES_DIR)
    print(METADATA_DIR)

    print("=" * 70)
    print("INGENIERÍA INVERSA COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()