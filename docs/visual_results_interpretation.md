# Interpretación de Resultados Visuales — HVRPTW Estocástico DSRSLCC

## Resumen

Este documento interpreta las 24 visualizaciones científicas del proyecto
*Fragilidad Operacional de Flota bajo Incertidumbre Dual en un HVRPTW Farmacéutico: Caso DSRSLCC–Sullana*.

Todas las figuras se generaron con `src/visualizaciones_cientificas_finales.py` (300 DPI, reproducible).

---

## A. MAPAS Y RED LOGÍSTICA

### Figura A1 — Red General HVRPTW

**Qué muestra**: 81 nodos IPRESS (Centros y Puestos de Salud), 820 arcos bidireccionales OSRM, 10 rutas baseline con depósito en Sullana.

**Por qué importa**: Verifica la cobertura geográfica completa del sistema. La red abarca desde la costa (Talara, Lobitos, Máncora) hasta la sierra (Ayabaca, Sapillica, Jililí), con distancias de 1–309 km al depósito.

**Interpretación**: El 100% de los nodos están conectados (grafo conexo verificado por BFS). Las rutas más largas corresponden a Hilux asignados a la sierra — paradójicamente, el vehículo con menor capacidad recorre las mayores distancias.

### Figura A2 — Mapa por Tipo de Vehículo

**Qué muestra**: Asignación geográfica de cada tipo de vehículo (FUSO azul, NLR verde, Hilux rojo).

**Por qué importa**: Evidencia la lógica del solver determinista: Hilux (S/ 1.5/km) se asigna a rutas lejanas para minimizar costo/km, mientras FUSO (S/ 2.5/km) cubre zonas más cercanas con mayor demanda.

**Interpretación**: El solver OR-Tools GLS prioriza costo sobre robustez. Los Hilux cubren 5 de 10 rutas con utilización >95%, lo que genera fragilidad sistémica.

### Figura A3 — Cadena de Frío

**Qué muestra**: Estado actual de la cadena de frío farmacéutica. Todos los nodos tienen `cold_chain_demand=0`.

**Por qué importa**: Documenta que la arquitectura está **preparada** pero no activa. Las 2 Fiat Ducato refrigeradas existen en la flota pero no se asignan a rutas frías porque la demanda cold-chain no ha sido calibrada con datos SISMED individuales.

**Interpretación**: Limitación conocida. La activación requiere clasificación SISMED de medicamentos termolábiles por IPRESS.

### Figura A4 — Fragilidad Operacional

**Qué muestra**: Rutas coloreadas por nivel de utilización de capacidad (verde=seguro, rojo=crítico). Grosor de línea proporcional al riesgo.

**Por qué importa**: Identifica visualmente las rutas que colapsan bajo incertidumbre. Las 5 rutas Hilux aparecen en rojo (>95% utilización), confirman el diagnóstico cuantitativo.

**Interpretación**: Las rutas 6–10 (Hilux) tienen un slack promedio de 46 kg contra una variabilidad de demanda de ~420 kg (1σ). Ratio slack/variabilidad = 0.11 — insuficiente para absorber incertidumbre.

### Figura A5 — Congestión y Tiempos

**Qué muestra**: Arcos coloreados por CV de tiempo de viaje, grosor proporcional a duración.

**Por qué importa**: Contrasta con los hallazgos Monte Carlo. Aunque la red tiene variabilidad de tiempos (CV=0.2 uniforme), el impacto en riesgo es marginal (<0.3% en costo) porque las ventanas de tiempo (8h) proveen slack suficiente (~3.5h de margen).

**Interpretación**: El tiempo NO es el factor dominante de riesgo en esta red. La variabilidad temporal está absorbida por ventanas generosas.

---

## B. VISUALIZACIONES MONTE CARLO

### Figura B6 — Distribución de Costos

