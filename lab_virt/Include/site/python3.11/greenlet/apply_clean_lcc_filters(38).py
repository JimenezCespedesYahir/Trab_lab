# ============================================================
# apply_clean_lcc_filters.py
# ============================================================

from playwright.sync_api import sync_playwright
import json
import time
import os
from datetime import datetime

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

OUTPUT_DIR = "clean_lcc_payloads"

SCREENSHOT_DIR = "clean_lcc_screenshots"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    SCREENSHOT_DIR,
    exist_ok=True
)

# ============================================================
# HELPERS
# ============================================================

def log(title):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

# ------------------------------------------------------------

def screenshot(page, name):

    path = os.path.join(
        SCREENSHOT_DIR,
        f"{name}.png"
    )

    page.screenshot(
        path=path,
        full_page=True
    )

# ------------------------------------------------------------

def save_payload(payload, idx):

    path = os.path.join(
        OUTPUT_DIR,
        f"payload_{idx}.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2
        )

# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=700
    )

    context = browser.new_context()

    page = context.new_page()

    captured_payloads = []

    # ========================================================
    # REQUEST INTERCEPTION
    # ========================================================

    def handle_request(request):

        if "/querydata" not in request.url:
            return

        try:

            post_data = request.post_data

            if not post_data:
                return

            payload = json.loads(post_data)

            captured_payloads.append(payload)

            idx = len(captured_payloads)

            save_payload(payload, idx)

            print("\n")
            print("=" * 70)
            print("QUERYDATA CAPTURADA")
            print("=" * 70)

            where_count = 0

            try:

                commands = payload.get(
                    "Commands",
                    []
                )

                for cmd in commands:

                    semantic = cmd.get(
                        "SemanticQueryDataShapeCommand",
                        {}
                    )

                    query = semantic.get(
                        "Query",
                        {}
                    )

                    where = query.get(
                        "Where",
                        []
                    )

                    where_count += len(where)

            except:
                pass

            print(f"WHERE: {where_count}")

        except Exception as e:

            print("REQUEST ERROR:", e)

    page.on(
        "request",
        handle_request
    )

    # ========================================================
    # RESET VISUAL STATE
    # ========================================================

    log("RESET VISUAL STATE")

    page.goto(
        POWERBI_URL,
        wait_until="networkidle",
        timeout=180000
    )

    time.sleep(15)

    screenshot(
        page,
        "01_dashboard_reset"
    )

    # ========================================================
    # OPEN FILTER PANEL
    # ========================================================

    log("ABRIENDO FILTROS")

    try:

        filtros = page.locator(
            "text=Filtros"
        ).first

        filtros.click(
            force=True
        )

        time.sleep(5)

    except Exception as e:

        print("NO SE PUDO ABRIR FILTROS")
        print(e)

    screenshot(
        page,
        "02_filters_opened"
    )

    # ========================================================
    # GET COMBOBOXES
    # ========================================================

    log("DETECTANDO COMBOBOXES")

    combos = page.locator(
        "[role='combobox']"
    )

    time.sleep(5)

    total = combos.count()

    print(f"TOTAL COMBOS: {total}")

    # ========================================================
    # PRINT COMBOBOXES
    # ========================================================

    for i in range(total):

        try:

            txt = combos.nth(i).inner_text()

            print("-" * 50)
            print(f"INDEX {i}")
            print(txt)

        except:
            pass

    # ========================================================
    # SAFE FILTER FUNCTION
    # ========================================================

    def apply_combo_filter(
        combo_index,
        value,
        label
    ):

        print("\n")
        print("=" * 70)
        print(f"APLICANDO: {label}")
        print("=" * 70)

        try:

            combo = combos.nth(
                combo_index
            )

            combo.scroll_into_view_if_needed()

            time.sleep(2)

            combo.click(
                force=True
            )

            time.sleep(3)

            # ------------------------------------------------
            # CTRL+A
            # ------------------------------------------------

            page.keyboard.press(
                "Control+A"
            )

            time.sleep(1)

            # ------------------------------------------------
            # CLEAR
            # ------------------------------------------------

            page.keyboard.press(
                "Backspace"
            )

            time.sleep(1)

            # ------------------------------------------------
            # TYPE
            # ------------------------------------------------

            page.keyboard.type(
                value,
                delay=80
            )

            time.sleep(4)

            # ------------------------------------------------
            # ENTER
            # ------------------------------------------------

            page.keyboard.press(
                "Enter"
            )

            print(f"{label}: {value}")

            time.sleep(12)

            screenshot(
                page,
                f"combo_{combo_index}_{label}"
            )

        except Exception as e:

            print(f"ERROR EN {label}")
            print(e)

    # ========================================================
    # APPLY FILTERS
    # ========================================================

    #
    # IMPORTANTE:
    #
    # NO tocar:
    #
    # Grupo Producto
    # ATC
    # Forma Farmacéutica
    # Listado Productos
    #
    # SOLO:
    #
    # Unidad ejecutora
    # Macroregion
    # Institucion
    #

    # --------------------------------------------------------
    # INDEX 1 = Unidad ejecutora
    # --------------------------------------------------------

    apply_combo_filter(
        1,
        "SALUD LUCIANO CASTILLO COLONNA",
        "UNIDAD_EJECUTORA"
    )

    # --------------------------------------------------------
    # INDEX 2 = Macroregion
    # --------------------------------------------------------

    apply_combo_filter(
        2,
        "NORTE",
        "MACROREGION"
    )

    # --------------------------------------------------------
    # INDEX 3 = Institucion
    # --------------------------------------------------------

    apply_combo_filter(
        3,
        "GOBIERNO REGIONAL",
        "INSTITUCION"
    )

    # ========================================================
    # FINAL WAIT
    # ========================================================

    log("WAITING FINAL RENDER")

    time.sleep(20)

    screenshot(
        page,
        "99_final_dashboard"
    )

    # ========================================================
    # VERIFY CLEAN FILTERS
    # ========================================================

    log("VERIFICANDO FILTROS")

    body_text = page.locator(
        "body"
    ).inner_text()

    validations = {

        "Unidad ejecutora aplicada":
            "SALUD LUCIANO CASTILLO COLONNA"
            in body_text,

        "Macroregion NORTE":
            "NORTE"
            in body_text,

        "Institucion Gobierno Regional":
            "GOBIERNO REGIONAL"
            in body_text,

        "Grupo Producto Todas":
            "Grupo Producto"
            in body_text
            and "Todas"
            in body_text,

        "ATC Todas":
            "ATC"
            in body_text
            and "Todas"
            in body_text,

        "Forma Farmaceutica Todas":
            "Forma Farmacéutica"
            in body_text
            and "Todas"
            in body_text
    }

    for k, v in validations.items():

        print(f"{k}: {v}")

    # ========================================================
    # SUMMARY
    # ========================================================

    log("SUMMARY")

    print(
        f"PAYLOADS CAPTURADOS: "
        f"{len(captured_payloads)}"
    )

    print(
        f"PAYLOAD DIR: "
        f"{OUTPUT_DIR}"
    )

    print(
        f"SCREENSHOTS DIR: "
        f"{SCREENSHOT_DIR}"
    )

    print("\n")
    print("=" * 70)
    print("PIPELINE CLEAN LCC COMPLETADO")
    print("=" * 70)

    input("\nENTER PARA CERRAR...")

    browser.close()