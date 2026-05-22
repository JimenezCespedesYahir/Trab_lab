# Calibración de Demanda Logística — Metodología SISMED

## 1. Diagnóstico de Datos Disponibles

### 1.1 Modelo Semántico PowerBI Identificado

Se identificaron las siguientes tablas relevantes en el modelo PowerBI DSRSLCC:

| Tabla | Campos clave | Rol |
|---|---|---|
| `data_historica_dispo12_consumo` | codigo_pre, codigo_med, mesano, stock, m_consumo, cc_items | Tabla de hechos (consumo/stock) |
| `CATALOGO_IPRESS_AEMS` | codpre_, DESCRIP, Categoria, Red, micro_red, Niveles | Dimensión establecimientos |
| `medicame` | CODIGO_MED, MEDICAMENT, TIPO, FF, ESTRATEGIC | Dimensión medicamentos |
| `Tb_listado_atc` | CODIGO_MED, ATC_1_Niv..ATC_5_Niv, Factor_Conversion_Uso | Clasificación ATC |
| `Periodo_variable` | Periodo_variable | Dimensión temporal |

### 1.2 Datos Extraídos

| Dataset | Registros | Contenido | Limitación |
|---|---|---|---|
| `sismed_sample_metotrexato.csv` | 314 | Consumo/stock de METOTREXATO 2.5mg | **Solo 1 producto** |
| `sismed_model_structure.csv` | 42 campos | Estructura completa del modelo | Solo metadatos, no datos |

### 1.3 Hallazgo Crítico

**Los datos SISMED completos NO han sido extraídos del PowerBI.** El repositorio contiene:
- La estructura del modelo semántico (tablas, campos, tipos)
- Queries de consulta (payloads PowerBI)
- **Solo 1 producto de muestra** (METOTREXATO 2.5mg TABLETA, código 04764)

La extracción de datos SISMED por establecimiento requiere una operación adicional contra el PowerBI DSRSLCC que aún no se ha realizado.

---

## 2. Metodología de Demanda Logística Propuesta

### 2.1 Definición del Problema

Convertir datos SISMED (items de medicamentos por establecimiento-periodo) en **demanda logística agregada** (kg/toneladas por establecimiento-periodo) para el modelo HVRPTW.

### 2.2 Fórmula Operacional Recomendada: CPMA Ponderado

**CPMA** = Consumo Promedio Mensual Ajustado

$$
d_i = \sum_{m \in \mathcal{M}} \text{CPMA}_{i,m} \times w_m
$$

donde:
- $d_i$: demanda logística del nodo $i$ (kg/mes)
- $\mathcal{M}$: conjunto de medicamentos distribuidos al nodo $i$
- $\text{CPMA}_{i,m}$: consumo promedio mensual ajustado del medicamento $m$ en el nodo $i$ (unidades/mes)
- $w_m$: peso unitario del medicamento $m$ (kg/unidad)

### 2.3 Cálculo del CPMA

$$
\text{CPMA}_{i,m} = \frac{\sum_{t \in T_{activo}} c_{i,m,t}}{|T_{activo}|}
$$

donde:
- $c_{i,m,t}$: consumo del medicamento $m$ en el establecimiento $i$ durante el periodo $t$
- $T_{activo}$: periodos con consumo > 0 (excluir meses sin movimiento para evitar sesgo)

**Justificación**: CPMA es la métrica estándar del SISMED peruano para programación de necesidades. Es preferible al promedio simple porque excluye periodos con desabastecimiento (consumo = 0 por falta de stock, no por falta de demanda).

### 2.4 Alternativas Evaluadas

| Alternativa | Ventajas | Desventajas | Recomendación |
|---|---|---|---|
| **CPMA ponderado** | Estándar SISMED, robusto a desabastecimiento | Requiere datos de peso unitario | **Recomendada** |
| Consumo promedio simple | Simple de calcular | Sesgado por desabastecimiento | No recomendada |
| Stock promedio | Disponible más fácilmente | No refleja demanda real | No recomendada |
| Demanda híbrida (CPMA + stock) | Más información | Compleja de justificar | Alternativa futura |
| Ponderación multicriterio | Flexible | Subjetiva | No recomendada inicialmente |

### 2.5 Conversión a Demanda Logística (kg)

Requiere la tabla de pesos unitarios por presentación farmacéutica:

$$
d_i^{kg} = \sum_{m \in \mathcal{M}} \text{CPMA}_{i,m} \times w_m^{kg}
$$

**Fuentes de peso unitario**:
1. Petitorio Nacional Único de Medicamentos Esenciales (PNUME)
2. Base de datos DIGEMID
3. Estimación por forma farmacéutica y concentración

---

## 3. Análisis de la Muestra Disponible (METOTREXATO)

### 3.1 Estadísticos Descriptivos

Basado en los 314 registros extraídos:

| Variable | Valor |
|---|---|
| Producto | METOTREXATO 2.5 mg TABLETA |
| Código | 04764 |
| Periodos | 61 (abril 2021 — abril 2026) |
| Categorías EE.SS. | CENTRO, HOSPITAL, FARMACIA, INSTITUTO, PUESTO |
| Tipo suministro | D (Demanda), S (Stock) |

