# Índice Maestro de Figuras Científicas — HVRPTW Estocástico DSRSLCC

## Metadatos del Proyecto

| Campo | Valor |
|-------|-------|
| Proyecto | Fragilidad Operacional de Flota bajo Incertidumbre Dual en HVRPTW Farmacéutico |
| Caso | DSRSLCC–Sullana, Piura, Perú |
| Figuras totales | 24 (48 archivos: PNG 300 DPI + SVG vectorial) |
| Tablas totales | 7 CSV publicables |
| Script | `src/visualizaciones_cientificas_finales.py` |
| Carpeta | `results/figures_final/` |

---

## Catálogo Completo de Figuras

### A. MAPAS Y RED LOGÍSTICA

---

#### Figura A1 — Red General HVRPTW

| Campo | Detalle |
|-------|---------|
| **Archivo** | `A1_red_general_hvrptw.png` / `.svg` |
| **Descripción** | Red logística completa: 81 IPRESS, 820 arcos bidireccionales OSRM, 10 rutas baseline, depósito central Sullana |
| **Interpretación técnica** | Verifica cobertura total (100% nodos alcanzables). Red dispersa costa-sierra con distancias 1–309 km. El grafo es conexo (verificado BFS). |
| **Interpretación operacional** | La red abarca desde Talara/Máncora (costa norte) hasta Ayabaca/Jililí (sierra). Las rutas más extensas se asignan paradójicamente al vehículo más pequeño (Hilux). |
| **Implicancia metodológica** | Valida que el modelo HVRPTW opera sobre datos geoespaciales reales (coordenadas Nominatim + distancias OSRM), no sobre instancias sintéticas. |
| **Hallazgo asociado** | La dispersión geográfica no es uniforme: concentración costera vs dispersión serrana, lo que influye en la asignación del solver. |
| **Mensaje científico** | "El sistema logístico farmacéutico de la DSRSLCC opera sobre una red real de 81 IPRESS con heterogeneidad geográfica significativa." |
| **Sección sugerida** | Metodología (Cap. 3), Paper Sec. II |
| **Impacto científico** | ★★★☆☆ — Contextual, necesario pero no diferenciador |

---

#### Figura A2 — Asignación por Tipo de Vehículo

| Campo | Detalle |
|-------|---------|
| **Archivo** | `A2_mapa_vehiculos.png` / `.svg` |
| **Descripción** | Rutas coloreadas por tipo de vehículo: FUSO (azul), NLR (verde), Hilux (rojo) |
| **Interpretación técnica** | El solver determinista asigna Hilux a 5 de 10 rutas, predominantemente las de mayor extensión geográfica, por su menor costo/km (S/ 1.5). |
| **Interpretación operacional** | La minimización de costo induce una asignación que concentra el vehículo más frágil en las rutas más críticas (largas, remotas, con menor posibilidad de reabastecimiento). |
| **Implicancia metodológica** | Evidencia visual del sesgo del solver determinista: optimiza costo inmediato sin considerar robustez operacional. |
| **Hallazgo asociado** | La asignación determinista es contraintuitiva: el vehículo más barato pero más frágil cubre la mayor proporción de la red. |
| **Mensaje científico** | "La optimización determinista de costo asigna el vehículo de menor capacidad a las rutas más extensas, generando fragilidad sistémica." |
| **Sección sugerida** | Resultados (Cap. 4), Paper Sec. IV |
| **Impacto científico** | ★★★★☆ — Ilustra visualmente el hallazgo central |

---

#### Figura A3 — Cadena de Frío Farmacéutica

| Campo | Detalle |
|-------|---------|
| **Archivo** | `A3_cadena_frio.png` / `.svg` |
| **Descripción** | Estado de la cadena de frío: todos los nodos con cold_chain_demand=0, arquitectura preparada con Fiat Ducato refrigerada |
| **Interpretación técnica** | La infraestructura de cold-chain existe (2 Ducato refrigeradas) pero no está activa por falta de clasificación SISMED de medicamentos termolábiles. |
| **Interpretación operacional** | Limitación operacional reconocida: la activación requiere datos SISMED individuales por IPRESS. No se inventó demanda fría. |
| **Implicancia metodológica** | Demuestra honestidad metodológica: se documentó la limitación en lugar de fabricar datos. |
| **Hallazgo asociado** | La cadena de frío es una extensión natural del modelo, pendiente de datos reales. |
| **Mensaje científico** | "La arquitectura de cold-chain está implementada pero requiere calibración SISMED para activación." |
| **Sección sugerida** | Limitaciones (Cap. 6), Trabajo futuro |
| **Impacto científico** | ★★☆☆☆ — Documenta limitación, menor impacto visual |

---

#### Figura A4 — Fragilidad Operacional

