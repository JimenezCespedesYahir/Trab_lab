# Modelo Central HVRPTW Robusto-Estocástico
## Optimización de Rutas para la Distribución Farmacéutica Pública — DSRSLCC

> **Versión:** 1.0  
> **Fecha:** 2026-05-20  
> **Ámbito:** Dirección Sub-Regional de Salud Luciano Castillo Colonna (DSRSLCC), Región Piura, Perú  
> **Paradigma:** Two-Stage Stochastic HVRPTW con CVaR

---

## Tabla de Contenidos

1. [Sistema Logístico Real DSRSLCC](#1-sistema-logístico-real-dsrslcc)
2. [Supuestos Operativos](#2-supuestos-operativos)
3. [Dataset Maestro Definitivo](#3-dataset-maestro-definitivo)
4. [Formulación Matemática Two-Stage Stochastic HVRPTW](#4-formulación-matemática-two-stage-stochastic-hvrptw)
5. [Incertidumbre Dual](#5-incertidumbre-dual)
6. [CVaR Optimization y Métricas de Riesgo](#6-cvar-optimization-y-métricas-de-riesgo)
7. [Arquitectura Experimental Monte Carlo](#7-arquitectura-experimental-monte-carlo)
8. [Algoritmo Simheuristic Recomendado](#8-algoritmo-simheuristic-recomendado)
9. [Validación Empírica y Roadmap Experimental](#9-validación-empírica-y-roadmap-experimental)
10. [Separación Infraestructura vs. Modelo Científico](#10-separación-infraestructura-vs-modelo-científico)

---

## 1. Sistema Logístico Real DSRSLCC

### 1.1 Contexto Institucional

La Dirección Sub-Regional de Salud Luciano Castillo Colonna (DSRSLCC) es responsable de la distribución de productos farmacéuticos, dispositivos médicos e insumos sanitarios a los establecimientos de salud de primer nivel en las provincias de Sullana, Ayabaca, Huancabamba, Paita, Talara, Morropón y Sechura de la Región Piura.

### 1.2 Estructura de la Red

| Componente | Descripción |
|---|---|
| **Depósito único** | Almacén Central DSRSLCC (Sullana): lat=-4.906564, lon=-80.728434 |
| **Nodos de demanda** | 81 establecimientos de salud activos con geocodificación validada (confianza MEDIUM/HIGH) |
| **Categorías** | 34 Centros de Salud, 43 Puestos de Salud, 4 establecimientos con clasificación especial |
| **Cobertura geográfica** | Provincias: Ayabaca, Huancabamba, Sullana, Morropón, Paita, Talara, Sechura |
| **Flota heterogénea** | 4 tipos de vehículos con capacidades diferenciadas (1.0–6.0 ton) |
| **Red vial** | 820 arcos OSRM validados con distancias y tiempos reales |

### 1.3 Depósito Central

```
ID:          DEPOT_DSRSLCC
Nombre:      Almacén Central DSRSLCC
Ubicación:   Sullana, Piura, Perú
Latitud:     -4.906564049486188
Longitud:    -80.72843391449476
Operación:   08:00 – 16:00
Función:     Único punto de origen/retorno para todas las rutas
```

---

## 2. Supuestos Operativos

### 2.1 Red de Distribución

| Supuesto | Especificación |
|---|---|
| **Topología** | Grafo dirigido completo entre depósito y nodos servidos |
| **Distancias** | Distancias reales OSRM (no euclidianas) |
| **Tiempos de viaje** | Tiempos OSRM con variabilidad estocástica (CV inicial = 0.2) |
| **Simetría** | Arcos bidireccionales (confirmado en dataset) |
| **Conectividad** | Todos los nodos son alcanzables desde el depósito |

### 2.2 Demanda

| Supuesto | Especificación |
|---|---|
| **Naturaleza** | Estocástica, log-normal con parámetros estimados por categoría |
| **Unidad** | Kilogramos de productos farmacéuticos por período |
| **Centro de Salud** | μ = 500 kg, σ = 100 kg (CV = 0.20) |
| **Puesto de Salud** | μ = 200 kg, σ = 50 kg (CV = 0.25) |
| **Correlación** | Inicialmente independiente entre nodos (relajable con datos SISMED) |
| **Cadena de frío** | Inicialmente 0% de demanda requiere cadena de frío (ajustable con análisis SISMED) |

### 2.3 Tiempos

| Supuesto | Especificación |
|---|---|
| **Horizonte de planificación** | Un día operativo (08:00–16:00) |
| **Tiempo de servicio — Centro de Salud** | 30 minutos (descarga, verificación, firma) |
| **Tiempo de servicio — Puesto de Salud** | 15 minutos |
| **Ventanas de tiempo — Cadena de frío** | 08:00–13:00 (5 horas efectivas) |
| **Ventanas de tiempo — Normal** | 08:00–16:00 (8 horas efectivas) |
| **Ventana depósito** | 08:00–16:00 |

### 2.4 Cadena de Frío

| Supuesto | Especificación |
|---|---|
| **Productos termosensibles** | Vacunas, insulinas, productos biológicos |
| **Rango de temperatura** | 2°C – 8°C |
| **Vehículos compatibles** | Solo Fiat Ducato refrigerada |
| **Restricción temporal** | Ventana de entrega reducida (08:00–13:00) |
| **Estado actual** | cold_chain_demand = 0 para todos los nodos (requiere análisis SISMED) |

### 2.5 Flota Vehicular

| Supuesto | Especificación |
|---|---|
| **Composición** | Heterogénea: 4 tipos de vehículos |
| **Disponibilidad** | Cada tipo tiene disponibilidad ilimitada (relajable en extensiones) |
| **Restricción de capacidad** | Cada vehículo tiene capacidad máxima en toneladas |
| **Restricción de autonomía** | Cada vehículo tiene autonomía máxima en kilómetros |
| **Costos** | Costo fijo por uso + costo variable por kilómetro |
| **Velocidad** | Velocidad promedio por tipo de vehículo |

---

## 3. Dataset Maestro Definitivo

### 3.1 Dataset de Nodos (`analytics/nodes_hvrptw.csv`)

81 establecimientos de salud activos filtrados desde `nodes_high_medium.csv` con geocodificación de confianza MEDIUM o HIGH.

**Columnas:**

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | string | Código único del establecimiento (= codigounico) |
| `ipress_code` | string | Código IPRESS (= codigounico) |
| `name` | string | Nombre del establecimiento |
| `latitude` | float | Latitud geocodificada |
| `longitude` | float | Longitud geocodificada |
| `categoria` | string | CENTRO DE SALUD / PUESTO DE SALUD / OTRO |
| `red` | string | Red de salud (vacío si no disponible en fuente) |
| `microred` | string | Micro-red de salud |
| `nivel_atencion` | string | Nivel de atención (I-1 a I-4, inferido de categoría) |
| `district` | string | Distrito |
| `province` | string | Provincia |
| `geocode_confidence` | string | Confianza de geocodificación (MEDIUM/HIGH) |
| `demand_mean` | float | Demanda media estimada (kg) |
| `demand_std` | float | Desviación estándar de demanda (kg) |
| `demand_cv` | float | Coeficiente de variación de demanda |
| `cold_chain_demand` | int | Demanda de cadena de frío (0/1) |
| `service_time` | int | Tiempo de servicio (minutos) |
| `tw_start` | string | Inicio de ventana de tiempo (HH:MM) |
| `tw_end` | string | Fin de ventana de tiempo (HH:MM) |
| `sanitary_priority` | int | Prioridad sanitaria (1-5) |

### 3.2 Dataset de Vehículos (`analytics/vehicles_hvrptw.csv`)

| vehicle_id | vehicle_name | capacity_ton | refrigeration | cold_chain_compatible | cost_per_km | fixed_cost | speed_kmh | autonomy_km |
|---|---|---|---|---|---|---|---|---|
| V1 | FUSO Canter 6T | 6.0 | No | No | 2.5 | 150 | 60 | 400 |
| V2 | Fiat Ducato Refrigerada | 3.0 | Yes | Yes | 3.0 | 200 | 50 | 350 |
| V3 | NLR 3.5 TON | 3.5 | No | No | 2.2 | 120 | 55 | 380 |
| V4 | Toyota Hilux | 1.0 | No | No | 1.8 | 80 | 70 | 500 |

### 3.3 Dataset de Arcos (`analytics/arcs_with_variability.csv`)

820 arcos OSRM con variabilidad estocástica agregada:

| Campo | Tipo | Descripción |
|---|---|---|
| `origin_id` | string | ID nodo origen |
| `destination_id` | string | ID nodo destino |
| `distance_km` | float | Distancia real OSRM (km) |
| `duration_min` | float | Duración OSRM (min) |
| `travel_time_mean` | float | Tiempo medio de viaje (= duration_min) |
| `travel_time_std` | float | Desviación estándar (= duration_min × 0.2) |
| `travel_time_cv` | float | Coeficiente de variación (0.2 inicial) |
| `road_risk` | int | Riesgo vial (1-5 según distancia) |
| `accessibility_score` | float | Score de accesibilidad (1.0 por defecto) |

### 3.4 Dataset de Ventanas de Tiempo (`analytics/time_windows.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | string | ID del nodo |
| `tw_start` | string | Hora de inicio (HH:MM) |
| `tw_end` | string | Hora de fin (HH:MM) |
| `tw_type` | string | COLD_CHAIN / NORMAL / DEPOT |

### 3.5 Dataset de Demanda Agregada (`analytics/demand_aggregated.csv`)

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | string | ID del nodo |
| `demand_mean` | float | Demanda media (kg) |
| `demand_std` | float | Desviación estándar (kg) |
| `demand_cv` | float | Coeficiente de variación |
| `cold_chain_demand` | int | Requiere cadena de frío (0/1) |

---

## 4. Formulación Matemática Two-Stage Stochastic HVRPTW

### 4.1 Conjuntos e Índices

| Símbolo | Definición |
|---|---|
| $\mathcal{N} = \{0, 1, \ldots, n\}$ | Conjunto de nodos: 0 = depósito, 1…n = clientes |
| $\mathcal{N}_c = \mathcal{N} \setminus \{0\}$ | Conjunto de clientes (81 establecimientos) |
| $\mathcal{K}$ | Conjunto de tipos de vehículos: {V1, V2, V3, V4} |
| $\mathcal{A} = \{(i,j) : i,j \in \mathcal{N}, i \neq j\}$ | Conjunto de arcos |
| $\Omega$ | Conjunto de escenarios estocásticos |
| $\omega \in \Omega$ | Escenario individual |

### 4.2 Parámetros Determinísticos

| Símbolo | Definición |
|---|---|
| $Q_k$ | Capacidad del vehículo tipo $k$ (toneladas) |
| $c_{ij}^k$ | Costo de traversar arco $(i,j)$ con vehículo tipo $k$ = $\text{cost\_per\_km}_k \times d_{ij}$ |
| $f_k$ | Costo fijo de usar vehículo tipo $k$ |
| $d_{ij}$ | Distancia del arco $(i,j)$ (km, OSRM) |
| $s_i$ | Tiempo de servicio en nodo $i$ (minutos) |
| $[e_i, l_i]$ | Ventana de tiempo del nodo $i$ |
| $R_k$ | Autonomía máxima del vehículo tipo $k$ (km) |
| $v_k$ | Velocidad promedio del vehículo tipo $k$ (km/h) |

### 4.3 Parámetros Estocásticos

| Símbolo | Definición |
|---|---|
| $\xi_i(\omega)$ | Demanda realizada del nodo $i$ en escenario $\omega$ |
| $\tau_{ij}(\omega)$ | Tiempo de viaje realizado del arco $(i,j)$ en escenario $\omega$ |
| $p(\omega)$ | Probabilidad del escenario $\omega$ |

### 4.4 Variables de Decisión

**Primera etapa (here-and-now):**

| Variable | Tipo | Definición |
|---|---|---|
| $x_{ij}^k \in \{0,1\}$ | Binaria | 1 si vehículo tipo $k$ atraviesa arco $(i,j)$ |
| $y_k \in \{0,1\}$ | Binaria | 1 si se usa al menos un vehículo tipo $k$ |

**Segunda etapa (wait-and-see):**

| Variable | Tipo | Definición |
|---|---|---|
| $u_i^k(\omega) \geq 0$ | Continua | Carga acumulada al llegar al nodo $i$ con vehículo $k$ en escenario $\omega$ |
| $t_i^k(\omega) \geq 0$ | Continua | Tiempo de llegada al nodo $i$ con vehículo $k$ en escenario $\omega$ |
| $w_i^k(\omega) \geq 0$ | Continua | Tiempo de espera en nodo $i$ en escenario $\omega$ |
| $r_i(\omega) \geq 0$ | Continua | Demanda no satisfecha (recourse) en nodo $i$ en escenario $\omega$ |

### 4.5 Formulación del Modelo

$$
\min \; Z = \underbrace{\sum_{k \in \mathcal{K}} f_k \cdot y_k + \sum_{k \in \mathcal{K}} \sum_{(i,j) \in \mathcal{A}} c_{ij}^k \cdot x_{ij}^k}_{\text{Costos primera etapa}} + \underbrace{\mathbb{E}_\omega \left[ \mathcal{Q}(\mathbf{x}, \omega) \right]}_{\text{Costos esperados segunda etapa}}
$$

Donde el costo de recurso de segunda etapa es:

$$
\mathcal{Q}(\mathbf{x}, \omega) = \sum_{i \in \mathcal{N}_c} \alpha \cdot r_i(\omega) + \sum_{i \in \mathcal{N}_c} \sum_{k \in \mathcal{K}} \beta \cdot \max(0, t_i^k(\omega) - l_i)
$$

Con $\alpha$ = penalización por demanda no servida, $\beta$ = penalización por violación de ventana de tiempo.

### 4.6 Restricciones

**Asignación y cobertura:**

$$
\sum_{k \in \mathcal{K}} \sum_{j \in \mathcal{N}} x_{ij}^k = 1 \quad \forall i \in \mathcal{N}_c \quad \text{(cada cliente visitado exactamente una vez)}
$$

**Conservación de flujo:**

$$
\sum_{i \in \mathcal{N}} x_{ij}^k = \sum_{i \in \mathcal{N}} x_{ji}^k \quad \forall j \in \mathcal{N}, \forall k \in \mathcal{K}
$$

**Origen/destino en depósito:**

$$
\sum_{j \in \mathcal{N}_c} x_{0j}^k \leq M \cdot y_k \quad \forall k \in \mathcal{K}
$$

$$
\sum_{j \in \mathcal{N}_c} x_{0j}^k = \sum_{j \in \mathcal{N}_c} x_{j0}^k \quad \forall k \in \mathcal{K}
$$

**Capacidad (segunda etapa, escenario $\omega$):**

$$
u_j^k(\omega) \geq u_i^k(\omega) + \xi_j(\omega) - Q_k(1 - x_{ij}^k) \quad \forall (i,j) \in \mathcal{A}, \forall k, \forall \omega
$$

$$
\xi_i(\omega) \leq u_i^k(\omega) \leq Q_k \quad \forall i \in \mathcal{N}_c, \forall k, \forall \omega
$$

**Ventanas de tiempo (segunda etapa, escenario $\omega$):**

$$
t_j^k(\omega) \geq t_i^k(\omega) + s_i + \tau_{ij}(\omega) - M(1 - x_{ij}^k) \quad \forall (i,j) \in \mathcal{A}, \forall k, \forall \omega
$$

$$
e_j \leq t_j^k(\omega) + w_j^k(\omega) \leq l_j \quad \forall j \in \mathcal{N}_c, \forall k, \forall \omega
$$

**Autonomía:**

$$
\sum_{(i,j) \in \mathcal{A}} d_{ij} \cdot x_{ij}^k \leq R_k \quad \forall k \in \mathcal{K}
$$

**Cadena de frío:**

$$
x_{ij}^k = 0 \quad \forall i \in \mathcal{N}_{cold}, \forall k \notin \mathcal{K}_{cold}, \forall j \in \mathcal{N}
$$

Donde $\mathcal{N}_{cold}$ = nodos con demanda de cadena de frío y $\mathcal{K}_{cold}$ = {V2} (vehículos refrigerados).

---

## 5. Incertidumbre Dual

### 5.1 Demanda Estocástica $\xi_i$

**Distribución:** Log-normal truncada

$$
\xi_i \sim \text{LogNormal}(\mu_i^{ln}, \sigma_i^{ln}) \quad \text{truncada en } [0, Q_{max}]
$$

Donde:
- $\mu_i^{ln} = \ln(\mu_i) - \frac{1}{2}\ln\left(1 + \frac{\sigma_i^2}{\mu_i^2}\right)$
- $\sigma_i^{ln} = \sqrt{\ln\left(1 + \frac{\sigma_i^2}{\mu_i^2}\right)}$

**Parámetros iniciales:**

| Categoría | $\mu_i$ (kg) | $\sigma_i$ (kg) | CV |
|---|---|---|---|
| Centro de Salud | 500 | 100 | 0.20 |
| Puesto de Salud | 200 | 50 | 0.25 |

**Actualización futura:** Los parámetros serán calibrados con datos históricos SISMED de consumo real.

### 5.2 Tiempos de Viaje Estocásticos $\tau_{ij}$

**Distribución:** Log-normal

$$
\tau_{ij} \sim \text{LogNormal}(\mu_{ij}^{ln}, \sigma_{ij}^{ln})
$$

Donde:
- $\mu_{ij}^{ln}$: calibrado desde `duration_min` OSRM
- $\sigma_{ij}^{ln}$: calibrado desde CV = 0.2 (valor inicial)

**Factores de variabilidad:**
- Distancia del arco (proxy de riesgo vial)
- Condiciones geográficas (sierra vs. costa)
- Estacionalidad (lluvias: diciembre–marzo)

### 5.3 Generación de Escenarios

Los escenarios $\omega \in \Omega$ se generan mediante muestreo Latin Hypercube Sampling (LHS) para representar combinaciones de demanda y tiempos de viaje:

$$
\omega = (\xi_1(\omega), \ldots, \xi_n(\omega), \tau_{ij}(\omega))_{\forall (i,j) \in \mathcal{A}}
$$

**Tamaño del ensemble:**
- Diseño experimental: |Ω| ∈ {100, 500, 1000, 5000}
- Validación: estabilidad de la solución vs. tamaño del ensemble

---

## 6. CVaR Optimization y Métricas de Riesgo

### 6.1 Formulación CVaR

El Conditional Value-at-Risk (CVaR) al nivel de confianza $\alpha$ cuantifica el costo esperado en los peores $(1-\alpha)$% escenarios:

$$
\text{CVaR}_\alpha(Z) = \min_{\eta \in \mathbb{R}} \left\{ \eta + \frac{1}{1-\alpha} \mathbb{E}\left[\max(Z(\omega) - \eta, 0)\right] \right\}
$$

### 6.2 Modelo Mean-CVaR

Combinamos minimización del costo esperado con control de riesgo:

$$
\min \; (1-\lambda) \cdot \mathbb{E}[Z(\omega)] + \lambda \cdot \text{CVaR}_\alpha(Z(\omega))
$$

Donde:
- $\lambda \in [0,1]$: peso de aversión al riesgo
- $\alpha \in \{0.90, 0.95, 0.99\}$: nivel de confianza CVaR

### 6.3 Linealización de CVaR

Introduciendo variable auxiliar $\eta$ y variables $z_\omega \geq 0$:

$$
\min \; (1-\lambda) \sum_{\omega} p(\omega) Z(\omega) + \lambda \left( \eta + \frac{1}{1-\alpha} \sum_{\omega} p(\omega) z_\omega \right)
$$

Sujeto a:

$$
z_\omega \geq Z(\omega) - \eta \quad \forall \omega \in \Omega
$$
$$
z_\omega \geq 0 \quad \forall \omega
$$

### 6.4 Métricas de Evaluación

| Métrica | Fórmula | Interpretación |
|---|---|---|
| **Expected cost** | $\mathbb{E}[Z(\omega)]$ | Costo promedio sobre todos los escenarios |
| **CVaR₉₅** | $\text{CVaR}_{0.95}(Z)$ | Costo esperado en el peor 5% |
| **VaR₉₅** | $\inf\{z : P(Z \leq z) \geq 0.95\}$ | Costo en percentil 95 |
| **VSS** | $Z_{EV} - Z_{SP}$ | Valor de la solución estocástica |
| **EVPI** | $Z_{SP} - Z_{WS}$ | Valor esperado de información perfecta |
| **Service level** | $1 - \frac{\sum r_i(\omega)}{\sum \xi_i(\omega)}$ | Fracción de demanda servida |
| **TW compliance** | Fracción de entregas dentro de ventana | Cumplimiento temporal |
| **Fleet utilization** | Uso efectivo vs. capacidad total | Eficiencia de flota |

---

## 7. Arquitectura Experimental Monte Carlo

### 7.1 Pipeline Experimental

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE EXPERIMENTAL                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. GENERACIÓN DE ESCENARIOS (Monte Carlo / LHS)                │
│     ├── Muestreo de demanda ξ_i ~ LogNormal(μ, σ)              │
│     ├── Muestreo de tiempos τ_ij ~ LogNormal(μ, σ)             │
│     └── Conjunto Ω = {ω_1, ..., ω_S}                           │
│                                                                  │
│  2. PRIMERA ETAPA: OPTIMIZACIÓN DE RUTAS                        │
│     ├── Selección de flota (y_k)                                │
│     ├── Asignación de rutas (x_ij^k)                            │
│     └── Minimización: costos fijos + variables + E[Q(x,ω)]     │
│                                                                  │
│  3. SEGUNDA ETAPA: EVALUACIÓN POR ESCENARIO                     │
│     ├── Simulación de demanda realizada                         │
│     ├── Simulación de tiempos de viaje realizados               │
│     ├── Cálculo de recourse (demanda no servida, retrasos)      │
│     └── Costo total por escenario Z(ω)                          │
│                                                                  │
│  4. MÉTRICAS DE RIESGO                                           │
│     ├── E[Z], Var[Z], CVaR_α                                   │
│     ├── VSS, EVPI                                                │
│     └── Service level, TW compliance                             │
│                                                                  │
│  5. ANÁLISIS DE SENSIBILIDAD                                     │
│     ├── Variación de λ (aversión al riesgo)                     │
│     ├── Variación de α (nivel de confianza CVaR)                │
│     ├── Variación de CV (demanda y tiempos)                     │
│     └── Variación de |Ω| (tamaño del ensemble)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Diseño Factorial

| Factor | Niveles | Valores |
|---|---|---|
| Tamaño ensemble $|\Omega|$ | 4 | {100, 500, 1000, 5000} |
| Nivel CVaR $\alpha$ | 3 | {0.90, 0.95, 0.99} |
| Peso de riesgo $\lambda$ | 5 | {0.0, 0.25, 0.50, 0.75, 1.0} |
| CV demanda | 3 | {0.10, 0.20, 0.30} |
| CV tiempos | 3 | {0.10, 0.20, 0.30} |
| **Total combinaciones** | | **540** |

### 7.3 Réplicas y Significancia Estadística

- **Réplicas independientes por configuración:** 30 (para intervalos de confianza al 95%)
- **Seeds aleatorias:** Fijadas para reproducibilidad
- **Test estadísticos:** Kruskal-Wallis para comparación no-paramétrica entre configuraciones
- **Total de ejecuciones:** 540 × 30 = 16,200

---

## 8. Algoritmo Simheuristic Recomendado

### 8.1 Justificación

El problema Two-Stage Stochastic HVRPTW con CVaR es NP-hard. Para instancias de tamaño real (81 nodos, 820 arcos, 4 tipos de vehículos), los solvers exactos no son prácticos. Se recomienda un enfoque **simheuristic** que integra simulación Monte Carlo dentro de una metaheurística.

### 8.2 Arquitectura del Algoritmo

```
ALGORITMO: SimHeuristic-HVRPTW-CVaR
────────────────────────────────────────────

ENTRADA: Datos del problema, parámetros algorítmicos
SALIDA:  Mejor solución robusta (rutas, flota, métricas)

1. INICIALIZACIÓN
   1.1  Generar solución inicial con heurística constructiva
        (Clarke-Wright savings adaptada para flota heterogénea)
   1.2  Generar ensemble de escenarios Ω mediante LHS

2. BUCLE PRINCIPAL (iteraciones = 1..MAX_ITER)
   2.1  FASE DETERMINÍSTICA:
        - Resolver HVRPTW determinístico con demanda/tiempo medio
        - Metaheurística: ALNS (Adaptive Large Neighborhood Search)
          · Operadores de destrucción: random, worst, Shaw, route
          · Operadores de reparación: greedy, regret-2, regret-3
          · Aceptación: Simulated Annealing
   
   2.2  FASE ESTOCÁSTICA (para top-K soluciones):
        - Para cada solución candidata:
          · Simular S escenarios de Ω
          · Evaluar: E[Z(ω)], CVaR_α(Z)
          · Calcular fitness: (1-λ)·E[Z] + λ·CVaR_α
   
   2.3  ACTUALIZACIÓN:
        - Actualizar mejor solución global
        - Ajustar pesos de operadores ALNS
        - Actualizar temperatura SA

3. INTENSIFICACIÓN FINAL
   3.1  Tomar las top-5 soluciones
   3.2  Re-evaluar con ensemble ampliado (5× más escenarios)
   3.3  Seleccionar solución final

4. RETORNO: Mejor solución + métricas completas
```

### 8.3 Parámetros Algorítmicos Sugeridos

| Parámetro | Valor sugerido | Notas |
|---|---|---|
| MAX_ITER | 10,000 | Iteraciones ALNS |
| Temperatura inicial SA | 100 | Calibrar con instancia |
| Cooling rate SA | 0.9997 | Enfriamiento lento |
| Top-K para simulación | 10 | Soluciones evaluadas estocásticamente |
| Escenarios rápidos $S_{fast}$ | 100 | Para evaluación rápida |
| Escenarios finales $S_{final}$ | 5,000 | Para evaluación final |
| Segmento ALNS | 100 | Para actualizar pesos operadores |
| Pesos iniciales operadores | Uniformes | Auto-adaptativos |

### 8.4 Heurística Constructiva Inicial

Adaptación de Clarke-Wright para flota heterogénea:

1. Crear rutas individuales depósito → cliente → depósito para cada nodo
2. Calcular savings: $s_{ij} = c_{0i} + c_{0j} - c_{ij}$
3. Ordenar savings descendente
4. Para cada par $(i,j)$ con saving positivo:
   - Verificar factibilidad: capacidad, autonomía, ventanas de tiempo, cadena de frío
   - Seleccionar vehículo más económico factible
   - Fusionar rutas si factible

---

## 9. Validación Empírica y Roadmap Experimental

### 9.1 Fases de Validación

| Fase | Descripción | Criterio de Éxito |
|---|---|---|
| **V1: Determinístico** | Resolver HVRPTW sin incertidumbre | Solución factible, costo base |
| **V2: Estocástico básico** | Two-stage con CV=0.1, |Ω|=100 | VSS > 0, solución estable |
| **V3: CVaR** | Agregar optimización CVaR | Frontera eficiente E[Z] vs CVaR |
| **V4: Calibración** | Datos SISMED reales | Mejora en service level |
| **V5: Escala completa** | |Ω|=5000, 30 réplicas | Resultados publicables |

### 9.2 Benchmarking

| Comparación | Método A | Método B | Métrica principal |
|---|---|---|---|
| Determinístico vs. Estocástico | EV (Expected Value) | SP (Stochastic Program) | VSS |
| Risk-neutral vs. Risk-averse | λ=0 | λ=0.5, λ=1.0 | CVaR₉₅ |
| Flota homogénea vs. heterogénea | Solo V1 | {V1,V2,V3,V4} | Costo total, feasibility |
| Sin/con cadena de frío | cold_chain=0 | cold_chain calibrado | Costo adicional refrigeración |

### 9.3 Roadmap

```
FASE 1 (Actual): Modelo y datos maestros
├── ✓ Formulación matemática completa
├── ✓ Datasets maestros consolidados
├── ✓ Arquitectura experimental definida
└── ✓ Documento central creado

FASE 2: Implementación determinística
├── Solver HVRPTW determinístico (Clarke-Wright + ALNS)
├── Validación con instancia DSRSLCC
└── Benchmark vs. solución manual actual

FASE 3: Integración estocástica
├── Generador de escenarios Monte Carlo / LHS
├── Evaluador de segunda etapa
├── Cálculo de VSS y EVPI
└── Implementación simheuristic

FASE 4: Optimización CVaR
├── Formulación Mean-CVaR
├── Frontera eficiente riesgo-costo
└── Análisis de sensibilidad completo

FASE 5: Calibración con datos reales
├── Integración datos SISMED
├── Calibración parámetros de demanda
├── Identificación nodos cadena de frío
└── Ajuste de CV tiempos por estacionalidad

FASE 6: Publicación y transferencia
├── Artículo científico
├── Herramienta de planificación para DSRSLCC
└── Manual de usuario
```

---

## 10. Separación Infraestructura vs. Modelo Científico

### Infraestructura (ya construida)

| Componente | Estado | Ubicación |
|---|---|---|
| ETL RENIPRESS | Completo | Scripts de scraping |
| Geocodificación Nominatim | Completo | `analytics/nodes_*.csv` |
| Ruteo OSRM | Completo | `analytics/arcs.csv` |
| Power BI reverse engineering | Completo | `analytics/powerbi_*` |
| Cache de geocodificación | Completo | `analytics/geocode_cache.json` |
| Cache OSRM | Completo | `analytics/osrm_cache.json` |

### Modelo Científico (a construir)

| Componente | Estado | Archivo |
|---|---|---|
| Formulación HVRPTW | **Documentado** | `docs/modelo_central_hvrptw.md` |
| Datasets maestros HVRPTW | **Consolidado** | `analytics/*_hvrptw.csv` |
| Dataset arcos con variabilidad | **Consolidado** | `analytics/arcs_with_variability.csv` |
| Dataset ventanas de tiempo | **Consolidado** | `analytics/time_windows.csv` |
| Dataset demanda agregada | **Consolidado** | `analytics/demand_aggregated.csv` |
| Solver determinístico | Pendiente | — |
| Generador de escenarios | Pendiente | — |
| SimHeuristic engine | Pendiente | — |
| CVaR optimizer | Pendiente | — |
| Framework experimental | Pendiente | — |

---

## Referencias Metodológicas

1. Birge, J.R. & Louveaux, F. (2011). *Introduction to Stochastic Programming*. Springer.
2. Rockafellar, R.T. & Uryasev, S. (2000). Optimization of Conditional Value-at-Risk. *Journal of Risk*, 2(3), 21–41.
3. Toth, P. & Vigo, D. (2014). *Vehicle Routing: Problems, Methods, and Applications*. SIAM.
4. Juan, A.A. et al. (2015). A review of simheuristics. *European Journal of Operational Research*, 246(3), 708–722.
5. Ropke, S. & Pisinger, D. (2006). An adaptive large neighborhood search heuristic for the pickup and delivery problem with time windows. *Transportation Science*, 40(4), 455–472.
6. Gendreau, M. et al. (2016). *Handbook of Metaheuristics*. Springer.
7. Oyola, J. et al. (2018). The stochastic vehicle routing problem: A literature review. *International Journal of Production Economics*, 199, 160–183.

---

*Documento generado como parte del proyecto de investigación operacional aplicada a la logística farmacéutica pública del sistema DSRSLCC, Región Piura, Perú.*
