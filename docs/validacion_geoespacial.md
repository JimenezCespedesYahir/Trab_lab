# Validación Geoespacial Avanzada — HVRPTW DSRSLCC

## 1. Clasificación de Coordenadas Duplicadas

Se identificaron 7 grupos de coordenadas duplicadas (16 nodos afectados). Clasificación:

### 1.1 AMBIGÜEDAD NOMINATIM (5 grupos, 12 nodos)

Nodos en el mismo distrito y categoría donde el geocodificador Nominatim resolvió al mismo punto de referencia (capital distrital o punto genérico).

| Grupo | Nodos | Distrito | Distancia al depósito | Observación |
|---|---|---|---|---|
| 1 | 1916 Chocán, 1923 Huiriquingue, 10726 Joras | AYABACA | 121.8 km | 3 PS rurales, zona montañosa |
| 2 | 1926 El Toldo, 19844 Huilco | AYABACA | 140.0 km | 2 PS remotos en frontera |
| 3 | 1986 Chica Alta, 1987 Sinchi Roca | TAMBO GRANDE | 34.8 km | 2 PS periurbanos |
| 4 | 2035 Mallares, 2038 Saman | MARCAVELICA | 9.0 km | 2 PS cercanos al depósito |
| 6 | 2047 Amotape, 2048 El Tambo | AMOTAPE | 30.5 km | 2 PS en zona costera |

**Acción**: Offset geográfico ±0.001° (~111m) aplicado. Las coordenadas reales de estos establecimientos pueden diferir en 1-10 km. Para el modelo HVRPTW, el impacto es limitado porque los arcos OSRM entre estos nodos y sus vecinos son correctos (basados en la red vial real, no en coordenadas exactas).

### 1.2 ERROR DE GEOCODIFICACIÓN (2 grupos, 5 nodos)

Nodos en **distritos diferentes** con la misma coordenada, indicando que el geocodificador falló en resolver la ubicación exacta.

| Grupo | Nodos | Distritos | Distancia al depósito |
|---|---|---|---|
| 5 | 2037 Tangarará, 2045 Santa Sofía | MARCAVELICA / IGNACIO ESCUDERO | 11.0 km |
| 7 | 2052 S.F. de Chocán, 2056 Puente de los Serranos, 2065 El Alamor | QUERECOTILLO / LANCONES | 18.8 km |

**Impacto**: Moderado. Estos nodos pertenecen a distritos diferentes y deberían tener coordenadas distintas. Los arcos OSRM pueden estar calculados desde una posición incorrecta.

**Recomendación**: Obtener coordenadas GPS reales o usar referencia distrital diferenciada.

---

## 2. Conectividad Operacional

### 2.1 Grafo HVRPTW

| Métrica | Valor |
|---|---|
| Nodos | 81 + 1 depósito = 82 |
| Arcos | 820 (todos bidireccionales) |
| Grafo conexo | **Sí** (BFS bidireccional desde depósito) |
| k-vecinos por nodo | 10 |
| Grado medio | 12.5 (min=10, max=20) |

### 2.2 Nodos Aislados (vecino más cercano > 20 km)

| Nodo | Nombre | Vecino más cercano | Observación |
|---|---|---|---|
| 1965 | CS Lagunas | 41.5 km | Zona montañosa Ayabaca |
| 1921 | PS Remolinos | 33.3 km | Zona fronteriza aislada |
| 1955 | CS Sapillica | 23.6 km | Sierra de Ayabaca |
| 2060 | CS Lancones | 21.3 km | Zona rural Sullana |

**Impacto en HVRPTW**: Estos nodos generan rutas largas con tiempo de viaje significativo. En Fase A determinista, es posible que requieran rutas dedicadas (vehículo asignado exclusivamente).

---

## 3. Anomalías en Arcos

### 3.1 Arcos con Alto Desvío (distancia_OSRM / haversine > 3.0)

Se detectaron **95 arcos** con ratio distancia/haversine > 3.0. Esto indica rutas sinuosas (carreteras de montaña, desvíos por la red vial).

| Arco | Distancia OSRM | Haversine | Ratio | Velocidad | Zona |
|---|---|---|---|---|---|
| Remolinos → El Toldo | 77.9 km | 16.7 km | 4.67 | 67 km/h | Sierra fronteriza |
| Remolinos → Huilco | 77.9 km | 16.7 km | 4.67 | 67 km/h | Sierra fronteriza |
| Espindola → Remolinos | 76.6 km | 21.0 km | 3.65 | 70 km/h | Sierra fronteriza |
| Ayabaca → Rodeopampa | 38.8 km | 11.4 km | 3.41 | 76 km/h | Sierra Ayabaca |
| Chocán → Jililí | 41.6 km | 12.8 km | 3.26 | 40 km/h | Sierra Ayabaca |

**Interpretación**: Los altos ratios son **consistentes con la geografía** de la región (sierra de Ayabaca, carreteras sinuosas). NO son errores de OSRM. Son restricciones reales del modelo.

### 3.2 Distribución de Distancias de Arcos

| Percentil | Distancia |
|---|---|
| P0 (mínimo) | 0.0 km |
| P25 | 9.8 km |
| P50 (mediana) | 21.8 km |
| P75 | 41.4 km |
| P100 (máximo) | 180.7 km |
| Media | 27.6 km |

### 3.3 Arcos con Distancia = 0

Existen arcos con distancia 0.0 km entre nodos con coordenadas duplicadas (pre-offset). Post-offset, estos arcos aún tienen distancia OSRM = 0 porque el servicio OSRM fue consultado con las coordenadas originales.

**Recomendación**: Para el modelo HVRPTW, asignar tiempo/distancia mínima de servicio (ε = 0.1 km, 1 min) a estos arcos para evitar degeneración numérica.

---

## 4. Cobertura Geográfica

### 4.1 Bounding Box

| Coordenada | Valor |
|---|---|
| Lat mínima | -5.2063 (sur, Talara) |
| Lat máxima | -4.1056 (norte, sierra Ayabaca) |
| Lon mínima | -81.3106 (oeste, costa Paita) |
| Lon máxima | -79.4792 (este, sierra fronteriza) |

### 4.2 Distribución por Provincia

| Provincia | Nodos | % | Zona |
|---|---|---|---|
| Sullana | 25 | 30.9% | Costa/valle |
| Ayabaca | 19 | 23.5% | Sierra |
| Paita | 14 | 17.3% | Costa |
| Piura | 13 | 16.0% | Valle |
| Talara | 10 | 12.3% | Costa norte |

### 4.3 Distancia al Depósito

| Rango | Nodos | % |
|---|---|---|
| 0–20 km | 22 | 27.2% |
| 20–50 km | 18 | 22.2% |
| 50–100 km | 27 | 33.3% |
| >100 km | 14 | 17.3% |

---

## 5. Riesgos y Recomendaciones

| Riesgo | Severidad | Recomendación |
|---|---|---|
| 16 nodos con coordenadas duplicadas | MEDIA | Obtener GPS real; offset actual es operacional |
| 4 nodos aislados (>20km a vecino) | BAJA | Considerar rutas dedicadas en Fase A |
| 95 arcos con alto desvío | INFO | Consistente con geografía; no requiere acción |
| Arcos con distancia=0 | BAJA | Asignar ε mínimo para estabilidad numérica |
| 2 grupos con error de geocodificación | MEDIA | Validar con coordenadas reales |

---

*Validación geoespacial avanzada — Proyecto HVRPTW DSRSLCC*
*Última actualización: Mayo 2026*
