# Discusión Científica — HVRPTW Estocástico DSRSLCC

## 1. Síntesis de Hallazgos

### 1.1 Hallazgo Principal

El sistema logístico farmacéutico DSRSLCC, modelado como HVRPTW con incertidumbre dual (demanda + tiempos), exhibe **vulnerabilidad estructural dominada por capacidad vehicular**, no por incertidumbre temporal.

### 1.2 Evidencia

| Evidencia | Valor |
|---|---|
| Cap violation rate (baseline, 2000 esc.) | 93% |
| TW violation rate | 8-10% |
| Reliability baseline | 5.9% |
| Δ E[cost] por demanda (CV=0.42) | +35.5% |
| Δ E[cost] por tiempo (CV=0.20) | +0.1% |
| Eliminación de Hilux → Reliability | 95-98% |
| CVaR₅%/E[cost] ratio | 1.72 |

---

## 2. ¿Por Qué Colapsa la Reliability?

### 2.1 Mecanismo

1. El solver determinista optimiza por costo mínimo.
2. Los Toyota Hilux tienen el costo/km más bajo (S/ 1.8).
3. El solver asigna 5 Hilux a rutas con ~954 kg (95% de 1,000 kg capacidad).
4. Con CV demanda = 0.42, la demanda excede 1,000 kg en ~50% de los escenarios por ruta.
5. Con 5 rutas Hilux, la probabilidad de que AL MENOS una viole capacidad es: 1 - (0.5)⁵ ≈ 97%.

### 2.2 Implicación

La reliability colapsa NO porque el sistema sea globalmente insuficiente (D/C = 0.32), sino porque la **optimización determinista de costo produce soluciones frágiles**. Este es un resultado clásico en optimización estocástica: las soluciones óptimas deterministas suelen ser ineficientes bajo incertidumbre.

---

## 3. ¿Por Qué Capacidad Domina Sobre Tiempos?

### 3.1 Estructura del Problema

- **Ventanas de tiempo**: 08:00-16:00 (8 horas).
- **Duración promedio de ruta**: ~200 km / 50 km/h = ~4h + servicio.
- **Slack temporal**: ~3-4 horas de margen → absorbe variabilidad de tiempos.

- **Capacidad Hilux**: 1,000 kg.
- **Carga asignada**: ~954 kg.
- **Slack de capacidad**: ~46 kg (4.6%) → no absorbe variabilidad de demanda (CV=0.42).

### 3.2 Ratio Slack/Variabilidad

| Factor | Slack disponible | Variabilidad (1σ) | Ratio |
|---|---|---|---|
| Tiempo | ~3-4h | ~0.8h (CV=0.2) | 4-5× |
| Capacidad (Hilux) | ~46 kg | ~400 kg (CV=0.42) | 0.11× |

El ratio de capacidad (0.11) es 40× menor que el de tiempo (4-5), explicando la dominancia absoluta del riesgo de capacidad.

---

## 4. Implicaciones Operacionales para DSRSLCC

### 4.1 Hallazgos Accionables

1. **Los Toyota Hilux no deben usarse para rutas de distribución estándar**. Su capacidad de 1 ton es adecuada solo para entregas puntuales o emergencias, no para distribución mensual regular con variabilidad.

2. **La flota actual es suficiente en capacidad total** (50 ton vs 16 ton de demanda), pero su **composición es inadecuada** para absorber variabilidad.

3. **Un buffer de capacidad del 15-25% eliminaría la mayoría de violaciones**, sin necesidad de vehículos adicionales.

### 4.2 Implicaciones Sanitarias

- La distribución farmacéutica con route reliability del 6% implica que en ~19 de cada 20 ciclos de distribución, al menos una ruta tiene problemas de capacidad.
- Esto no significa desabastecimiento (service level = 100%), pero sí **retrasos y sobrecostos** por viajes adicionales o redistribución.
- En distribución de medicamentos críticos, la reliability debería ser ≥85% para operación estable.

---

## 5. Contribución Metodológica

### 5.1 Aportaciones

1. **Framework HVRPTW con evaluación estocástica aplicada a logística farmacéutica pública**: Integración de datos SISMED reales con modelo OR.

2. **Identificación de dominancia de capacidad sobre tiempo**: Resultado no trivial que contradice la intuición inicial (se esperaría que tiempos de viaje en zona rural fueran el factor dominante).

3. **Demostración de fragilidad de soluciones deterministas**: El gap del 61% entre costo determinista y estocástico cuantifica el "precio de la certidumbre".

4. **Análisis de sensibilidad del factor de conversión item→kg**: Demuestra robustez del hallazgo principal bajo diferentes supuestos de peso.

### 5.2 Comparación con Literatura

| Aspecto | Este estudio | Literatura VRP estocástica |
|---|---|---|
| Fuente de riesgo dominante | Capacidad | Típicamente tiempos o demanda |
| Gap det/estoc | 61% | 10-40% (típico) |
| Reliability baseline | 6% | 50-90% (típico) |
| Causa | Heterogeneidad de flota extrema | — |

El gap inusualmente alto (61%) y la reliability baja (6%) se explican por la **heterogeneidad extrema de la flota** (ratio de capacidad mayor/menor = 6000/1000 = 6:1), que es específica de logística farmacéutica pública en zonas rurales.

---

## 6. Limitaciones

### 6.1 Limitaciones de Datos

1. **Demanda no medida por establecimiento**: Asignada uniformemente dentro de categoría CENTRO/PUESTO.
2. **Factor de conversión item→kg no verificado**: Estimación operacional, no medición directa.
3. **Sin datos de despacho real**: No se puede validar contra entregas históricas.
4. **Muestra SISMED limitada**: 12 de ~200+ medicamentos para ratio de categorías.

### 6.2 Limitaciones del Modelo

1. **Rutas fijas en evaluación estocástica**: No hay recourse (re-optimización por escenario).
2. **Distribuciones asumidas**: Normal truncada y LogNormal son aproximaciones operacionales.
3. **Independencia entre nodos**: No captura correlaciones regionales de demanda.
4. **Sin estacionalidad**: Modelo estático (promedio mensual), no dinámico.

### 6.3 Limitaciones Computacionales

1. **OR-Tools como solver**: No garantiza optimalidad global (GLS es metaheurística).
2. **Tiempo de resolución**: 60-120s puede ser insuficiente para instancias mayores.
3. **Sin paralelización**: Evaluación de escenarios es secuencial.

---

## 7. Futuras Líneas de Investigación

### 7.1 Inmediatas (Fase E-F)

1. **Optimización CVaR**: Integrar aversión al riesgo en la función objetivo para producir rutas más robustas.
2. **Buffer de capacidad como restricción**: Implementar `load ≤ α × capacity` con α ∈ [0.75, 0.85].
3. **Simheuristic**: Combinar heurística constructiva con simulación integrada.

### 7.2 Mediano Plazo

1. **Datos de despacho real**: Obtener pesos de despacho de almacén DSRSLCC.
2. **Estacionalidad**: Incorporar patrones mensuales/estacionales de consumo SISMED.
3. **Correlación de demanda**: Modelar dependencia regional (brotes, campañas).

### 7.3 Largo Plazo

1. **Multi-periodo**: Planificación de distribución semanal/mensual con inventarios.
2. **Cadena de frío activa**: Activar restricciones de temperatura cuando datos SISMED lo permitan.
3. **Benchmarking**: Comparar con rutas históricas cuando estén disponibles.

---

*Discusión científica — HVRPTW estocástico DSRSLCC*
*Última actualización: Mayo 2026*