**Qué muestra**: Histograma + KDE de costos bajo 500 escenarios estocásticos, con líneas de referencia para costo determinista, E[Costo] y VaR 5%.

**Por qué importa**: Evidencia la brecha determinista-estocástico (+61%). La distribución tiene skewness positiva (0.88), cola derecha pesada — justifica el uso de CVaR.

**Interpretación**: El costo determinista (S/ 5,089) subestima sistemáticamente el costo real operacional. El 95% de los escenarios exceden el costo determinista. La distribución no-Normal invalida análisis puramente basados en media y varianza.

### Figura B7 — Convergencia Monte Carlo

**Qué muestra**: Estabilidad de E[Costo], IC 95% relativo, CVaR y reliability para n=100, 500, 1000, 2000.

**Por qué importa**: Valida la suficiencia del tamaño muestral. El IC 95% relativo baja de 10.2% (n=100) a 2.5% (n=2000).

**Interpretación**: Convergencia confirmada para n≥1000 (IC <4%). El CVaR se estabiliza desde n=500. La simulación con 2000 escenarios es estadísticamente suficiente.

### Figura B8 — Distribución de Reliability

**Qué muestra**: Proporción de escenarios factibles (sin violaciones) vs infactibles, y distribución del número de violaciones.

**Por qué importa**: Solo el 6.2% de los escenarios cumplen todas las restricciones → reliability extremadamente baja.

**Interpretación**: La infactibilidad proviene predominantemente de violaciones de capacidad (93.5% de escenarios), no de tiempo (9.6%). Esto es consistente con el análisis slack/variabilidad.

### Figura B9 — Distribución de Violaciones de Capacidad

**Qué muestra**: Histograma del exceso de capacidad (kg) en escenarios con violación, y su CDF.

**Por qué importa**: Cuantifica la severidad de las violaciones, no solo su frecuencia.

**Interpretación**: El exceso medio es ~305 kg, mediana ~200 kg. El 95% de las violaciones exceden menos de 800 kg, lo que indica que buffers de capacidad moderados podrían mitigar gran parte del riesgo.

### Figura B10 — Boxplots de KPIs

**Qué muestra**: Distribución de costo, carga, utilización y violaciones bajo 500 escenarios.

**Por qué importa**: Visión compacta de la dispersión de todos los KPIs estocásticos.

**Interpretación**: El costo presenta outliers significativos (hasta S/ 17,809). La utilización varía poco (CV=5.3%), confirmando que el problema es de capacidad absoluta, no de distribución de carga.

### Figura B11 — Heatmap de Sensibilidad Cruzada

**Qué muestra**: Matrices de E[Costo], reliability y cap violations para 12 combinaciones de CV demanda (0.1–0.4) × CV tiempo (0.1–0.3).

**Por qué importa**: Demuestra que el costo crece casi exclusivamente con CV demanda. Las columnas (CV tiempo) son casi uniformes → confirma dominancia de capacidad.

**Interpretación**: Aumentar CV demanda de 0.1→0.4 incrementa costo +48%. Aumentar CV tiempo de 0.1→0.3 incrementa costo <1%. La evidencia es contundente: **capacidad domina sobre tiempo**.

### Figura B12 — Curvas VaR y CVaR

**Qué muestra**: VaR(α) y CVaR(α) para α ∈ [1%, 50%], con anotaciones en α=1%, 5%, 10%.

**Por qué importa**: Permite al tomador de decisiones seleccionar su nivel de aversión al riesgo y evaluar el costo correspondiente.

**Interpretación**: CVaR siempre excede VaR (como debe ser). La brecha CVaR-VaR es ~15-20% para α<10%, indicando cola pesada. Para α=5%: VaR=S/ 12,789, CVaR=S/ 14,149 — 2.5× el costo determinista.

---

## C. FRAGILIDAD DE FLOTA

### Figura C13 — Ratio Slack/Variabilidad (FIGURA CLAVE)

