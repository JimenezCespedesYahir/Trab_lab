# Validación Científica de Datasets HVRPTW — DSRSLCC

## Reporte de Auditoría y Calibración

---

## 1. Validación Geoespacial

### 1.1 Coordenadas Duplicadas Detectadas

Se detectaron **7 grupos de coordenadas duplicadas** dentro de los 81 nodos HVRPTW (confianza MEDIUM/HIGH):

| Grupo | Nodos | Coordenadas | Observación |
|---|---|---|---|
| 1 | 1916, 1923, 10726 | (-4.5649, -79.6842) | 3 nodos comparten misma ubicación — posible geocodificación al mismo punto de referencia |
| 2 | 1926, 19844 | (-4.6151, -79.4995) | 2 nodos en El Toldo/Huilco |
| 3 | 1986, 1987 | (-4.8904, -80.4146) | Chica Alta / Sinchi Roca |
| 4 | 2035, 2038 | (-4.8325, -80.7621) | Mallares / Saman |
| 5 | 2037, 2045 | (-4.8850, -80.8254) | Tangarara / Santa Sofia |
| 6 | 2047, 2048 | (-4.8869, -81.0031) | Amotape / El Tambo |
| 7 | 2052, 2056, 2065 | (-4.7853, -80.6101) | San Francisco de Chocan / Puente de los Serranos / El Alamor |

**Impacto operacional**: Las coordenadas duplicadas generan arcos con distancia/tiempo = 0 entre esos nodos, lo cual distorsiona el modelo HVRPTW. La solución es:
- Aplicar un **offset geográfico mínimo** (±0.001° ≈ 111m) para diferenciar nodos operacionalmente distintos
- Documentar como **limitación de geocodificación** hasta obtener coordenadas GPS reales

**Acción tomada**: Se agrega columna `duplicate_coord_group` al dataset `nodes_hvrptw.csv` para identificar nodos afectados.

### 1.2 Cobertura Geográfica

| Métrica | Valor |
|---|---|
| Rango latitud | [-5.2063, -4.1056] |
| Rango longitud | [-81.3106, -79.4792] |
| Distancia mínima al depósito | 0.7 km (CS Nuevo Sullana) |
| Distancia máxima al depósito | 141.4 km (PS Espindola) |
| Distancia media al depósito | 55.2 km |
| Nodos > 100 km del depósito | 14 (17.3%) |

### 1.3 Distribución Territorial

| Provincia | Nodos | % |
|---|---|---|
| Sullana | 25 | 30.9% |
| Ayabaca | 19 | 23.5% |
| Paita | 14 | 17.3% |
| Piura | 13 | 16.0% |
| Talara | 10 | 12.3% |

### 1.4 Conectividad del Grafo

| Métrica | Valor |
|---|---|
| Arcos totales | 820 |
| Todos bidireccionales | Sí |
| Grafo conexo (BFS desde depósito) | **Sí — todos los 81 nodos son alcanzables** |
| Arcos por nodo (k-nearest) | 10 |
| Grado medio de nodo | 12.5 (mín: 10, máx: 20) |

---

## 2. Validación de Demanda

### 2.1 Estado Actual: Datos SISMED NO Disponibles

**Hallazgo crítico**: El repositorio contiene la **estructura del modelo semántico PowerBI** (`data_historica_dispo12_consumo`) con los campos SISMED relevantes, pero **NO se han extraído datos de consumo real**. Los campos del modelo SISMED identificados son:

| Campo SISMED | Tipo | Descripción |
|---|---|---|
| `codigo_pre` | string | Código del establecimiento |
| `codigo_med` | string | Código del medicamento |
| `mesano` | string | Periodo (YYYYMM) |
| `stock` | numeric | Stock al cierre |
| `m_consumo` | numeric | Consumo total |
| `m_consumo_vta` | numeric | Consumo por venta |
| `m_consumo_sis` | numeric | Consumo SIS |
| `m_consumo_intersan` | numeric | Consumo intersanitario |
| `m_consumo_donacion` | numeric | Consumo donación |
| `stock_fin_ult_periodo` | numeric | Stock fin último periodo |
| `m_precio` | decimal | Precio |
| `cc_items` | numeric | Items cadena de frío |

