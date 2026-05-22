# Validación Estadística — Monte Carlo HVRPTW

## 1. Diseño Experimental

### 1.1 Configuración

| Parámetro | Valor |
|---|---|
| Solver | OR-Tools 9.15 (GLS) |
| Modelo | HVRPTW determinista (Fase A) |
| Evaluación | Monte Carlo con rutas fijas |
| Distribución demanda | Normal truncada (μ, σ de SISMED) |
| Distribución tiempos | LogNormal (μ, σ de arcos OSRM) |
| Semillas | Reproducibles (seed=42, 123) |
| Penalización TW | S/ 50 por violación |
| Penalización capacidad | S/ 10 por kg excedente |

### 1.2 Réplicas Ejecutadas

| Experimento | Escenarios | Semilla | Propósito |
|---|---|---|---|
| Piloto | 100 | 42 | Validación inicial |
| Extenso | 500 | 123 | Convergencia estadística |
| Sensibilidad | 12 × 100 | 42 | Análisis de impacto de CV |

---

## 2. Resultados Monte Carlo

### 2.1 KPIs Estocásticos (500 escenarios)

| KPI | Valor | IC 95% |
|---|---|---|
| **E[costo]** | **S/ 8,213** | [8,004 — 8,422] |
| σ[costo] | S/ 2,384 | — |
| CV[costo] | 0.290 | — |
| Mediana | S/ 7,289 | — |
| **VaR 5%** | **S/ 12,789** | — |
| **CVaR 5%** | **S/ 14,149** | — |
| Costo base (sin penalización) | S/ 5,184 | — |
| Penalización media | S/ 3,029 | — |

### 2.2 Robustez Operacional

| Métrica | 100 esc. | 500 esc. |
|---|---|---|
| Route reliability | 3.0% | 6.2% |
| Service level | 100% | 100% |
| TW violation rate | 10.0% | 8.4% |
| Cap violation rate | 97.0% | 92.8% |
| Utilización media | 64.4% | 64.4% |

### 2.3 Interpretación

1. **Costo esperado +61%**: El costo estocástico (S/ 8,213) supera el determinista (S/ 5,089) en 61%, principalmente por penalizaciones de capacidad excedida.

2. **Route reliability baja (6.2%)**: Solo el 6% de los escenarios no tienen ninguna violación. Esto indica que el baseline determinista es vulnerable a variabilidad.

3. **Cap violation rate alta (93%)**: Con CV demanda=0.42 (SISMED), en el 93% de escenarios al menos un vehículo excede capacidad. Causa: los Toyota Hilux (1 ton) están al 95% de utilización determinista, con poca tolerancia a incrementos de demanda.

4. **Service level 100%**: Todos los nodos son servidos en todos los escenarios. La cobertura es robusta.

---

## 3. Convergencia Monte Carlo

### 3.1 Estabilidad del Estimador

| Escenarios | E[costo] | σ[costo] | Ancho IC 95% |
|---|---|---|---|
| 100 | S/ 8,109 | S/ 2,093 | S/ 820 |
| 500 | S/ 8,213 | S/ 2,384 | S/ 418 |

- El IC 95% se reduce de S/ 820 a S/ 418 (49% reducción)
- La diferencia entre 100 y 500 escenarios es ~1.3% en E[costo]
- 500 escenarios provee convergencia aceptable para esta instancia

### 3.2 Error Relativo

- Error relativo del estimador (500 esc.): ±2.5% (IC 95% / 2 / media)
- Para reducir a ±1%: requiere ~1,500 escenarios
- Para reducir a ±0.5%: requiere ~6,000 escenarios

---

## 4. Análisis de Distribución de Costos

### 4.1 Estadísticos Descriptivos (500 escenarios)

| Estadístico | Valor |
|---|---|
| Media | S/ 8,213 |
| Mediana | S/ 7,289 |
| Desv. estándar | S/ 2,384 |
| Mínimo | S/ 5,089 |
| Máximo | S/ 18,989 |
| Asimetría | Positiva (cola derecha) |
| Rango | S/ 13,900 |

### 4.2 Cuantiles de Costo

| Cuantil | Valor |
|---|---|
| P5 | S/ 5,089 |
| P25 | S/ 5,839 |
| P50 | S/ 7,289 |
| P75 | S/ 10,039 |
| P95 | S/ 12,789 |
| P99 | S/ 15,339 |

---

## 5. Comparación Determinista vs Estocástico

| Métrica | Determinista | Estocástico (E[·]) | Δ |
|---|---|---|---|
| Costo total | S/ 5,089 | S/ 8,213 | +61% |
| Rutas | 10 | 10 (fijo) | 0% |
| Nodos servidos | 81/81 | 81/81 | 0% |
| Utilización | 76.5% | 64.4% | -12.1pp |
| TW cumplimiento | 100% | 91.6% | -8.4pp |
| Cap cumplimiento | 100% | 7.2% | -92.8pp |

### 5.1 Análisis del Gap

El gap del 61% entre determinista y estocástico se descompone en:
- **Penalización por capacidad**: ~S/ 2,800 (91% del gap)
- **Penalización por TW**: ~S/ 230 (7% del gap)
- **Otros**: ~S/ 60 (2%)

La capacidad es el factor dominante de riesgo. Esto justifica la necesidad de:
1. Re-optimizar rutas con margen de capacidad (Fase E)
2. Considerar CVaR en la función objetivo
3. Evaluar redistribución de carga entre vehículos

---

## 6. Limitaciones

1. **Rutas fijas**: Se evalúa el baseline determinista; no se re-optimiza por escenario.
2. **Demanda calibrada con estimación de peso**: El factor 10g/item introduce incertidumbre.
3. **CV de SISMED basado en 12 medicamentos**: Puede no ser representativo del CV real.
4. **Independencia de escenarios**: Se asume independencia entre demanda de nodos.
5. **Sin recourse**: No hay acción correctiva cuando se detecta violación.

---

*Validación estadística — Fase experimental HVRPTW DSRSLCC*
*Monte Carlo: 100 + 500 escenarios, 12 combinaciones de sensibilidad*
*Última actualización: Mayo 2026*
