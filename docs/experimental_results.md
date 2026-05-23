# Resultados Experimentales — HVRPTW DSRSLCC

## 1. Resumen Ejecutivo

### 1.1 Contexto

Se ejecutó una fase experimental completa sobre el modelo HVRPTW determinista (Fase A) para logística farmacéutica pública DSRSLCC, incluyendo:

- Calibración de demanda con datos SISMED reales
- Baseline computacional con OR-Tools
- Simulación Monte Carlo (100 + 500 escenarios)
- Análisis de sensibilidad (12 combinaciones)

### 1.2 Resultados Clave

| Métrica | Determinista | Estocástico (E[·]) |
|---|---|---|
| Costo total | S/ 5,089 | S/ 8,213 |
| Rutas | 10 | 10 |
| Nodos servidos | 81/81 | 81/81 |
| Route reliability | 100% | 6.2% |
| CVaR 5% | — | S/ 14,149 |

---

## 2. Calibración SISMED

### 2.1 Datos Extraídos

| Fuente | Registros | Medicamentos | Periodos |
|---|---|---|---|
| Top 200 medicamentos | 200 | 200 | 61 (acumulado) |
| Detalle 12 medicamentos | 500 | 12 | 61 (mensual) |
| Muestra metotrexato | 314 | 1 | 61 (mensual) |

### 2.2 Demanda Calibrada

| Categoría | N | Demanda (kg/mes) | CV | Fuente |
|---|---|---|---|---|
| Centro de Salud | 34 | 318.2 ± 133.6 | 0.42 | SISMED CPMA |
| Puesto de Salud | 44 | 106.4 ± 47.9 | 0.45 | SISMED CPMA |
| Otro | 3 | 222.7 ± 89.1 | 0.40 | Estimado |
| **Total** | **81** | **16,169 kg** | — | — |

### 2.3 Metodología de Conversión

```
Items SISMED → kg logísticos:
1. Total items/mes (top 200, sin O₂): 1,550,067
2. Ratio CENTRO/PUESTO: 2.31 (de muestra 12 meds)
3. Peso por item: 10g (escenario medio, incluye empaque)
4. Total: ~16.2 ton/mes
```

### 2.4 Limitaciones de la Calibración

1. **Peso por item estimado**: 10g es un escenario medio. Rango real: 3-20g.
2. **Ratio basado en 12 medicamentos**: Puede no ser representativo.
3. **No hay datos por establecimiento individual**: Consumo asignado uniformemente dentro de cada categoría.
4. **Periodos futuros en datos PowerBI**: Algunos periodos 2025-2026 son proyecciones.

---

## 3. Baseline Determinista

### 3.1 Resultados (SISMED-calibrado)

| KPI | Valor |
|---|---|
| Rutas | 10 |
| Vehículos usados | 10/16 |
| Nodos servidos | 81/81 (100%) |
| Distancia total | 2,019.6 km |
| Costo total | S/ 5,088.77 |
| Utilización media | 76.5% |
| Runtime | 120s |

### 3.2 Asignación de Flota

| Tipo | Usados | Carga total | Utilización |
|---|---|---|---|
| FUSO Canter 6T | 1 | 3,190 kg | 53% |
| NLR 3.5 TON | 4 | 8,172 kg | 58% |
| Toyota Hilux | 5 | 4,780 kg | 96% |
| Fiat Ducato | 0 | 0 kg | — |

---

## 4. Monte Carlo

### 4.1 Distribución de Costos (500 escenarios)

| Percentil | Costo (S/) |
|---|---|
| P5 (mejor caso) | 5,089 |
| P25 | 5,839 |
| P50 (mediana) | 7,289 |
| P75 | 10,039 |
| P95 (peor caso) | 12,789 |
| VaR 1% | 15,339 |
| CVaR 1% | 17,119 |

### 4.2 Descomposición del Riesgo

| Componente | Contribución al gap estocástico |
|---|---|
| Penalización capacidad | 91% |
| Penalización TW | 7% |
| Variación operacional | 2% |

---

## 5. Comparación Operacional