| Campo | Detalle |
|-------|---------|
| **Archivo** | `A4_fragilidad_operacional.png` / `.svg` |
| **Descripción** | Rutas coloreadas por utilización de capacidad (RdYlGn inverso). Grosor proporcional al riesgo. |
| **Interpretación técnica** | Las 5 rutas Hilux aparecen en rojo (>95% utilización), con grosor máximo. Las rutas FUSO/NLR en verde-amarillo (42–73%). |
| **Interpretación operacional** | Identifica geográficamente las zonas de vulnerabilidad: toda la subred asignada a Hilux está en riesgo de violación bajo incertidumbre. |
| **Implicancia metodológica** | Conecta la métrica cuantitativa (ratio slack/variabilidad) con la representación geoespacial. Permite al gestor logístico identificar rutas críticas en el mapa. |
| **Hallazgo asociado** | La fragilidad se concentra geográficamente en las rutas de sierra y costa norte — las más alejadas del depósito. |
| **Mensaje científico** | "La fragilidad operacional tiene patrón geográfico: las rutas más remotas son las más vulnerables." |
| **Sección sugerida** | Resultados (Cap. 4), Discusión (Cap. 5) |
| **Impacto científico** | ★★★★☆ — Alta relevancia para gestión operacional |

---

#### Figura A5 — Congestión y Variabilidad Temporal

| Campo | Detalle |
|-------|---------|
| **Archivo** | `A5_congestion_tiempos.png` / `.svg` |
| **Descripción** | Arcos coloreados por CV de tiempo de viaje, grosor proporcional a duración |
| **Interpretación técnica** | CV temporal uniforme (0.2) en toda la red — las distancias OSRM son el factor de diferenciación, no la variabilidad. |
| **Interpretación operacional** | Contrasta con el hallazgo principal: aunque existe variabilidad temporal, las ventanas de 8h absorben el riesgo. El tiempo NO es la restricción activa. |
| **Implicancia metodológica** | Evidencia visual que complementa el análisis de sensibilidad: CV tiempo tiene impacto <1% en costo. |
| **Hallazgo asociado** | El ratio slack/variabilidad temporal (4.38) es 40× superior al de capacidad Hilux (0.11). |
| **Mensaje científico** | "La variabilidad temporal es absorbida por las ventanas generosas — no es el factor de riesgo dominante." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Importante como contraste, pero no es hallazgo central |

---

### B. VISUALIZACIONES MONTE CARLO

---

#### Figura B6 — Distribución de Costos Determinista vs Estocástico

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B6_distribucion_costos.png` / `.svg` |
| **Descripción** | Histograma + KDE de 500 escenarios MC con líneas de referencia: determinista (S/ 5,089), E[Costo] (S/ 8,213), VaR 5% (S/ 12,789) |
| **Interpretación técnica** | Distribución unimodal con skewness=0.88, cola derecha pesada. El 95% de escenarios excede el costo determinista. Distribución no-Normal (rechazada por Shapiro-Wilk, p<0.001). |
| **Interpretación operacional** | El planificador que usa el costo determinista subestima el costo real en 61% en promedio, y hasta 250% en el peor caso. La penalización por violaciones domina la cola derecha. |
| **Implicancia metodológica** | Justifica el uso de CVaR sobre E[Costo] para toma de decisiones risk-averse. La no-Normalidad invalida análisis paramétricos simples. |
| **Hallazgo asociado** | Gap determinista-estocástico +61% — hallazgo principal cuantitativo. |
| **Mensaje científico** | "La evaluación determinista subestima sistemáticamente el costo operacional real; la distribución asimétrica justifica métricas de riesgo de cola." |
| **Sección sugerida** | Resultados (Cap. 4), Paper Sec. IV (Fig. principal) |
| **Impacto científico** | ★★★★★ — Evidencia central del gap determinista-estocástico |

---

#### Figura B7 — Convergencia Monte Carlo

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B7_convergencia_montecarlo.png` / `.svg` |
| **Descripción** | 4 paneles: E[Costo] con IC 95%, IC relativo, CVaR 5%, reliability para n=100,500,1000,2000 |
| **Interpretación técnica** | IC 95% relativo: 10.2% (n=100) → 5.0% (n=500) → 3.6% (n=1000) → 2.5% (n=2000). Convergencia confirmada ≥1000. CVaR estable desde n=500. |
| **Interpretación operacional** | 2000 escenarios son suficientes para decisiones operacionales. La estabilidad del CVaR indica que las métricas de riesgo son confiables. |
| **Implicancia metodológica** | Validación estadística obligatoria para simulación Monte Carlo. Demuestra suficiencia muestral y reproduce el estándar de OR experimental. |
| **Hallazgo asociado** | Convergencia con n=1000+ (IC <4%), CVaR estable desde n=500. |
| **Mensaje científico** | "La simulación Monte Carlo converge a partir de 1000 escenarios, con IC 95% relativo inferior al 4%." |
| **Sección sugerida** | Metodología/Resultados (Cap. 3–4), Paper Sec. III |
| **Impacto científico** | ★★★★☆ — Validación metodológica esencial |

