# Discusión Científica — HVRPTW Estocástico DSRSLCC

## 1. Síntesis de Hallazgos

### 1.1 Hallazgo Principal

El sistema logístico farmacéutico DSRSLCC, modelado como HVRPTW con incertidumbre dual (demanda + tiempos), exhibe **vulnerabilidad estructural dominada por capacidad vehicular**, no por incertidumbre temporal.

### 1.2 Evidencia Cuantitativa

| Evidencia | Valor |
|---|---|
| Cap violation rate (baseline, 2000 esc.) | 93% |
| TW violation rate | 8-10% |
| Reliability baseline | 5.9% |
| Δ E[cost] por demanda (CV=0.42) | +35.5% |
| Δ E[cost] por tiempo (CV=0.20) | +0.1% |
| Eliminación de Hilux → Reliability | 95-98% |
| CVaR₅%/E[cost] ratio | 1.72 |
| Gap determinista/estocástico | 61% |

---

## 2. Interpretación Causal

### 2.1 ¿Por Qué Colapsa la Reliability?

**Cadena causal identificada:**

```
Minimización de costo determinista
    → Preferencia por Hilux (costo/km más bajo: S/ 1.8)
        → Asignación de 5 rutas a Hilux (1,000 kg capacidad)
            → Carga promedio: 954 kg (95% utilización)
                → Slack de capacidad: 46 kg (4.6%)
                    → CV demanda = 0.42 → σ ≈ 400 kg
                        → P(exceder 1,000 kg | una ruta) ≈ 50%
                            → P(al menos una violación | 5 rutas) ≈ 97%
```

La reliability colapsa NO porque el sistema sea globalmente insuficiente (D/C = 0.32), sino porque la **optimización determinista de costo produce asignaciones frágiles**. Esto constituye un ejemplo empírico del fenómeno teórico conocido en programación estocástica: las soluciones óptimas deterministas frecuentemente son ineficientes — o incluso infactibles — bajo incertidumbre.

La diferencia con la teoría es que aquí el mecanismo es específico y cuantificable: no es un efecto difuso de "incertidumbre general", sino una interacción precisa entre heterogeneidad de flota, función objetivo, y variabilidad de demanda.

### 2.2 ¿Por Qué Capacidad Domina Sobre Tiempos?

**Explicación por ratio slack/variabilidad:**

| Factor | Recurso disponible | Slack | Variabilidad (1σ) | Ratio slack/σ |
|---|---|---|---|---|
| Tiempo | 8h ventana | ~3-4h | ~0.8h (CV=0.2) | **4-5×** |
| Capacidad (Hilux) | 1,000 kg | ~46 kg | ~400 kg (CV=0.42) | **0.11×** |
| Capacidad (FUSO) | 6,000 kg | ~2,400 kg | ~1,500 kg (CV=0.42) | **1.6×** |
| Capacidad (NLR) | 3,500 kg | ~1,200 kg | ~700 kg (CV=0.42) | **1.7×** |

El ratio slack/variabilidad de los Hilux (0.11) es **40× inferior** al ratio temporal (4-5). Incluso los vehículos más grandes (FUSO, NLR) tienen ratios >1.5, lo que explica por qué al eliminar los Hilux la reliability salta a 95-98%.

La dominancia de capacidad sobre tiempo no es universal; es consecuencia de:
1. Ventanas de tiempo amplias (8h) que proporcionan slack generoso
2. Rutas relativamente cortas (promedio ~200 km, ~4h)
3. Capacidad marginal de Hilux combinada con alta variabilidad de demanda

En una red con ventanas más restrictivas (ej: cadena de frío con ventana de 2-3h), la dominancia podría invertirse.

### 2.3 ¿Por Qué la Minimización Determinista Induce Fragilidad?

La función objetivo determinista optimiza:

```
min Σ (costo_fijo_v + costo_km_v × distancia_v)
```

Esta función NO penaliza el slack de capacidad. El solver trata capacidad como restricción dura (`carga ≤ capacidad`) evaluada con demanda puntual, no como distribución. Consecuencia: selecciona el vehículo más barato que cumpla la restricción marginalmente.

Si la función objetivo incluyera un término de robustez:

```
min Σ costo_v + λ × Σ P(carga_v > capacidad_v)
```

el solver evitaría asignaciones marginales. Esto es precisamente lo que justifica la transición a optimización CVaR (Fase E).

---

## 3. Implicaciones Operacionales

### 3.1 Riesgos Logísticos Identificados para DSRSLCC

**Riesgo 1: Viajes adicionales no planificados**

Con 93% de probabilidad de violación de capacidad, en ~19 de cada 20 ciclos de distribución al menos una ruta tendrá exceso de carga. El exceso promedio es 305 kg, requiriendo un viaje adicional o redistribución ad-hoc. Esto genera:
- Sobrecosto estimado: S/ 3,071/ciclo (+61% sobre planificación)
- Tiempo adicional no planificado
- Riesgo de desabastecimiento temporal de establecimientos al final de ruta

**Riesgo 2: Sobrecarga vehicular**

Operar Hilux con carga >1,000 kg es un riesgo mecánico y de seguridad vial. En la práctica, el personal probablemente rechaza la carga excedente, generando viajes parciales.

**Riesgo 3: Ineficiencia sistémica invisible**

Sin un modelo estocástico, la planificación determinista aparenta ser óptima (S/ 5,089, 100% servicio). Los costos reales (S/ 8,160) permanecen invisibles en la planificación pero se manifiestan en la operación como "imprevistos".

### 3.2 Vulnerabilidad Operativa

