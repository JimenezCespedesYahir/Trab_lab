# Análisis de Sensibilidad — HVRPTW Estocástico

## 1. Diseño del Experimento

### 1.1 Variables de Control

| Variable | Niveles | Justificación |
|---|---|---|
| CV demanda | 0.10, 0.20, 0.30, 0.40 | Rango de variabilidad SISMED (real: 0.42) |
| CV tiempos de viaje | 0.10, 0.20, 0.30 | Rango de variabilidad vial |
| α (CVaR) | 0.01, 0.05, 0.10 | Niveles de aversión al riesgo estándar |

### 1.2 Diseño Factorial

- **Combinaciones**: 4 × 3 = 12 configuraciones
- **Escenarios por combinación**: 100
- **Total de evaluaciones**: 1,200
- **Semilla**: 42 (reproducible)
- **Tiempo de resolución**: ~60s por baseline + evaluación instantánea

---

## 2. Resultados

### 2.1 Costo Esperado (S/) por Combinación

| Demand CV \ Time CV | 0.10 | 0.20 | 0.30 |
|---|---|---|---|
| **0.10** | 5,319 | 5,324 | 5,333 |
| **0.20** | 6,080 | 6,084 | 6,094 |
| **0.30** | 6,950 | 6,955 | 6,964 |
| **0.40** | 7,865 | 7,869 | 7,879 |

### 2.2 CVaR 5% (S/) por Combinación

| Demand CV \ Time CV | 0.10 | 0.20 | 0.30 |
|---|---|---|---|
| **0.10** | 6,604 | 6,171 | 6,171 |
| **0.20** | 9,029 | 8,144 | 8,161 |
| **0.30** | 11,579 | 10,257 | 10,273 |
| **0.40** | 14,179 | 12,416 | 12,432 |

### 2.3 Route Reliability por Combinación

| Demand CV \ Time CV | 0.10 | 0.20 | 0.30 |
|---|---|---|---|
| **0.10** | 0.330 | 0.300 | 0.230 |
| **0.20** | 0.120 | 0.120 | 0.090 |
| **0.30** | 0.070 | 0.070 | 0.050 |
| **0.40** | 0.040 | 0.040 | 0.030 |

### 2.4 Capacity Violation Rate por Combinación

| Demand CV \ Time CV | 0.10 | 0.20 | 0.30 |
|---|---|---|---|
| **0.10** | 0.66 | 0.66 | 0.66 |
| **0.20** | 0.88 | 0.88 | 0.88 |
| **0.30** | 0.93 | 0.93 | 0.93 |
| **0.40** | 0.96 | 0.96 | 0.96 |

---

## 3. Hallazgos Principales

### 3.1 Impacto de la Variabilidad de Demanda

- **Factor dominante**: La variabilidad de demanda tiene mucho mayor impacto que la de tiempos.
- **Incremento de costo**: De CV=0.10 a CV=0.40, el E[costo] aumenta 48% (S/ 5,319 → S/ 7,865).
- **Degradación de reliability**: De 33% (CV=0.10) a 4% (CV=0.40).
- **Causa**: Los Toyota Hilux (1 ton, 5 unidades usadas) operan al 95% de capacidad. Cualquier incremento de demanda viola capacidad.

### 3.2 Impacto de la Variabilidad de Tiempos

- **Factor menor**: El CV de tiempos tiene impacto marginal en costo (<0.3% por nivel).
- **TW violations**: Aumenta de 1% (CV=0.10) a 27% (CV=0.30), pero genera pocas penalizaciones.
- **Explicación**: Las ventanas de tiempo son amplias (08:00-16:00, 8 horas) y las rutas promedio son ~200 km (3-4h), dejando margen suficiente.

### 3.3 Interacción Demanda × Tiempo

- **Efecto multiplicativo marginal**: La interacción es aditiva, no multiplicativa. Los efectos son casi independientes.
- **Implicación**: Se puede tratar la incertidumbre de demanda y tiempo por separado en la optimización.

### 3.4 Sensibilidad del CVaR

El ratio CVaR/E[costo] indica la severidad del riesgo:

| Demand CV | CVaR₅%/E[costo] | Interpretación |
|---|---|---|
| 0.10 | 1.24 | Riesgo bajo |
| 0.20 | 1.49 | Riesgo moderado |
| 0.30 | 1.67 | Riesgo significativo |
| 0.40 | 1.80 | Riesgo alto |

---

## 4. Recomendaciones

1. **Priorizar gestión de capacidad**: La demanda estocástica es el principal driver de riesgo. Re-dimensionar rutas con slack de capacidad.

2. **Redistribuir carga a FUSO**: Los FUSO Canter (6 ton) tienen utilización del 53%. Transferir nodos de Hilux a FUSO reduciría violaciones.

3. **CVaR justificado para CV ≥ 0.20**: Con CV de SISMED real (~0.42), la diferencia E[costo] vs CVaR₅% es del 80%, justificando optimización risk-averse.

4. **Tiempos de viaje secundarios**: No requieren optimización robusta inmediata dado el margen operacional de las ventanas.

---

## 5. Figuras Generadas

| Archivo | Contenido |
|---|---|
| `results/figures/sensitivity_analysis.png` | Heatmaps de costo, CVaR, reliability; curvas de sensibilidad |
| `results/figures/cost_distribution.png` | Histograma, boxplots, distribución de utilización |
| `results/figures/robustness_analysis.png` | TW violations, convergencia reliability, service level |
| `results/figures/montecarlo_convergence.png` | Convergencia de la media con IC 95% |

---

*Análisis de sensibilidad — HVRPTW DSRSLCC*
*12 combinaciones × 100 escenarios*
*Última actualización: Mayo 2026*