---

#### Figura B8 — Distribución de Reliability

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B8_distribucion_reliability.png` / `.svg` |
| **Descripción** | Pie chart de factibilidad (6.2% factible vs 93.8% infactible) + histograma de violaciones |
| **Interpretación técnica** | Solo 31 de 500 escenarios son completamente factibles. Las violaciones de capacidad dominan (media 2.16/escenario) sobre TW (media 0.086). |
| **Interpretación operacional** | La solución determinista "funciona" solo en el 6.2% de las realizaciones de demanda. En operación real, 9 de cada 10 días habrá al menos una violación. |
| **Implicancia metodológica** | Reliability <10% es un indicador de fragilidad estructural, no de variabilidad aleatoria. Justifica intervención en composición de flota. |
| **Hallazgo asociado** | Route reliability 5.9–6.5% bajo calibración SISMED. |
| **Mensaje científico** | "La solución determinista falla en el 94% de los escenarios estocásticos." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★★☆ — Evidencia impactante del colapso de reliability |

---

#### Figura B9 — Distribución de Violaciones de Capacidad

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B9_violaciones_capacidad.png` / `.svg` |
| **Descripción** | Histograma de exceso de capacidad (kg) en escenarios con violación + CDF acumulativa |
| **Interpretación técnica** | Exceso medio: ~305 kg, mediana ~200 kg. El 80% de violaciones exceden <500 kg. CDF muestra concentración en excesos moderados. |
| **Interpretación operacional** | Las violaciones no son catastróficas en magnitud — un buffer de 500 kg eliminaría ~80% de las violaciones. Pero en vehículos de 1 ton, 305 kg representa el 30% de la capacidad. |
| **Implicancia metodológica** | La severidad de violaciones es tan relevante como su frecuencia. La CDF permite dimensionar buffers de capacidad. |
| **Hallazgo asociado** | Buffer 75% (cap utilizable = 75%) reduce violaciones de 93.5% a 55.5%. |
| **Mensaje científico** | "Las violaciones son frecuentes pero de magnitud moderada — mitigables con buffers o reasignación vehicular." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Complementaria a B8 |

---

#### Figura B10 — Boxplots de KPIs Estocásticos

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B10_boxplots_kpis.png` / `.svg` |
| **Descripción** | 4 boxplots: costo total, carga total, utilización promedio, violaciones de capacidad |
| **Interpretación técnica** | Costo: mediana S/ 7,839, Q3 S/ 9,419, outliers hasta S/ 17,809. Utilización: baja varianza (CV=5.3%). Carga: centrada en 16,169 kg nominal. |
| **Interpretación operacional** | La baja varianza de utilización confirma que el problema es de capacidad absoluta (Hilux al límite), no de distribución de carga entre rutas. |
| **Implicancia metodológica** | Visión sintética de la dispersión de KPIs. Útil para comparación con otros sistemas de distribución farmacéutica. |
| **Hallazgo asociado** | CV de costo (29%) >> CV de utilización (5.3%) — la variabilidad se amplifica en el costo vía penalizaciones. |
| **Mensaje científico** | "La variabilidad de demanda se amplifica desproporcionadamente en el costo total por efecto de penalizaciones." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Síntesis útil pero no diferenciadora |

---

#### Figura B11 — Heatmap de Sensibilidad Cruzada

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B11_heatmap_sensibilidad.png` / `.svg` |
| **Descripción** | 3 heatmaps: E[Costo], reliability, cap violations para 12 combinaciones CV demanda (0.1–0.4) × CV tiempo (0.1–0.3) |
| **Interpretación técnica** | Las filas (CV demanda) muestran gradiente fuerte: costo +48% entre CV=0.1 y CV=0.4. Las columnas (CV tiempo) son casi uniformes: <1% de variación. |
| **Interpretación operacional** | El gestor logístico debe priorizar la reducción de incertidumbre de demanda (mejores pronósticos SISMED) sobre mejoras viales. |
| **Implicancia metodológica** | **Evidencia definitiva de dominancia**: la incertidumbre de capacidad domina sobre la temporal. Esto no se observaría sin análisis de sensibilidad cruzada. |
| **Hallazgo asociado** | Capacidad domina sobre tiempo — hallazgo central robusto. |
| **Mensaje científico** | "La incertidumbre de demanda explica >95% de la variabilidad del sistema; la incertidumbre temporal es estadísticamente marginal." |
| **Sección sugerida** | Resultados (Cap. 4), Paper Sec. IV (Fig. principal) |
| **Impacto científico** | ★★★★★ — Evidencia definitiva de dominancia |

