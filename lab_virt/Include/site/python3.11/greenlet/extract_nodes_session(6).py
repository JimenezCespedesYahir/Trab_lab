from playwright.sync_api import sync_playwright
import requests
import pandas as pd
import json
import os
import time

# CONFIG
URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
    "?action=mostrarBuscar#no-back-button"
)

AJAX_URL = (
    "http://app20.susalud.gob.pe:8080/"
    "registro-renipress-webapp/"
    "listadoEstablecimientosRegistrados.htm"
)

SEARCH_TERM = "DIR.SUB-REG.DE SALUD LUCIANO CASTILLO C."

os.makedirs("analytics", exist_ok=True)

# PLAYWRIGHT
with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("ABRIENDO RENIPRESS...")

    page.goto(URL, timeout=120000)

    time.sleep(5)

    print("Página cargada.")

    # EXTRAER COOKIES
    cookies = page.context.cookies()

    print("COOKIES DETECTADAS")

    for c in cookies:
        print(c["name"], c["value"])

    # REQUESTS SESSION
    session = requests.Session()

    for c in cookies:
        session.cookies.set(
            c["name"],
            c["value"]
        )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": URL,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    # PARAMS
    params = {
        "action": "cargarEstablecimientos",
        "txt_filtrar": SEARCH_TERM,
        "cmb_departamento": "0",
        "cmb_provincia": "0",
        "cmb_distrito": "0",
        "cmb_red": "0",
        "cmb_microRed": "0",
        "cmb_categoria": "0",
        "iDisplayStart": "0",
        "iDisplayLength": "1000",
        "sEcho": "1"
    }

    print("CONSULTANDO AJAX...")

    response = session.post(
        AJAX_URL,
        data=params,
        headers=headers,
        timeout=120
    )

    print("STATUS:", response.status_code)

    with open(
        "ajax_response.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(response.text)

    print("RAW RESPONSE GUARDADA")

    print("PRIMEROS 5000 CARACTERES")

    print(response.text[:5000])

    # JSON
    try:
        data = response.json()

        print("JSON DETECTADO")

        print(data.keys())

    except Exception as e:
        print("ERROR JSON")
        print(e)

        browser.close()
        exit()

    # DETECTAR DATASET
    dataset = None

    for key in ["aaData", "data", "items"]:

        if key in data:
            dataset = data[key]

            print(f"DATASET ENCONTRADO: {key}")

            break

    if dataset is None:

        print("NO SE ENCONTRÓ DATASET")

        print(json.dumps(data, indent=4))

        browser.close()
        exit()

    # DATAFRAME
    df = pd.DataFrame(dataset)

    print("COLUMNAS")

    print(df.columns.tolist())

    print("TOTAL REGISTROS")

    print(len(df))

    # EXPORT
    output_path = "analytics/nodes_master_sullana.csv"

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("EXPORTADO")

    print(output_path)

    print(df.head())

    time.sleep(20)

    browser.close()