| Indicador | Valor | Interpretación |
|---|---|---|
| Route reliability | 6% | Operacionalmente inaceptable |
| Service level | 100% | Todos los nodos son visitados (pero carga puede ser incompleta) |
| CVaR₅% | S/ 14,021 | En el 5% peor de los casos, costo es 2.75× el determinista |
| Gap promedio | 61% | Más de la mitad del costo real no aparece en la planificación |

### 3.3 Recomendaciones de Gestión de Flota

1. **Restricción operacional inmediata**: No asignar Hilux a rutas con carga esperada >750 kg (buffer 25%).
2. **Reasignación de flota**: Sustituir 4-6 Hilux por NLR (3.5 ton) o vehículos similares para distribución regular.
3. **Uso diferenciado de Hilux**: Reservar para entregas urgentes, suministros específicos, o rutas con demanda conocida y estable <500 kg.
4. **Buffer de planificación**: Incorporar regla operacional de cargar al 75-85% de capacidad nominal.

### 3.4 Implicaciones Sanitarias

La distribución farmacéutica es un servicio esencial. Una reliability del 6% implica que la planificación logística falla consistentemente, aunque el sistema compensate mediante improvisación operativa. Las consecuencias sanitarias potenciales:

- Retrasos en entrega de medicamentos a Puestos de Salud rurales
- Priorización ad-hoc que puede perjudicar a establecimientos más alejados
- Costos ocultos que reducen recursos disponibles para el sistema de salud

Sin embargo, es importante no exagerar: el service level del 100% indica que todos los nodos son visitados. La fragilidad se manifiesta como sobrecostos y retrasos, no como desabastecimiento total.

---

## 4. Relación con Literatura

### 4.1 HVRPTW (Heterogeneous VRP with Time Windows)

El HVRPTW ha sido estudiado extensivamente, pero predominantemente en contexto determinista. La contribución de este trabajo es la **evaluación estocástica post-optimización** que cuantifica la fragilidad de soluciones deterministas en flotas con alta heterogeneidad.

En la literatura HVRPTW, la heterogeneidad de flota típicamente se modela con ratios de capacidad 2-3:1. El ratio 6:1 de DSRSLCC (FUSO 6T vs Hilux 1T) es inusualmente alto y produce efectos no observados en instancias con heterogeneidad moderada.

### 4.2 Stochastic VRP

La literatura de SVRP (Stochastic VRP) ha documentado el gap entre soluciones deterministas y estocásticas, típicamente en el rango 10-40%. El gap de 61% observado aquí es significativamente mayor, explicado por:
- Heterogeneidad extrema de flota (no presente en benchmarks SVRP estándar)
- Variabilidad alta de demanda (CV=0.42, superior al CV=0.10-0.20 típico en benchmarks)
- Estructura de penalización que amplifica violaciones de capacidad

### 4.3 Fleet Composition y Fleet Size

La literatura de fleet composition (FSP) estudia la selección óptima de tipos de vehículos. Los resultados de esta investigación aportan evidencia empírica de que la composición de flota tiene impacto mayor sobre robustez operacional que la capacidad total, especialmente cuando la función objetivo no incorpora incertidumbre.

### 4.4 Healthcare Logistics

La logística farmacéutica pública tiene características específicas:
- Demanda inelástica (los medicamentos deben llegar)
- Variabilidad influida por factores epidemiológicos
- Flotas heterogéneas por restricciones presupuestarias
- Prioridad de cobertura sobre eficiencia

Estas características hacen que la robustez sea más crítica que en logística comercial, donde el costo de fallo es menor.

---

## 5. Análisis de Robustez de Hallazgos

### 5.1 Robustez bajo Factor de Conversión

| Factor | Cap domina sobre TW | Hallazgo robusto |
|---|---|---|
| 5g/item | Sí (45% > 0%) | Sí |
| 10g/item | Sí (93% > 10%) | Sí |
| 20g/item | Sí (90% > 6.5%) | Sí |
| 50g/item | Sí (99.5% > 0%) | Sí |

### 5.2 Robustez bajo Configuración de Flota

El hallazgo de que los Hilux son el cuello de botella se confirma por los experimentos de eliminación:
- Con Hilux: reliability 6.5%, cap violations 93.5%
- Sin Hilux (+NLR): reliability 95.5%, cap violations 3.5%
- Sin Hilux (+FUSO): reliability 98.0%, cap violations 0.0%

### 5.3 Robustez bajo Diferentes Niveles de CV

| CV Demanda | Cap violations | Hallazgo consistente |
|---|---|---|
| 0.20 | ~45% | Sí (capacidad > tiempo) |
| 0.42 | ~93% | Sí |
| 0.60 | ~95% | Sí |

---

## 6. Futuras Líneas de Investigación

### 6.1 Extensiones Inmediatas

1. **Optimización CVaR**: Integrar aversión al riesgo en la función objetivo para generar soluciones inherentemente más robustas.
2. **Buffer de capacidad como restricción**: `load ≤ α × capacity` con α optimizado.
3. **Simheuristic**: Evaluación estocástica integrada en el proceso de búsqueda.

### 6.2 Extensiones de Datos

1. **Datos de despacho real**: Validar conversión item→kg con pesos reales del almacén.
2. **Datos por IPRESS**: Obtener consumo individual para calibración heterogénea.
3. **Estacionalidad**: Modelar patrones temporales de demanda SISMED.

### 6.3 Extensiones Metodológicas

1. **Correlación de demanda**: Modelar dependencia regional por factores epidemiológicos.
2. **Ventanas heterogéneas**: Diferenciar horarios por zona geográfica y accesibilidad.
3. **Multi-periodo**: Planificación dinámica con reposición de inventario.