### 2.2 Demandas Actuales: Placeholders

Las demandas actuales son **estimaciones placeholder** basadas en categoría:

| Categoría | demand_mean (kg) | demand_std (kg) | CV | Justificación |
|---|---|---|---|---|
| Centro de Salud | 500 | 100 | 0.20 | Estimación por nivel de complejidad |
| Puesto de Salud | 200 | 50 | 0.25 | Estimación proporcional |
| Otro | 300 | 75 | 0.25 | Promedio intermedio |

**Limitación**: Estas NO son demandas calibradas. Son valores temporales para habilitar pruebas del modelo HVRPTW.

### 2.3 Ruta de Calibración Requerida

Para obtener demanda logística real se necesita:

1. **Extraer datos SISMED** del PowerBI DSRSLCC (tabla `data_historica_dispo12_consumo`)
2. **Agregar consumo por establecimiento-periodo**: `SUM(m_consumo)` por `codigo_pre` × `mesano`
3. **Convertir unidades**: items SISMED → kg/toneladas (requiere tabla de pesos unitarios por medicamento)
4. **Calcular estadísticos**: media, desviación estándar, CV por establecimiento (mínimo 12 meses)
5. **Detectar outliers**: consumos atípicos por emergencias sanitarias, desabastecimiento
6. **Evaluar estacionalidad**: variación mensual, picos epidemiológicos
7. **Identificar cadena de frío**: filtrar `cc_items > 0` para activar `cold_chain_demand`

### 2.4 Suficiencia de Flota vs Demanda

| Métrica | Valor |
|---|---|
| Demanda total media (placeholder) | 26,700 kg = 26.7 ton |
| Capacidad total flota (1 viaje) | 24,000 kg = 24.0 ton |
| **Ratio demanda/capacidad** | **1.11** (demanda > capacidad) |

**Observación**: Con demandas placeholder, la flota NO es suficiente en un solo viaje. Esto implica:
- Se requieren múltiples viajes/días de distribución
- O las demandas placeholder están sobreestimadas
- Calibración SISMED es prioritaria para determinar suficiencia real

---

## 3. Validación de Flota

### 3.1 Flota Configurada

| Vehículo | Capacidad | Refrigeración | Cantidad | Cap. total |
|---|---|---|---|---|
| FUSO Canter 6T | 6,000 kg | No | 2 | 12,000 kg |
| Fiat Ducato Refrig. | 3,000 kg | Sí | 1 | 3,000 kg |
| NLR 3.5 TON | 3,500 kg | No | 2 | 7,000 kg |
| Toyota Hilux | 1,000 kg | No | 2 | 2,000 kg |
| **Total** | — | — | **7** | **24,000 kg** |

### 3.2 Observaciones

- **Cantidad de vehículos**: las cantidades (2, 1, 2, 2) son **estimaciones iniciales**. Se requiere confirmación con la DSRSLCC de la flota real disponible.
- **Solo 1 vehículo refrigerado**: si se activa cadena de frío, la capacidad refrigerada es limitada (3,000 kg).
- **Autonomía**: todos los vehículos cubren el nodo más lejano (141.4 km × 2 = 282.8 km ida y vuelta < 350 km mínima autonomía).

---

## 4. Validación Temporal

### 4.1 Estado Actual: Ventanas Homogéneas

| Tipo | tw_start | tw_end | Nodos |
|---|---|---|---|
| DEPOT | 08:00 | 16:00 | 1 |
| NORMAL | 08:00 | 16:00 | 81 |
| COLD_CHAIN | 08:00 | 13:00 | 0 (ninguno activo) |

**Limitación**: Todas las ventanas de tiempo son idénticas (08:00-16:00). Esto es una **simplificación** que reduce la complejidad del modelo y puede subvalorar las restricciones temporales reales.

### 4.2 Heterogeneidad Temporal Propuesta

Para una versión más realista (implementar progresivamente):