### 3.2 Consumo por Categoría (tipo S = Stock)

| Categoría | Total acumulado | Periodos con stock | Media mensual |
|---|---|---|---|
| HOSPITAL | 6,559,695 | 61/61 | 107,536 |
| INSTITUTO | 874,693 | 61/61 | 14,339 |
| FARMACIA INSTITUCIONAL | 61,932 | 60/61 | 1,032 |
| CENTRO | 33,767 | 60/61 | 563 |
| PUESTO | 1,764 | 35/61 | 50 |

### 3.3 Observaciones Metodológicas

1. **Escala de diferencias**: El consumo entre HOSPITAL y PUESTO difiere en ~2,000x. Esto es consistente con la realidad (hospitales tienen mayor complejidad y volumen).
2. **Intermitencia en PUESTO**: Solo 35/61 periodos con stock, indicando distribución irregular o desabastecimiento frecuente.
3. **Un solo producto**: Esta muestra NO es representativa para calibrar demanda logística total. Se necesitan datos de TODOS los productos.

---

## 4. Estrategia de Demanda Placeholder Justificada

### 4.1 Mientras No Hay Datos SISMED Completos

En ausencia de datos SISMED completos, se utiliza una **estimación por categoría** basada en:

1. **Literatura**: estándares MINSA de dotación farmacéutica por nivel de atención
2. **Proporcionalidad**: ratio observado en muestra (CENTRO/PUESTO ≈ 10:1 en stock)
3. **Orden de magnitud**: distribución mensual regional ≈ 20-30 toneladas para ~80 establecimientos

### 4.2 Valores Placeholder Actuales

| Categoría | demand_mean (kg) | demand_std (kg) | CV | Justificación |
|---|---|---|---|---|
| Centro de Salud | 500 | 100 | 0.20 | Nivel I-3/I-4, mayor volumen |
| Puesto de Salud | 200 | 50 | 0.25 | Nivel I-1/I-2, menor volumen, mayor variabilidad |
| Otro | 300 | 75 | 0.25 | Promedio intermedio |

**Estado de calibración**: `PLACEHOLDER` — requiere reemplazo con datos SISMED reales.

### 4.3 Análisis de Sensibilidad Recomendado

Para evaluar robustez del modelo HVRPTW ante incertidumbre en la calibración:

| Escenario | Factor | demand_mean CS | demand_mean PS |
|---|---|---|---|
| Base (placeholder) | 1.0x | 500 kg | 200 kg |
| Demanda baja | 0.5x | 250 kg | 100 kg |
| Demanda alta | 1.5x | 750 kg | 300 kg |
| Demanda extrema | 2.0x | 1,000 kg | 400 kg |

---

## 5. Ruta Crítica para Calibración Real

### Paso 1: Extracción SISMED (prioridad ALTA)

Extraer de PowerBI DSRSLCC la tabla `data_historica_dispo12_consumo` con:
- Filtro: `codigo_pre` ∈ {códigos de los 81 nodos HVRPTW}
- Campos: `codigo_pre, codigo_med, mesano, m_consumo, stock, cc_items, m_precio`
- Periodo: últimos 24 meses (mínimo 12)

### Paso 2: Tabla de Pesos Unitarios

Obtener peso por unidad de presentación farmacéutica para convertir items → kg.
- Fuente: DIGEMID, PNUME, o estimación por forma farmacéutica

### Paso 3: Cálculo CPMA por Establecimiento

```
Para cada establecimiento i:
  Para cada medicamento m:
    CPMA_im = promedio(consumo_imt para t con consumo > 0)
  demanda_i_kg = SUM(CPMA_im * peso_m)
  demanda_i_std = STD(SUM_mensual(consumo_imt * peso_m))
  CV_i = demanda_i_std / demanda_i_kg
```

### Paso 4: Identificación Cadena de Frío

```
cold_chain_i = 1 si SUM(cc_items_im) > 0 para algún m
```

### Paso 5: Validación Estadística

- Distribución de demanda por categoría (histograma, box-plot)
- Test de normalidad (Shapiro-Wilk, Kolmogorov-Smirnov)
- Detección de outliers (IQR, Z-score)
- Análisis de estacionalidad (descomposición aditiva/multiplicativa)
- Autocorrelación temporal

---

## 6. Limitaciones y Riesgos

| Limitación | Impacto | Mitigación |
|---|---|---|
| Solo 1 producto extraído | No representativo | Extracción completa SISMED requerida |
| Sin tabla de pesos unitarios | No se puede convertir items → kg | Estimación por FF o datos DIGEMID |
| Periodos futuros en datos (2025-2026) | Datos proyectados, no reales | Filtrar a periodos históricos confirmados |
| Desabastecimiento oculta demanda | CPMA puede subestimar | Usar solo periodos con stock > 0 |
| Agregación por categoría pierde heterogeneidad | Establecimientos similares tratados igual | Calibrar individualmente cuando datos disponibles |

---

*Documento de calibración — Proyecto HVRPTW DSRSLCC*
*Estado: En proceso — datos SISMED parciales*
*Última actualización: Mayo 2026*
