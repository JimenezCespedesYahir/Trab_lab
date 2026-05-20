import requests
from bs4 import BeautifulSoup
import re

URL = "https://app.powerbi.com/view?r=eyJrIjoiMDZmZjE0OTctMDhhMy00NGEyLWFlYTktODExNDFjMDc0Yjc0IiwidCI6IjExMzgxOTYwLWVkYWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)

print("STATUS:", response.status_code)

html = response.text

print("LONGITUD HTML:", len(html))

# Buscar referencias Power BI
matches = re.findall(r'config|modelsAndExploration|dataset', html)

print("MATCHES:", matches[:20])

with open("raw/powerbi_page.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML guardado.")