**Qué muestra**: Ratio slack/variabilidad(1σ) por recurso. Umbral de fragilidad = 1.0.

**Por qué importa**: Es el **diagnóstico principal** del trabajo. Explica cuantitativamente por qué la capacidad domina:
- Tiempo: ratio 4.38 (seguro, 4σ de margen)
- FUSO: ratio 1.87 (aceptable)
- NLR: ratio 1.71 (aceptable)
- Hilux: ratio **0.11** (crítico — 40× peor que tiempo)

**Interpretación**: El Hilux opera con menos de 0.12σ de margen. Cualquier desviación de demanda >12% del nominal viola capacidad. Esto no se detecta con análisis determinista.

### Figura C14 — Utilización por Vehículo

**Qué muestra**: Utilización de capacidad de cada ruta, con umbrales de 85% y 95%.

**Por qué importa**: Las 5 rutas Hilux superan el umbral crítico de 95%, mientras las rutas FUSO/NLR operan bajo 75%.

**Interpretación**: La optimización determinista de costo produce una distribución de utilización bimodal: vehículos grandes subutilizados y vehículos pequeños sobreutilizados.

### Figura C15 — Comparación Con/Sin Hilux

**Qué muestra**: 4 métricas comparando baseline (con Hilux) vs reemplazo por NLR y FUSO.

**Por qué importa**: Demuestra que eliminar Hilux y redistribuir a NLR/FUSO transforma reliability de 6.5% a 95.5%/98.0%.

**Interpretación**: El costo con NLR (+NLR, sin Hilux) es S/ 5,386 — solo 6% más que determinista, pero con 95.5% reliability. Esto sugiere que **la composición de flota es más importante que la capacidad total**.

### Figura C16 — Matriz de Robustez

**Qué muestra**: Scatter plot de E[Costo] vs Reliability para las 10 configuraciones experimentales. Tamaño proporcional a tasa de violación.

**Por qué importa**: Permite identificar visualmente la frontera costo-robustez y las configuraciones Pareto-óptimas.

**Interpretación**: Las configuraciones "sin Hilux" dominan (cuadrante superior-izquierdo: bajo costo + alta reliability). La adición de capacidad (+10%, +20%) sin cambiar composición tiene efecto limitado.

### Figura C17 — Violaciones por Tipo de Vehículo

**Qué muestra**: Slack determinista, utilización y número de rutas por tipo de vehículo.

**Por qué importa**: Descompone la fragilidad por tipo de vehículo, mostrando que el problema se concentra en Hilux.

**Interpretación**: FUSO tiene ~2,810 kg de slack, NLR ~1,200 kg, Hilux solo 46 kg. A pesar de tener el menor slack, Hilux tiene el mayor número de rutas asignadas (5 de 10).

### Figura C18 — Análisis de Cuello de Botella

**Qué muestra**: Comparación de capacidad, costo/km, eficiencia costo/capacidad, y diagrama causal de por qué el solver induce fragilidad.

**Por qué importa**: Formaliza la cadena causal completa: Solver minimiza costo/km → Hilux es barato → se sobreasigna → utilización >95% → sin slack → cualquier σ viola capacidad → reliability colapsa.

**Interpretación**: El Hilux tiene la mejor eficiencia costo/km (S/ 1.5/km) pero la peor eficiencia costo/capacidad. La optimización determinista no penaliza la fragilidad operacional.

---

## D. RESULTADOS HVRPTW

### Figura D19 — KPI Dashboard

**Qué muestra**: 8 KPIs principales en formato dashboard: costo determinista, E[Costo] MC, reliability, CVaR, rutas, nodos, distancia, utilización.

**Por qué importa**: Visión ejecutiva de todos los indicadores clave en una sola figura.

**Interpretación**: El contraste entre 100% cobertura/service-level y 5.9% reliability es el hallazgo central: el sistema sirve todos los nodos pero con alta probabilidad de violación.

