# OBJETIVO:
# Capturar EXACTAMENTE el request real Power BI
# hacia conceptualschema.
#
# IMPORTANTE:
# NO estamos adivinando payloads.
# Estamos interceptando el request real.
#
# FUNCIONALIDADES:
# ✅ intercept request real
# ✅ capturar method
# ✅ capturar headers
# ✅ capturar body
# ✅ capturar cookies
# ✅ guardar replay request
# ✅ persistencia incremental
# ✅ auditoría científica
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

OUTPUT_DIR = "analytics/conceptualschema_capture"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().isoformat()

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

# ================================================================
# VARIABLES
# ================================================================

captured = False

captured_request = {}

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
    # INTERCEPTOR
    # ============================================================

    def handle_request(request):

        global captured
        global captured_request

        try:

            url = request.url.lower()

            # ----------------------------------------------------
            # DETECTAR conceptualschema
            # ----------------------------------------------------

            if "conceptualschema" in url:

                captured = True

                print("=" * 70)
                print("CONCEPTUALSCHEMA REQUEST DETECTADO")
                print("=" * 70)

                print("METHOD:")
                print(request.method)

                print("=" * 70)

                print("URL:")
                print(request.url)

                print("=" * 70)

                # ------------------------------------------------
                # HEADERS
                # ------------------------------------------------

                headers = dict(
                    request.headers
                )

                print("HEADERS DETECTADOS")

                # ------------------------------------------------
                # POST DATA
                # ------------------------------------------------

                post_data = request.post_data

                # ------------------------------------------------
                # COOKIES
                # ------------------------------------------------

                cookies = context.cookies()

                # ------------------------------------------------
                # CONSTRUIR PAYLOAD
                # ------------------------------------------------

                captured_request = {

                    "capture_timestamp": now(),

                    "request": {

                        "method": request.method,

                        "url": request.url,

                        "headers": headers,

                        "post_data": post_data

                    },

                    "cookies": cookies
                }

                # ------------------------------------------------
                # EXPORT RAW
                # ------------------------------------------------

                save_json(

                    captured_request,

                    os.path.join(
                        OUTPUT_DIR,
                        "captured_conceptualschema_request.json"
                    )

                )

                # ------------------------------------------------
                # CURL REPLAY
                # ------------------------------------------------

                curl_headers = ""

                for k, v in headers.items():

                    curl_headers += (
                        f'-H "{k}: {v}" '
                    )

                curl_command = (
                    f'curl -X {request.method} '
                    f'"{request.url}" '
                    f'{curl_headers} '
                )

                if post_data:

                    curl_command += (
                        f"--data '{post_data}'"
                    )

                with open(

                    os.path.join(
                        OUTPUT_DIR,
                        "replay_request.sh"
                    ),

                    "w",

                    encoding="utf-8"

                ) as f:

                    f.write(curl_command)

                # ------------------------------------------------
                # RESUMEN
                # ------------------------------------------------

                print("=" * 70)
                print("REQUEST CAPTURADO")
                print("=" * 70)

                print("POST DATA LENGTH:")

                if post_data:

                    print(len(post_data))

                else:

                    print("NO POST DATA")

                print("=" * 70)

                print("COOKIES:")

                print(len(cookies))

                print("=" * 70)

        except Exception as e:

            print("ERROR REQUEST:")
            print(e)

    # ============================================================
    # RESPONSE INTERCEPTOR
    # ============================================================

    def handle_response(response):

        try:

            if "conceptualschema" in response.url.lower():

                print("=" * 70)
                print("CONCEPTUALSCHEMA RESPONSE")
                print("=" * 70)

                print("STATUS:")
                print(response.status)

                print("=" * 70)

                # ------------------------------------------------
                # RAW RESPONSE
                # ------------------------------------------------

                try:

                    body = response.text()

                except Exception:

                    body = ""

                with open(

                    os.path.join(
                        OUTPUT_DIR,
                        "conceptualschema_response.txt"
                    ),

                    "w",

                    encoding="utf-8"

                ) as f:

                    f.write(body)

                print("RESPONSE GUARDADA")

                print("=" * 70)

                print("PRIMEROS 2000 CARACTERES")
                print("=" * 70)

                print(body[:2000])

        except Exception as e:

            print("ERROR RESPONSE:")
            print(e)

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
    # ABRIR POWER BI
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
    # ESPERAR INTERACCIONES
    # ============================================================

    print("=" * 70)
    print("ESPERANDO REQUESTS...")
    print("=" * 70)

    time.sleep(40)

    # ============================================================
    # SCREENSHOT
    # ============================================================

    page.screenshot(

        path=os.path.join(
            OUTPUT_DIR,
            "dashboard_loaded.png"
        ),

        full_page=True

    )

    # ============================================================
    # RESUMEN FINAL
    # ============================================================

    print("=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    print("CAPTURED:", captured)

    print("=" * 70)

    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    print(
        "captured_conceptualschema_request.json"
    )

    print(
        "conceptualschema_response.txt"
    )

    print(
        "replay_request.sh"
    )

    print(
        "dashboard_loaded.png"
    )

    print("=" * 70)
    print("CAPTURA COMPLETADA")
    print("=" * 70)

    time.sleep(10)

    browser.close()