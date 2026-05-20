# ================================================================
# inspect_territorial_payloads.py
# ================================================================
#
# OBJETIVO:
#
# Analizar payloads querydata ya capturados
# para descubrir EXACTAMENTE cómo Power BI
# codifica territorialmente:
#
# "SALUD LUCIANO CASTILLO COLONNA"
#
# ================================================================
#
# DESCUBRIR:
#
# ✅ WHERE clauses
# ✅ literals territoriales
# ✅ entity names
# ✅ property names
# ✅ codificación LCC
# ✅ filtros jurisdiccionales
# ✅ joins territoriales
# ✅ columnas territoriales
# ✅ jerarquía territorial
#
# ================================================================
#
# INPUT:
#
# analytics/lcc_capture/payloads/*.json
#
# OUTPUT:
#
# territorial_payload_analysis.csv
# detected_literals.csv
# detected_where_clauses.csv
# territorial_entities.csv
# territorial_properties.csv
# replayable_territorial_queries.csv
# territorial_summary.json
#
# ================================================================

import pandas as pd
import json
import os
import re
from collections import Counter
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

PAYLOAD_DIR = (
    "analytics/lcc_capture/payloads"
)

OUTPUT_DIR = (
    "analytics/territorial_payload_analysis"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ================================================================
# TERRITORIAL KEYWORDS
# ================================================================

TERRITORIAL_KEYWORDS = [

    "luciano",

    "castillo",

    "sullana",

    "piura",

    "red",

    "micro",

    "disa",

    "diresa",

    "geresa",

    "diris",

    "unidad ejecutora",

    "ejecutora",

    "establecimiento",

    "ipress",

    "departamento",

    "provincia",

    "distrito",

    "codpre",

    "ubigeo"
]

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

# ------------------------------------------------

def load_json(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(f"ERROR JSON: {path}")
        print(e)

        return None

# ------------------------------------------------

def find_literals(text):

    literals = re.findall(

        r'"Literal"\s*:\s*\{\s*"Value"\s*:\s*"([^"]+)"',

        text,

        re.IGNORECASE
    )

    return literals

# ------------------------------------------------

def find_entities(text):

    entities = re.findall(

        r'"Entity"\s*:\s*"([^"]+)"',

        text,

        re.IGNORECASE
    )

    return entities

# ------------------------------------------------

def find_properties(text):

    props = re.findall(

        r'"Property"\s*:\s*"([^"]+)"',

        text,

        re.IGNORECASE
    )

    return props

# ------------------------------------------------

def find_where(text):

    where = re.findall(

        r'"Where"\s*:\s*\[(.*?)\]',

        text,

        re.DOTALL
    )

    return where

# ------------------------------------------------

def contains_territorial(text):

    if text is None:
        return False

    text = str(text).lower()

    return any(
        k in text
        for k in TERRITORIAL_KEYWORDS
    )

# ------------------------------------------------

def extract_keywords(text):

    text_lower = str(text).lower()

    found = []

    for k in TERRITORIAL_KEYWORDS:

        if k in text_lower:

            found.append(k)

    return found

# ================================================================
# DATASETS
# ================================================================

payload_profiles = []

literal_rows = []

where_rows = []

entity_rows = []

property_rows = []

replayable_rows = []

# ================================================================
# LOAD FILES
# ================================================================

print("=" * 70)
print("CARGANDO PAYLOADS")
print("=" * 70)

files = [

    f for f in os.listdir(PAYLOAD_DIR)

    if f.endswith(".json")
]

print(f"PAYLOAD FILES: {len(files)}")

# ================================================================
# PROCESS FILES
# ================================================================

for file in files:

    path = os.path.join(
        PAYLOAD_DIR,
        file
    )

    data = load_json(path)

    if data is None:
        continue

    payload = data.get(
        "payload",
        ""
    )

    payload_text = str(payload)

    # ============================================================
    # BASIC PROFILE
    # ============================================================

    literals = find_literals(
        payload_text
    )

    entities = find_entities(
        payload_text
    )

    properties = find_properties(
        payload_text
    )

    where_clauses = find_where(
        payload_text
    )

    keywords_found = extract_keywords(
        payload_text
    )

    profile = {

        "file":
            file,

        "timestamp":
            now(),

        "payload_length":
            len(payload_text),

        "literals_count":
            len(literals),

        "entities_count":
            len(entities),

        "properties_count":
            len(properties),

        "where_count":
            len(where_clauses),

        "territorial_detected":
            contains_territorial(
                payload_text
            ),

        "contains_lcc":
            "LUCIANO"
            in payload_text.upper(),

        "contains_sullana":
            "SULLANA"
            in payload_text.upper(),

        "contains_piura":
            "PIURA"
            in payload_text.upper(),

        "keywords_found":
            ", ".join(
                keywords_found
            )
    }

    payload_profiles.append(
        profile
    )

    # ============================================================
    # LITERALS
    # ============================================================

    for lit in literals:

        row = {

            "file":
                file,

            "literal":
                lit,

            "territorial":
                contains_territorial(
                    lit
                )
        }

        literal_rows.append(
            row
        )

    # ============================================================
    # ENTITIES
    # ============================================================

    for ent in entities:

        row = {

            "file":
                file,

            "entity":
                ent,

            "territorial":
                contains_territorial(
                    ent
                )
        }

        entity_rows.append(
            row
        )

    # ============================================================
    # PROPERTIES
    # ============================================================

    for prop in properties:

        row = {

            "file":
                file,

            "property":
                prop,

            "territorial":
                contains_territorial(
                    prop
                )
        }

        property_rows.append(
            row
        )

    # ============================================================
    # WHERE
    # ============================================================

    for idx, w in enumerate(where_clauses):

        row = {

            "file":
                file,

            "where_id":
                idx,

            "where_text":
                w[:3000],

            "territorial":
                contains_territorial(
                    w
                ),

            "contains_lcc":
                "LUCIANO"
                in w.upper(),

            "contains_sullana":
                "SULLANA"
                in w.upper(),

            "contains_piura":
                "PIURA"
                in w.upper()
        }

        where_rows.append(
            row
        )

    # ============================================================
    # REPLAYABLE
    # ============================================================

    replayable_rows.append({

        "file":
            file,

        "territorial":
            contains_territorial(
                payload_text
            ),

        "contains_lcc":
            "LUCIANO"
            in payload_text.upper(),

        "contains_sullana":
            "SULLANA"
            in payload_text.upper(),

        "contains_piura":
            "PIURA"
            in payload_text.upper(),

        "payload_preview":
            payload_text[:5000]
    })

# ================================================================
# DATAFRAMES
# ================================================================

df_profiles = pd.DataFrame(
    payload_profiles
)

df_literals = pd.DataFrame(
    literal_rows
)

df_where = pd.DataFrame(
    where_rows
)

df_entities = pd.DataFrame(
    entity_rows
)

df_properties = pd.DataFrame(
    property_rows
)

df_replayable = pd.DataFrame(
    replayable_rows
)

# ================================================================
# EXPORT
# ================================================================

print("=" * 70)
print("EXPORTANDO RESULTADOS")
print("=" * 70)

df_profiles.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "territorial_payload_analysis.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_literals.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "detected_literals.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_where.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "detected_where_clauses.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_entities.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "territorial_entities.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_properties.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "territorial_properties.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_replayable.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "replayable_territorial_queries.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

# ================================================================
# SUMMARY
# ================================================================

summary = {

    "payloads":
        len(df_profiles),

    "territorial_payloads":
        int(
            df_profiles[
                "territorial_detected"
            ].sum()
        ),

    "payloads_with_lcc":
        int(
            df_profiles[
                "contains_lcc"
            ].sum()
        ),

    "payloads_with_sullana":
        int(
            df_profiles[
                "contains_sullana"
            ].sum()
        ),

    "payloads_with_piura":
        int(
            df_profiles[
                "contains_piura"
            ].sum()
        ),

    "total_literals":
        len(df_literals),

    "total_entities":
        len(df_entities),

    "total_properties":
        len(df_properties),

    "total_where":
        len(df_where)
}

with open(

    os.path.join(
        OUTPUT_DIR,
        "territorial_summary.json"
    ),

    "w",

    encoding="utf-8"

) as f:

    json.dump(
        summary,
        f,
        ensure_ascii=False,
        indent=4
    )

# ================================================================
# CONSOLE SUMMARY
# ================================================================

print("=" * 70)
print("TOP TERRITORIAL ENTITIES")
print("=" * 70)

if len(df_entities) > 0:

    print(

        df_entities[
            "entity"
        ].value_counts().head(20)
    )

print("=" * 70)
print("TOP TERRITORIAL PROPERTIES")
print("=" * 70)

if len(df_properties) > 0:

    print(

        df_properties[
            "property"
        ].value_counts().head(20)
    )

print("=" * 70)
print("TOP LITERALS")
print("=" * 70)

if len(df_literals) > 0:

    print(

        df_literals[
            "literal"
        ].value_counts().head(20)
    )

print("=" * 70)
print("SUMMARY")
print("=" * 70)

for k, v in summary.items():

    print(f"{k}: {v}")

print("=" * 70)
print("ANÁLISIS TERRITORIAL COMPLETADO")
print("=" * 70)