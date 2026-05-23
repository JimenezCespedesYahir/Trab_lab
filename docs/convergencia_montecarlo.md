# Convergencia Monte Carlo — HVRPTW DSRSLCC

## 1. Diseño del Experimento

### 1.1 Objetivo

Verificar la estabilidad del estimador Monte Carlo para diferentes tamaños de muestra y validar la suficiencia del número de escenarios.

### 1.2 Configuración

| Parámetro | Valor |
|---|---|
| Escenarios evaluados | 100, 500, 1000, 2000 |
| Semilla | 42 (superset: primeros n de 2000) |
| Demanda CV | SISMED (CS=0.42, PS=0.45) |
| Tiempo CV | 0.20 |
| Solver | OR-Tools GLS, 60s |

---

## 2. Resultados de Convergencia

### 2.1 Estabilidad del Costo Esperado

| N escenarios | E[cost] (S/) | σ[cost] | CI 95% width | CI 95% relativo |
|---|---|---|---|---|
| 100 | 7,717 | 2,010 | S/ 787 | 10.20% |
| 500 | 8,346 | 2,386 | S/ 418 | 5.01% |
| 1,000 | 8,221 | 2,367 | S/ 293 | 3.56% |
| **2,000** | **8,160** | **2,342** | **S/ 205** | **2.52%** |

### 2.2 Estabilidad del CVaR 5%

| N escenarios | CVaR 5% (S/) | Δ vs 2000 |
|---|---|---|
| 100 | 11,883 | -15.2% |
| 500 | 14,112 | +0.7% |
| 1,000 | 14,043 | +0.2% |
| **2,000** | **14,021** | — |

### 2.3 Estabilidad de la Reliability

| N escenarios | Reliability | Δ vs 2000 |
|---|---|---|
| 100 | 0.100 | +69% |
| 500 | 0.048 | -19% |
| 1,000 | 0.057 | -3% |
| **2,000** | **0.059** | — |

---

## 3. Análisis de Distribución

### 3.1 Estadísticos Descriptivos (2000 escenarios)

| Estadístico | Valor |
|---|---|
| Media | S/ 8,160 |
| Mediana | S/ 7,097 |
| Desv. estándar | S/ 2,342 |
| Mínimo | S/ 5,097 |
| Máximo | S/ 19,157 |
| **Skewness** | **0.884** |
| **Kurtosis** | **0.745** |
| Shapiro-Wilk p-value | < 0.000001 |

### 3.2 Interpretación

1. **Asimetría positiva (0.884)**: La distribución tiene cola derecha pronunciada. Los escenarios desfavorables (alta demanda) generan costos desproporcionadamente altos por penalizaciones de capacidad. Esto es consistente con la estructura no lineal de las penalizaciones.

2. **Curtosis positiva (0.745)**: Colas ligeramente más pesadas que la Normal. Consistente con la combinación de una masa en S/ 5,097 (costo base sin penalización) y una cola por penalizaciones.

3. **No es Normal (p < 0.001)**: El test de Shapiro-Wilk rechaza normalidad. La distribución es mejor descrita como una distribución mixta: componente discreto en el costo base + componente continuo por penalizaciones.

### 3.3 Implicaciones para CVaR

La asimetría positiva justifica el uso de CVaR como medida de riesgo: la media no captura adecuadamente el riesgo en la cola derecha. CVaR₅% = S/ 14,021 (72% más que E[cost]) refleja la severidad real de los escenarios adversos.

---

## 4. Evaluación de Convergencia

### 4.1 Criterios

| Criterio | 100 | 500 | 1000 | 2000 |
|---|---|---|---|---|
| CI relativo < 5% | NO (10.2%) | NO (5.0%) | SÍ (3.6%) | SÍ (2.5%) |
| CVaR estable (Δ < 5%) | NO (-15%) | SÍ (+0.7%) | SÍ (+0.2%) | REF |
| Reliability estable (Δ < 10%) | NO (+69%) | NO (-19%) | SÍ (-3%) | REF |

### 4.2 Recomendación

- **100 escenarios**: Insuficiente para CVaR y reliability.
- **500 escenarios**: Aceptable para E[cost] y CVaR, marginal para reliability.
- **1000 escenarios**: Adecuado para todos los KPIs principales.
- **2000 escenarios**: Convergencia confirmada (CI relativo 2.5%).

**Recomendación**: Usar **≥1000 escenarios** para resultados publicables.

---

## 5. Validación de Distribuciones Asumidas

### 5.1 Demanda ~ Normal Truncada

- **Justificación**: CPMA (Consumo Promedio Mensual Ajustado) tiene variación temporal que se aproxima a Normal por CLT sobre agregación de múltiples medicamentos.
- **Truncamiento en 10% de μ**: Evita demandas negativas o irrealistamente bajas.
- **Limitación**: Asume simetría en la variación, cuando la realidad puede ser asimétrica (desabastecimiento → sesgo inferior, picos estacionales → sesgo superior).

### 5.2 Tiempos ~ LogNormal

- **Justificación**: Tiempos de viaje son positivos y con cola derecha (retrasos). LogNormal es la distribución estándar en la literatura VRP para tiempos de viaje.
- **Parametrización**: μ y σ derivados del tiempo OSRM y CV asumido.
- **Limitación**: No captura eventos extremos (cortes de carretera, desastres) ni patrones horarios.

### 5.3 Estas son aproximaciones operacionales

Las distribuciones no están ajustadas a datos históricos de viajes o entregas reales. Son **aproximaciones funcionales** basadas en:
- Estructura teórica (CLT para demanda, cola positiva para tiempos)
- Parámetros calibrados con SISMED (CV) y OSRM (μ)
- Práctica estándar en literatura OR

---

## 6. Validación de Independencia

### 6.1 Supuesto

Se asume independencia entre:
- Demanda de diferentes nodos en un mismo escenario
- Tiempos de viaje de diferentes arcos en un mismo escenario
- Demanda y tiempos de viaje

### 6.2 Realismo

| Supuesto | Realismo | Justificación |
|---|---|---|
| Independencia entre demandas de nodos | Moderado | Brotes epidémicos pueden correlacionar demanda regionalmente |
| Independencia entre tiempos de arcos | Bajo | Condiciones climáticas/viales afectan múltiples arcos simultáneamente |
| Independencia demanda-tiempo | Alto | No hay mecanismo causal directo |

### 6.3 Limitación Documentada

La correlación positiva entre tiempos de viaje (condiciones climáticas adversas afectan toda la red) podría subestimar el riesgo de violaciones TW. Sin embargo, dado que el riesgo TW es marginal (8-10%), este efecto no altera la conclusión principal de dominancia de capacidad.

---

*Convergencia Monte Carlo — HVRPTW DSRSLCC*
*2000 escenarios, validación de distribuciones y supuestos*
*Última actualización: Mayo 2026*
