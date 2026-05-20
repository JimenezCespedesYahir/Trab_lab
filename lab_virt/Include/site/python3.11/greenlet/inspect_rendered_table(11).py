from playwright.sync_api import sync_playwright
import time

URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
    "?action=mostrarBuscar"
)

SEARCH_TERM = "DIR.SUB-REG.DE SALUD LUCIANO CASTILLO C."

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(URL, timeout=120000)

    time.sleep(5)

    # =====================================================
    # BUSCAR
    # =====================================================

    page.click('input[name="txt_filtrar"]')

    page.keyboard.type(
        SEARCH_TERM,
        delay=100
    )

    time.sleep(2)

    page.keyboard.press("Enter")

    print("=" * 60)
    print("BUSQUEDA EJECUTADA")
    print("=" * 60)

    time.sleep(10)

    # =====================================================
    # EXTRAER HTML TABLA
    # =====================================================

    html = page.content()

    with open(
        "rendered_page.html",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(html)

    print("=" * 60)
    print("HTML COMPLETO GUARDADO")
    print("=" * 60)

    # =====================================================
    # FILAS
    # =====================================================

    rows = page.locator("tr")

    total = rows.count()

    print("=" * 60)
    print(f"TOTAL FILAS: {total}")
    print("=" * 60)

    for i in range(min(total, 20)):

        try:

            txt = rows.nth(i).inner_text()

            print("=" * 60)
            print(f"FILA {i}")
            print("=" * 60)

            print(txt)

        except:
            pass

    time.sleep(20)

    browser.close()