---

#### Figura B12 — Curvas VaR y CVaR

| Campo | Detalle |
|-------|---------|
| **Archivo** | `B12_var_cvar_curvas.png` / `.svg` |
| **Descripción** | VaR(α) y CVaR(α) para α ∈ [1%, 50%], con anotaciones en α=1%, 5%, 10% |
| **Interpretación técnica** | Para α=5%: VaR=S/ 12,789, CVaR=S/ 14,149 (2.78× determinista). Brecha CVaR-VaR ~15–20% para α<10% indica cola pesada. |
| **Interpretación operacional** | Un gestor risk-averse (α=5%) debe presupuestar S/ 14,149/mes — no S/ 5,089 — para absorber riesgo. |
| **Implicancia metodológica** | Herramienta de decisión bajo aversión al riesgo. La forma de las curvas justifica el uso de CVaR como métrica robusta. |
| **Hallazgo asociado** | CVaR 5% = S/ 14,149 — 2.78× el costo determinista. |
| **Mensaje científico** | "El CVaR como métrica de riesgo de cola captura hasta 2.8× el costo determinista, evidenciando riesgo no detectable con análisis de valor esperado." |
| **Sección sugerida** | Resultados (Cap. 4), Paper Sec. IV |
| **Impacto científico** | ★★★★☆ — Relevante para decisiones bajo riesgo |

---

### C. FRAGILIDAD DE FLOTA

---

#### Figura C13 — Ratio Slack/Variabilidad (FIGURA CENTRAL)

| Campo | Detalle |
|-------|---------|
| **Archivo** | `C13_slack_variabilidad.png` / `.svg` |
| **Descripción** | 2 paneles: (a) barras de ratio slack/variabilidad(1σ) por recurso con umbral de fragilidad, (b) descomposición slack vs variabilidad |
| **Interpretación técnica** | Tiempo: ratio 4.38 (4σ de margen → seguro). FUSO: 1.87 (aceptable). NLR: 1.71 (aceptable). Ducato: 1.23 (marginal). **Hilux: 0.11** (crítico — 0.11σ de margen). |
| **Interpretación operacional** | El Hilux opera con 46 kg de slack contra 420 kg de variabilidad (1σ). Cualquier desviación de demanda >12% del nominal viola capacidad. Esto genera 93.5% de escenarios con violación. |
| **Implicancia metodológica** | **Contribución metodológica original**: el ratio slack/variabilidad como métrica diagnóstica unificada permite comparar dimensiones heterogéneas (tiempo vs capacidad) en una escala común. Es la métrica que explica cuantitativamente por qué capacidad domina sobre tiempo. |
| **Hallazgo asociado** | Hilux ratio = 0.11 (40× peor que tiempo) — explica la dominancia de capacidad. |
| **Mensaje científico** | "El ratio slack/variabilidad revela que el Toyota Hilux opera 40 veces más cerca de su límite que el sistema temporal, constituyendo el cuello de botella estructural del sistema." |
| **Sección sugerida** | Resultados/Discusión (Cap. 4–5), Paper Sec. IV (Fig. CENTRAL) |
| **Impacto científico** | ★★★★★ — **FIGURA CENTRAL DE LA INVESTIGACIÓN** |

---

#### Figura C14 — Utilización por Vehículo

| Campo | Detalle |
|-------|---------|
| **Archivo** | `C14_utilizacion_vehiculos.png` / `.svg` |
| **Descripción** | Barras horizontales de utilización por ruta, con umbrales 85% y 95% |
| **Interpretación técnica** | Distribución bimodal: Hilux 95.4–96.4%, NLR 42.4–72.7%, FUSO 53.2%. Las 5 rutas Hilux superan el umbral crítico. |
| **Interpretación operacional** | La asignación del solver produce vehículos grandes subutilizados junto a vehículos pequeños sobreutilizados — ineficiencia de robustez. |
| **Implicancia metodológica** | Complementa C13 con datos por ruta individual. Permite identificar qué rutas específicas necesitan intervención. |
| **Hallazgo asociado** | Utilización bimodal: 95%+ (Hilux) vs <73% (resto). |
| **Mensaje científico** | "La utilización determinista muestra un patrón bimodal: vehículos grandes ociosos junto a vehículos pequeños saturados." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Detalle de soporte |

---

#### Figura C15 — Comparación Con/Sin Hilux