| Categoría | tw_start | tw_end | Justificación |
|---|---|---|---|
| Centro de Salud urbano | 07:30 | 17:00 | Horario extendido de atención |
| Centro de Salud rural | 08:00 | 15:00 | Restricción logística rural |
| Puesto de Salud | 08:00 | 14:00 | Horario reducido, un turno |
| Cadena de frío (cuando activa) | 08:00 | 13:00 | Restricción térmica |
| Depósito | 07:00 | 17:00 | Horario operativo almacén |

**Recomendación**: Mantener ventanas homogéneas para Fase A (determinista), e introducir heterogeneidad en Fase B como análisis de sensibilidad.

---

## 5. Cadena de Frío

### 5.1 Estado Actual

- `cold_chain_demand = 0` para **todos** los 81 nodos
- Solo el Fiat Ducato tiene refrigeración (`cold_chain_compatible = Yes`)
- Ventanas de cadena de frío (08:00-13:00) están definidas pero no activas

### 5.2 Arquitectura Preparada

La arquitectura del modelo soporta cadena de frío:
- Campo `cold_chain_demand` en `nodes_hvrptw.csv` y `demand_aggregated.csv`
- Campo `tw_type = COLD_CHAIN` en `time_windows.csv`
- Restricción (C7) en formulación MILP: `y_i^{kv} ≤ cold_compatible_k`
- Vehículo V2_FIAT_DUCATO con `refrigeration = Yes`

### 5.3 Activación Futura

Para activar cadena de frío se requiere:
1. Extraer campo `cc_items` de SISMED por establecimiento
2. Identificar nodos con `cc_items > 0` (tienen medicamentos termosensibles)
3. Actualizar `cold_chain_demand = 1` en esos nodos
4. Las ventanas de tiempo COLD_CHAIN se activarán automáticamente

---

## 6. Resumen de Hallazgos y Acciones

### Hallazgos Críticos

| # | Hallazgo | Severidad | Acción |
|---|---|---|---|
| H1 | Demandas son placeholder, no calibradas con SISMED | **ALTA** | Requiere extracción de datos SISMED |
| H2 | 7 grupos de coordenadas duplicadas (15 nodos afectados) | MEDIA | Offset geográfico aplicado, documentado |
| H3 | Ventanas de tiempo homogéneas | BAJA | Aceptable para Fase A, diversificar en Fase B |
| H4 | Cadena de frío inactiva (`cold_chain_demand = 0`) | BAJA | Arquitectura lista, requiere datos SISMED |
| H5 | Cantidades de flota no confirmadas | MEDIA | Requiere datos operacionales DSRSLCC |
| H6 | 14 nodos a >100 km del depósito | INFO | Impacta planificación de rutas (rutas largas) |

### Qué Falta para Calibración Completa

| Dato Faltante | Por Qué Importa | Cómo Obtenerlo |
|---|---|---|
| Consumo SISMED por EE.SS. | Calibrar demanda real | Extraer tabla `data_historica_dispo12_consumo` del PowerBI |
| Peso unitario por medicamento | Convertir items → kg | Base de datos de formulario nacional o DIGEMID |
| Items cadena de frío por EE.SS. | Activar `cold_chain_demand` | Campo `cc_items` de SISMED |
| Flota real disponible | Confirmar cantidades | Consulta directa a DSRSLCC |
| Horarios reales por EE.SS. | Diversificar ventanas temporales | Base de datos RENIPRESS (campo `horaAtencion`) |
| Coordenadas GPS reales | Resolver duplicados | Visita de campo o GPS institucional |

### Alternativas Metodológicas (mientras no hay datos SISMED)

1. **Demanda proporcional al nivel de atención**: usar categoría como proxy (actual implementación)
2. **Demanda basada en población adscrita**: si se obtiene dato de población del distrito, calcular consumo per cápita esperado
3. **Análisis de sensibilidad**: variar demandas en rango [50%, 200%] del placeholder para evaluar robustez del modelo
4. **Escenarios extremos**: probar con demanda media ±2σ para evaluar capacidad de la flota

---

*Validación realizada: Mayo 2026*
*Fuentes: nodes_high_medium.csv, arcs.csv, nodes_duplicate_coordinates.csv, powerbi_semantic/*
