# Validación de Demanda SISMED — Auditoría de Conversión item→kg

## 1. Problema Metodológico

La demanda logística del HVRPTW requiere unidades de peso (kg). Los datos SISMED registran consumo en **items** (unidades farmacéuticas). La conversión items→kg introduce un supuesto no verificable directamente:

```
demanda_kg = items_mensuales × peso_por_item
```

El peso por item depende de la composición del mix de productos, que varía por establecimiento y periodo.

---

## 2. Datos SISMED Disponibles

### 2.1 Fuentes Extraídas

| Fuente | Registros | Cobertura |
|---|---|---|
| Top 200 medicamentos | 200 | Consumo total acumulado (61 periodos) |
| 12 medicamentos detallados | 500 | Mensual × categoría (CENTRO/PUESTO) |
| Muestra metotrexato | 314 | Mensual × 5 categorías EE.SS. |

### 2.2 Hallazgos Clave

- **Total consumption (top 200, sin O₂)**: 1,550,067 items/mes
- **Ratio CENTRO/PUESTO**: 2.31:1 (de muestra 12 medicamentos)
- **CV temporal**: CENTRO=0.42, PUESTO=0.45

### 2.3 Limitaciones Críticas

1. **No hay datos por IPRESS individual**: SISMED PowerBI expone datos agregados por categoría de establecimiento, NO por establecimiento individual.
2. **No hay tabla de pesos unitarios**: No se dispone de peso por presentación farmacéutica.
3. **Composición del mix desconocida por establecimiento**: Un Centro de Salud y un Puesto de Salud reciben diferentes mezclas de medicamentos.
4. **Periodos incluyen proyecciones**: Algunos datos 2025-2026 pueden ser proyectados, no históricos reales.

---

## 3. Terminología Correcta

| Término | Uso |
|---|---|
| **Demanda calibrada** | Basada en datos SISMED reales con conversión estimada |
| **Demanda inferida** | Aproximada a partir de categoría, no medida directamente |
| **Demanda aproximada por tipología** | Asignada uniformemente dentro de CENTRO o PUESTO |
| **Estimación operacional** | No verificable sin datos de despacho real |

**NO usar**: "demanda exacta", "demanda real por IPRESS", "demanda medida".

---

## 4. Auditoría del Factor de Conversión

### 4.1 Escenarios Evaluados

| Factor | Peso/item | Total mensual | D/C ratio | Interpretación |
|---|---|---|---|---|
| **5g** | 0.005 kg | 8,084 kg | 0.162 | Tabletas puras, sin empaque |
| **10g** | 0.010 kg | 16,169 kg | 0.323 | Mix general con empaque básico |
| **20g** | 0.020 kg | 32,337 kg | 0.647 | Mix con injectables/líquidos |
| **50g** | 0.050 kg | 80,843 kg | 1.617 | Dominado por líquidos/gases |

### 4.2 Impacto en KPIs Estocásticos (200 escenarios)

| Factor | E[cost] | Reliability | Cap Viol | TW Viol | Rutas |
|---|---|---|---|---|---|
| 5g | S/ 4,972 | 55.0% | 45.0% | 0.0% | 9 |
| **10g** | **S/ 8,150** | **6.5%** | **93.5%** | **10.0%** | **10** |
| 20g | S/ 12,232 | 8.5% | 90.0% | 6.5% | 10 |
| 50g | S/ 31,583 | 0.5% | 99.5% | 0.0% | 16 |

### 4.3 Robustez del Hallazgo "Capacity-Driven Risk"

**El hallazgo es ROBUSTO**: En los 4 escenarios de conversión, la tasa de violación de capacidad SIEMPRE domina sobre las violaciones de tiempo. El riesgo por capacidad es estructural, no un artefacto de la conversión.

| Factor | Cap Viol > TW Viol | Dominante |
|---|---|---|
| 5g | 45.0% > 0.0% | CAPACIDAD |
| 10g | 93.5% > 10.0% | CAPACIDAD |
| 20g | 90.0% > 6.5% | CAPACIDAD |
| 50g | 99.5% > 0.0% | CAPACIDAD |

### 4.4 Sensibilidad de la Reliability

La reliability varía dramáticamente:
- 5g: 55% (operacionalmente aceptable)
- 10g: 6.5% (operacionalmente preocupante)
- 20g: 8.5% (similar a 10g)
- 50g: 0.5% (operacionalmente inviable)

**Implicación**: La conclusión sobre reliability depende críticamente del factor de conversión. Con 5g, el sistema es moderadamente robusto; con 10g+, es frágil.

---

## 5. Plausibilidad Farmacéutica del Factor de Conversión

### 5.1 Análisis del Mix de Productos DSRSLCC

Del top 10 por consumo (excluyendo O₂):

| Medicamento | Tipo | Peso aprox/item |
|---|---|---|
| Losartán 50mg tableta | Tableta | 0.5-1g |
| Ác. fólico + ferroso | Tableta | 1-2g |
| Preservativos | Unidad | 3-5g |
| Metformina 850mg | Tableta | 1-2g |
| Paracetamol 500mg | Tableta | 0.8-1.5g |
| Carbonato de calcio | Tableta | 2-3g |
| NaCl 2mL inyectable | Ampolla | 5-10g |
| Ác. acetilsalicílico | Tableta | 0.5-1g |
| Atorvastatina 20mg | Tableta | 0.3-0.5g |

### 5.2 Estimación Razonada

- **Sin empaque**: 1-3g promedio (tabletas dominan >80% del volumen)
- **Con blíster/caja individual**: 3-5g
- **Con empaque logístico (caja de despacho)**: 5-15g
- **Unidad logística completa (con documentación, caja, protección)**: 10-25g

### 5.3 Recomendación

El factor **5-10g/item** es el más plausible para despacho farmacéutico público:
- La distribución de DSRSLCC usa cajas de despacho, no items individuales
- El peso incluye empaque logístico pero no pallets
- Rango defendible: **5-15g/item** con punto medio en **10g/item**

---

## 6. Conclusiones de la Auditoría

1. **El hallazgo "capacity-driven risk" es robusto** independientemente del factor de conversión.

2. **La magnitud del riesgo sí depende del factor**: Con 5g el sistema es moderadamente robusto (55% reliability); con 10g+ es frágil (<10%).

3. **El factor 10g/item es una estimación razonable** pero con incertidumbre significativa (rango 5-15g).

4. **Recomendación para publicación**: Presentar resultados con análisis de sensibilidad del factor (como en este documento), no como valor fijo.

5. **Para calibración definitiva se requiere**: Datos de peso real de despacho de DSRSLCC (no disponibles en SISMED).

---

*Validación de demanda — HVRPTW DSRSLCC*
*Auditoría del factor de conversión item→kg*
*Última actualización: Mayo 2026*