| Campo | Detalle |
|-------|---------|
| **Archivo** | `C15_con_sin_hilux.png` / `.svg` |
| **Descripción** | 4 paneles: E[Costo], reliability, cap violations, CVaR para baseline vs -Hilux+NLR vs -Hilux+FUSO |
| **Interpretación técnica** | Baseline: reliability 6.5%, cap viol 93.5%. Sin Hilux +NLR: reliability 95.5%, cap viol 3.5%, costo +6%. Sin Hilux +FUSO: reliability 98.0%, cap viol 0%, costo +14%. |
| **Interpretación operacional** | **Recomendación operacional concreta**: reemplazar Hilux por NLR o FUSO elimina virtualmente la fragilidad con incremento de costo marginal. El ROI de robustez es extremadamente favorable. |
| **Implicancia metodológica** | Demuestra que la composición de flota importa más que la capacidad total. La flota actual tiene 50 ton vs 16 ton de demanda — el problema no es cantidad sino distribución. |
| **Hallazgo asociado** | Reemplazo de Hilux: reliability 6.5% → 95.5–98.0%. |
| **Mensaje científico** | "La composición de flota — no la capacidad total — determina la robustez operacional del sistema." |
| **Sección sugerida** | Resultados/Discusión (Cap. 4–5), Paper Sec. IV |
| **Impacto científico** | ★★★★★ — Evidencia directa de la recomendación operacional |

---

#### Figura C16 — Matriz de Robustez Operacional

| Campo | Detalle |
|-------|---------|
| **Archivo** | `C16_matriz_robustez.png` / `.svg` |
| **Descripción** | Scatter: E[Costo] vs reliability para 10 configuraciones, tamaño ∝ cap violations |
| **Interpretación técnica** | Las configuraciones sin Hilux dominan (cuadrante superior-izquierdo). La adición marginal de capacidad (+10%, +20%) sin cambiar composición tiene efecto limitado (<15% mejora en reliability). |
| **Interpretación operacional** | La frontera Pareto costo-robustez muestra que hay configuraciones estrictamente dominantes. El baseline está en el cuadrante peor (alto costo ajustado, baja reliability). |
| **Implicancia metodológica** | Análisis multi-criterio típico de OR. Permite al decisor visualizar tradeoffs costo-riesgo y seleccionar configuración según su perfil de riesgo. |
| **Hallazgo asociado** | Las configuraciones sin Hilux son Pareto-dominantes. |
| **Mensaje científico** | "Existen configuraciones de flota estrictamente dominantes que mejoran simultáneamente costo esperado y reliability." |
| **Sección sugerida** | Resultados/Discusión (Cap. 4–5), Paper Sec. IV |
| **Impacto científico** | ★★★★☆ — Síntesis visual de experimentos |

---

#### Figura C17 — Violaciones por Tipo de Vehículo

| Campo | Detalle |
|-------|---------|
| **Archivo** | `C17_violaciones_por_vehiculo.png` / `.svg` |
| **Descripción** | 3 paneles: slack determinista, utilización, rutas asignadas por tipo de vehículo |
| **Interpretación técnica** | FUSO: slack 2,810 kg. NLR: slack ~956–1,656 kg. Hilux: slack 46 kg. A pesar del menor slack, Hilux tiene 5 de 10 rutas. |
| **Interpretación operacional** | Desproporción entre slack y carga de trabajo: el vehículo más frágil tiene la mayor carga operacional (50% de rutas). |
| **Implicancia metodológica** | Descomposición por tipo que complementa el análisis agregado. Útil para informe técnico a gestores de flota. |
| **Hallazgo asociado** | Hilux: 50% de rutas, 5% de slack — desbalance estructural. |
| **Mensaje científico** | "El vehículo con menor margen operacional absorbe la mayor carga de rutas por la minimización de costo." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Detalle de soporte |

---

#### Figura C18 — Análisis de Cuello de Botella

| Campo | Detalle |
|-------|---------|
| **Archivo** | `C18_cuello_botella.png` / `.svg` |
| **Descripción** | 4 paneles: capacidad, costo/km, eficiencia costo/capacidad, diagrama causal completo |
| **Interpretación técnica** | Hilux: mejor costo/km (S/ 1.5) pero peor eficiencia costo/capacidad. El diagrama causal formaliza: solver minimiza costo/km → sobreasigna Hilux → utilización >95% → sin slack → CV SISMED viola capacidad → reliability colapsa. |
| **Interpretación operacional** | Explica POR QUÉ el solver hace lo que hace. La minimización de costo no es un error — es racional en el contexto determinista. El error es usar una solución determinista en un entorno estocástico. |
| **Implicancia metodológica** | Formaliza la cadena causal completa, conectando el comportamiento del solver con el colapso de reliability. Es la base argumentativa de la discusión científica. |
| **Hallazgo asociado** | Cadena causal: minimización costo → sobreasignación Hilux → fragilidad → colapso reliability. |
| **Mensaje científico** | "La cadena causal demuestra que la fragilidad no es accidental sino una consecuencia estructural de la optimización determinista." |
| **Sección sugerida** | Discusión (Cap. 5), Paper Sec. V |
| **Impacto científico** | ★★★★★ — Explicación causal del hallazgo central |

