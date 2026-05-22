# Estructura para Paper/Tesis — HVRPTW Estocástico DSRSLCC

## 1. Título Propuesto

### Opción A (Tesis)
**Evaluación Estocástica del Problema de Ruteo de Vehículos Heterogéneos con Ventanas de Tiempo para Distribución Farmacéutica Pública: Caso DSRSLCC, Piura**

### Opción B (Paper — enfoque en hallazgo)
**Stochastic Fragility of Deterministic Fleet Assignments in Heterogeneous Vehicle Routing: Evidence from Public Pharmaceutical Distribution in Peru**

### Opción C (Paper — enfoque metodológico)
**A Monte Carlo Framework for Evaluating Stochastic Risk in Heterogeneous Fleet Pharmaceutical Distribution Networks**

---

## 2. Abstract Estructurado

### Contexto
La distribución de medicamentos en sistemas de salud pública utiliza flotas heterogéneas en redes rurales con demanda variable. La planificación determinista es la práctica estándar.

### Objetivo
Evaluar la robustez de soluciones HVRPTW deterministas bajo incertidumbre dual (demanda y tiempos de viaje) en un caso real de logística farmacéutica pública en Perú.

### Método
Se implementó un framework que integra: (1) datos SISMED del sistema de salud peruano como fuente de parámetros de incertidumbre, (2) OSRM/OpenStreetMap para tiempos y distancias reales, (3) OR-Tools como solver HVRPTW, y (4) simulación Monte Carlo (2,000 escenarios) con análisis de sensibilidad multidimensional. Se evaluó un sistema con 81 establecimientos, 16 vehículos de 4 tipos (ratio de capacidad 6:1), y demanda calibrada con SISMED.

### Resultados
La solución determinista (S/ 5,089, 100% reliability) exhibe un gap de costo del 61% y route reliability del 6% bajo incertidumbre realista. La capacidad vehicular, no la incertidumbre temporal, es el factor dominante de riesgo (93% de violaciones). El cuello de botella son los vehículos de menor capacidad (1 ton), que operan al 95% de capacidad determinista. La sustitución de estos vehículos por unidades de 3.5+ ton restaura la reliability a 95-98%.

### Conclusión
La optimización determinista de costo en flotas con heterogeneidad extrema induce fragilidad operacional estructural. La composición de flota, no la capacidad total, determina la robustez bajo incertidumbre.

---

## 3. Keywords

Heterogeneous Vehicle Routing Problem, Time Windows, Stochastic Optimization, Monte Carlo Simulation, Pharmaceutical Logistics, Public Health Supply Chain, Fleet Composition, Risk Analysis, CVaR, SISMED

---

## 4. Estructura IMRAD Detallada

### I. Introduction (Introducción)
1. **Contexto del problema**: Distribución farmacéutica pública, DSRSLCC, logística sanitaria
2. **Relevancia**: Impacto en acceso a medicamentos, costos del sistema de salud
3. **Gap en la literatura**: HVRPTW con evaluación estocástica en healthcare logistics reales
4. **Objetivo de investigación**: Evaluar robustez de soluciones deterministas bajo incertidumbre dual
5. **Contribuciones**: Framework, hallazgo de fragilidad, metodología de diagnóstico de flota

### II. Literature Review (Revisión de Literatura)
1. **VRP y variantes**: CVRP, VRPTW, HVRPTW
2. **VRP estocástico**: SVRP, demand uncertainty, travel time uncertainty
3. **Healthcare logistics**: Pharmaceutical distribution, vaccine logistics
4. **Fleet composition**: FSP, heterogeneous fleet optimization
5. **Risk measures**: VaR, CVaR en VRP
6. **Simheuristics y Monte Carlo en VRP**

### III. Methodology (Metodología)

#### III.1 Sistema Logístico
- Descripción de DSRSLCC
- Red de establecimientos (81 nodos)
- Flota heterogénea (4 tipos, ratio 6:1)
- Características operacionales

#### III.2 Formulación HVRPTW
- Modelo matemático
- Conjuntos, parámetros, variables
- Función objetivo
- Restricciones

#### III.3 Calibración de Datos
- Extracción SISMED (PowerBI DSR)
- Metodología CPMA
- Conversión item→kg
- Limitaciones y supuestos

