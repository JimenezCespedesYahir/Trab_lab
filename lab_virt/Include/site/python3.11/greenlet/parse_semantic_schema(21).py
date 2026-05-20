# ================================================================
# parse_semantic_schema.py
# ================================================================
# OBJETIVO:
# Parsear profesionalmente el conceptual schema Power BI SISMED
#
# FUNCIONALIDADES:
# ✅ recorrer TODAS las entidades
# ✅ detectar tablas
# ✅ detectar columnas
# ✅ detectar relaciones
# ✅ detectar measures
# ✅ detectar jerarquías
# ✅ detectar entidades EE.SS
# ✅ detectar entidades tiempo
# ✅ detectar entidades producto
# ✅ detectar entidades jurisdicción
# ✅ persistencia incremental
# ✅ auditoría científica
#
# INPUT:
# analytics/powerbi_semantic/raw/raw_conceptualschema.json
#
# OUTPUT:
# semantic_entities.csv
# semantic_properties.csv
# semantic_measures.csv
# semantic_hierarchies.csv
# semantic_relationships.csv
# eess_entities.csv
# temporal_entities.csv
# product_entities.csv
# jurisdiction_entities.csv
#
# ================================================================

import json
import pandas as pd
import os
from datetime import datetime

# ================================================================
# CONFIG
# ================================================================

INPUT_FILE = (
    "analytics/conceptualschema_capture/"
    "conceptualschema_response.txt"
)

