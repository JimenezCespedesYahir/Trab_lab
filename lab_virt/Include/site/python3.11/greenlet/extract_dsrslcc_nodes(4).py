from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os

SEARCH_TERM = "DIR.SUB-REG.DE SALUD LUCIANO CASTILLO C."

OUTPUT_DIR = "analytics"
os.makedirs(OUTPUT_DIR, exist_ok=True)

URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
    "?action=mostrarBuscar#no-back-button"
)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("=" * 60)
    print("ABRIENDO RENIPRESS...")
    print("=" * 60)

    page.goto(URL, timeout=120000)

    time.sleep(5)

    # =====================================================
    # FILTRO
    # =====================================================

    print("Buscando input txt_filtrar...")

    page.fill(
        'input[name="txt_filtrar"]',
        SEARCH_TERM
    )

    time.sleep(3)

    print("Filtro aplicado.")

    # =====================================================
    # ESPERAR TABLA
    # =====================================================

    print("Esperando resultados...")

    time.sleep(10)

    # =====================================================
    # EXTRAER TABLA HTML
    # =====================================================

    html = page.content()

    with open(
        "renipress_filtered.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    print("HTML filtrado guardado.")

    # =====================================================
    # LEER TABLAS
    # =====================================================

    try:

        tables = pd.read_html(html)

        print(f"Tablas encontradas: {len(tables)}")

    except Exception as e:

        print("ERROR LEYENDO TABLAS:")
        print(e)

        browser.close()
        exit()

    # =====================================================
    # MOSTRAR TABLAS
    # =====================================================

    target_df = None

    for idx, df in enumerate(tables):

        print("=" * 40)
        print(f"TABLA {idx}")
        print("=" * 40)

        print(df.head())

        cols = [str(c).lower() for c in df.columns]

        if any(
            "ipress" in c
            or "establecimiento" in c
            or "institución" in c
            for c in cols
        ):

            target_df = df.copy()

    # =====================================================
    # VALIDACIÓN
    # =====================================================

    if target_df is None:

        print("NO SE IDENTIFICÓ TABLA OBJETIVO")

        browser.close()
        exit()

    # =====================================================
    # LIMPIEZA
    # =====================================================

    target_df.columns = [
        str(c).strip()
        for c in target_df.columns
    ]

    target_df = target_df.drop_duplicates()

    target_df["node_id"] = (
        range(1, len(target_df) + 1)
    )

    # =====================================================
    # EXPORTAR
    # =====================================================

    output_path = (
        OUTPUT_DIR
        + "/nodes_master_sullana.csv"
    )

    target_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("=" * 60)
    print("EXPORTACIÓN COMPLETADA")
    print("=" * 60)

    print(f"Archivo: {output_path}")

    print("=" * 60)
    print("TOTAL EE.SS.")
    print("=" * 60)

    print(len(target_df))

    print("=" * 60)
    print(target_df.head())
    print("=" * 60)

    time.sleep(20)

    browser.close()