### Figura D20 — Gantt de Rutas

**Qué muestra**: Cronograma de cada ruta con segmentos de servicio (opaco) y tránsito (translúcido).

**Por qué importa**: Verifica que todas las rutas operan dentro de la ventana 08:00–16:00 en el escenario determinista.

**Interpretación**: Las rutas 1, 5 y 7 son las más largas (~7.5h). Todas las rutas completan antes de las 16:00, confirmando que el tiempo no es restricción activa en el baseline.

### Figura D21 — Carga por Ruta

**Qué muestra**: Carga asignada vs capacidad por ruta, con % de utilización.

**Por qué importa**: Visualiza la disparidad entre vehículos grandes (FUSO: 53% util) y pequeños (Hilux: 95%+ util).

**Interpretación**: Las rutas Hilux están al límite. Las rutas FUSO/NLR tienen capacidad ociosa significativa. Una reasignación reduciría riesgo sin costo adicional significativo.

### Figura D22 — Distancia por Vehículo

**Qué muestra**: Distancia recorrida por cada ruta, coloreada por tipo de vehículo.

**Por qué importa**: Los Hilux recorren en promedio más distancia que los FUSO — el solver los asigna a rutas lejanas por su bajo costo/km.

**Interpretación**: Ruta 7 (Hilux, 309 km) y Ruta 10 (Hilux, 296 km) son las más largas. Esto expone las rutas más alejadas al vehículo más frágil.

### Figura D23 — Tiempo por Ruta

**Qué muestra**: Descomposición del tiempo total por ruta en servicio y tránsito.

**Por qué importa**: Confirma que ninguna ruta excede la ventana de 8 horas.

**Interpretación**: El ratio tránsito/servicio varía: rutas de sierra tienen más tránsito, rutas costeras más servicio. El slack temporal promedio es ~3.5h.

### Figura D24 — Utilización Espacial

**Qué muestra**: (a) Distribución geográfica de demanda (heatmap), (b) asignación de vehículos.

**Por qué importa**: Relaciona la geografía de demanda con la decisión de asignación del solver.

**Interpretación**: Los Centros de Salud (demanda alta, 318 kg) están distribuidos en toda la red. El solver no considera la distribución espacial de riesgo al asignar vehículos.

---

## Tablas Complementarias

| Tabla | Archivo | Contenido |
|-------|---------|-----------|
| 1 | `tabla_01_kpi_resumen.csv` | KPIs determinista vs estocástico |
| 2 | `tabla_02_sensibilidad_conversion.csv` | Sensibilidad del factor item→kg |
| 3 | `tabla_03_experimentos_flota.csv` | 10 configuraciones de flota |
| 4 | `tabla_04_convergencia_mc.csv` | Convergencia MC (100–2000) |
| 5 | `tabla_05_sensibilidad_cruzada.csv` | CV demanda × CV tiempo |
| 6 | `tabla_06_rutas_baseline.csv` | Detalle de rutas baseline |
| 7 | `tabla_07_slack_variabilidad.csv` | Ratio slack/variabilidad por recurso |

---

## Trazabilidad

```
analytics/nodes_hvrptw.csv        → Figuras A1–A5, D24
analytics/arcs_with_variability.csv → Figuras A1, A5
analytics/vehicles_hvrptw.csv     → Figuras C17, C18
results/baseline_routes.csv       → Figuras A1–A4, C14, D20–D24
results/montecarlo_results_500.csv → Figuras B6, B8–B10, B12
results/convergence_analysis.csv  → Figura B7
results/sensitivity_analysis.csv  → Figura B11
results/sensitivity_conversion_factor.csv → Tabla 2
results/capacity_experiments.csv  → Figuras C15, C16, Tabla 3
```

Script: `src/visualizaciones_cientificas_finales.py`
Reproducción: `python src/visualizaciones_cientificas_finales.py`
