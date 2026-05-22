# Material para Sustentación — HVRPTW Estocástico DSRSLCC

## 1. Principales Hallazgos (Mensajes Clave)

### Mensaje 1: "La planificación determinista oculta un 61% de sobrecosto real"
- El baseline determinista reporta S/ 5,089 y 100% de cumplimiento
- Bajo incertidumbre realista (datos SISMED), el costo esperado es S/ 8,160
- La planificación aparenta ser óptima, pero en la operación se manifiestan "imprevistos" sistemáticos

### Mensaje 2: "El problema no es falta de capacidad, es composición de flota"
- La flota tiene 50 ton de capacidad, la demanda es 16 ton (3× excedente)
- Sin embargo, la reliability es solo 6%
- Causa: los Hilux (1 ton) son asignados por bajo costo pero no absorben variabilidad

### Mensaje 3: "Cambiar la composición de la flota resuelve el 95% del problema"
- Reemplazar Hilux por NLR (3.5T): reliability 6% → 95.5%
- No se necesita más capacidad total, se necesita mejor distribución de capacidad

### Mensaje 4: "Los datos SISMED son suficientes para modelar incertidumbre"
- Se extrajo CV real del sistema SISMED peruano
- CS=0.42, PS=0.45: variabilidad suficiente para calibrar modelos estocásticos
- Framework transferible a otras DIRESA/DIRIS

### Mensaje 5: "El hallazgo es robusto, no depende de supuestos específicos"
- Robusto bajo 4 factores de conversión (5g, 10g, 20g, 50g)
- Robusto bajo 10 configuraciones de flota
- Convergencia confirmada con 2000 escenarios (CI 95% = 2.5%)

---

## 2. Posibles Críticas y Respuestas

### Crítica: "La demanda no es real, son estimaciones"

**Respuesta**:
- Los parámetros de variabilidad (CV) SÍ provienen de datos SISMED reales
- La demanda media es estimada por categoría (CENTRO/PUESTO), no por IPRESS — esto se documenta explícitamente como limitación
- Se realizó análisis de sensibilidad con 4 factores de conversión (5g→50g), y el hallazgo principal es robusto en todos
- Para calibración definitiva se requiere datos del sistema de despacho del almacén, no disponibles vía PowerBI
- La terminología utilizada es "estimación operacional", no "demanda medida"

### Crítica: "¿Cómo justifican el factor de 10g/item?"

**Respuesta**:
- Es una estimación basada en el mix de productos SISMED donde >80% son tabletas (0.5-2g/unidad)
- Con empaque logístico (blíster, caja individual, caja de despacho): 5-15g rango plausible
- Punto medio conservador: 10g/item
- Se evaluaron 4 escenarios y se demostró que el hallazgo no depende del valor exacto
- Para verificación definitiva: pesar despachos reales del almacén DSRSLCC

### Crítica: "Normal truncada y LogNormal son supuestos, no datos"

**Respuesta**:
- Correcto — son aproximaciones operacionales estándar en la literatura VRP estocástica
- Normal truncada: justificada por CLT sobre agregación de múltiples medicamentos
- LogNormal: justificada por positividad y cola derecha de tiempos de viaje
- Los PARÁMETROS sí son datos: CV de SISMED, μ de OSRM
- La alternativa (no modelar incertidumbre) es peor que modelarla aproximadamente

### Crítica: "No implementaron optimización estocástica, solo evaluación"

**Respuesta**:
- Correcto — es evaluación post-optimización, no optimización estocástica
- La contribución es el DIAGNÓSTICO: cuantificar la fragilidad de la solución determinista
- La evaluación demuestra la NECESIDAD de optimización estocástica (CVaR), que es trabajo futuro (Fase E)
- La evaluación post-optimización es un paso metodológico estándar antes de implementar optimización bajo incertidumbre

### Crítica: "OR-Tools no garantiza optimalidad"

**Respuesta**:
- Correcto — GLS es metaheurística, no método exacto
- Para la evaluación estocástica, no se requiere optimalidad del baseline: se evalúa la robustez de una solución "buena", no de la solución "óptima"
- El hallazgo (fragilidad de Hilux) es ESTRUCTURAL, no depende de la optimalidad de la solución

