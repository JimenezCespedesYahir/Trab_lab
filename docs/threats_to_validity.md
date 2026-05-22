# Amenazas a la Validez — HVRPTW Estocástico DSRSLCC

## 1. Validez Interna

### 1.1 Factor de Conversión item→kg

| Amenaza | Severidad | Mitigación |
|---|---|---|
| El peso por item (10g) es una estimación | **ALTA** | Análisis de sensibilidad con 4 factores (5g, 10g, 20g, 50g). Hallazgo principal (capacity-driven risk) es robusto bajo todos los factores. |
| El mix de productos varía por establecimiento | MEDIA | No hay datos para diferenciar. Se documenta como limitación. |

### 1.2 Distribuciones Asumidas

| Amenaza | Severidad | Mitigación |
|---|---|---|
| Normal truncada puede no representar demanda real | MEDIA | CV de SISMED (0.42) es dato real. Distribución es aproximación operacional estándar. |
| LogNormal puede no representar tiempos reales | BAJA | Impacto de tiempos es marginal (<0.3%); error en distribución no altera conclusiones. |
| No se ajustaron distribuciones a datos históricos | MEDIA | No existen datos históricos de entrega. Se documenta explícitamente. |

### 1.3 Independencia de Escenarios

| Amenaza | Severidad | Mitigación |
|---|---|---|
| Correlación entre demandas de nodos cercanos | MEDIA | Efecto probable pero difícil de cuantificar sin datos. Documentado. |
| Correlación entre tiempos de arcos (clima/vías) | BAJA | Impacto de tiempos es marginal; correlación no altera conclusiones. |

---

## 2. Validez Externa

### 2.1 Generalización

| Amenaza | Severidad | Mitigación |
|---|---|---|
| Resultados específicos a DSRSLCC | MEDIA | Framework es generalizable; parámetros son específicos. Documentado. |
| Flota específica (Hilux como cuello de botella) | BAJA | Hallazgo es que la heterogeneidad de flota crea fragilidad; generalizable a otras redes. |
| Datos SISMED peruanos | BAJA | Metodología CPMA es estándar SISMED; aplicable a otras DIRESA/DIRIS. |

### 2.2 Representatividad

| Amenaza | Severidad | Mitigación |
|---|---|---|
| 81 nodos (subset de 207 totales) | MEDIA | Se seleccionaron nodos ACTIVOS con geocodificación MEDIUM/HIGH. |
| 12 de ~200 medicamentos para ratio categoría | MEDIA | Los 12 incluyen medicamentos de alto y bajo consumo. |
| 61 periodos incluyen proyecciones futuras | BAJA | El CV calculado es sobre todo el rango; sesgo esperado bajo. |

---

## 3. Validez de Constructo

### 3.1 Medición de Demanda

| Amenaza | Severidad | Mitigación |
|---|---|---|
| "Demanda calibrada" no es demanda medida | **ALTA** | Terminología corregida. Se usa "estimación operacional" en contextos rigurosos. |
| Demanda asignada uniformemente por categoría | MEDIA | Es la mejor aproximación sin datos por IPRESS. |
| cold_chain_demand = 0 para todos | BAJA | No hay datos SISMED para activar. Arquitectura preparada. |

### 3.2 Medición de Riesgo

| Amenaza | Severidad | Mitigación |
|---|---|---|
| Penalizaciones (TW: S/50, cap: S/10/kg) son arbitrarias | MEDIA | Son parámetros del modelo, no datos. Se documentan como supuestos. |
| Reliability es binaria (todo-o-nada por ruta) | BAJA | Es la definición estándar en VRP estocástico. |
| CVaR calculado post-hoc, no integrado en optimización | BAJA | Se documenta que es evaluación, no optimización risk-averse. |

---

## 4. Validez Estadística

### 4.1 Convergencia

| Amenaza | Severidad | Mitigación |
|---|---|---|
| 100 escenarios insuficientes para CVaR | BAJA | Se verificó convergencia con 100/500/1000/2000. Se recomienda ≥1000. |
| Semilla fija puede sesgar resultados | BAJA | Se usaron semillas múltiples (42, 123) con resultados consistentes. |
| Distribución no Normal (skewness=0.88) | BAJA | Se usa CVaR (no requiere normalidad) y IC basado en CLT (válido para n≥100). |

### 4.2 Tamaño de Muestra

| Amenaza | Severidad | Mitigación |
|---|---|---|
| 200 escenarios para experimentos de capacidad | BAJA | CI 95% relativo ~5%, adecuado para comparaciones relativas. |
| 12 combinaciones de sensibilidad × 100 | BAJA | Diseño factorial completo. |

---

## 5. Resumen de Severidad

| Categoría | Alta | Media | Baja |
|---|---|---|---|
| Validez interna | 1 (conversión item→kg) | 3 | 1 |
| Validez externa | 0 | 2 | 2 |
| Validez de constructo | 1 (demanda no medida) | 2 | 2 |
| Validez estadística | 0 | 0 | 4 |
| **Total** | **2** | **7** | **9** |

### 5.1 Amenazas de Alta Severidad

1. **Factor de conversión item→kg no verificado**: Mitigado con análisis de sensibilidad que demuestra robustez del hallazgo principal.

2. **Demanda no medida por IPRESS**: Mitigado con terminología correcta y documentación explícita. No hay fuente de datos que resuelva esto sin acceso al sistema de despacho de almacén DSRSLCC.

### 5.2 Evaluación Global

Las amenazas de alta severidad están **mitigadas pero no eliminadas**. Los hallazgos principales (capacity-driven risk, fragilidad de Hilux, gap det/estoc del 61%) son robustos bajo los análisis de sensibilidad realizados. Las conclusiones cuantitativas exactas (reliability=6%, CVaR=S/ 14,021) deben interpretarse como **órdenes de magnitud**, no como estimaciones precisas.

---

*Amenazas a la validez — HVRPTW estocástico DSRSLCC*
*Última actualización: Mayo 2026*