---

### D. RESULTADOS HVRPTW

---

#### Figura D19 — KPI Dashboard Científico

| Campo | Detalle |
|-------|---------|
| **Archivo** | `D19_kpi_dashboard.png` / `.svg` |
| **Descripción** | 8 tarjetas de KPIs: costo det/estoc, reliability, CVaR, rutas, nodos, distancia, utilización |
| **Interpretación técnica** | Contraste entre métricas "verdes" (100% cobertura, 81/81 nodos) y métricas "rojas" (5.9% reliability, CVaR S/ 14,021). |
| **Interpretación operacional** | Visión ejecutiva: el sistema sirve todos los nodos pero es frágil. El dashboard permite comunicar a stakeholders no técnicos. |
| **Implicancia metodológica** | Formato de resumen para presentaciones y reportes. |
| **Hallazgo asociado** | Cobertura 100% ≠ robustez (reliability 5.9%). |
| **Mensaje científico** | "Cobertura operacional completa no garantiza robustez bajo incertidumbre." |
| **Sección sugerida** | Sustentación (slide resumen), Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Síntesis ejecutiva |

---

#### Figura D20 — Diagrama Gantt de Rutas

| Campo | Detalle |
|-------|---------|
| **Archivo** | `D20_gantt_rutas.png` / `.svg` |
| **Descripción** | Cronograma de 10 rutas con segmentos de servicio y tránsito, ventana 08:00–16:00 |
| **Interpretación técnica** | Todas las rutas completan antes de 16:00. Slack temporal promedio ~3.5h (ratio 4.38). Las rutas más largas (R1, R5, R7) usan ~7.5h. |
| **Interpretación operacional** | Confirma que el tiempo NO es restricción activa en el baseline determinista. Hay margen temporal suficiente. |
| **Implicancia metodológica** | Validación visual de factibilidad temporal. Complementa el análisis cuantitativo de slack temporal. |
| **Hallazgo asociado** | Tiempo no es restricción activa — slack temporal abundante. |
| **Mensaje científico** | "Las ventanas de tiempo de 8 horas proporcionan margen suficiente para absorber la variabilidad temporal." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Validación visual necesaria |

---

#### Figura D21 — Carga por Ruta vs Capacidad

| Campo | Detalle |
|-------|---------|
| **Archivo** | `D21_carga_por_ruta.png` / `.svg` |
| **Descripción** | Barras emparejadas: capacidad nominal vs carga asignada por ruta, con % utilización |
| **Interpretación técnica** | Disparidad visual clara: barras grises (capacidad) mucho mayores que barras coloreadas (carga) para FUSO/NLR, casi iguales para Hilux. |
| **Interpretación operacional** | FUSO tiene 2,810 kg ociosos; Hilux tiene 46 kg. La reasignación de carga de Hilux a rutas FUSO/NLR es trivial en capacidad. |
| **Implicancia metodológica** | Complementa C14 con vista de barras emparejadas. |
| **Hallazgo asociado** | Capacidad ociosa en vehículos grandes vs saturación en pequeños. |
| **Mensaje científico** | "Existe capacidad ociosa significativa en FUSO/NLR que podría absorber la carga actualmente asignada a Hilux." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Soporte visual |

---

#### Figura D22 — Distancia por Vehículo

| Campo | Detalle |
|-------|---------|
| **Archivo** | `D22_distancia_por_vehiculo.png` / `.svg` |
| **Descripción** | Barras de distancia por ruta, coloreadas por tipo de vehículo |
| **Interpretación técnica** | Hilux recorre en promedio más distancia (promedio ~207 km) que FUSO (99 km) y NLR (222 km). Ruta 7 (Hilux): 309 km, la más larga. |
| **Interpretación operacional** | El solver asigna Hilux a rutas lejanas por menor costo/km. Paradójicamente, el vehículo más frágil recorre las mayores distancias. |
| **Implicancia metodológica** | Conexión entre costo/km y asignación geográfica. |
| **Hallazgo asociado** | Hilux: mayor distancia + menor capacidad = máxima fragilidad. |
| **Mensaje científico** | "El solver asigna el vehículo más frágil a las rutas más extensas por su bajo costo/km." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★★☆☆ — Detalle de soporte |

---

#### Figura D23 — Tiempo por Ruta

