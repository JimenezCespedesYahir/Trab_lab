# Amenazas a la Validez — HVRPTW Estocástico DSRSLCC

## 1. Limitaciones de ALTA Prioridad

### 1.1 Demanda SISMED Agregada por Categoría

**Descripción**: Los datos SISMED disponibles proporcionan consumo a nivel de categoría de establecimiento (CENTRO DE SALUD vs PUESTO DE SALUD), no por establecimiento individual (IPRESS). La demanda se asigna uniformemente dentro de cada categoría.

**Impacto potencial**: Establecimientos de la misma categoría pueden tener demandas significativamente diferentes por factores como: población asignada, perfil epidemiológico local, capacidad instalada, personal disponible.

**Severidad**: **ALTA** — afecta directamente la distribución de demanda entre nodos y por tanto las asignaciones de ruta.

**Mitigación**:
- Se utilizan los ratios CENTRO/PUESTO reales de SISMED (2.31:1)
- El CV por categoría (CS=0.42, PS=0.45) refleja la variabilidad real observada en los datos
- La demanda se denomina "estimación operacional por tipología", no "demanda medida"
- Para obtener datos por IPRESS se requiere acceso al sistema de despacho de almacén DSRSLCC (no disponible vía PowerBI)

**Efecto en hallazgos**: El hallazgo principal (capacity-driven risk) depende del total de demanda por ruta, no de la distribución individual. La asignación uniforme puede subestimar la heterogeneidad real, pero no cambia la estructura del problema.

---

### 1.2 Ausencia de Datos IPRESS-Level Exactos

**Descripción**: No se dispone de datos de consumo ni despacho por establecimiento individual. Los 81 nodos reciben demanda estimada basada en su categoría.

**Impacto potencial**: Un Centro de Salud con categoría I-4 y 15 camas tiene demanda muy diferente a uno con categoría I-3 y 5 camas. Esta heterogeneidad no se captura.

**Severidad**: **ALTA** — la calibración individual por nodo es necesaria para planificación operacional real.

**Mitigación**:
- Se documenta explícitamente como limitación
- El framework está diseñado para incorporar datos individuales cuando estén disponibles
- Los resultados se presentan como análisis de sensibilidad, no como predicciones exactas

---

### 1.3 Conversión item→kg Aproximada

**Descripción**: SISMED registra consumo en items (unidades farmacéuticas). La conversión a kg usa un factor estimado de 10g/item, no verificado con datos de peso real.

**Impacto potencial**: El factor real puede variar de 3-50g dependiendo del mix de productos. Esto afecta la demanda total y por tanto las violaciones de capacidad.

**Severidad**: **ALTA** — directamente vinculado al hallazgo principal.

**Mitigación**:
- Análisis de sensibilidad con 4 factores (5g, 10g, 20g, 50g)
- El hallazgo capacity-driven risk es robusto en los 4 escenarios
- El rango 5-15g es farmacéuticamente plausible para despacho con empaque
- Para verificación definitiva se requiere datos de peso de despacho del almacén DSRSLCC

---

## 2. Limitaciones de MEDIA Prioridad

### 2.1 Independencia Estadística entre Demandas

**Descripción**: Se asume que la demanda de cada nodo es independiente. En realidad, brotes epidémicos, campañas de vacunación o desabastecimiento regional pueden correlacionar demandas.

**Severidad**: MEDIA — la correlación positiva incrementaría el riesgo conjunto (peor caso simultáneo), haciendo que el análisis actual potencialmente subestime el riesgo.

**Mitigación**: El impacto está acotado porque la reliability ya es extremadamente baja (6%). Correlación empeoraría un resultado que ya es desfavorable.

### 2.2 Independencia entre Tiempos de Viaje

**Descripción**: Los tiempos de viaje se generan independientemente por arco. Las condiciones climáticas o viales afectan múltiples arcos simultáneamente.

**Severidad**: MEDIA-BAJA — dado que tiempos explican solo 5% del incremento de costo, la correlación temporal tiene impacto limitado en los resultados agregados.

### 2.3 Distribuciones No Ajustadas a Datos Históricos

**Descripción**: La Normal truncada (demanda) y LogNormal (tiempos) son distribuciones estándar en la literatura, pero no se ajustaron a series temporales de datos reales de entrega o viaje.

**Severidad**: MEDIA — son aproximaciones operacionales funcionales, no distribuciones calibradas empíricamente.

**Mitigación**: Los parámetros (CV) sí provienen de datos reales (SISMED para demanda, literatura para tiempos OSRM).

### 2.4 Penalizaciones Arbitrarias

**Descripción**: Las penalizaciones por violación (TW: S/50 por evento, capacidad: S/10 por kg excedente) son parámetros del modelo, no datos observados.

**Severidad**: MEDIA — afectan la magnitud del gap pero no la dirección del hallazgo.

