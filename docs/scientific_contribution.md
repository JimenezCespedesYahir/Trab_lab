# Contribución Científica — HVRPTW Estocástico para Logística Farmacéutica Pública

## 1. ¿Qué Descubrió Esta Investigación?

### 1.1 Descubrimiento Principal

En un sistema de distribución farmacéutica pública con flota heterogénea (HVRPTW), la **optimización determinista de costo mínimo induce fragilidad operacional estructural** al sobreutilizar vehículos de baja capacidad y bajo costo. Esta fragilidad se manifiesta como una route reliability del 6% bajo incertidumbre realista, a pesar de que la capacidad total de la flota es 3× la demanda.

### 1.2 Mecanismo Identificado

1. El solver determinista minimiza costo total.
2. Los vehículos más pequeños (Toyota Hilux, 1 ton) tienen el menor costo/km.
3. El solver los asigna preferentemente, operando al 95% de capacidad.
4. Con variabilidad de demanda CV=0.42 (dato SISMED real), la demanda excede capacidad en ~50% de los escenarios por ruta.
5. Con múltiples rutas en Hilux, la probabilidad de fallo del sistema se acumula a >97%.

### 1.3 Resultado Contraintuitivo

Se esperaría que en una red logística rural con distancias de 5-120 km y vías no pavimentadas, la **incertidumbre temporal** fuera el factor de riesgo dominante. Sin embargo, los datos muestran que las ventanas de 8 horas proporcionan slack suficiente para absorber variabilidad temporal, mientras que la capacidad de los Hilux no tiene margen para absorber variabilidad de demanda.

---

## 2. Aporte Metodológico

### 2.1 Framework de Evaluación Estocástica para HVRPTW Farmacéutico

Se desarrolló un framework reproducible que integra:

- **Datos SISMED reales** (sistema nacional peruano de medicamentos) como fuente de parámetros de incertidumbre
- **OSRM + OpenStreetMap** para tiempos y distancias de viaje reales
- **OR-Tools** como solver HVRPTW determinista
- **Simulación Monte Carlo** para evaluación estocástica post-optimización
- **Análisis de sensibilidad multidimensional** (demanda, tiempo, conversión, flota)

Este framework es transferible a otras DIRESA/DIRIS del sistema de salud peruano.

### 2.2 Cuantificación del "Precio de la Certidumbre"

Se cuantificó formalmente la brecha entre planificación determinista y realidad estocástica:
- **Gap de costo**: +61% (S/ 5,089 → S/ 8,160)
- **Gap de reliability**: -94 puntos porcentuales (100% → 6%)

Estos gaps son inusualmente altos comparados con la literatura VRP estocástica (típicamente 10-40%), y se explican por la heterogeneidad extrema de la flota (ratio de capacidad 6:1).

### 2.3 Metodología de Diagnóstico de Composición de Flota

Se propone un procedimiento de diagnóstico para evaluar si la composición de una flota heterogénea es adecuada bajo incertidumbre:

1. Resolver HVRPTW determinista
2. Evaluar con Monte Carlo bajo CV real (de SISMED u otra fuente)
3. Calcular ratio slack/variabilidad por tipo de vehículo
4. Identificar vehículos con ratio < 1.0 como "frágiles"
5. Evaluar configuraciones alternativas de flota

---

## 3. Aporte Operacional

### 3.1 Para DSRSLCC Específicamente

1. Los Toyota Hilux no deben asignarse a rutas de distribución mensual regular.
2. Un buffer de capacidad del 15-25% reduce violaciones de 93% a 55-75%.
3. Reemplazar Hilux por NLR (3.5 ton) lleva la reliability de 6% a 95%.
4. La inversión en vehículos de mayor capacidad tiene retorno por reducción de viajes adicionales y penalizaciones.

### 3.2 Para Logística Farmacéutica Pública en General

1. La planificación determinista de distribución farmacéutica es insuficiente en redes con demanda variable.
2. La composición de flota importa más que la capacidad total cuando hay heterogeneidad significativa.
3. Los sistemas SISMED existentes proporcionan datos suficientes para parametrizar modelos estocásticos.

---

## 4. ¿Qué Diferencia Este Trabajo de un VRP Clásico?

| Aspecto | VRP clásico | Este trabajo |
|---|---|---|
| Demanda | Conocida con certeza | Estocástica con CV de SISMED |
| Tiempos | Deterministas | LogNormal con CV de OSRM |
| Flota | Homogénea o mildly heterogeneous | Heterogeneidad extrema (ratio 6:1) |
| Evaluación | Solución única | 2000 escenarios Monte Carlo |
| Riesgo | No considerado | CVaR, VaR, reliability, violations |
| Datos | Benchmarks académicos | Datos reales del sistema de salud peruano |
| Hallazgo | Rutas óptimas | **Fragilidad de rutas óptimas bajo incertidumbre** |
| Diagnóstico | — | Identificación de vehículos frágiles por ratio slack/variabilidad |

---

## 5. Lo Que Este Trabajo NO Afirma

1. **No afirma que la solución estocástica sea mejor que la determinista** — no se implementó optimización estocástica; solo evaluación.
2. **No afirma optimalidad** — OR-Tools usa metaheurística (GLS), no garantiza óptimo global.
3. **No afirma que los datos SISMED sean exactos** — son estimaciones operacionales con limitaciones documentadas.
4. **No afirma generalización automática** — los resultados cuantitativos son específicos a DSRSLCC; el framework y la metodología de diagnóstico sí son generalizables.
5. **No afirma que eliminar Hilux sea la solución** — afirma que es una de las configuraciones que mejora robustez, y que la heterogeneidad extrema de flota es el factor estructural.