| Campo | Detalle |
|-------|---------|
| **Archivo** | `D23_tiempo_por_ruta.png` / `.svg` |
| **Descripción** | Barras apiladas: servicio + tránsito por ruta, con línea de ventana máxima (8h) |
| **Interpretación técnica** | Ratio tránsito/servicio varía: rutas de sierra tienen más tránsito (60–70%), rutas costeras más servicio (50–60%). Ninguna excede 8h. |
| **Interpretación operacional** | El margen temporal es consistente en todas las rutas. No hay rutas temporalmente críticas en el baseline. |
| **Implicancia metodológica** | Descomposición servicio/tránsito útil para análisis operacional detallado. |
| **Hallazgo asociado** | Slack temporal abundante en todas las rutas. |
| **Mensaje científico** | "Ninguna ruta se acerca al límite temporal, confirmando que la capacidad — no el tiempo — es la restricción activa." |
| **Sección sugerida** | Resultados (Cap. 4) |
| **Impacto científico** | ★★☆☆☆ — Complementaria |

---

#### Figura D24 — Utilización Espacial

| Campo | Detalle |
|-------|---------|
| **Archivo** | `D24_utilizacion_espacial.png` / `.svg` |
| **Descripción** | 2 paneles: (a) heatmap de demanda geográfica, (b) asignación de vehículos a IPRESS |
| **Interpretación técnica** | Los Centros de Salud (318 kg, demanda alta) están distribuidos uniformemente. La asignación vehicular no correlaciona con la demanda local sino con la distancia al depósito. |
| **Interpretación operacional** | El solver no considera la distribución espacial de riesgo. Un enfoque risk-aware asignaría vehículos con mayor slack a zonas de alta demanda. |
| **Implicancia metodológica** | Sugiere extensión del modelo: restricciones de asignación risk-aware por zona geográfica. |
| **Hallazgo asociado** | La asignación vehicular no considera riesgo geográfico. |
| **Mensaje científico** | "La asignación del solver determinista es ciega al riesgo geográfico — no correlaciona capacidad con demanda local." |
| **Sección sugerida** | Discusión (Cap. 5), Trabajo futuro |
| **Impacto científico** | ★★★☆☆ — Relevante para extensiones futuras |

---

## RANKING DE IMPACTO CIENTÍFICO

### Las 5 Figuras MÁS IMPORTANTES Científicamente

| Rank | Código | Nombre | Justificación |
|------|--------|--------|---------------|
| **1** | **C13** | **Slack/Variabilidad** | **Figura central de la investigación.** Cuantifica por qué capacidad domina: Hilux ratio 0.11 vs tiempo 4.38. Es la contribución metodológica original (métrica diagnóstica unificada). Ninguna otra figura tiene este poder explicativo. |
| **2** | **B6** | **Distribución Costos** | Evidencia cuantitativa del gap determinista-estocástico (+61%). Es la primera prueba de que el determinismo es insuficiente. La asimetría (skewness=0.88) justifica CVaR. |
| **3** | **B11** | **Heatmap Sensibilidad** | Evidencia definitiva de dominancia: demanda explica >95% de variabilidad. Las columnas uniformes (CV tiempo) son visualmente contundentes. |
| **4** | **C15** | **Con/Sin Hilux** | Traduce el hallazgo en recomendación operacional concreta: reliability 6.5%→98.0% al reemplazar Hilux. ROI de robustez excepcional. |
| **5** | **C18** | **Cuello Botella** | Formaliza la cadena causal completa. Conecta solver → asignación → fragilidad → colapso. Base de la discusión científica. |

### Las 5 Mejores para Sustentación

| Rank | Código | Propósito en exposición |
|------|--------|------------------------|
| 1 | A1 | "Trabajamos con datos reales: 81 IPRESS, 820 arcos OSRM" |
| 2 | B6 | "El determinista subestima 61% el costo real operacional" |
| 3 | C13 | "El Hilux opera con ratio 0.11 — 40× más frágil que el tiempo" |
| 4 | C15 | "Reemplazar Hilux: reliability de 6% a 98% con solo +6% costo" |
| 5 | D19 | "Cobertura perfecta (81/81) pero reliability de solo 5.9%" |

### Las 8 Mejores para Paper

| # Paper | Código | Rol en el paper |
|---------|--------|-----------------|
| Fig. 1 | A1 | Contexto geográfico del caso de estudio |
| Fig. 2 | B6 | Distribución de costos — evidencia del gap |
| Fig. 3 | B7 | Validación de convergencia MC |
| Fig. 4 | B11 | Sensibilidad cruzada — dominancia de capacidad |
| Fig. 5 | C13 | Ratio slack/variabilidad — hallazgo central |
| Fig. 6 | C15 | Impacto de composición de flota |
| Fig. 7 | C16 | Frontera Pareto costo-robustez |
| Fig. 8 | C18 | Cadena causal del cuello de botella |

### Figuras Redundantes o Débiles