### 5.1 Benchmark Interno

No existen rutas operacionales reales documentadas en el repositorio para comparación directa. Los KPIs baseline sirven como primer benchmark interno.

### 5.2 Referencia Dimensional

| Métrica | Baseline DSRSLCC | Rango típico VRP farmacéutico* |
|---|---|---|
| Nodos por ruta | 8.1 | 5-15 |
| Distancia media/ruta | 202 km | 50-300 km |
| Utilización | 76.5% | 70-90% |
| Vehículos usados/disponibles | 63% | 50-80% |

*Referencia: rangos típicos en literatura OR para distribución farmacéutica regional.

### 5.3 Limitaciones del Benchmark

1. **Sin rutas reales**: DSRSLCC no tiene rutas optimizadas documentadas.
2. **Sin datos de costo real**: Los costos son estimados (costo/km × distancia).
3. **Sin historial de servicio**: No hay datos de cumplimiento histórico de entregas.

---

## 6. Preparación CVaR (Fase E)

### 6.1 Datasets Preparados

| Dataset | Archivo | Registros |
|---|---|---|
| KPIs estocásticos | `results/stochastic_kpis.csv` | 20 métricas |
| Resultados MC 100 | `results/montecarlo_results.csv` | 100 escenarios |
| Resultados MC 500 | `results/montecarlo_results_500.csv` | 500 escenarios |
| Sensibilidad | `results/sensitivity_analysis.csv` | 12 configuraciones |
| Demanda calibrada | `analytics/demand_calibrated.csv` | 81 nodos |

### 6.2 Métricas Disponibles para CVaR

| Métrica | Disponible | Fuente |
|---|---|---|
| VaR α=0.01, 0.05, 0.10 | Sí | stochastic_kpis.csv |
| CVaR α=0.01, 0.05, 0.10 | Sí | stochastic_kpis.csv |
| Distribución de costos | Sí | montecarlo_results.csv |
| Costo por escenario | Sí | montecarlo_results.csv |
| Sensibilidad CVaR a CV | Sí | sensitivity_analysis.csv |

### 6.3 Arquitectura para CVaR

Para la Fase E, la implementación requerirá:

```
min_x  (1-λ) × E[C(x,ξ)] + λ × CVaR_α[C(x,ξ)]

donde:
  x = decisiones de ruteo
  ξ = escenarios (demanda + tiempos)
  λ = peso de aversión al riesgo [0,1]
  α = nivel de confianza CVaR
```

El framework Monte Carlo ya genera los escenarios necesarios. Solo falta integrar la optimización risk-averse en el solver.

---

## 7. Revisión Computacional

### 7.1 Tiempos de Ejecución

| Componente | Tiempo |
|---|---|
| Carga de datos | 0.02s |
| Baseline (120s límite) | 120s |
| MC 100 escenarios | 60s (solver) + <1s (evaluación) |
| MC 500 escenarios | 60s (solver) + <1s (evaluación) |
| Sensibilidad (12×100) | 721s (12 baselines × 60s) |
| Figuras | <5s |
| **Total** | **~845s (~14 min)** |

### 7.2 Memoria

| Componente | Memoria |
|---|---|
| OR-Tools solver | ~23 MB |
| Matrices numpy (82×82) | ~0.05 MB |
| 500 escenarios demanda | ~0.3 MB |
| 500 escenarios tiempo | ~13 MB |
| **Total** | **~40 MB** |

### 7.3 Escalabilidad

| Instancia | Nodos | Tiempo solver | Tiempo MC 100 |
|---|---|---|---|
| Actual | 81 | 60-120s | ~60s |
| Doble | ~160 | >600s | ~600s |
| Completa (207) | 207 | >1800s | >1800s |

Para instancias >100 nodos, se recomienda:
- Reducir time_limit del solver a 30s
- Usar heurísticas constructivas en lugar de GLS
- Implementar paralelización de evaluación de escenarios

---

*Resultados experimentales — HVRPTW DSRSLCC*
*Fase A determinista + evaluación estocástica*
*Última actualización: Mayo 2026*
