# Experimentos de Capacidad y Flota — HVRPTW DSRSLCC

## 1. Motivación

El análisis Monte Carlo identificó que la **capacidad vehicular** es el factor dominante de riesgo operacional:
- Cap violation rate: 93.5% (vs TW violation rate: 10%)
- Route reliability: 6.5%
- Principal fuente de penalización: Toyota Hilux al 95% de capacidad determinista

Este documento presenta experimentos sistemáticos para:
1. Determinar configuraciones que reducen riesgo
2. Identificar vehículos que generan fragilidad
3. Evaluar si el problema es de flota insuficiente o de asignación/ruteo

---

## 2. Configuraciones Evaluadas

### 2.1 Escalamiento de Capacidad

| Experimento | Descripción |
|---|---|
| baseline | Flota real: FUSO×4, Ducato×2, NLR×4, Hilux×6 |
| cap_+10% | Capacidad de cada vehículo +10% |
| cap_+20% | Capacidad de cada vehículo +20% |
| cap_+50% | Capacidad de cada vehículo +50% |
| buffer_85% | Usar solo 85% de capacidad nominal (15% buffer) |
| buffer_75% | Usar solo 75% de capacidad nominal (25% buffer) |

### 2.2 Cambios de Flota

| Experimento | Composición | Vehículos | Capacidad total |
|---|---|---|---|
| no_hilux_+NLR | FUSO×4, Ducato×2, NLR×10, Hilux×0 | 16 | 59,000 kg |
| no_hilux_+FUSO | FUSO×10, Ducato×2, NLR×4, Hilux×0 | 16 | 80,000 kg |
| extra_ducato | FUSO×4, Ducato×4, NLR×4, Hilux×6 | 18 | 56,000 kg |
| extra_NLR | FUSO×4, Ducato×2, NLR×8, Hilux×6 | 20 | 64,000 kg |

---

## 3. Resultados (200 escenarios cada uno)

### 3.1 Tabla Comparativa

| Experimento | Rutas | E[cost] | Reliability | Cap Viol | D/C |
|---|---|---|---|---|---|
| **baseline** | 10 | **S/ 8,150** | **6.5%** | **93.5%** | 0.323 |
| cap_+10% | 11 | S/ 7,780 | 14.5% | 84.5% | 0.294 |
| cap_+20% | 9 | S/ 7,218 | 11.0% | 88.0% | 0.269 |
| cap_+50% | 9 | S/ 7,377 | 13.5% | 86.0% | 0.216 |
| buffer_85% | 9 | S/ 6,517 | 25.0% | 75.0% | 0.380 |
| buffer_75% | 9 | S/ 6,194 | 43.0% | 55.5% | 0.431 |
| **no_hilux_+NLR** | **9** | **S/ 5,386** | **95.5%** | **3.5%** | 0.249 |
| **no_hilux_+FUSO** | **9** | **S/ 5,818** | **98.0%** | **0.0%** | 0.202 |
| extra_ducato | 10 | S/ 7,803 | 12.0% | 88.0% | 0.289 |
| extra_NLR | 9 | S/ 7,002 | 16.0% | 84.0% | 0.253 |

### 3.2 Ranking por Reliability

| Rank | Experimento | Reliability | Cap Viol |
|---|---|---|---|
| 1 | no_hilux_+FUSO | 98.0% | 0.0% |
| 2 | no_hilux_+NLR | 95.5% | 3.5% |
| 3 | buffer_75% | 43.0% | 55.5% |
| 4 | buffer_85% | 25.0% | 75.0% |
| 5 | extra_NLR | 16.0% | 84.0% |
| 6 | cap_+10% | 14.5% | 84.5% |
| 7 | cap_+50% | 13.5% | 86.0% |
| 8 | extra_ducato | 12.0% | 88.0% |
| 9 | cap_+20% | 11.0% | 88.0% |
| 10 | **baseline** | **6.5%** | **93.5%** |

---

