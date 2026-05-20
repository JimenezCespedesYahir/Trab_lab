# OBJETIVO:
# Ingeniería semántica avanzada sobre modelo Power BI SISMED
#
# Este script:
#
# ✅ perfila entidades analíticas
# ✅ infiere FACT vs DIMENSION
# ✅ detecta tablas EE.SS
# ✅ detecta tablas tiempo
# ✅ detecta tablas producto
# ✅ detecta tablas consumo
# ✅ calcula métricas estructurales
# ✅ genera datasets analíticos
#
# INPUT:
# semantic_entities.csv
# semantic_properties.csv
#
# OUTPUT:
# entity_profiles.csv
# probable_fact_tables.csv
# probable_dimension_tables.csv
# eess_candidate_tables.csv
# temporal_candidate_tables.csv
# product_candidate_tables.csv
# consumption_candidate_tables.csv
#
# ================================================================

import pandas as pd
import os
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

INPUT_DIR = (
    "analytics/powerbi_semantic/parsed"
)

OUTPUT_DIR = (
    "analytics/powerbi_semantic/inspection"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ================================================================
# INPUT FILES
# ================================================================

ENTITIES_FILE = os.path.join(
    INPUT_DIR,
    "semantic_entities.csv"
)

PROPERTIES_FILE = os.path.join(
    INPUT_DIR,
    "semantic_properties.csv"
)

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

FACT_KEYWORDS = [
    "historica",
    "consumo",
    "fact",
    "movimiento",
    "transaccion",
    "data",
    "stock",
    "dispo",
    "ventas"
]

DIMENSION_KEYWORDS = [
    "dim",
    "catalogo",
    "maestro",
    "producto",
    "establecimiento",
    "tiempo",
    "jurisdiccion",
    "ubigeo"
]

EESS_KEYWORDS = [
    "eess",
    "establecimiento",
    "ipress",
    "hospital",
    "centro",
    "puesto",
    "codigounico",
    "renipress",
    "farmacia"
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
    "farmaceutico",
    "presentacion"
]

CONSUMPTION_KEYWORDS = [
    "consumo",
    "stock",
    "cpma",
    "precio",
    "tot",
    "sis",
    "int",
    "vta"
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

# ================================================================
# LOAD DATA
# ================================================================

print("=" * 70)
print("CARGANDO DATASETS")
print("=" * 70)

df_entities = pd.read_csv(
    ENTITIES_FILE
)

df_properties = pd.read_csv(
    PROPERTIES_FILE
)

print("Entities:", len(df_entities))
print("Properties:", len(df_properties))

# ================================================================
# ENTITY PROFILING
# ================================================================

print("=" * 70)
print("GENERANDO ENTITY PROFILES")
print("=" * 70)

profiles = []

# ================================================================
# LOOP ENTITIES
# ================================================================

for _, entity_row in df_entities.iterrows():

    entity_name = entity_row[
        "entity_name"
    ]

    # ------------------------------------------------------------
    # FILTRAR PROPERTIES
    # ------------------------------------------------------------

    entity_props = df_properties[
        df_properties["entity_name"]
        == entity_name
    ]

    property_names = (
        entity_props[
            "property_name"
        ]
        .astype(str)
        .tolist()
    )

    # ------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------

    total_properties = len(
        property_names
    )

    numeric_fields = entity_props[
        entity_props["data_type"].isin([2, 3, 4])
    ]

    numeric_count = len(
        numeric_fields
    )

    temporal_fields = [
        p for p in property_names
        if contains_keywords(
            p,
            TEMPORAL_KEYWORDS
        )
    ]

    product_fields = [
        p for p in property_names
        if contains_keywords(
            p,
            PRODUCT_KEYWORDS
        )
    ]

    eess_fields = [
        p for p in property_names
        if contains_keywords(
            p,
            EESS_KEYWORDS
        )
    ]

    jurisdiction_fields = [
        p for p in property_names
        if contains_keywords(
            p,
            JURISDICTION_KEYWORDS
        )
    ]

    consumption_fields = [
        p for p in property_names
        if contains_keywords(
            p,
            CONSUMPTION_KEYWORDS
        )
    ]

    # ------------------------------------------------------------
    # ENTITY TEXT
    # ------------------------------------------------------------

    entity_text = (
        str(entity_name)
        + " "
        + " ".join(property_names)
    ).lower()

    # ------------------------------------------------------------
    # FACT SCORE
    # ------------------------------------------------------------

    fact_score = 0

    if contains_keywords(
        entity_name,
        FACT_KEYWORDS
    ):
        fact_score += 5

    fact_score += len(
        consumption_fields
    )

    fact_score += numeric_count * 0.2

    # ------------------------------------------------------------
    # DIMENSION SCORE
    # ------------------------------------------------------------

    dimension_score = 0

    if contains_keywords(
        entity_name,
        DIMENSION_KEYWORDS
    ):
        dimension_score += 5

    dimension_score += len(
        jurisdiction_fields
    ) * 0.5

    dimension_score += len(
        temporal_fields
    ) * 0.5

    # ------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------

    if fact_score > dimension_score:

        semantic_role = "FACT"

    else:

        semantic_role = "DIMENSION"

    # ------------------------------------------------------------
    # PROFILE RECORD
    # ------------------------------------------------------------

    profile = {

        "entity_name": entity_name,

        "semantic_role": semantic_role,

        "fact_score": round(
            fact_score,
            2
        ),

        "dimension_score": round(
            dimension_score,
            2
        ),

        "total_properties": total_properties,

        "numeric_fields": numeric_count,

        "temporal_fields_count": len(
            temporal_fields
        ),

        "product_fields_count": len(
            product_fields
        ),

        "eess_fields_count": len(
            eess_fields
        ),

        "jurisdiction_fields_count": len(
            jurisdiction_fields
        ),

        "consumption_fields_count": len(
            consumption_fields
        ),

        "temporal_fields": (
            "; ".join(temporal_fields)
        ),

        "product_fields": (
            "; ".join(product_fields)
        ),

        "eess_fields": (
            "; ".join(eess_fields)
        ),

        "jurisdiction_fields": (
            "; ".join(jurisdiction_fields)
        ),

        "consumption_fields": (
            "; ".join(consumption_fields)
        ),

        "timestamp": now()
    }

    profiles.append(profile)

# ================================================================
# DATAFRAME
# ================================================================

df_profiles = pd.DataFrame(
    profiles
)

# ================================================================
# FACT TABLES
# ================================================================

df_fact = df_profiles[
    df_profiles["semantic_role"]
    == "FACT"
].copy()

# ================================================================
# DIMENSION TABLES
# ================================================================

df_dimension = df_profiles[
    df_profiles["semantic_role"]
    == "DIMENSION"
].copy()

# ================================================================
# EESS CANDIDATES
# ================================================================

df_eess = df_profiles[
    df_profiles["eess_fields_count"] > 0
].copy()

# ================================================================
# TEMPORAL CANDIDATES
# ================================================================

df_temporal = df_profiles[
    df_profiles["temporal_fields_count"] > 0
].copy()

# ================================================================
# PRODUCT CANDIDATES
# ================================================================

df_product = df_profiles[
    df_profiles["product_fields_count"] > 0
].copy()

# ================================================================
# CONSUMPTION CANDIDATES
# ================================================================

df_consumption = df_profiles[
    df_profiles["consumption_fields_count"] > 0
].copy()

# ================================================================
# SORT
# ================================================================

df_fact = df_fact.sort_values(
    by="fact_score",
    ascending=False
)

df_dimension = df_dimension.sort_values(
    by="dimension_score",
    ascending=False
)

# ================================================================
# EXPORT CSV
# ================================================================

print("=" * 70)
print("EXPORTANDO RESULTADOS")
print("=" * 70)

df_profiles.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "entity_profiles.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_fact.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "probable_fact_tables.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_dimension.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "probable_dimension_tables.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_eess.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "eess_candidate_tables.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_temporal.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "temporal_candidate_tables.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_product.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "product_candidate_tables.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_consumption.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "consumption_candidate_tables.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

# ================================================================
# TOP FACT TABLES
# ================================================================

print("=" * 70)
print("TOP FACT TABLES")
print("=" * 70)

print(

    df_fact[
        [
            "entity_name",
            "fact_score",
            "consumption_fields_count",
            "numeric_fields"
        ]
    ].head(10)

)

# ================================================================
# TOP EESS
# ================================================================

print("=" * 70)
print("TOP EESS TABLES")
print("=" * 70)

print(

    df_eess[
        [
            "entity_name",
            "eess_fields_count",
            "jurisdiction_fields_count"
        ]
    ].head(10)

)

# ================================================================
# SUMMARY
# ================================================================

print("=" * 70)
print("RESUMEN FINAL")
print("=" * 70)

print("ENTITY PROFILES:", len(df_profiles))
print("FACT TABLES:", len(df_fact))
print("DIMENSION TABLES:", len(df_dimension))
print("EESS CANDIDATES:", len(df_eess))
print("TEMPORAL CANDIDATES:", len(df_temporal))
print("PRODUCT CANDIDATES:", len(df_product))
print("CONSUMPTION CANDIDATES:", len(df_consumption))

print("=" * 70)
print("ARCHIVOS GENERADOS")
print("=" * 70)

print("entity_profiles.csv")
print("probable_fact_tables.csv")
print("probable_dimension_tables.csv")
print("eess_candidate_tables.csv")
print("temporal_candidate_tables.csv")
print("product_candidate_tables.csv")
print("consumption_candidate_tables.csv")

print("=" * 70)
print("INSPECCIÓN SEMÁNTICA COMPLETADA")
print("=" * 70)