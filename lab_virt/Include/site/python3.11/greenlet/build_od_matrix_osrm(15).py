# Proyecto:
# HVRPTW Farmacéutico - DSRSLCC Sullana
# Construcción profesional de:
# arcs.csv
# Componentes:
# Depot central
# Haversine prefilter
# k-nearest neighbors
# Radio territorial
# OSRM routing
# Retry
# Cache persistente
# Persistencia incremental
# QA espacial
# Red bidireccional

import pandas as pd
import numpy as np
import requests
import time
import json
import os
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# CONFIG

INPUT_FILE = "analytics/nodes_high_medium.csv"

OUTPUT_FILE = "analytics/arcs.csv"

CACHE_FILE = "analytics/osrm_cache.json"

os.makedirs("analytics", exist_ok=True)

# DEPOT CENTRAL

DEPOT = {
    "codigounico": "DEPOT_DSRSLCC",
    "nombrerazonsocial":
        "ALMACEN CENTRAL DSRSLCC",

    "latitude": -4.906564049486188,
    "longitude": -80.72843391449476,

    "distrito": "SULLANA",
    "provincia": "SULLANA",
    "departamento": "PIURA"
}

# PARÁMETROS RED

K_NEIGHBORS = 10

MAX_RADIUS_KM = 150

OSRM_BASE_URL = (
    "http://router.project-osrm.org/route/v1/driving/"
)

RATE_LIMIT_SECONDS = 1.0

MAX_RETRIES = 3

TIMEOUT = 60

# LOAD DATA

print("=" * 60)
print("CARGANDO NODOS")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

print(f"Nodos originales: {len(df)}")

# AGREGAR DEPOT

depot_df = pd.DataFrame([DEPOT])

nodes = pd.concat(
    [depot_df, df],
    ignore_index=True
)

print(f"Nodos + depot: {len(nodes)}")

# CACHE

if os.path.exists(CACHE_FILE):

    with open(
        CACHE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        route_cache = json.load(f)

    print(f"Cache cargado: {len(route_cache)}")

else:

    route_cache = {}

# HAVERSINE

def haversine_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    lon1, lat1, lon2, lat2 = map(
        radians,
        [lon1, lat1, lon2, lat2]
    )

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * asin(sqrt(a))

    r = 6371

    return c * r

# OSRM ROUTING

def get_osrm_route(
    origin_lon,
    origin_lat,
    dest_lon,
    dest_lat
):

    url = (
        OSRM_BASE_URL
        + f"{origin_lon},{origin_lat};"
        + f"{dest_lon},{dest_lat}"
    )

    params = {
        "overview": "false",
        "steps": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    if (
        "routes" not in data
        or len(data["routes"]) == 0
    ):
        return None

    route = data["routes"][0]

    return {
        "distance_km":
            route["distance"] / 1000,

        "duration_min":
            route["duration"] / 60
    }

# PRE-FILTER

print("=" * 60)
print("GENERANDO PREFILTER")
print("=" * 60)

candidate_arcs = []

for i, origin in nodes.iterrows():

    temp_neighbors = []

    for j, dest in nodes.iterrows():

        if i == j:
            continue

        hav_km = haversine_km(

            origin["latitude"],
            origin["longitude"],

            dest["latitude"],
            dest["longitude"]
        )

        if hav_km <= MAX_RADIUS_KM:

            temp_neighbors.append({

                "origin_idx": i,
                "dest_idx": j,

                "origin_id":
                    origin["codigounico"],

                "destination_id":
                    dest["codigounico"],

                "haversine_km": hav_km
            })

    # KNN

    temp_neighbors = sorted(
        temp_neighbors,
        key=lambda x: x["haversine_km"]
    )

    temp_neighbors = temp_neighbors[:K_NEIGHBORS]

    candidate_arcs.extend(temp_neighbors)

print(f"Arcos candidatos: {len(candidate_arcs)}")

# ROUTING

results = []

for idx, arc in enumerate(candidate_arcs):

    print("=" * 60)
    print(
        f"ARCO {idx+1}/{len(candidate_arcs)}"
    )
    print("=" * 60)

    origin = nodes.iloc[arc["origin_idx"]]
    dest = nodes.iloc[arc["dest_idx"]]

    cache_key = (
        f"{origin['codigounico']}_"
        f"{dest['codigounico']}"
    )

    # CACHE

    if cache_key in route_cache:

        print("USANDO CACHE")

        route_data = route_cache[cache_key]

    else:

        route_data = None

        for retry in range(MAX_RETRIES):

            try:

                print(
                    f"Intento {retry+1}"
                )

                route_data = get_osrm_route(

                    origin["longitude"],
                    origin["latitude"],

                    dest["longitude"],
                    dest["latitude"]
                )

                if route_data is not None:

                    route_cache[
                        cache_key
                    ] = route_data

                    with open(
                        CACHE_FILE,
                        "w",
                        encoding="utf-8"
                    ) as f:

                        json.dump(
                            route_cache,
                            f,
                            indent=4,
                            ensure_ascii=False
                        )

                    break

            except Exception as e:

                print("ERROR:", e)

                time.sleep(5)

        time.sleep(RATE_LIMIT_SECONDS)

    # QA    

    if route_data is None:

        status = "FAILED"

        distance_km = np.nan
        duration_min = np.nan

    else:

        status = "SUCCESS"

        distance_km = (
            route_data["distance_km"]
        )

        duration_min = (
            route_data["duration_min"]
        )

    # RECORD

    record = {

        # IDs
        "origin_id":
            origin["codigounico"],

        "destination_id":
            dest["codigounico"],

        # Names
        "origin_name":
            origin["nombrerazonsocial"],

        "destination_name":
            dest["nombrerazonsocial"],

        # Coordinates
        "origin_lat":
            origin["latitude"],

        "origin_lon":
            origin["longitude"],

        "destination_lat":
            dest["latitude"],

        "destination_lon":
            dest["longitude"],

        # Distances
        "haversine_km":
            arc["haversine_km"],

        "distance_km":
            distance_km,

        # Time
        "duration_min":
            duration_min,

        # Network
        "neighbor_rank":
            idx,

        "max_radius_km":
            MAX_RADIUS_KM,

        "k_neighbors":
            K_NEIGHBORS,

        # QA
        "route_status":
            status,

        "route_provider":
            "OSRM",

        "route_timestamp":
            datetime.utcnow().isoformat(),

        # Bidirectional
        "bidirectional":
            True
    }

    results.append(record)

    # SAVE INCREMENTAL    

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
print("FINALIZADO")
print("=" * 60)

print(final_df["route_status"].value_counts())

print("=" * 60)
print("TOTAL ARCOS")
print("=" * 60)

print(len(final_df))

print("=" * 60)
print("EXPORTADO")
print("=" * 60)

print(OUTPUT_FILE)