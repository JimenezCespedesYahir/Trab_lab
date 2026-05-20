from playwright.sync_api import sync_playwright
import time

URL = "http://app20.susalud.gob.pe:8080/registro-renipress-webapp/listadoEstablecimientosRegistrados.htm?action=mostrarBuscar#no-back-button"

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("=" * 60)
    print("ABRIENDO RENIPRESS...")
    print("=" * 60)

    page.goto(URL, timeout=120000)

    time.sleep(10)

    print("=" * 60)
    print("TÍTULO:")
    print(page.title())
    print("=" * 60)

    print("URL FINAL:")
    print(page.url)

    print("=" * 60)

    # Guardar HTML completo
    html = page.content()

    with open(
        "renipress_full.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    print("HTML guardado.")

    # Mostrar inputs encontrados
    inputs = page.locator("input")

    total_inputs = inputs.count()

    print("=" * 60)
    print(f"INPUTS ENCONTRADOS: {total_inputs}")
    print("=" * 60)

    for i in range(total_inputs):

        try:
            inp = inputs.nth(i)

            name = inp.get_attribute("name")
            typ = inp.get_attribute("type")

            print(i, name, typ)

        except:
            pass

    print("=" * 60)
    print("MANTENIENDO NAVEGADOR ABIERTO...")
    print("=" * 60)

    time.sleep(60)

    browser.close()