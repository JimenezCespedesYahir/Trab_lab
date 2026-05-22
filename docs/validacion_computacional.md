# Validación Computacional — Baseline HVRPTW Determinista

## 1. Configuración del Experimento

### 1.1 Solver

| Parámetro | Valor |
|---|---|
| Solver | Google OR-Tools 9.15 |
| Motor | CP-SAT Routing |
| Estrategia inicial | PATH_CHEAPEST_ARC |
| Metaheurística | GUIDED_LOCAL_SEARCH |
| Tiempo límite | 120 segundos |
| Lenguaje | Python 3.12 |

### 1.2 Instancia

| Parámetro | Valor |
|---|---|
| Nodos (clientes) | 81 |
| Depósito | 1 |
| Tipos de vehículo | 4 |
| Vehículos totales | 16 |
| Demanda total | 26,700 kg |
| Capacidad total | 50,000 kg |
| Arcos (matriz de distancia) | 82 × 82 = 6,724 |
| Ventanas de tiempo | 08:00-16:00 (homogéneas) |

---

## 2. Resultados Baseline

### 2.1 KPIs Principales

| KPI | Valor | Unidad |
|---|---|---|
| **Rutas generadas** | 9 | rutas |
| Vehículos utilizados | 9 / 16 | unidades |
| **Nodos servidos** | **81 / 81** | nodos (100%) |
| Nodos no servidos | 0 | — |
| **Distancia total** | 1,961.8 | km |
| Costo variable | S/ 4,360.68 | soles |
| Costo fijo | S/ 1,160.00 | soles |
| **Costo total** | **S/ 5,520.68** | soles |
| Carga total | 26,700 | kg |
| **Utilización promedio** | **71.8%** | — |
| Distancia media/ruta | 218.0 | km |
| Nodos promedio/ruta | 9.0 | — |

### 2.2 Detalle por Ruta

| Ruta | Vehículo | Nodos | Distancia (km) | Carga (kg) | Utilización |
|---|---|---|---|---|---|
| 1 | FUSO Canter 6T | 13 | 103.5 | 4,400 | 73% |
| 2 | FUSO Canter 6T | 12 | 195.6 | 3,900 | 65% |
| 3 | FUSO Canter 6T | 11 | 224.5 | 3,200 | 53% |
| 4 | FUSO Canter 6T | 11 | 56.6 | 4,300 | 72% |
| 5 | NLR 3.5 TON | 6 | 295.9 | 1,800 | 51% |
| 6 | NLR 3.5 TON | 7 | 246.6 | 2,800 | 80% |
| 7 | NLR 3.5 TON | 8 | 252.2 | 2,800 | 80% |
| 8 | NLR 3.5 TON | 8 | 263.9 | 2,500 | 71% |
| 9 | Toyota Hilux | 5 | 323.1 | 1,000 | 100% |

### 2.3 Asignación de Flota

| Tipo | Disponibles | Usados | Capacidad usada |
|---|---|---|---|
| FUSO Canter 6T | 4 | 4 | 15,800 / 24,000 kg (66%) |
| Fiat Ducato Refrig. | 2 | 0 | 0 / 6,000 kg (0%) |
| NLR 3.5 TON | 4 | 4 | 9,900 / 14,000 kg (71%) |
| Toyota Hilux | 6 | 1 | 1,000 / 6,000 kg (17%) |

**Observación**: La Fiat Ducato (refrigerada) no fue utilizada porque `cold_chain_demand = 0` y su costo/km es mayor. El solver prefiere vehículos no refrigerados más económicos. Cuando se active cadena de frío, la Ducato será asignada a esos nodos.

---

## 3. Performance Computacional

### 3.1 Tiempos de Ejecución

| Fase | Tiempo |
|---|---|
| Carga de datos | 0.02 s |
| Creación del modelo | 0.01 s |
| Resolución (GLS) | 120.02 s |
| **Total** | **120.05 s** |

### 3.2 Convergencia del Solver

| Métrica | Valor |
|---|---|
| Soluciones encontradas | 1,504 |
| Mejor solución (objetivo) | 552,033 (centavos) |
| Solución inicial | 832,612 |
| Mejora total | 33.7% |
| Branches explorados | 8,398 |
| Failures | 3,674 |
| Vecinos evaluados | 9,834,775 |
| Velocidad | 69 branches/s |

### 3.3 Escalabilidad

| Tamaño instancia | Nodos | Vehículos | Tiempo estimado |
|---|---|---|---|
| Actual | 81 | 16 | 120 s (límite) |
| Reducida (Sullana) | 25 | 8 | ~5-10 s |
| Completa (207 nodos) | 207 | 16 | >300 s (requiere heurística) |

---

## 4. Factibilidad

### 4.1 Restricciones Activas

| Restricción | Estado | Observación |
|---|---|---|
| Capacidad | Activa | Ruta 9 al 100% (Hilux) |
| Ventanas de tiempo | Activa | Todas cumplidas |
| Retorno al depósito | Cumplido | Todas las rutas retornan antes de 16:00 |
| Demanda total servida | **100%** | 81/81 nodos |

### 4.2 Posibles Cuellos de Botella

| Cuello de botella | Descripción | Impacto |
|---|---|---|
| Nodos remotos (>100 km) | 14 nodos consumen distancia desproporcionada | Ruta 9 (323 km, 1 Hilux) |
| Ventanas homogéneas | No hay diferenciación real de horarios | Reduce presión temporal |
| Demanda placeholder | Puede ser significativamente diferente con SISMED | Afecta asignación de flota |
| Tiempo de resolución | GLS no converge completamente en 120s | Solución puede mejorar con más tiempo |

---

## 5. Evaluación de Robustez (Preliminar)

### 5.1 Métricas de Robustez (para Fases B-D)

Estas métricas se evaluarán cuando se incorpore incertidumbre:

| Métrica | Definición | Valor baseline (determinista) |
|---|---|---|
| Route reliability | P(cumplir TW dado variabilidad) | 100% (sin variabilidad) |
| Service level | % nodos servidos | 100% |
| TW compliance | % ventanas cumplidas | 100% |
| Capacity violation | Exceso sobre capacidad | 0 kg |
| Cost gap | Δ costo estocástico vs determinista | 0% (baseline) |

### 5.2 Análisis de Sensibilidad Pendiente

| Parámetro | Rango a evaluar | Fase |
|---|---|---|
| Demanda (CV) | 0.1 — 0.5 | Fase C |
| Tiempo de viaje (CV) | 0.1 — 0.4 | Fase B |
| Número de escenarios | 100 — 10,000 | Fase D |
| α (CVaR) | 0.05 — 0.20 | Fase E |

---

## 6. Conclusiones

1. **Factibilidad confirmada**: El baseline HVRPTW determinista con OR-Tools resuelve la instancia de 81 nodos + 16 vehículos en 120 segundos, sirviendo el 100% de los nodos.

2. **Costo baseline**: S/ 5,520.68 (distancia: 1,961.8 km, 9 rutas). Este valor sirve como referencia para evaluación de fases estocásticas.

3. **Utilización eficiente**: 71.8% promedio indica buena asignación de flota. 7 de 16 vehículos no utilizados (capacidad de reserva).

4. **Próximos pasos**: Incorporar variabilidad en tiempos de viaje (Fase B) y demanda (Fase C) para evaluar degradación del costo y service level.

5. **Limitación principal**: Demandas placeholder. La calibración SISMED alterará significativamente la estructura de rutas.

---

*Validación computacional — Baseline Fase A*
*Solver: OR-Tools 9.15, GLS, 120s*
*Última actualización: Mayo 2026*
