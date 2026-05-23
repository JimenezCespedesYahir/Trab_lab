# Figuras y Tablas para Publicación — HVRPTW Estocástico DSRSLCC

## Convenciones

- **Resolución**: 300 DPI (PNG) + SVG vectorial
- **Estilo**: serif, gridlines sutiles (α=0.3), sin spines superiores/derecho
- **Colores**: paleta consistente (azul=#2980B9, verde=#27AE60, rojo=#C0392B, naranja=#E67E22, morado=#8E44AD)
- **Formato de captions**: APA 7ª edición adaptado

---

## Catálogo de Figuras

### Figura 1 (A1) — Red HVRPTW

**Caption**: Red logística HVRPTW de la DSRSLCC–Sullana compuesta por 81 IPRESS (26 Centros de Salud, 55 Puestos de Salud), 820 arcos bidireccionales con distancias OSRM reales, y 10 rutas baseline generadas por OR-Tools GLS. El depósito central (Almacén DSRSLCC) se ubica en Sullana (lat -4.9066, lon -80.7284). Los marcadores cuadrados representan Centros de Salud y los circulares Puestos de Salud.

**Archivo**: `A1_red_general_hvrptw.png` / `.svg`
**Uso**: Tesis Cap. 3 (Metodología), Paper Sec. II (Problem Description)

---

### Figura 2 (A2) — Asignación Vehicular

**Caption**: Asignación de rutas por tipo de vehículo en la solución baseline determinista. FUSO Canter 6T (azul): 1 ruta costera. NLR 3.5T (verde): 4 rutas mixtas. Toyota Hilux 1T (rojo): 5 rutas predominantemente de sierra. El solver determinista asigna el vehículo de menor costo/km (Hilux, S/ 1.5/km) a las rutas más extensas, induciendo sobreutilización (>95%) en los vehículos de menor capacidad.

**Archivo**: `A2_mapa_vehiculos.png` / `.svg`
**Uso**: Tesis Cap. 4 (Resultados), Paper Sec. IV (Results)

---

### Figura 3 (A4) — Fragilidad Operacional

**Caption**: Mapa de fragilidad operacional con rutas coloreadas según utilización de capacidad (escala RdYlGn inversa). Rutas con utilización >90% aparecen en tonos rojos con mayor grosor. Las 5 rutas asignadas a Toyota Hilux superan el 95% de utilización, indicando un slack de capacidad insuficiente (46 kg promedio) frente a la variabilidad de demanda (σ ≈ 420 kg).

**Archivo**: `A4_fragilidad_operacional.png` / `.svg`
**Uso**: Tesis Cap. 4, Paper Sec. IV (Key Finding)

---

### Figura 4 (B6) — Distribución de Costos

**Caption**: Distribución del costo total bajo 500 escenarios Monte Carlo con incertidumbre dual (demanda Normal truncada, CV=0.42/0.45; tiempos LogNormal, CV=0.2). La línea roja punteada indica el costo determinista (S/ 5,089), la verde el costo esperado (S/ 8,213, +61%), y la naranja el VaR al 5% (S/ 12,789). La distribución presenta asimetría positiva (skewness=0.88), justificando el uso de métricas de riesgo de cola como CVaR.

**Archivo**: `B6_distribucion_costos.png` / `.svg`
**Uso**: Tesis Cap. 4 (Principal), Paper Sec. IV (Fig. 1)

---

### Figura 5 (B7) — Convergencia Monte Carlo

**Caption**: Análisis de convergencia de la simulación Monte Carlo para n = {100, 500, 1000, 2000} escenarios. (a) Costo esperado con intervalo de confianza al 95%. (b) Ancho relativo del IC, que decrece de 10.2% (n=100) a 2.5% (n=2000). (c) Estabilidad del CVaR al 5%. (d) Route reliability. La convergencia se confirma a partir de n=1000 (IC relativo <4%), y el CVaR se estabiliza desde n=500.

**Archivo**: `B7_convergencia_montecarlo.png` / `.svg`
**Uso**: Tesis Cap. 4, Paper Sec. III (Experimental Setup)

---

### Figura 6 (B11) — Sensibilidad Cruzada

**Caption**: Heatmaps de sensibilidad cruzada para 12 combinaciones de CV de demanda (0.1–0.4) × CV de tiempo de viaje (0.1–0.3). (a) Costo esperado. (b) Route reliability. (c) Tasa de violación de capacidad. El costo crece casi exclusivamente con el CV de demanda (+48% entre CV=0.1 y CV=0.4), mientras el CV de tiempo tiene impacto marginal (<1%), confirmando la **dominancia de la incertidumbre de capacidad** sobre la temporal.

**Archivo**: `B11_heatmap_sensibilidad.png` / `.svg`
**Uso**: Tesis Cap. 4 (Fig. principal), Paper Sec. IV (Fig. 2)

---

### Figura 7 (B12) — Curvas VaR y CVaR

**Caption**: Value-at-Risk (VaR) y Conditional Value-at-Risk (CVaR) como función del nivel de riesgo α ∈ [1%, 50%]. Para α=5%: VaR = S/ 12,789, CVaR = S/ 14,149 (2.78× el costo determinista). La brecha CVaR–VaR de ~15–20% para α<10% evidencia la presencia de cola pesada en la distribución de costos, ratificando que análisis basados únicamente en el valor esperado subestiman significativamente el riesgo operacional.

**Archivo**: `B12_var_cvar_curvas.png` / `.svg`
**Uso**: Tesis Cap. 4, Paper Sec. IV

---

### Figura 8 (C13) — Ratio Slack/Variabilidad (FIGURA DIAGNÓSTICA CLAVE)

**Caption**: Ratio slack/variabilidad(1σ) para cada recurso del sistema HVRPTW. El umbral de fragilidad (ratio=1.0) separa recursos seguros (>1) de vulnerables (<1). El recurso temporal (ventana 8h) presenta ratio 4.38 (4σ de margen). Los vehículos FUSO y NLR mantienen ratios aceptables (1.6–1.9). El Toyota Hilux exhibe ratio **0.11** — indicando que su slack disponible (46 kg) equivale a solo 0.11 desviaciones estándar de la demanda (σ≈420 kg). Este ratio es 40× inferior al temporal, explicando cuantitativamente por qué la capacidad, y no el tiempo, domina el riesgo operacional del sistema.

**Archivo**: `C13_slack_variabilidad.png` / `.svg`
**Uso**: Tesis Cap. 4 (Fig. principal), Paper Sec. IV (Fig. 3 — Key Diagnostic)

---

### Figura 9 (C15) — Impacto de Eliminación de Hilux

**Caption**: Comparación de métricas de riesgo entre la configuración baseline (con Toyota Hilux) y dos alternativas de reemplazo: sustitución por NLR 3.5T y por FUSO Canter 6T. La eliminación de Hilux incrementa la route reliability de 6.5% a 95.5% (con NLR) y 98.0% (con FUSO), con incrementos de costo de apenas +6% y +14% respectivamente. La tasa de violación de capacidad se reduce de 93.5% a 3.5% (NLR) y 0.0% (FUSO), confirmando que la **composición de flota** — no la capacidad total — es el factor determinante de robustez operacional.

**Archivo**: `C15_con_sin_hilux.png` / `.svg`
**Uso**: Tesis Cap. 4, Paper Sec. IV (Fig. 4)

---

### Figura 10 (C16) — Matriz de Robustez

**Caption**: Frontera costo-robustez para 10 configuraciones experimentales de flota. El tamaño de cada punto es proporcional a la tasa de violación de capacidad. Las configuraciones sin Hilux (verde) dominan el cuadrante ideal (bajo costo, alta reliability), mientras el baseline con Hilux (rojo) presenta el peor perfil costo-riesgo. La adición de capacidad marginal (+10%, +20%) sin modificar composición tiene impacto limitado en reliability.

**Archivo**: `C16_matriz_robustez.png` / `.svg`
**Uso**: Tesis Cap. 4, Paper Sec. IV

---

### Figura 11 (C18) — Cadena Causal del Cuello de Botella

**Caption**: Descomposición del cuello de botella operacional. (a) Capacidad nominal por vehículo. (b) Costo por km. (c) Eficiencia costo/capacidad. (d) Diagrama causal: el solver determinista minimiza costo/km → asigna Hilux (S/ 1.5/km, más barato) → utilización >95% → slack insuficiente → variabilidad SISMED (CV=0.42) viola capacidad → reliability colapsa al 5.9%.

**Archivo**: `C18_cuello_botella.png` / `.svg`
**Uso**: Tesis Cap. 5 (Discusión), Paper Sec. V (Discussion)

---

### Figura 12 (D19) — Dashboard de KPIs

**Caption**: Panel resumen de indicadores clave de desempeño del sistema HVRPTW–DSRSLCC. Valores deterministas y estocásticos (2000 escenarios) presentados como tarjetas de métricas. El contraste entre cobertura perfecta (81/81 nodos) y route reliability de 5.9% constituye el hallazgo central: el sistema determinista garantiza servicio pero no robustez.

**Archivo**: `D19_kpi_dashboard.png` / `.svg`
**Uso**: Tesis Cap. 4, Presentación de sustentación (slide 3)

---

### Figura 13 (D20) — Diagrama Gantt

**Caption**: Cronograma de las 10 rutas baseline con segmentos de servicio (barras opacas) y tránsito (barras translúcidas), coloreados por tipo de vehículo. Todas las rutas operan dentro de la ventana [08:00, 16:00]. Las rutas más extensas (R1, R5, R7) utilizan ~7.5h de las 8h disponibles, con slack temporal de ~30 min.

**Archivo**: `D20_gantt_rutas.png` / `.svg`
**Uso**: Tesis Cap. 4

---

### Figura 14 (D21) — Carga vs Capacidad por Ruta

**Caption**: Comparación de carga asignada (coloreada por tipo de vehículo) versus capacidad nominal (gris) para cada ruta. Los porcentajes indican utilización. Las 5 rutas Hilux operan a >95%, mientras las rutas FUSO y NLR mantienen entre 42% y 73%.

**Archivo**: `D21_carga_por_ruta.png` / `.svg`
**Uso**: Tesis Cap. 4

---

## Catálogo de Tablas

### Tabla 1 — KPI Resumen Determinista vs Estocástico

**Caption**: Comparación de indicadores clave de desempeño entre la solución determinista baseline (OR-Tools GLS, 120s) y la evaluación estocástica Monte Carlo (2000 escenarios, semillas reproducibles). El gap de costo (+60.4%) y el colapso de reliability (100% → 5.9%) evidencian la insuficiencia del enfoque determinista para planificación logística farmacéutica bajo incertidumbre.

**Archivo**: `tabla_01_kpi_resumen.csv`

---

### Tabla 2 — Sensibilidad del Factor de Conversión

**Caption**: Análisis de sensibilidad del factor de conversión items→kg para 4 escenarios (5g, 10g, 20g, 50g por item). El hallazgo de dominancia de capacidad sobre tiempo es robusto: la tasa de violación de capacidad excede 45% en todos los escenarios, y la reliability nunca supera 55%.

**Archivo**: `tabla_02_sensibilidad_conversion.csv`

---

### Tabla 3 — Experimentos de Flota

**Caption**: Resultados de 10 configuraciones experimentales de flota evaluadas bajo 200 escenarios Monte Carlo cada una. Las configuraciones sin Hilux (+NLR y +FUSO) alcanzan reliability superior al 95% con incrementos de costo inferiores al 15%.

**Archivo**: `tabla_03_experimentos_flota.csv`

---

### Tabla 4 — Convergencia Monte Carlo

**Caption**: Métricas de convergencia de la simulación Monte Carlo. El intervalo de confianza al 95% relativo decrece de 10.2% (n=100) a 2.5% (n=2000), confirmando suficiencia muestral a partir de 1000 escenarios.

**Archivo**: `tabla_04_convergencia_mc.csv`

---

### Tabla 5 — Sensibilidad Cruzada CV Demanda × CV Tiempo

**Caption**: Resultados de 12 combinaciones de coeficientes de variación de demanda (0.1–0.4) y tiempo de viaje (0.1–0.3). El costo esperado crece +48% al incrementar CV demanda, pero <1% al incrementar CV tiempo.

**Archivo**: `tabla_05_sensibilidad_cruzada.csv`

---

### Tabla 6 — Detalle de Rutas Baseline

**Caption**: Descripción detallada de las 10 rutas baseline incluyendo vehículo asignado, capacidad, carga, utilización, distancia, número de paradas y slack disponible.

**Archivo**: `tabla_06_rutas_baseline.csv`

---

### Tabla 7 — Ratio Slack/Variabilidad

**Caption**: Diagnóstico cuantitativo de fragilidad por recurso. El ratio slack/variabilidad(1σ) clasifica cada recurso del sistema según su margen operacional. El Toyota Hilux presenta ratio 0.11 — indicando que su slack (46 kg) es insuficiente para absorber incluso 12% de la desviación estándar de demanda.

**Archivo**: `tabla_07_slack_variabilidad.csv`

---

## Figuras Recomendadas para Paper (8 máximo)

| # Paper | Código | Nombre | Justificación |
|---------|--------|--------|---------------|
| Fig. 1 | A1 | Red HVRPTW | Contexto geográfico |
| Fig. 2 | B6 | Distribución costos | Hallazgo: gap det-estoc |
| Fig. 3 | B7 | Convergencia MC | Validación metodológica |
| Fig. 4 | B11 | Heatmap sensibilidad | Evidencia: dominancia capacidad |
| Fig. 5 | C13 | Slack/variabilidad | **Hallazgo principal** |
| Fig. 6 | C15 | Con/Sin Hilux | Impacto operacional |
| Fig. 7 | C16 | Matriz robustez | Frontera costo-robustez |
| Fig. 8 | C18 | Cuello botella | Cadena causal |

## Figuras Recomendadas para Sustentación (5 slides)

| Slide | Código | Mensaje clave |
|-------|--------|---------------|
| 1 | A1 | "Red real de 81 IPRESS con datos OSRM" |
| 2 | B6 | "El determinista subestima 61% el costo real" |
| 3 | C13 | "El Hilux opera con ratio 0.11 — 40× peor que tiempo" |
| 4 | C15 | "Reemplazar Hilux: reliability de 6% a 98%" |
| 5 | D19 | "Dashboard: cobertura perfecta ≠ robustez" |

---

## Reproducción

```bash
cd /path/to/Trab_lab
python src/visualizaciones_cientificas_finales.py
```

Salida: `results/figures_final/` (48 archivos: 24 PNG + 24 SVG)
Tablas: `results/final_tables/` (7 CSV)