OUTPUT_DIR = (
    "analytics/powerbi_semantic/parsed"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ================================================================
# HELPERS
# ================================================================

def now():

    return datetime.utcnow().isoformat()

# ------------------------------------------------

def contains_keywords(text, keywords):

    if text is None:
        return False

    text = str(text).lower()

    return any(
        kw.lower() in text
        for kw in keywords
    )

# ================================================================
# KEYWORDS
# ================================================================

EESS_KEYWORDS = [
    "eess",
    "establecimiento",
    "ipress",
    "institucion",
    "codigounico",
    "codigo_unico",
    "renipress",
    "farmacia",
    "hospital",
    "centro",
    "puesto",
    "microred",
    "red",
    "disa",
    "diris",
    "geresa",
    "unidadejecutora",
    "ubigeo"
]

TEMPORAL_KEYWORDS = [
    "fecha",
    "mes",
    "mesano",
    "periodo",
    "anio",
    "año",
    "anno",
    "year",
    "month",
    "time"
]

PRODUCT_KEYWORDS = [
    "producto",
    "medicamento",
    "codigo_med",
    "codigo_pre",
    "farmaceutico",
    "dispositivo",
    "sanitario",
    "presentacion",
    "generico"
]

JURISDICTION_KEYWORDS = [
    "disa",
    "diris",
    "geresa",
    "red",
    "microred",
    "departamento",
    "provincia",
    "distrito",
    "ubigeo",
    "region",
    "unidad"
]

MEASURE_KEYWORDS = [
    "consumo",
    "stock",
    "precio",
    "cpma",
    "indicador",
    "venta",
    "sis",
    "int",
    "tot"
]

# ================================================================
# CARGAR JSON
# ================================================================

print("=" * 70)
print("CARGANDO CONCEPTUAL SCHEMA")
print("=" * 70)

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    raw_text = f.read()

# ================================================================
# INSPECCIÓN JSON
# ================================================================

print("=" * 70)
print("INSPECCIONANDO JSON")
print("=" * 70)

print(raw_text[:1000])

print("=" * 70)

# ================================================================
# PARSE JSON
# ================================================================

schema_json = json.loads(raw_text)

print("TIPO ROOT:")
print(type(schema_json))

print("=" * 70)

if isinstance(schema_json, dict):

    print("KEYS ROOT:")
    print(schema_json.keys())

print("=" * 70)

# ================================================================
# DETECTAR SCHEMAS
# ================================================================

schemas = []

if isinstance(schema_json, dict):

    if "schemas" in schema_json:

        schemas = schema_json["schemas"]

    elif "Schemas" in schema_json:

        schemas = schema_json["Schemas"]

    else:

        print("NO SE ENCONTRÓ schemas EN ROOT")

        print(schema_json.keys())

elif isinstance(schema_json, list):

    schemas = schema_json

print("=" * 70)
print("TOTAL SCHEMAS:")
print(len(schemas))
print("=" * 70)

if len(schemas) == 0:

    raise Exception(
        "No se encontraron schemas."
    )

if len(schemas) == 0:

    raise Exception(
        "No se encontraron schemas."
    )

main_schema = schemas[0].get(
    "schema",
    {}
)

# ================================================================
# ENTITIES
# ================================================================

entities = main_schema.get(
    "Entities",
    []
)

print("ENTITIES DETECTADAS:", len(entities))

# ================================================================
# DATASETS
# ================================================================

all_entities = []
all_properties = []
all_measures = []
all_hierarchies = []
all_relationships = []

eess_entities = []
temporal_entities = []
product_entities = []
jurisdiction_entities = []

# ================================================================
# RECORRER ENTITIES
# ================================================================

for entity in entities:

    entity_name = entity.get(
        "Name",
        None
    )

    edm_name = entity.get(
        "EdmName",
        None
    )

    entity_record = {

        "entity_name": entity_name,
        "edm_name": edm_name,
        "timestamp": now()
    }

    all_entities.append(entity_record)

    entity_text = (
        str(entity_name)
        + " "
        + str(edm_name)
    )

    # ============================================================
    # CLASIFICACIÓN ENTITIES
    # ============================================================

    if contains_keywords(
        entity_text,
        EESS_KEYWORDS
    ):

        eess_entities.append(entity_record)

    if contains_keywords(
        entity_text,
        TEMPORAL_KEYWORDS
    ):

        temporal_entities.append(entity_record)

    if contains_keywords(
        entity_text,
        PRODUCT_KEYWORDS
    ):

        product_entities.append(entity_record)

    if contains_keywords(
        entity_text,
        JURISDICTION_KEYWORDS
    ):

        jurisdiction_entities.append(entity_record)

    # ============================================================
    # PROPERTIES
    # ============================================================

    properties = entity.get(
        "Properties",
        []
    )

    for prop in properties:

        prop_name = prop.get(
            "Name",
            None
        )

        data_type = prop.get(
            "DataType",
            None
        )

        stable_name = prop.get(
            "StableName",
            None
        )

        format_string = prop.get(
            "FormatString",
            None
        )

        property_record = {

            "entity_name": entity_name,

            "property_name": prop_name,

            "data_type": data_type,

            "stable_name": stable_name,

            "format_string": format_string
        }

        all_properties.append(
            property_record
        )

        prop_text = (
            str(entity_name)
            + " "
            + str(prop_name)
        )

        # --------------------------------------------------------
        # DETECTAR ENTIDADES IMPORTANTES POR PROPERTIES
        # --------------------------------------------------------

        if contains_keywords(
            prop_text,
            EESS_KEYWORDS
        ):

            eess_entities.append({

                "entity_name": entity_name,
                "property_name": prop_name
            })

        if contains_keywords(
            prop_text,
            TEMPORAL_KEYWORDS
        ):

            temporal_entities.append({

                "entity_name": entity_name,
                "property_name": prop_name
            })

        if contains_keywords(
            prop_text,
            PRODUCT_KEYWORDS
        ):

            product_entities.append({

                "entity_name": entity_name,
                "property_name": prop_name
            })

        if contains_keywords(
            prop_text,
            JURISDICTION_KEYWORDS
        ):

            jurisdiction_entities.append({

                "entity_name": entity_name,
                "property_name": prop_name
            })

    # ============================================================
    # MEASURES
    # ============================================================

    measures = entity.get(
        "Measures",
        []
    )

    for measure in measures:

        measure_name = measure.get(
            "Name",
            None
        )

        expression = measure.get(
            "Expression",
            None
        )

        measure_record = {

            "entity_name": entity_name,

            "measure_name": measure_name,

            "expression": str(expression)
        }

        all_measures.append(
            measure_record
        )

    # ============================================================
    # HIERARCHIES
    # ============================================================

    hierarchies = entity.get(
        "Hierarchies",
        []
    )

    for hierarchy in hierarchies:

        hierarchy_name = hierarchy.get(
            "Name",
            None
        )

        hierarchy_record = {

            "entity_name": entity_name,

            "hierarchy_name": hierarchy_name
        }

        all_hierarchies.append(
            hierarchy_record
        )

# ================================================================
# RELATIONSHIPS
# ================================================================

relationships = main_schema.get(
    "Relationships",
    []
)

for rel in relationships:

    all_relationships.append(rel)

# ================================================================
# DATAFRAMES
# ================================================================

df_entities = pd.DataFrame(
    all_entities
).drop_duplicates()

df_properties = pd.DataFrame(
    all_properties
).drop_duplicates()

df_measures = pd.DataFrame(
    all_measures
).drop_duplicates()

df_hierarchies = pd.DataFrame(
    all_hierarchies
).drop_duplicates()

df_relationships = pd.DataFrame(
    all_relationships
).drop_duplicates()

df_eess = pd.DataFrame(
    eess_entities
).drop_duplicates()

df_temporal = pd.DataFrame(
    temporal_entities
).drop_duplicates()

df_product = pd.DataFrame(
    product_entities
).drop_duplicates()

df_jurisdiction = pd.DataFrame(
    jurisdiction_entities
).drop_duplicates()

# ================================================================
# EXPORT CSV
# ================================================================

print("=" * 70)
print("EXPORTANDO CSV")
print("=" * 70)

df_entities.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "semantic_entities.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_properties.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "semantic_properties.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_measures.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "semantic_measures.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_hierarchies.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "semantic_hierarchies.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_relationships.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "semantic_relationships.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_eess.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "eess_entities.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_temporal.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "temporal_entities.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

df_product.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "product_entities.csv"
    ),

    index=False,
        encoding="utf-8-sig"
)

df_jurisdiction.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "jurisdiction_entities.csv"
    ),

    index=False,
    encoding="utf-8-sig"
)

# ================================================================
# RESUMEN FINAL
# ================================================================

print("=" * 70)
print("RESUMEN FINAL")
print("=" * 70)

print("ENTITIES:", len(df_entities))
print("PROPERTIES:", len(df_properties))
print("MEASURES:", len(df_measures))
print("HIERARCHIES:", len(df_hierarchies))
print("RELATIONSHIPS:", len(df_relationships))

print("=" * 70)

print("EESS ENTITIES:", len(df_eess))
print("TEMPORAL ENTITIES:", len(df_temporal))
print("PRODUCT ENTITIES:", len(df_product))
print("JURISDICTION ENTITIES:", len(df_jurisdiction))

print("=" * 70)
print("ARCHIVOS GENERADOS")
print("=" * 70)

print("semantic_entities.csv")
print("semantic_properties.csv")
print("semantic_measures.csv")
print("semantic_hierarchies.csv")
print("semantic_relationships.csv")
print("eess_entities.csv")
print("temporal_entities.csv")
print("product_entities.csv")
print("jurisdiction_entities.csv")

print("=" * 70)
print("PARSEO SEMÁNTICO COMPLETADO")
print("=" * 70)