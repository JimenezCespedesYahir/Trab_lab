# Validación de Flota — HVRPTW DSRSLCC

## 1. Flota Actualizada

### 1.1 Cantidades Corregidas

| Vehículo | Capacidad | Refrigeración | Cantidad anterior | **Cantidad corregida** |
|---|---|---|---|---|
| V1 FUSO Canter 6T | 6,000 kg | No | 2 | **4** |
| V2 Fiat Ducato Refrigerada | 3,000 kg | Sí | 1 | **2** |
| V3 NLR 3.5 TON | 3,500 kg | No | 2 | **4** |
| V4 Toyota Hilux | 1,000 kg | No | 2 | **6** |
| **Total** | — | — | **7** | **16** |

### 1.2 Capacidad Total

| Métrica | Valor anterior | **Valor corregido** |
|---|---|---|
| Vehículos totales | 7 | **16** |
| Capacidad total (1 viaje) | 24,000 kg | **50,000 kg** |
| Capacidad refrigerada | 3,000 kg | **6,000 kg** |
| Capacidad no refrigerada | 21,000 kg | **44,000 kg** |

---

## 2. Suficiencia Operacional

### 2.1 Análisis Demanda vs Capacidad

| Escenario | Demanda total (kg) | Capacidad (kg) | Ratio D/C | Suficiencia |
|---|---|---|---|---|
| Placeholder actual | 26,700 | 50,000 | 0.53 | **Sí** — 53% utilización |
| Demanda × 1.5 | 40,050 | 50,000 | 0.80 | **Sí** — 80% utilización |
| Demanda × 2.0 | 53,400 | 50,000 | 1.07 | **Marginal** — requiere 2 viajes |

### 2.2 Cobertura por Tipo de Vehículo

| Vehículo | Capacidad unitaria | Nodos que puede servir solo | Uso típico |
|---|---|---|---|
| FUSO 6T | 6,000 kg | Cualquier CS o PS individual | Rutas principales, alto volumen |
| Fiat Ducato | 3,000 kg | CS medio o múltiples PS | Cadena de frío (cuando activa) |
| NLR 3.5T | 3,500 kg | CS medio o múltiples PS | Rutas secundarias |
| Toyota Hilux | 1,000 kg | 1-5 PS pequeños | Zonas rurales/remotas, acceso difícil |

### 2.3 Análisis de Utilización Esperada

Con demanda placeholder (26.7 ton) y 50 ton de capacidad:

- **Utilización global**: 53% — hay exceso de capacidad
- **Vehículos necesarios** (estimación): ~8-10 de 16 (depende de clustering geográfico)
- **Rutas esperadas**: 8-12 rutas por ciclo de distribución

### 2.4 Factores Operacionales

| Factor | Valor | Impacto |
|---|---|---|
| Autonomía mínima | 350 km (Ducato) | Cubre ida y vuelta al nodo más lejano (282.8 km) |
| Nodo más lejano | 141.4 km (PS Espíndola) | Requiere ruta dedicada (ida+vuelta ≈ 5h) |
| Velocidad promedio ponderada | ~58 km/h | Aceptable para red vial mixta |
| Jornada operativa | 8h (08:00-16:00) | Limita distancia máxima por ruta a ~230 km |

---

## 3. Compatibilidad con Modelo HVRPTW

### 3.1 Estructura del Problema

| Parámetro | Valor |
|---|---|
| Nodos (clientes) | 81 |
| Tipos de vehículo | 4 |
| Vehículos totales | 16 |
| Depósito | 1 (DSRSLCC Sullana) |
| Restricciones activas | Capacidad, ventanas de tiempo, retorno a depósito |
| Cadena de frío | Preparada, no activa |

### 3.2 Complejidad Computacional

- Espacio de búsqueda: O(n! × k) donde n=81 nodos, k=16 vehículos
- Clase: NP-hard
- Solver recomendado: OR-Tools CP-SAT / Routing para Fase A

---

## 4. Costos Operacionales Estimados

### 4.1 Estructura de Costos

| Componente | Fórmula | Unidad |
|---|---|---|
| Costo variable | Σ (distancia_ruta × cost_per_km) | S/ |
| Costo fijo | Σ (fixed_cost × vehículos_usados) | S/ por ciclo |
| Costo total | Variable + Fijo | S/ por ciclo |

### 4.2 Estimación de Costos (placeholder)

Con distancia promedio de ~55 km al nodo y ~10 rutas:

| Componente | Estimación |
|---|---|
| Distancia total estimada | ~800-1,200 km por ciclo |
| Costo variable | ~S/ 2,000-3,000 |
| Costo fijo | ~S/ 1,000-1,500 (8-10 vehículos) |
| **Costo total estimado** | **S/ 3,000-4,500 por ciclo** |

**Nota**: Estimación preliminar. Los KPIs reales se calcularán con el baseline OR-Tools.

---

## 5. Observaciones

1. **Exceso de capacidad**: Con 50 ton de capacidad y 26.7 ton de demanda placeholder, hay margen operacional significativo. Esto es positivo para robustez.
2. **Solo 2 refrigerados**: Si cadena de frío se activa, la capacidad refrigerada (6 ton) puede ser limitante. Monitorear cuando datos SISMED cc_items disponibles.
3. **Toyota Hilux** (6 unidades): Capacidad unitaria baja (1 ton) pero útil para nodos remotos con acceso difícil.
4. **Jornada de 8h**: Limita la distancia máxima por ruta. Nodos >100 km (14 nodos, 17%) pueden requerir rutas dedicadas.

---

*Validación de flota — Proyecto HVRPTW DSRSLCC*
*Flota actualizada: 4+2+4+6 = 16 vehículos, 50 ton capacidad total*
*Última actualización: Mayo 2026*