**Mitigación**: Se evaluaron implícitamente en sensibilidad. El hallazgo (cap > TW) depende de las tasas de violación, no de los montos de penalización.

### 2.5 Representatividad de la Muestra de Nodos

**Descripción**: 81 de 207 establecimientos totales, seleccionados por estado ACTIVO y geocodificación MEDIUM/HIGH.

**Severidad**: MEDIA — los 126 excluidos podrían alterar la estructura de rutas.

**Mitigación**: Se seleccionaron por criterios objetivos (estado, calidad de geocodificación), no por conveniencia. El framework escala a más nodos.

### 2.6 Simplificación de Tiempos de Servicio

**Descripción**: Tiempos de servicio fijos (30 min CS, 15 min PS) no reflejan variabilidad operacional (carga/descarga, verificación, documentación).

**Severidad**: MEDIA-BAJA — afecta cumplimiento de ventanas pero tiempos son el factor minoritario de riesgo.

### 2.7 Ventanas de Tiempo Homogéneas

**Descripción**: Todos los nodos tienen ventana 08:00-16:00. En la práctica, algunos establecimientos pueden tener horarios diferentes.

**Severidad**: MEDIA-BAJA — la homogeneidad proporciona slack generoso que reduce impacto.

---

## 3. Limitaciones de BAJA Prioridad

### 3.1 Solver Heurístico (No Óptimo Global)

**Descripción**: OR-Tools usa GLS (Guided Local Search), que no garantiza optimalidad global.

**Severidad**: BAJA — el baseline es una solución "buena" suficiente para evaluación estocástica. La optimalidad exacta del baseline no altera el hallazgo de fragilidad.

### 3.2 Cadena de Frío No Activada

**Descripción**: cold_chain_demand = 0 para todos los nodos. Solo Ducato tiene refrigeración.

**Severidad**: BAJA — la arquitectura está preparada. La activación requiere datos SISMED de medicamentos termosensibles.

### 3.3 Sin Estacionalidad

**Descripción**: El modelo usa demanda promedio mensual, sin patrones estacionales.

**Severidad**: BAJA — el CV de SISMED captura parte de la variabilidad estacional implícitamente.

### 3.4 Evaluación Post-Optimización (Sin Recourse)

**Descripción**: Los escenarios Monte Carlo evalúan las rutas fijas del baseline; no hay re-optimización por escenario (no hay recourse).

**Severidad**: BAJA — esto sobreestima el impacto de la incertidumbre (en la práctica se re-planifica). El hallazgo de fragilidad sigue siendo válido como cota superior de riesgo.

### 3.5 Semilla Fija

**Descripción**: Se usa semilla 42 para reproducibilidad. Diferentes semillas podrían dar resultados ligeramente diferentes.

**Severidad**: BAJA — se verificó con semillas múltiples; resultados consistentes. La convergencia a 2000 escenarios minimiza efecto de semilla.

### 3.6 Sin Paralelización Computacional

**Descripción**: La evaluación de escenarios es secuencial.

**Severidad**: BAJA — afecta solo el runtime (~30 min), no la calidad de resultados.

---

## 4. Resumen de Severidad

| Categoría | Alta | Media | Baja |
|---|---|---|---|
| Datos | 3 (SISMED agregada, IPRESS, conversión) | 3 (independencia demanda, distribuciones, muestra) | 2 (estacionalidad, cadena frío) |
| Modelo | 0 | 3 (penalizaciones, servicios, ventanas) | 3 (solver, recourse, semilla) |
| Computacional | 0 | 0 | 1 (paralelización) |
| **Total** | **3** | **6** | **6** |

---

## 5. Evaluación de Impacto en Hallazgos

### 5.1 ¿Las limitaciones invalidan los hallazgos principales?

| Hallazgo | Limitaciones que podrían afectarlo | ¿Invalidado? |
|---|---|---|
| Capacity-driven risk | Conversión item→kg | NO — robusto bajo 4 factores |
| Hilux como cuello de botella | IPRESS-level exacto | NO — es estructural (capacidad 1T) |
| Gap det/estoc 61% | Todas las de datos | PARCIAL — la magnitud es sensible, la dirección no |
| Reliability 6% | Penalizaciones, distribuciones | PARCIAL — el valor exacto es estimado, el colapso es robusto |
| Tiempo marginal vs capacidad | Ventanas homogéneas | PARCIAL — con ventanas restrictivas podría cambiar |

### 5.2 Conclusión sobre Validez

Las amenazas de alta severidad están **mitigadas pero no eliminadas**. Los hallazgos cualitativos (dirección, estructura) son robustos. Los hallazgos cuantitativos (valores exactos de reliability, CVaR, gap) deben interpretarse como **órdenes de magnitud**, no como estimaciones precisas.

La investigación es **científicamente defendible** bajo las mitigaciones documentadas, siempre que las limitaciones se presenten con honestidad y las conclusiones se cualifiquen apropiadamente.