### Crítica: "81 nodos de 207 no es representativo"

**Respuesta**:
- Se seleccionaron nodos ACTIVOS con geocodificación MEDIUM/HIGH — criterio objetivo
- Los 126 excluidos están INACTIVOS o con geocodificación de baja confianza
- El framework escala; los resultados cualitativos se mantienen al aumentar nodos

### Crítica: "Las penalizaciones son arbitrarias"

**Respuesta**:
- Las penalizaciones son parámetros del modelo que cuantifican el costo de violaciones
- El hallazgo depende de las TASAS de violación (93% cap, 10% TW), no de los montos
- Con cualquier penalización positiva (cap > 0, TW > 0), la dominancia de capacidad se mantiene

### Crítica: "Sin recourse, sobreestiman el impacto"

**Respuesta**:
- Correcto — las rutas son fijas; en la práctica se re-planifica
- La evaluación sin recourse es una COTA SUPERIOR del riesgo
- Sirve para cuantificar el "peor caso operacional" si no se re-planifica
- La re-planificación tiene costos propios (tiempo, coordinación) que no se modelan

---

## 3. Fortalezas Reales

| Fortaleza | Evidencia |
|---|---|
| Datos reales, no benchmarks artificiales | SISMED, OSRM, establecimientos de salud reales |
| Framework reproducible | Código Python, datos CSV, semillas fijas |
| Análisis de sensibilidad exhaustivo | 4 factores conversión × 12 CV × 10 flotas × 2000 escenarios |
| Hallazgo robusto | Consistente bajo todos los análisis |
| Limitaciones documentadas con honestidad | threats_to_validity.md con 15 amenazas clasificadas |
| Resultado contraintuitivo | Capacidad > tiempo en red rural |
| Contribución transferible | Aplicable a cualquier DIRESA/DIRIS con SISMED |

---

## 4. Limitaciones Honestas

1. **No es optimización estocástica** — es evaluación. La optimización CVaR es trabajo futuro.
2. **Demanda no verificada por IPRESS** — estimaciones por categoría, no mediciones individuales.
3. **Factor de conversión no verificado** — rango 5-15g plausible, no un dato medido.
4. **Sin datos de despacho real** — no se puede validar contra la operación histórica.
5. **Sin estacionalidad** — modelo estático de promedio mensual.
6. **Solver heurístico** — no garantiza optimalidad global del baseline.

Estas limitaciones están documentadas y mitigadas en la medida de lo posible. No invalidan los hallazgos principales.

---

## 5. Contribución Principal (Elevator Pitch)

> "Demostramos que la planificación determinista de distribución farmacéutica en el sistema de salud peruano oculta un 61% de sobrecosto operacional, causado no por falta de capacidad total sino por la composición de la flota. La optimización de costo selecciona vehículos baratos pero pequeños, creando rutas que fallan en el 94% de los escenarios realistas. La solución no es más vehículos, sino vehículos mejor dimensionados."

---

## 6. Preguntas Esperadas y Preparación

### Pregunta: "¿Cuál es la recomendación práctica para DSRSLCC?"
**Respuesta**: No usar Hilux para distribución mensual regular; implementar buffer de capacidad del 15-25%; evaluar sustitución gradual por NLR o similares.

### Pregunta: "¿Cómo se compara con otras investigaciones?"
**Respuesta**: El gap de 61% es significativamente mayor que el típico 10-40% en literatura SVRP, explicado por la heterogeneidad extrema de flota (ratio 6:1) que es específica de logística pública.

### Pregunta: "¿Qué haría diferente si empezara de nuevo?"
**Respuesta**: Obtener datos de peso de despacho real del almacén desde el inicio; buscar datos de consumo por IPRESS (no solo por categoría); implementar CVaR desde la Fase C.

### Pregunta: "¿Cómo se implementaría en la práctica?"
**Respuesta**: El framework se ejecuta con Python estándar + OR-Tools. Requiere datos OSRM (disponibles vía API pública), datos SISMED (acceso vía PowerBI), y ~30 minutos de cómputo para evaluación completa.