## 4. Hallazgos

### 4.1 Hallazgo Principal: Toyota Hilux es el Cuello de Botella

**Eliminar los Hilux y reemplazarlos por NLR o FUSO elimina casi completamente las violaciones de capacidad.**

- `no_hilux_+FUSO`: Reliability 98.0%, Cap Viol 0.0%
- `no_hilux_+NLR`: Reliability 95.5%, Cap Viol 3.5%

Los Toyota Hilux (1,000 kg capacidad) son asignados a rutas con ~954 kg de demanda determinista (95% utilización). Con CV=0.42, la demanda excede 1,000 kg en la mayoría de escenarios.

### 4.2 Escalar Capacidad No Resuelve el Problema Completamente

Aumentar la capacidad de todos los vehículos (+10%, +20%, +50%) mejora solo marginalmente:
- cap_+50%: Reliability sube de 6.5% a solo 13.5%
- Causa: los Hilux siguen siendo el cuello de botella incluso con +50% (1,500 kg vs ~1,400 kg de demanda posible)

### 4.3 Los Buffers de Capacidad Son Más Efectivos que Escalar

- buffer_75%: Reliability 43% (el solver redistribuye carga asignando menos demanda por ruta)
- buffer_85%: Reliability 25%
- Estos buffers fuerzan al solver a dejar margen, lo cual es una estrategia operacional viable

### 4.4 El Problema es de Asignación, No de Flota Insuficiente

La flota total (50 ton) tiene 3× la demanda (16 ton). El problema NO es capacidad total insuficiente, sino que:
1. Los Hilux son demasiado pequeños para las rutas que les asigna el solver
2. El solver asigna Hilux por su bajo costo/km (S/ 1.8 vs S/ 2.2-3.0)
3. La optimización de costo penaliza la robustez

---

## 5. Impacto Relativo de Factores

### 5.1 Aislamiento de Factores (200 escenarios)

| Factor | ΔE[cost] vs determinista | Reliability |
|---|---|---|
| Determinista puro | 0% | 100% |
| Solo demanda CV=0.20 | +19.3% | 13.0% |
| Solo demanda CV=0.42 (SISMED) | +35.5% | 22.5% |
| Solo demanda CV=0.60 | +95.2% | 4.5% |
| Solo tiempo CV=0.10 | +0.0% | 100% |
| Solo tiempo CV=0.20 | +0.1% | 90.0% |
| Solo tiempo CV=0.30 | +0.3% | 71.0% |
| Ambos (SISMED) | +59.1% | 6.0% |
| Ambos (alto) | +95.5% | 4.0% |

### 5.2 Contribución Relativa al Riesgo

```
Demanda (CV=0.42): explica ~95% del incremento de costo
Tiempo (CV=0.20):  explica ~5% del incremento de costo

Demanda: factor dominante en cap violations (93%)
Tiempo:  factor dominante en TW violations (10%), pero bajo impacto total
```

---

## 6. Recomendaciones Operacionales

### 6.1 Para DSRSLCC

1. **Evitar asignar Hilux a rutas con alta demanda**: Su capacidad de 1 ton es insuficiente para absorber variabilidad.
2. **Considerar buffer de capacidad del 15-25%**: Reduce cap violations de 93% a 55-75%.
3. **Redistribuir nodos de Hilux a NLR/FUSO**: Mejora reliability de 6.5% a >95%.

### 6.2 Para el Modelo

1. **Integrar buffer de capacidad como restricción**: `load ≤ 0.85 × capacity` en lugar de `load ≤ capacity`.
2. **Objetivo CVaR**: Los resultados justifican la implementación de CVaR (Fase E), especialmente para la cola de costos por capacidad.
3. **Heterogeneidad de flota importa**: No basta con escalar capacidad total; la composición de la flota es determinante.

---

*Experimentos de capacidad — HVRPTW DSRSLCC*
*10 configuraciones × 200 escenarios*
*Última actualización: Mayo 2026*
