# Conclusiones — HVRPTW Estocástico para Logística Farmacéutica Pública DSRSLCC

## 1. Conclusiones Derivadas de los Resultados

### Conclusión 1: La planificación determinista de distribución farmacéutica produce soluciones operacionalmente frágiles

La evaluación Monte Carlo (2,000 escenarios) del baseline HVRPTW determinista reveló un gap de costo del 61% (S/ 5,089 → S/ 8,160) y un colapso de route reliability de 100% a 5.9%. La solución que aparenta ser óptima bajo certidumbre falla en el 94% de los escenarios estocásticos realistas.

*Evidencia*: Gap E[cost] +61%, reliability 5.9%, convergencia confirmada con CI 95% relativo de 2.5% (2000 escenarios).

### Conclusión 2: El riesgo operacional está dominado por capacidad vehicular, no por incertidumbre temporal

La demanda explica ~95% del incremento de costo estocástico; la variabilidad de tiempos de viaje explica ~5%. Las violaciones de capacidad (93%) dominan sobre las violaciones de ventanas de tiempo (8-10%).

*Evidencia*: Análisis de aislamiento de factores (demanda ΔE[cost]+35.5% vs tiempo +0.1%), robusto bajo 4 factores de conversión item→kg.

*Mecanismo*: Las ventanas de 8 horas proporcionan slack temporal de 3-4 horas (ratio slack/σ = 4-5), mientras que la capacidad de los Hilux tiene slack de solo 46 kg (ratio slack/σ = 0.11).

### Conclusión 3: La composición de flota importa más que la capacidad total

La flota tiene 3× la demanda (50 ton vs 16 ton). Sin embargo, la reliability es 6%. El cuello de botella son los Toyota Hilux (1,000 kg), que operan al 95% de capacidad determinista y fallan bajo cualquier variabilidad positiva de demanda.

*Evidencia*: Eliminar Hilux y reemplazar por NLR o FUSO (manteniendo 16 vehículos) lleva reliability a 95-98% y reduce E[cost] a S/ 5,386-5,818.

### Conclusión 4: La heterogeneidad extrema de flota amplifica la fragilidad bajo incertidumbre

El ratio de capacidad mayor/menor (FUSO 6T / Hilux 1T = 6:1) es inusualmente alto. La optimización de costo explota esta heterogeneidad seleccionando Hilux por su bajo costo/km (S/ 1.8), creando asignaciones eficientes pero frágiles.

*Evidencia*: El gap det/estoc de 61% excede significativamente los valores típicos en literatura SVRP (10-40%), explicado por la interacción entre heterogeneidad de flota y función objetivo determinista.

### Conclusión 5: Los datos SISMED permiten parametrizar modelos estocásticos de distribución farmacéutica

Se demostró que los datos del sistema SISMED (consumo, stock, CPMA) proporcionan parámetros de incertidumbre (CV por categoría de establecimiento) suficientes para calibrar modelos estocásticos, a pesar de no disponer de datos por establecimiento individual.

*Evidencia*: CV de SISMED (CS=0.42, PS=0.45) producen resultados estocásticos con convergencia verificada y hallazgos robustos bajo análisis de sensibilidad.

---

## 2. Recomendaciones Operacionales

### Para DSRSLCC

1. **No asignar Toyota Hilux a rutas de distribución mensual regular** con carga esperada >750 kg.
2. **Incorporar buffer de capacidad del 15-25%** en la planificación de rutas.
3. **Evaluar la sustitución gradual de Hilux** por vehículos de 3+ toneladas para distribución regular.
4. **Reservar Hilux** para entregas urgentes, suministros específicos, o rutas con demanda verificada <500 kg.

### Para el Sistema de Salud

1. **Replicar el framework** en otras DIRESA/DIRIS con datos SISMED y OSRM.
2. **Incorporar análisis estocástico** en la planificación logística farmacéutica, no solo determinista.
3. **Documentar pesos reales de despacho** para calibrar el factor de conversión item→kg.

---

## 3. Limitaciones de las Conclusiones

Las conclusiones cuantitativas (reliability 6%, gap 61%, CVaR S/ 14,021) deben interpretarse como **órdenes de magnitud**, no como predicciones precisas. La dirección de los hallazgos (capacity > time, Hilux como cuello de botella, fragilidad determinista) es robusta bajo los análisis de sensibilidad realizados.

Las principales incertidumbres remanentes son:
1. Factor de conversión item→kg (rango 5-15g, mitigado con sensibilidad)
2. Demanda por IPRESS individual (no disponible, mitigado con ratios SISMED por categoría)
3. Distribuciones asumidas (no ajustadas a datos históricos de entrega)

---

## 4. Contribución del Trabajo

1. **Framework reproducible** para evaluación estocástica de HVRPTW en logística farmacéutica pública, integrable con datos SISMED y OSRM.

2. **Evidencia empírica** de que la optimización determinista induce fragilidad en flotas heterogéneas, cuantificando el "precio de la certidumbre" en un caso real.

3. **Metodología de diagnóstico** de composición de flota basada en ratio slack/variabilidad por tipo de vehículo.

4. **Resultado contraintuitivo documentado**: en esta red rural, la incertidumbre temporal (que se esperaría dominante) es marginal comparada con la de capacidad.

---

## 5. Trabajo Futuro

### Extensiones prioritarias

1. **Optimización CVaR** (Fase E): Integrar aversión al riesgo en la función objetivo para generar rutas inherentemente robustas.
2. **Calibración por IPRESS**: Obtener datos de consumo individual para heterogeneizar la demanda entre nodos.
3. **Validación con datos de despacho real**: Verificar factor de conversión y demandas con registros del almacén.

### Extensiones de mediano plazo

4. **Simheuristic** (Fase F): Integrar simulación Monte Carlo en el proceso de búsqueda heurística.
5. **Buffer de capacidad optimizado**: Determinar el nivel óptimo de buffer (α) que minimice CVaR.
6. **Estacionalidad de demanda**: Incorporar patrones temporales de SISMED.

---

*Estas conclusiones se derivan exclusivamente de los resultados experimentales documentados. No se afirma optimalidad universal, causalidad absoluta, ni generalización automática a otros sistemas logísticos.*
