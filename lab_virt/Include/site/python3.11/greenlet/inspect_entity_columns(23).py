# OBJETIVO:
# Inspección profunda de columnas SISMED Power BI
#
# Este script:
#
# ✅ extrae TODAS las columnas por entidad
# ✅ perfila columnas
# ✅ detecta llaves potenciales
# ✅ detecta joins potenciales
# ✅ detecta granularidad temporal
# ✅ detecta granularidad producto
# ✅ detecta granularidad EE.SS
# ✅ detecta surrogate keys
# ✅ detecta columnas jurisdiccionales
#
# ENTIDADES PRIORITARIAS:
# - data_historica_dispo12_consumo
# - CATALOGO_IPRESS_AEMS
# - medicame
# - Tb_listado_atc
#
# INPUT:
# semantic_properties.csv
#
# OUTPUT:
# entity_column_profiles.csv
# potential_join_keys.csv
# temporal_columns.csv
# product_columns.csv
# eess_columns.csv
# jurisdiction_columns.csv
# surrogate_key_candidates.csv
# priority_entities_columns.csv
#
# ================================================================

import pandas as pd
import os
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

INPUT_FILE = (
    "analytics/powerbi_semantic/parsed/"
    "semantic_properties.csv"
)

OUTPUT_DIR = (
    "analytics/powerbi_semantic/columns_inspection"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ================================================================
# PRIORITY ENTITIES
# ================================================================

PRIORITY_ENTITIES = [

    "data_historica_dispo12_consumo",

    "CATALOGO_IPRESS_AEMS",

    "medicame",

    "Tb_listado_atc"
]

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().isoformat()

# ------------------------------------------------

def contains_keywords(text, keywords):

    if pd.isna(text):
        return False

    text = str(text).lower()

    return any(
        kw.lower() in text
        for kw in keywords
    )

# ================================================================
# KEYWORDS
# ================================================================

JOIN_KEYWORDS = [
    "id",
    "codigo",
    "code",
    "key",
    "codigounico",
    "codigo_med",
    "codigo_pre",
    "ubigeo"
]

TEMPORAL_KEYWORDS = [
    "mes",
    "mesano",
    "fecha",
    "periodo",
    "anio",
    "anno",
    "year",
    "month"
]

PRODUCT_KEYWORDS = [
    "producto",
    "medicamento",
    "codigo_med",
    "codigo_pre",
    "atc",
    "farmaceutico",
    "presentacion"
]

EESS_KEYWORDS = [
    "eess",
    "establecimiento",
    "ipress",
    "hospital",
    "puesto",
    "centro",
    "codigounico",
    "renipress"
]

JURISDICTION_KEYWORDS = [
    "red",
    "microred",
    "disa",
    "diris",
    "geresa",
    "departamento",
    "provincia",
    "distrito",
    "ubigeo"
]

SURROGATE_KEYWORDS = [
    "id",
    "_id",
    "key",
    "codigo"
]

# ================================================================
# LOAD DATA
# ================================================================

print("=" * 70)
print("CARGANDO PROPERTIES")
print("=" * 70)

df = pd.read_csv(
    INPUT_FILE
)

print("TOTAL PROPERTIES:", len(df))

# ================================================================
# NORMALIZE
# ================================================================

df["property_name"] = (
    df["property_name"]
    .astype(str)
)

df["entity_name"] = (
    df["entity_name"]
    .astype(str)
)

# ================================================================
# DATASETS
# ================================================================

profiles = []

join_candidates = []

temporal_columns = []

product_columns = []

eess_columns = []

jurisdiction_columns = []

surrogate_candidates = []

priority_columns = []

# ================================================================
# LOOP PROPERTIES
# ================================================================

for _, row in df.iterrows():

    entity = row["entity_name"]

    prop = row["property_name"]

    dtype = row.get(
        "data_type",
        None
    )

    stable_name = row.get(
        "stable_name",
        None
    )

    format_string = row.get(
        "format_string",
        None
    )

    text = (
        entity
        + " "
        + prop
    ).lower()

    # ============================================================
    # COLUMN PROFILE
    # ============================================================

    profile = {

        "entity_name": entity,

        "property_name": prop,

        "data_type": dtype,

        "stable_name": stable_name,

        "format_string": format_string,

        "is_temporal": contains_keywords(
            text,
            TEMPORAL_KEYWORDS
        ),

        "is_product": contains_keywords(
            text,
            PRODUCT_KEYWORDS
        ),

        "is_eess": contains_keywords(
            text,
            EESS_KEYWORDS
        ),

        "is_jurisdiction": contains_keywords(
            text,
            JURISDICTION_KEYWORDS
        ),

        "is_join_candidate": contains_keywords(
            text,
            JOIN_KEYWORDS
        ),

        "is_surrogate_candidate": contains_keywords(
            text,
            SURROGATE_KEYWORDS
        ),

        "timestamp": now()
    }

    profiles.append(profile)

    # ============================================================
    # JOIN KEYS
    # ============================================================

    if profile["is_join_candidate"]:

        join_candidates.append(profile)

    # ============================================================
    # TEMPORAL
    # ============================================================

    if profile["is_temporal"]:

        temporal_columns.append(profile)

    # ============================================================
    # PRODUCT
    # ============================================================

    if profile["is_product"]:

        product_columns.append(profile)

    # ============================================================
    # EESS
    # ============================================================

    if profile["is_eess"]:

        eess_columns.append(profile)

    # ============================================================
    # JURISDICTION
    # ============================================================

    if profile["is_jurisdiction"]:

        jurisdiction_columns.append(profile)

    # ============================================================
    # SURROGATE KEYS
    # ============================================================

    if profile["is_surrogate_candidate"]:

        surrogate_candidates.append(profile)

    # ============================================================
    # PRIORITY ENTITIES
    # ============================================================

    if entity in PRIORITY_ENTITIES:

        priority_columns.append(profile)

# ================================================================
# DATAFRAMES
# ================================================================

df_profiles = pd.DataFrame(
    profiles
)

df_joins = pd.DataFrame(
    join_candidates
)

df_temporal = pd.DataFrame(
    temporal_columns
)

df_product = pd.DataFrame(
    product_columns
)

df_eess = pd.DataFrame(
    eess_columns
)

df_jurisdiction = pd.DataFrame(
    jurisdiction_columns
)

df_surrogate = pd.DataFrame(
    surrogate_candidates
)

df_priority = pd.DataFrame(
    priority_columns
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
        "entity_column_profiles.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_joins.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "potential_join_keys.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_temporal.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "temporal_columns.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_product.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "product_columns.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_eess.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "eess_columns.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_jurisdiction.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "jurisdiction_columns.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_surrogate.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "surrogate_key_candidates.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_priority.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "priority_entities_columns.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

# ================================================================
# PRIORITY ENTITY SUMMARY
# ================================================================

print("=" * 70)
print("PRIORITY ENTITIES")
print("=" * 70)

for entity in PRIORITY_ENTITIES:

    print("-" * 70)

    print(entity)

    subset = df_priority[
        df_priority["entity_name"]
        == entity
    ]

    cols = subset[
        "property_name"
    ].tolist()

    for c in cols:

        print("  >", c)

# ================================================================
# CRITICAL DETECTION
# ================================================================

print("=" * 70)
print("CRITICAL DETECTIONS")
print("=" * 70)

# ------------------------------------------------
# codigounico
# ------------------------------------------------

codigounico_detected = df_profiles[
    df_profiles["property_name"]
    .str.contains(
        "codigounico",
        case=False,
        na=False
    )
]

print("CODIGOUNICO DETECTED:")
print(len(codigounico_detected))

if len(codigounico_detected) > 0:

    print(
        codigounico_detected[
            [
                "entity_name",
                "property_name"
            ]
        ]
    )

# ------------------------------------------------
# mesano
# ------------------------------------------------

mesano_detected = df_profiles[
    df_profiles["property_name"]
    .str.contains(
        "mesano",
        case=False,
        na=False
    )
]

print("=" * 70)
print("MESANO DETECTED:")
print(len(mesano_detected))

if len(mesano_detected) > 0:

    print(
        mesano_detected[
            [
                "entity_name",
                "property_name"
            ]
        ]
    )

# ------------------------------------------------
# codigo_med
# ------------------------------------------------

codigo_med_detected = df_profiles[
    df_profiles["property_name"]
    .str.contains(
        "codigo_med",
        case=False,
        na=False
    )
]

print("=" * 70)
print("CODIGO_MED DETECTED:")
print(len(codigo_med_detected))

if len(codigo_med_detected) > 0:

    print(
        codigo_med_detected[
            [
                "entity_name",
                "property_name"
            ]
        ]
    )

# ================================================================
# SUMMARY
# ================================================================

print("=" * 70)
print("RESUMEN FINAL")
print("=" * 70)

print("COLUMN PROFILES:", len(df_profiles))
print("JOIN CANDIDATES:", len(df_joins))
print("TEMPORAL COLUMNS:", len(df_temporal))
print("PRODUCT COLUMNS:", len(df_product))
print("EESS COLUMNS:", len(df_eess))
print("JURISDICTION COLUMNS:", len(df_jurisdiction))
print("SURROGATE CANDIDATES:", len(df_surrogate))

print("=" * 70)
print("ARCHIVOS GENERADOS")
print("=" * 70)

print("entity_column_profiles.csv")
print("potential_join_keys.csv")
print("temporal_columns.csv")
print("product_columns.csv")
print("eess_columns.csv")
print("jurisdiction_columns.csv")
print("surrogate_key_candidates.csv")
print("priority_entities_columns.csv")

print("=" * 70)
print("COLUMN INSPECTION COMPLETED")
print("=" * 70)