| Código | Evaluación | Recomendación |
|--------|-----------|---------------|
| A3 | Débil — cold_chain_demand=0 en todos los nodos | Mover a apéndice o limitaciones |
| D23 | Parcialmente redundante con D20 (Gantt ya muestra tiempos) | Incluir solo si se necesita descomposición servicio/tránsito |
| B10 | Los boxplots repiten información de B6 y B9 | Considerar como apéndice |
| D22 | Parcialmente redundante con A2 (ya muestra distancia) | Incluir solo en tesis, no en paper |

---

## RANKING DE IMPACTO POR DIMENSIÓN

| Dimensión | Figura | Justificación |
|-----------|--------|---------------|
| **Figura central** | C13 | Ratio slack/variabilidad: métrica diagnóstica original que unifica análisis de tiempo y capacidad |
| **Demuestra fragilidad** | C15 | El contraste 6.5% → 98.0% reliability es la evidencia más impactante de fragilidad |
| **Demuestra incertidumbre** | B6 | La distribución asimétrica con skewness=0.88 visualiza la incertidumbre operacional |
| **Demuestra robustez** | B11 | Las columnas uniformes del heatmap prueban que el hallazgo es robusto a variación de CV tiempo |
| **Demuestra fallo determinista** | C18 | La cadena causal explica el mecanismo exacto por el cual el determinismo falla |

---

## STORYBOARD PARA SUSTENTACIÓN

### Orden óptimo de presentación (15–20 min)

| # | Slide | Figura | Duración | Mensaje |
|---|-------|--------|----------|---------|
| 1 | **Problema** | A1 | 2 min | "La DSRSLCC–Sullana distribuye medicamentos a 81 IPRESS en una red costa-sierra de 300+ km" |
| 2 | **Modelo** | A2 | 1 min | "Implementamos un HVRPTW con flota heterogénea: FUSO, NLR, Ducato, Hilux" |
| 3 | **Baseline** | D19 | 1.5 min | "El solver determinista genera 10 rutas con costo S/ 5,089 y 100% cobertura" |
| 4 | **Incertidumbre** | B6 | 2 min | "Pero bajo incertidumbre real (SISMED): el costo sube 61% y la reliability colapsa al 6%" |
| 5 | **Evidencia MC** | B7 | 1.5 min | "Esto se valida con 2000 escenarios Monte Carlo, convergencia confirmada (IC 2.5%)" |
| 6 | **Diagnóstico** | C13 | 3 min | "¿POR QUÉ? El ratio slack/variabilidad revela: Hilux opera con 0.11σ de margen — 40× peor que el tiempo" |
| 7 | **Dominancia** | B11 | 2 min | "La demanda explica >95% del riesgo. El tiempo es marginal (<1%). Esto es robusto." |
| 8 | **Solución** | C15 | 2 min | "Reemplazar Hilux por NLR: reliability 6% → 96%, costo +6%. La composición importa más que la cantidad." |
| 9 | **Robustez** | C16 | 1.5 min | "Las configuraciones sin Hilux dominan en la frontera Pareto costo-reliability" |
| 10 | **Causalidad** | C18 | 2 min | "La cadena causal: solver minimiza costo/km → sobreasigna Hilux → sin slack → colapso" |
| 11 | **Conclusión** | D19 | 1 min | "Contribución: la optimización determinista induce fragilidad en flotas heterogéneas. Ratio slack/variabilidad como diagnóstico." |

### Narrativa central (elevator pitch):

> "El solver determinista hace exactamente lo que se le pide — minimizar costo — pero al hacerlo asigna el vehículo más barato (Hilux, S/ 1.5/km) a la mayor cantidad de rutas. Esto deja solo 46 kg de margen contra 420 kg de variabilidad. El resultado: la solución 'óptima' falla en el 94% de los escenarios reales. Reemplazar Hilux por NLR transforma reliability de 6% a 96% con solo 6% más de costo."

---

## TABLAS COMPLEMENTARIAS

| # | Archivo | Descripción | Sección sugerida |
|---|---------|-------------|-----------------|
| T1 | `tabla_01_kpi_resumen.csv` | KPIs det vs estoc (9 métricas) | Resultados |
| T2 | `tabla_02_sensibilidad_conversion.csv` | 4 factores item→kg | Validación |
| T3 | `tabla_03_experimentos_flota.csv` | 10 configuraciones | Resultados |
| T4 | `tabla_04_convergencia_mc.csv` | n=100–2000 | Metodología |
| T5 | `tabla_05_sensibilidad_cruzada.csv` | 12 combinaciones CV | Resultados |
| T6 | `tabla_06_rutas_baseline.csv` | 10 rutas detalladas | Resultados |
| T7 | `tabla_07_slack_variabilidad.csv` | Ratio por recurso | Discusión |
