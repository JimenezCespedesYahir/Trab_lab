import pandas as pd
import numpy as np
import requests
import time
import json
import os
from datetime import datetime

# CONFIG

INPUT_FILE = (
    "analytics/nodes_geocoding_input.csv"
)

OUTPUT_FILE = (
    "analytics/nodes_geocoded_nominatim.csv"
)

CACHE_FILE = (
    "analytics/geocode_cache.json"
)

GEOCODER_URL = (
    "https://nominatim.openstreetmap.org/search"
)

HEADERS = {
    "User-Agent":
    "HVRPTW-SULLANA-RESEARCH/1.0"
}

RATE_LIMIT_SECONDS = 1.5
MAX_RETRIES = 3
TIMEOUT = 30

# LOAD DATA

print("=" * 60)
print("CARGANDO DATASET...")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"Registros: {len(df)}")

# CACHE

if os.path.exists(CACHE_FILE):

    with open(
        CACHE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        cache = json.load(f)

    print(f"Cache cargado: {len(cache)}")

else:

    cache = {}

# HELPERS

def nominatim_search(query):

    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "addressdetails": 1
    }

    response = requests.get(
        GEOCODER_URL,
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    return response.json()

# CONFIDENCE

def classify_confidence(level_used, result):

    importance = result.get(
        "importance",
        0
    )

    if level_used == "PRIMARY":

        if importance >= 0.5:
            return "HIGH"

        return "MEDIUM"

    if level_used == "SECONDARY":
        return "MEDIUM"

    return "LOW"

# PROCESS

results = []

for idx, row in df.iterrows():

    print("=" * 60)
    print(f"PROCESANDO {idx+1}/{len(df)}")
    print("=" * 60)

    success = False

    query_levels = [

        ("PRIMARY", row["query_primary"]),
        ("SECONDARY", row["query_secondary"]),
        ("FALLBACK", row["query_fallback"])
    ]

    attempts = 0

    for level_name, query in query_levels:

        if pd.isna(query) or not str(query).strip():
            continue

        query = str(query).strip()

        print(f"[{level_name}] {query}")

        
        # CACHE
        

        if query in cache:

            print("USANDO CACHE")

            result = cache[query]

            if result:

                success = True

                confidence = classify_confidence(
                    level_name,
                    result
                )

                row["latitude"] = result.get("lat")
                row["longitude"] = result.get("lon")

                row["geocode_source"] = "CACHE"

                row["geocode_confidence"] = confidence
                row["geocode_level"] = level_name

                row["geocode_status"] = "SUCCESS"

                row["geocode_query_used"] = query

                row["geocode_attempts"] = attempts

                row["geocode_provider"] = "NOMINATIM"

                row["geocode_timestamp"] = (
                    datetime.utcnow().isoformat()
                )

                row["geocode_display_name"] = (
                    result.get("display_name")
                )

                row["geocode_type"] = (
                    result.get("type")
                )

                row["geocode_importance"] = (
                    result.get("importance")
                )

                row["geocode_bbox"] = str(
                    result.get("boundingbox")
                )

                break

            continue

        
        # RETRIES
       

        for retry in range(MAX_RETRIES):

            attempts += 1

            try:

                print(
                    f"Intento {retry+1}"
                )

                data = nominatim_search(query)

                time.sleep(RATE_LIMIT_SECONDS)

                if len(data) == 0:

                    print("SIN RESULTADOS")

                    cache[query] = None

                    break

                result = data[0]

                cache[query] = result

                with open(
                    CACHE_FILE,
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        cache,
                        f,
                        ensure_ascii=False,
                        indent=4
                    )

                confidence = classify_confidence(
                    level_name,
                    result
                )

                row["latitude"] = result.get("lat")
                row["longitude"] = result.get("lon")

                row["geocode_source"] = (
                    "NOMINATIM"
                )

                row["geocode_confidence"] = (
                    confidence
                )

                row["geocode_level"] = (
                    level_name
                )

                row["geocode_status"] = (
                    "SUCCESS"
                )

                row["geocode_query_used"] = (
                    query
                )

                row["geocode_attempts"] = (
                    attempts
                )

                row["geocode_provider"] = (
                    "NOMINATIM"
                )

                row["geocode_timestamp"] = (
                    datetime.utcnow().isoformat()
                )

                row["geocode_display_name"] = (
                    result.get("display_name")
                )

                row["geocode_type"] = (
                    result.get("type")
                )

                row["geocode_importance"] = (
                    result.get("importance")
                )

                row["geocode_bbox"] = str(
                    result.get("boundingbox")
                )

                success = True

                print("SUCCESS")

                break

            except Exception as e:

                print("ERROR:", e)

                time.sleep(5)

        if success:
            break

    
    # FAILED
    

    if not success:

        row["geocode_status"] = "FAILED"

        row["geocode_provider"] = (
            "NOMINATIM"
        )

    
    # APPEND
    

    results.append(row)

   
    # INCREMENTAL SAVE
    

    partial_df = pd.DataFrame(results)

    partial_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("GUARDADO INCREMENTAL")

# FINAL

final_df = pd.DataFrame(results)

print("=" * 60)
print("GEOCODING FINALIZADO")
print("=" * 60)

print(final_df["geocode_status"].value_counts())

print("=" * 60)
print("CONFIDENCE")
print("=" * 60)

print(
    final_df["geocode_confidence"]
    .value_counts(dropna=False)
)

print("=" * 60)
print("EXPORTADO")
print("=" * 60)

print(OUTPUT_FILE)