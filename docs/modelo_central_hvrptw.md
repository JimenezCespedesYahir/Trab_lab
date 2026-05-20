# Modelo Central HVRPTW Robusto-Estocástico para Logística Farmacéutica Pública

## DSRSLCC — Dirección Sub Regional de Salud Luciano Castillo Colonna

---

## Tabla de Contenidos

1. [Sistema Logístico Real DSRSLCC](#1-sistema-logístico-real-dsrslcc)
2. [Supuestos Operativos](#2-supuestos-operativos)
3. [Dataset Maestro Definitivo](#3-dataset-maestro-definitivo)
4. [Formulación Matemática HVRPTW](#4-formulación-matemática-hvrptw)
5. [Incertidumbre Dual](#5-incertidumbre-dual)
6. [CVaR Optimization y Métricas de Riesgo](#6-cvar-optimization-y-métricas-de-riesgo)
7. [Arquitectura Experimental Monte Carlo](#7-arquitectura-experimental-monte-carlo)
8. [Algoritmo Simheuristic](#8-algoritmo-simheuristic)
9. [Validación Empírica y Roadmap Experimental](#9-validación-empírica-y-roadmap-experimental)

---

## 1. Sistema Logístico Real DSRSLCC

### 1.1 Contexto Institucional

La Dirección Sub Regional de Salud Luciano Castillo Colonna (DSRSLCC) es la entidad responsable de la distribución de productos farmacéuticos, dispositivos médicos e insumos de salud a los establecimientos de salud públicos en las provincias de Sullana, Ayabaca, Huancabamba, Paita, Talara y Morropón en la región Piura, Perú.

### 1.2 Estructura de Red Logística

| Componente | Descripción |
|---|---|
| **Depósito único** | Almacén Central DSRSLCC (Sullana) |
| **Coordenadas depósito** | lat: -4.906564, lon: -80.728434 |
| **Nodos de demanda** | 81 establecimientos de salud activos con geocodificación MEDIUM/HIGH |
| **Tipología de nodos** | Centros de Salud (CS), Puestos de Salud (PS) |
| **Cobertura geográfica** | Provincias de Sullana, Ayabaca, Huancabamba, Paita, Talara, Morropón |
| **Flota** | Heterogénea: 4 tipos de vehículos con diferentes capacidades |
| **Horizonte de planificación** | Distribución mensual (programación regular SISMED) |

### 1.3 Tipología de Establecimientos

| Tipo | Cantidad | Nivel de Complejidad | Demanda Relativa |
|---|---|---|---|
| Centro de Salud (CS) | 34 | Mayor (I-3, I-4) | Alta |
| Puesto de Salud (PS) | 43 | Menor (I-1, I-2) | Baja-Media |
| Otros establecimientos | 4 | Variable | Variable |
| **Total** | **81** | — | — |

### 1.4 Flota Vehicular Heterogénea

| Vehículo | Capacidad (ton) | Refrigeración | Costo/km (S/.) | Costo fijo (S/.) | Velocidad (km/h) | Autonomía (km) |
|---|---|---|---|---|---|---|
| FUSO Canter 6T | 6.0 | No | 2.5 | 150 | 60 | 400 |
| Fiat Ducato Refrigerada | 3.0 | Sí | 3.0 | 200 | 50 | 350 |
| NLR 3.5 TON | 3.5 | No | 2.2 | 120 | 55 | 380 |
| Toyota Hilux | 1.0 | No | 1.8 | 80 | 70 | 500 |

---

## 2. Supuestos Operativos

### 2.1 Red de Transporte

- **Grafo dirigido** basado en distancias reales OSRM (Open Source Routing Machine)
- **820 arcos** calculados con rutas terrestres reales
- Tiempos y distancias asimétricas (ida ≠ vuelta en algunos tramos)
- Red vial: combinación de carreteras asfaltadas, afirmadas y trochas
- Restricción de accesibilidad: algunos establecimientos rurales con acceso limitado en época de lluvias

### 2.2 Demanda

- **Unidad de demanda**: toneladas métricas de productos farmacéuticos por periodo
- **Frecuencia**: distribución mensual según programación SISMED
- **Demanda estocástica**: variabilidad inherente por fluctuaciones epidemiológicas, estacionalidad y emergencias sanitarias
- Centros de Salud: demanda media estimada = 500 kg, σ = 100 kg (CV = 0.20)
- Puestos de Salud: demanda media estimada = 200 kg, σ = 50 kg (CV = 0.25)
- **Nota**: valores iniciales estimados; requieren calibración con datos SISMED históricos reales

### 2.3 Tiempos de Viaje

- Basados en OSRM con datos OpenStreetMap
- **Variabilidad estocástica**: CV = 0.20 inicial (factores: clima, tráfico, estado de vía)
- Tiempos de servicio fijos por tipo de establecimiento:
  - Centro de Salud: 30 minutos
  - Puesto de Salud: 15 minutos

### 2.4 Ventanas de Tiempo

| Tipo | Apertura | Cierre | Aplicación |
|---|---|---|---|
| Depósito | 08:00 | 16:00 | Horario operativo del almacén |
| Cadena de frío | 08:00 | 13:00 | Productos termosensibles |
| Normal | 08:00 | 16:00 | Productos regulares |

### 2.5 Cadena de Frío

- **Estado actual**: `cold_chain_demand = 0` para todos los nodos (requiere análisis SISMED)
- Cuando se active: solo vehículos con `refrigeration = Yes` pueden servir nodos con cadena de frío
- Ventana de tiempo restringida a 08:00-13:00 para garantizar integridad térmica
- **No se modela degradación térmica** (simplificación operativa validada por horizonte corto de distribución)

---

## 3. Dataset Maestro Definitivo

### 3.1 Arquitectura de Datos

```
analytics/
├── nodes_hvrptw.csv          # Nodos con atributos HVRPTW
├── vehicles_hvrptw.csv       # Flota heterogénea
├── arcs_with_variability.csv # Arcos con variabilidad estocástica
├── time_windows.csv          # Ventanas de tiempo por nodo
└── demand_aggregated.csv     # Demanda agregada con incertidumbre
```

### 3.2 Dataset de Nodos (`nodes_hvrptw.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | string | Identificador único del nodo (= codigounico) |
| `ipress_code` | string | Código IPRESS (= codigounico) |
| `nombre` | string | Nombre del establecimiento |
| `latitude` | float | Latitud geocodificada |
| `longitude` | float | Longitud geocodificada |
| `categoria` | string | CENTRO DE SALUD / PUESTO DE SALUD / OTRO |
| `red` | string | Red de salud (vacío si no disponible) |
| `microred` | string | Micro red de salud (vacío si no disponible) |
| `nivel_atencion` | string | Nivel de atención inferido |
| `district` | string | Distrito |
| `province` | string | Provincia |
| `geocode_confidence` | string | Nivel de confianza de geocodificación |
| `demand_mean` | float | Demanda media estimada (kg) |
| `demand_std` | float | Desviación estándar de demanda (kg) |
| `demand_cv` | float | Coeficiente de variación de demanda |
| `cold_chain_demand` | int | Requiere cadena de frío (0/1) |
| `service_time` | int | Tiempo de servicio (minutos) |
| `tw_start` | string | Inicio ventana de tiempo (HH:MM) |
| `tw_end` | string | Fin ventana de tiempo (HH:MM) |
| `sanitary_priority` | int | Prioridad sanitaria (1-5) |

**Fuente**: Filtrado desde `nodes_high_medium.csv` (establecimientos ACTIVOS, geocode_confidence MEDIUM/HIGH)

### 3.3 Dataset de Vehículos (`vehicles_hvrptw.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `vehicle_id` | string | Identificador del tipo de vehículo |
| `vehicle_name` | string | Nombre comercial |
| `capacity_ton` | float | Capacidad en toneladas |
| `capacity_kg` | float | Capacidad en kilogramos |
| `refrigeration` | string | Tiene refrigeración (Yes/No) |
| `cold_chain_compatible` | string | Compatible con cadena de frío (Yes/No) |
| `cost_per_km` | float | Costo variable por kilómetro (S/.) |
| `fixed_cost` | float | Costo fijo por ruta (S/.) |
| `speed_kmh` | float | Velocidad promedio (km/h) |
| `autonomy_km` | float | Autonomía máxima (km) |
| `quantity` | int | Cantidad disponible (flota) |

### 3.4 Dataset de Arcos (`arcs_with_variability.csv`)

Extensión del dataset `arcs.csv` original con columnas de variabilidad estocástica:

| Campo adicional | Tipo | Descripción |
|---|---|---|
| `travel_time_mean` | float | Tiempo medio de viaje (= duration_min) |
| `travel_time_std` | float | Desviación estándar (= duration_min × 0.2) |
| `travel_time_cv` | float | Coeficiente de variación (0.2 inicial) |
| `road_risk` | int | Riesgo vial (1-5 según distancia) |
| `accessibility_score` | float | Score de accesibilidad (1.0 inicial) |

### 3.5 Dataset de Ventanas de Tiempo (`time_windows.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | string | Identificador del nodo |
| `tw_start` | string | Hora de inicio (HH:MM) |
| `tw_end` | string | Hora de cierre (HH:MM) |
| `tw_type` | string | Tipo: DEPOT / COLD_CHAIN / NORMAL |

### 3.6 Dataset de Demanda Agregada (`demand_aggregated.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | string | Identificador del nodo |
| `nombre` | string | Nombre del establecimiento |
| `categoria` | string | Categoría del establecimiento |
| `demand_mean` | float | Demanda media (kg) |
| `demand_std` | float | Desviación estándar (kg) |
| `demand_cv` | float | Coeficiente de variación |
| `cold_chain_demand` | int | Requiere cadena de frío (0/1) |

---

## 4. Formulación Matemática HVRPTW

### 4.1 Notación

**Conjuntos:**

| Símbolo | Definición |
|---|---|
| $\mathcal{N} = \{0, 1, 2, \ldots, n\}$ | Conjunto de nodos (0 = depósito) |
| $\mathcal{N}^+ = \mathcal{N} \setminus \{0\}$ | Nodos de demanda (clientes) |
| $\mathcal{K}$ | Conjunto de tipos de vehículos |
| $\mathcal{V}_k$ | Conjunto de vehículos disponibles de tipo $k$ |
| $\mathcal{A} = \{(i,j) : i,j \in \mathcal{N}, i \neq j\}$ | Conjunto de arcos |
| $\Omega$ | Conjunto de escenarios estocásticos |

**Parámetros:**

| Símbolo | Definición |
|---|---|
| $d_i$ | Demanda del nodo $i$ (determinista, Fase A) |
| $Q_k$ | Capacidad del vehículo tipo $k$ |
| $c_{ij}^k$ | Costo de traversar arco $(i,j)$ con vehículo tipo $k$ |
| $t_{ij}$ | Tiempo de viaje en arco $(i,j)$ (determinista, Fase A) |
| $s_i$ | Tiempo de servicio en nodo $i$ |
| $[a_i, b_i]$ | Ventana de tiempo del nodo $i$ |
| $f_k$ | Costo fijo de utilizar un vehículo tipo $k$ |
| $R_k$ | Autonomía máxima del vehículo tipo $k$ (km) |

**Variables de decisión:**

| Símbolo | Definición |
|---|---|
| $x_{ij}^{kv} \in \{0,1\}$ | 1 si el vehículo $v$ de tipo $k$ traversa arco $(i,j)$ |
| $y_i^{kv} \in \{0,1\}$ | 1 si el nodo $i$ es servido por vehículo $v$ de tipo $k$ |
| $w_i^{kv} \geq 0$ | Tiempo de llegada del vehículo $v$ tipo $k$ al nodo $i$ |
| $u_i^{kv} \geq 0$ | Carga acumulada del vehículo $v$ tipo $k$ al llegar a nodo $i$ |

### 4.2 Fase A: HVRPTW Determinista (Baseline)

**Función objetivo — Minimizar costo total:**

$$
\min Z = \sum_{k \in \mathcal{K}} \sum_{v \in \mathcal{V}_k} \left[ f_k \cdot \sum_{j \in \mathcal{N}^+} x_{0j}^{kv} + \sum_{(i,j) \in \mathcal{A}} c_{ij}^k \cdot x_{ij}^{kv} \right]
$$

**Sujeto a:**

**(C1) Cobertura completa** — cada cliente es visitado exactamente una vez:

$$
\sum_{k \in \mathcal{K}} \sum_{v \in \mathcal{V}_k} y_i^{kv} = 1 \quad \forall i \in \mathcal{N}^+
$$

**(C2) Conservación de flujo:**

$$
\sum_{i \in \mathcal{N}} x_{ij}^{kv} = y_j^{kv} \quad \forall j \in \mathcal{N}^+, \forall k \in \mathcal{K}, \forall v \in \mathcal{V}_k
$$

$$
\sum_{j \in \mathcal{N}} x_{ij}^{kv} = y_i^{kv} \quad \forall i \in \mathcal{N}^+, \forall k \in \mathcal{K}, \forall v \in \mathcal{V}_k
$$

**(C3) Capacidad vehicular:**

$$
\sum_{i \in \mathcal{N}^+} d_i \cdot y_i^{kv} \leq Q_k \quad \forall k \in \mathcal{K}, \forall v \in \mathcal{V}_k
$$

**(C4) Ventanas de tiempo:**

$$
a_i \leq w_i^{kv} \leq b_i \quad \forall i \in \mathcal{N}, \forall k \in \mathcal{K}, \forall v \in \mathcal{V}_k
$$

**(C5) Consistencia temporal** (eliminación de subtours):

$$
w_i^{kv} + s_i + t_{ij} - M(1 - x_{ij}^{kv}) \leq w_j^{kv} \quad \forall (i,j) \in \mathcal{A}, \forall k, \forall v
$$

**(C6) Autonomía vehicular:**

$$
\sum_{(i,j) \in \mathcal{A}} d_{ij}^{dist} \cdot x_{ij}^{kv} \leq R_k \quad \forall k \in \mathcal{K}, \forall v \in \mathcal{V}_k
$$

**(C7) Compatibilidad cadena de frío:**

$$
y_i^{kv} \leq \text{cold\_compatible}_k \quad \forall i \in \mathcal{N}^+: \text{cold\_chain}_i = 1, \forall k, \forall v
$$

**(C8) Inicio y retorno al depósito:**

$$
\sum_{j \in \mathcal{N}^+} x_{0j}^{kv} = \sum_{j \in \mathcal{N}^+} x_{j0}^{kv} \leq 1 \quad \forall k \in \mathcal{K}, \forall v \in \mathcal{V}_k
$$

### 4.3 Costo de Arcos

$$
c_{ij}^k = \text{cost\_per\_km}_k \times d_{ij}^{dist}
$$

donde $d_{ij}^{dist}$ es la distancia real OSRM en km del arco $(i,j)$.

---

## 5. Incertidumbre Dual

### 5.1 Fase B: Tiempos de Viaje Estocásticos

Los tiempos de viaje reales son variables aleatorias:

$$
\tilde{\tau}_{ij} \sim \text{LogNormal}(\mu_{ij}, \sigma_{ij}^2)
$$

donde:
- $\mu_{ij}$: tiempo medio de viaje OSRM (= `duration_min`)
- $\sigma_{ij} = 0.20 \times \mu_{ij}$: desviación estándar inicial (CV = 0.20)

**Justificación de LogNormal**: los tiempos de viaje son estrictamente positivos y presentan asimetría positiva (retrasos más probables que adelantos).

**Restricción de ventana de tiempo estocástica:**

$$
P\left(w_i^{kv} \leq b_i\right) \geq 1 - \alpha \quad \forall i \in \mathcal{N}^+
$$

donde $\alpha$ es el nivel de riesgo aceptable (inicialmente $\alpha = 0.05$).

### 5.2 Fase C: Demanda Estocástica

La demanda de cada nodo es una variable aleatoria:

$$
\tilde{\xi}_i \sim \text{Normal}(\mu_i^d, (\sigma_i^d)^2) \quad \forall i \in \mathcal{N}^+
$$

con truncamiento en $[0, 2\mu_i^d]$ para evitar demandas negativas o irrealistas.

| Categoría | $\mu_i^d$ (kg) | $\sigma_i^d$ (kg) | CV |
|---|---|---|---|
| Centro de Salud | 500 | 100 | 0.20 |
| Puesto de Salud | 200 | 50 | 0.25 |

**Restricción de capacidad estocástica:**

$$
P\left(\sum_{i \in \mathcal{N}^+} \tilde{\xi}_i \cdot y_i^{kv} \leq Q_k\right) \geq 1 - \beta \quad \forall k, \forall v
$$

### 5.3 Formulación Two-Stage Stochastic Programming

**Primera etapa (here-and-now):**
- Decisiones de ruteo: $x_{ij}^{kv}$, $y_i^{kv}$
- Se toman ANTES de conocer las realizaciones de incertidumbre

**Segunda etapa (wait-and-see):**
- Acciones correctivas ante realizaciones $\omega \in \Omega$
- Recurso: penalización por violación de capacidad o ventana de tiempo

$$
\min_{x,y} \left[ c^T x + \mathbb{E}_\omega [Q(x, \omega)] \right]
$$

donde $Q(x, \omega)$ es el costo de recurso en el escenario $\omega$:

$$
Q(x, \omega) = \sum_{i \in \mathcal{N}^+} \left[ \pi_i^{cap} \cdot [\text{exceso capacidad}]_i^\omega + \pi_i^{tw} \cdot [\text{violación TW}]_i^\omega \right]
$$

---

## 6. CVaR Optimization y Métricas de Riesgo

### 6.1 Integración Progresiva (Fase E)

**Nota metodológica**: CVaR NO se implementa inmediatamente. Se integra progresivamente después de validar las Fases A-D.

### 6.2 Conditional Value-at-Risk (CVaR)

Para un nivel de confianza $\beta$ (típicamente 0.95):

$$
\text{CVaR}_\beta(Z) = \min_{\eta} \left\{ \eta + \frac{1}{1-\beta} \mathbb{E}\left[ (Z - \eta)^+ \right] \right\}
$$

### 6.3 Formulación Mean-CVaR

$$
\min \lambda \cdot \mathbb{E}[Z(\omega)] + (1-\lambda) \cdot \text{CVaR}_\beta[Z(\omega)]
$$

donde $\lambda \in [0,1]$ es el parámetro de aversión al riesgo:
- $\lambda = 1$: optimización neutral al riesgo (solo valor esperado)
- $\lambda = 0$: máxima aversión al riesgo (solo CVaR)
- $\lambda \in (0,1)$: trade-off intermedio

### 6.4 Métricas de Riesgo (KPIs Experimentales)

| Métrica | Definición | Uso |
|---|---|---|
| **Route reliability** | $P(\text{ruta cumple TW y capacidad})$ | KPI experimental |
| **Expected cost** | $\mathbb{E}[Z(\omega)]$ | Benchmark determinista vs. estocástico |
| **Cost VaR** | Costo al percentil $\beta$ | Análisis de cola |
| **Cost CVaR** | Media condicional sobre VaR | Medida de riesgo coherente |
| **Service level** | % de nodos servidos dentro de TW | Calidad de servicio |
| **Capacity violation rate** | % de rutas con exceso de capacidad | Factibilidad operacional |

**Importante**: Route reliability y robustez se tratan inicialmente como KPIs experimentales y métricas de validación, NO como restricciones duras.

---

## 7. Arquitectura Experimental Monte Carlo

### 7.1 Fase D: Generación de Escenarios

**Procedimiento de simulación Monte Carlo:**

```
Para cada réplica r = 1, ..., R:
  1. Generar realizaciones de demanda: ξ_i^r ~ Normal(μ_i, σ_i²)  ∀i ∈ N⁺
  2. Generar realizaciones de tiempos: τ_ij^r ~ LogNormal(μ_ij, σ_ij²)  ∀(i,j) ∈ A
  3. Evaluar solución x* (de Fase A) bajo escenario r
  4. Registrar: costo total, violaciones TW, violaciones capacidad, servicio
```

### 7.2 Parámetros de Simulación

| Parámetro | Valor inicial | Justificación |
|---|---|---|
| Número de escenarios ($|\Omega|$) | 1,000 | Balance precisión/costo computacional |
| Réplicas Monte Carlo ($R$) | 30 | Significancia estadística (CLT) |
| Semilla aleatoria | 42 | Reproducibilidad |
| CV demanda (CS) | 0.20 | Estimación conservadora |
| CV demanda (PS) | 0.25 | Mayor variabilidad en establecimientos pequeños |
| CV tiempos de viaje | 0.20 | Estimación por condiciones viales regionales |
| Nivel de confianza CVaR ($\beta$) | 0.95 | Estándar en OR |
| Nivel de riesgo TW ($\alpha$) | 0.05 | 95% de cumplimiento de ventanas |

### 7.3 Métricas de Evaluación por Escenario

```
Para cada escenario ω:
  - Costo total de rutas: Z(ω)
  - Número de violaciones de ventana de tiempo
  - Exceso de capacidad total (kg)
  - Distancia total recorrida (km)
  - Número de vehículos utilizados
  - Tasa de servicio (% nodos servidos a tiempo)
```

### 7.4 Análisis Estadístico

- **Intervalos de confianza** al 95% para cada KPI
- **Distribución empírica** de costos totales → histograma + QQ-plot
- **Análisis de sensibilidad**: variación de CV de demanda y tiempos
- **Comparación**: solución determinista vs. estocástica vs. CVaR-aware

---

## 8. Algoritmo Simheuristic

### 8.1 Fase F: Algoritmo Simheuristic Recomendado

**Arquitectura general:**

```
Algoritmo SimHeuristic-HVRPTW:
  Input: instancia HVRPTW, parámetros estocásticos
  Output: solución robusta x*

  1. FASE CONSTRUCCIÓN:
     - Resolver HVRPTW determinista (Clark-Wright savings o nearest neighbor)
     - Obtener solución inicial x₀

  2. FASE MEJORA LOCAL:
     Para iter = 1 hasta max_iter:
       - Aplicar operadores de vecindad:
         • 2-opt intra-ruta
         • Or-opt (reubicación de segmentos)
         • Cross-exchange inter-ruta
         • Vehicle swap (cambio de tipo de vehículo)
       - Evaluar mejora con función objetivo determinista

  3. FASE SIMULACIÓN (Monte Carlo):
     Para cada solución candidata x':
       - Simular S escenarios estocásticos
       - Calcular E[Z(x', ω)] y CVaR_β[Z(x', ω)]
       - Si x' domina a x* en ambas métricas → x* ← x'

  4. FASE INTENSIFICACIÓN:
     - Refinar las top-K soluciones con más escenarios (S' >> S)
     - Seleccionar solución final basada en criterio Mean-CVaR

  Return x*
```

### 8.2 Operadores de Vecindad

| Operador | Tipo | Descripción |
|---|---|---|
| 2-opt | Intra-ruta | Inversión de segmento dentro de una ruta |
| Or-opt | Intra-ruta | Reubicación de 1-3 nodos consecutivos |
| Relocate | Inter-ruta | Mover un nodo de una ruta a otra |
| Cross-exchange | Inter-ruta | Intercambio de segmentos entre rutas |
| Vehicle swap | Inter-tipo | Cambiar tipo de vehículo asignado a ruta |

### 8.3 Criterio de Aceptación

- **Greedy** para fase de mejora local
- **Simulated Annealing** con temperatura adaptativa para escapar de óptimos locales
- **Criterio de filtrado**: solo evaluar con Monte Carlo las soluciones que mejoran el determinista en ≥ 2%

---

## 9. Validación Empírica y Roadmap Experimental

### 9.1 Plan de Fases

```
FASE A: HVRPTW Determinista
├── Implementar formulación MILP
├── Resolver con solver exacto (Gurobi/CPLEX/HiGHS)
├── Benchmark: costo, distancia, vehículos, tiempo CPU
└── Validar: todas las restricciones satisfechas

FASE B: Travel-time Uncertainty
├── Incorporar tiempos estocásticos LogNormal
├── Evaluar solución Fase A bajo incertidumbre temporal
├── Medir: tasa de violación de ventanas de tiempo
└── KPI: route reliability

FASE C: Demand Uncertainty
├── Incorporar demanda estocástica Normal truncada
├── Evaluar solución Fase A bajo incertidumbre de demanda
├── Medir: tasa de violación de capacidad
└── KPI: capacity violation rate

FASE D: Monte Carlo Validation
├── Generar 1,000 escenarios combinados (demanda + tiempos)
├── Evaluar soluciones Fases A-C bajo escenarios
├── Análisis estadístico completo
├── Comparación determinista vs. estocástico
└── Análisis de sensibilidad (CV, α, β)

FASE E: CVaR Risk Aversion
├── Implementar formulación Mean-CVaR
├── Variar λ ∈ {0.0, 0.25, 0.5, 0.75, 1.0}
├── Generar frontera eficiente costo-riesgo
└── Analizar trade-off rendimiento vs. robustez

FASE F: SimHeuristic / Metaheuristic
├── Implementar algoritmo simheuristic
├── Calibrar parámetros con diseño experimental
├── Comparar con solución exacta (gap de optimalidad)
└── Escalar a instancias grandes si solver exacto no escala
```

### 9.2 Validación Operacional

| Criterio | Método | Umbral |
|---|---|---|
| Factibilidad de rutas | Verificación de restricciones | 100% |
| Cobertura de nodos | Todos los nodos servidos | 100% |
| Cumplimiento de TW | Simulación Monte Carlo | ≥ 95% |
| Utilización vehicular | Carga promedio / Capacidad | ≥ 60% |
| Distancia total | Comparación vs. rutas actuales | Mejora ≥ 10% |
| Costo total | Benchmark vs. operación actual | Cuantificar ahorro |

### 9.3 Comparación con Benchmarks

1. **Operación actual DSRSLCC** (si datos disponibles): baseline operacional
2. **Nearest neighbor heuristic**: baseline algorítmico simple
3. **Clark-Wright savings**: baseline algorítmico clásico
4. **HVRPTW determinista óptimo**: Fase A como referencia
5. **Stochastic HVRPTW**: Fases B-C como referencia estocástica

### 9.4 Requisitos de Publicabilidad

| Aspecto | Requisito | Estado |
|---|---|---|
| Datos reales | Establecimientos reales DSRSLCC | Disponible |
| Geocodificación validada | MEDIUM/HIGH confidence | Disponible |
| Ruteo real | OSRM con datos OSM | Disponible |
| Formulación matemática | MILP + two-stage stochastic | Documentada |
| Framework experimental | Monte Carlo + análisis estadístico | Diseñado |
| Reproducibilidad | Semillas fijas, datos versionados | En implementación |

---

## Separación Metodológica Explícita

### INFRAESTRUCTURA (ya existente — NO modificar)
- ETL de datos RENIPRESS
- Power BI reverse engineering
- Geocodificación Nominatim
- Ruteo OSRM
- Datasets base: `nodes_high_medium.csv`, `arcs.csv`

### MODELO CIENTÍFICO (a construir — este documento)
- Formulación HVRPTW
- Stochastic programming
- CVaR (progresivo)
- Monte Carlo validation
- Simheuristic algorithm
- Datasets derivados HVRPTW: `nodes_hvrptw.csv`, `vehicles_hvrptw.csv`, `arcs_with_variability.csv`, `time_windows.csv`, `demand_aggregated.csv`

---

## Principios Metodológicos

1. **Elegancia metodológica**: formulación limpia, notación consistente, sin complejidad innecesaria
2. **Coherencia OR**: seguir convenciones estándar de investigación operativa
3. **Publicabilidad**: estructura y rigor para journal/conferencia peer-reviewed
4. **Estabilidad computacional**: modelos que se resuelven en tiempo razonable
5. **Complejidad por fases**: crecer la complejidad gradualmente (A→B→C→D→E→F)
6. **Realismo sin sobrecomplejidad**: evitar DRO, Wasserstein ambiguity sets, adaptive robust optimization, multistage recourse extremo, emergency routing complejo, thermal degradation modeling avanzado

---

*Documento generado como parte del proyecto de investigación HVRPTW aplicado a logística farmacéutica pública DSRSLCC.*
*Datasets consolidados en directorio `analytics/`.*
*Última actualización: Mayo 2026.*
