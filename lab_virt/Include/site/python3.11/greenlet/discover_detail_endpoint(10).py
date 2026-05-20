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

    # =====================================================
    # INTERCEPTAR REQUESTS
    # =====================================================

    def log_request(request):

        url = request.url

        if (
            "detalle" in url.lower()
            or "ver" in url.lower()
            or "establecimiento" in url.lower()
        ):

            print("=" * 60)
            print("REQUEST DETALLE DETECTADA")
            print("=" * 60)

            print("METHOD:")
            print(request.method)

            print("=" * 60)
            print("URL:")
            print(url)

            print("=" * 60)

            if request.post_data:

                print("POST DATA:")
                print(request.post_data)

    page.on("request", log_request)

    # =====================================================
    # ABRIR
    # =====================================================

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
    print("BÚSQUEDA EJECUTADA")
    print("=" * 60)

    time.sleep(10)

    # =====================================================
    # CLICK PRIMER REGISTRO
    # =====================================================

    print("=" * 60)
    print("HACIENDO CLICK EN PRIMER EESS")
    print("=" * 60)

    links = page.locator("a")

    total = links.count()

    print(f"Links detectados: {total}")

    clicked = False

    for i in range(total):

        try:

            txt = links.nth(i).inner_text()

            if txt.strip():

                print(i, txt)

            href = links.nth(i).get_attribute("href")

            if href:

                print("HREF:", href)

            # intentar click
            if not clicked and txt.strip():

                links.nth(i).click()

                clicked = True

                print("=" * 60)
                print("CLICK EJECUTADO")
                print("=" * 60)

                break

        except:
            pass

    time.sleep(20)

    browser.close()