#### III.4 Evaluación Estocástica
- Distribuciones: Normal truncada (demanda), LogNormal (tiempos)
- Generación de escenarios Monte Carlo
- Evaluación post-optimización
- Métricas: VaR, CVaR, reliability, violations

#### III.5 Diseño Experimental
- Convergencia (100-2000 escenarios)
- Sensibilidad: CV demanda, CV tiempo, factor de conversión
- Experimentos de flota (10 configuraciones)
- Análisis de impacto relativo

### IV. Results (Resultados)

#### IV.1 Baseline Determinista
- Tabla: KPIs baseline
- Figura: Mapa de rutas

#### IV.2 Evaluación Estocástica
- Tabla: Comparación determinista vs estocástico
- Figura: Distribución de costos (histograma + KDE)
- Figura: Convergencia Monte Carlo

#### IV.3 Análisis de Sensibilidad
- Tabla: Sensibilidad CV demanda × CV tiempo
- Tabla: Sensibilidad factor de conversión
- Figura: Heatmap de sensibilidad

#### IV.4 Experimentos de Flota
- Tabla: 10 configuraciones × KPIs
- Figura: Reliability por configuración

#### IV.5 Análisis de Impacto Relativo
- Tabla: Contribución de cada factor
- Diagnóstico de cuello de botella

### V. Discussion (Discusión)
1. Interpretación causal del colapso de reliability
2. Explicación de la dominancia de capacidad sobre tiempo (ratio slack/variabilidad)
3. Por qué la minimización determinista induce fragilidad
4. Implicaciones operacionales para DSRSLCC
5. Relación con literatura HVRPTW y SVRP
6. Hallazgo contraintuitivo: tiempo no domina en red rural

### VI. Conclusions (Conclusiones)
1. Cinco conclusiones derivadas de resultados
2. Recomendaciones operacionales
3. Contribuciones del trabajo
4. Trabajo futuro (CVaR, simheuristic, calibración IPRESS)

### VII. Limitations (Limitaciones)
- Remitir a threats_to_validity.md

---

## 5. Propuesta de Tablas y Figuras

### Tablas

| # | Contenido | Sección |
|---|---|---|
| T1 | Descripción de la flota vehicular DSRSLCC | III.1 |
| T2 | Parámetros de demanda calibrada por categoría | III.3 |
| T3 | KPIs del baseline determinista | IV.1 |
| T4 | Comparación determinista vs estocástico (2000 esc.) | IV.2 |
| T5 | Convergencia MC: E[cost], CVaR, reliability por n | IV.2 |
| T6 | Sensibilidad CV demanda × CV tiempo | IV.3 |
| T7 | Sensibilidad factor de conversión item→kg | IV.3 |
| T8 | Experimentos de flota: 10 configuraciones | IV.4 |
| T9 | Impacto relativo de factores (aislamiento) | IV.5 |
| T10 | VaR y CVaR por nivel α | IV.2 |

### Figuras

| # | Contenido | Sección |
|---|---|---|
| F1 | Mapa de la red DSRSLCC (81 nodos, depósito) | III.1 |
| F2 | Distribución de costos: histograma + KDE + boxplot | IV.2 |
| F3 | Convergencia MC: E[cost] y CI 95% vs n escenarios | IV.2 |
| F4 | Q-Q plot de normalidad | IV.2 |
| F5 | Heatmap sensibilidad E[cost] × (CV demanda, CV tiempo) | IV.3 |
| F6 | Sensibilidad del factor de conversión (barras) | IV.3 |
| F7 | Reliability por configuración de flota (barras horizontales) | IV.4 |
| F8 | Ratio slack/variabilidad por tipo de vehículo | V |

---

## 6. Roadmap de Redacción

### Fase 1: Redacción core (ya disponible)
- [x] Formulación matemática (modelo_central_hvrptw.md)
- [x] Resultados experimentales (results_chapter.md)
- [x] Discusión científica (scientific_discussion.md)
- [x] Limitaciones (threats_to_validity.md)
- [x] Conclusiones (final_conclusions.md)

### Fase 2: Complementos
- [ ] Revisión de literatura (requiere búsqueda bibliográfica real)
- [ ] Introducción formal
- [ ] Formato según revista/universidad objetivo
- [ ] Referencias bibliográficas verificadas

### Fase 3: Refinamiento
- [ ] Figuras publicables (formato journal)
- [ ] Tablas en formato estándar
- [ ] Revisión de estilo académico
- [ ] Verificación de consistencia numérica
