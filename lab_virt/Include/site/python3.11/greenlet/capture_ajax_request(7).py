from playwright.sync_api import sync_playwright
import time

URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
    "?action=mostrarBuscar#no-back-button"
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
        
        if request.post_data:

            with open(
                "captured_post_data.txt",
                "w",
                encoding="utf-8"
                ) as f:
                
                f.write(request.post_data)

        url = request.url

        if "cargarEstablecimientos" in url:

            print("=" * 60)
            print("AJAX REQUEST DETECTADA")
            print("=" * 60)

            print("METHOD:")
            print(request.method)

            print("=" * 60)
            print("URL:")
            print(url)

            print("=" * 60)
            print("HEADERS:")
            print(request.headers)

            print("=" * 60)
            print("POST DATA:")
            print(request.post_data)

    page.on("request", log_request)

    # ABRIR PÁGINA

    page.goto(URL, timeout=120000)

    time.sleep(5)
    
    # ESCRIBIR FILTRO REAL    
    
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

    print("=" * 60)
    print("FILTRO ESCRITO")
    print("=" * 60)

    
    # ESPERAR AJAX
    

    time.sleep(15)

    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)

    time.sleep(30)

    browser.close()