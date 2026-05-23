# Pipeline de Reproducibilidad Científica

## Resumen

Este documento describe cómo reproducir completamente la investigación
*Fragilidad Operacional de Flota bajo Incertidumbre Dual en un HVRPTW Farmacéutico: Caso DSRSLCC–Sullana*.

La pipeline reproduce todas las etapas desde datos hasta figuras publicables,
garantizando determinismo mediante semillas fijas y trazabilidad total.

---

## Requisitos

| Componente | Versión | Nota |
|-----------|---------|------|
| Python | ≥3.12 | Probado con 3.12.8 |
| OR-Tools | ≥9.8 | Solver HVRPTW |
| NumPy | ≥1.26 | Simulación MC |
| SciPy | ≥1.12 | KDE, estadística |
| Matplotlib | ≥3.8 | Visualización |
| Pandas | ≥2.1 | Datos |
| Pillow | ≥10.0 | Verificación DPI |

Instalación:
```bash
pip install -r requirements.txt
```

---

## Ejecución Rápida

```bash
# Pipeline completa (45–90 min)
make all

# Solo baseline determinista (2 min)
make baseline

# Solo Monte Carlo 500 escenarios (10–15 min)
make montecarlo

# Solo figuras (2 min, requiere resultados previos)
make figures

# Solo paper-ready (1 min)
make paper

# Sanity checks
make check
```

---

## Pipeline Detallada (Etapas A–G)

### Etapa A — Preprocessing y Calibración SISMED

**Datos de entrada:**
- `analytics/nodes_hvrptw.csv` — 81 IPRESS con coordenadas, demanda, categoría
- `analytics/vehicles_hvrptw.csv` — 4 tipos de vehículo, 16 unidades
- `analytics/arcs_with_variability.csv` — 820 arcos con distancias OSRM
- `analytics/demand_calibrated.csv` — Demanda calibrada SISMED

**Metodología de calibración:**
- CPMA (Consumo Promedio Mensual Ajustado) como variable base
- Ratio CENTRO/PUESTO = 2.31:1 (extraído de SISMED real)
- CV demanda: CS=0.42, PS=0.45
- Factor de conversión items→kg: 10g/item (sensibilidad 5g–50g documentada)

**Documentación:** `docs/calibracion_demanda_sismed.md`

### Etapa B — Red Vial y Validación Geoespacial

**Validaciones:**
- Conectividad: 81/81 nodos alcanzables desde depósito (BFS)
- Coordenadas: rango válido Piura (-3.5° a -5.5° lat, -79° a -82° lon)
- Duplicados: 7 grupos corregidos con offset ±0.001°
- Arcos: 820 bidireccionales, distancias 0.1–309 km

**Documentación:** `docs/validacion_geoespacial.md`

### Etapa C — Baseline HVRPTW Determinista

```bash
python src/baseline_hvrptw_ortools.py --time-limit 120
```

**Solver:** OR-Tools Guided Local Search (GLS), 120 segundos
**Resultados:**
- 10 rutas, S/ 5,089, 1,962 km
- 81/81 nodos servidos (100% cobertura)
- Utilización media 71.8%
- Runtime: ~120s, ~1500 soluciones exploradas

**Salida:** `results/baseline_kpis.csv`, `results/baseline_routes.csv`

### Etapa D — Monte Carlo + Sensibilidad

```bash
make montecarlo MC_SCENARIOS=500
```

**Parámetros:**
- Demanda: Normal truncada, CV=0.42 (CS) / 0.45 (PS)
- Tiempos: LogNormal, CV=0.20
- Semilla: 42 (reproducible)
- Escenarios: 500 (piloto), 2000 (completo)

**Salida:** `results/montecarlo_results_500.csv`

### Etapa E — Validación Científica

```bash
make validate
```

**Ejecuta:**
- Sensibilidad item→kg (5g, 10g, 20g, 50g)
- Convergencia MC (100, 500, 1000, 2000 escenarios)
- 10 experimentos de flota (baseline, +cap, -Hilux, buffers)
- Cálculo de ratio slack/variabilidad

**Salida:**
- `results/sensitivity_conversion_factor.csv`
- `results/convergence_analysis.csv`
- `results/capacity_experiments.csv`
- `results/sensitivity_analysis.csv`

### Etapa F — Figuras Científicas

```bash
make figures
```

**Genera:** 24 figuras × 2 formatos (PNG 300 DPI + SVG) = 48 archivos
**Salida:** `results/figures_final/`, `results/final_tables/`

### Etapa G — Paper-Ready

```bash
make paper
```

**Genera:** 8 figuras × 2 formatos (PNG 300 DPI + PDF vectorial) = 16 archivos
**Salida:** `results/figures_paper/`

---

## Control de Reproducibilidad

### Seeds Fijas

| Componente | Semilla | Localización |
|-----------|---------|-------------|
| Monte Carlo | 42 | `montecarlo_hvrptw.py:seed` |
| NumPy RNG | 42 | `np.random.seed(42)` |
| OR-Tools | Determinista | `first_solution_strategy=PATH_CHEAPEST_ARC` |

### Determinismo

- El baseline OR-Tools GLS es cuasi-determinista (mismo resultado con mismo time-limit)
- Monte Carlo con seed=42 produce resultados idénticos entre ejecuciones
- Las figuras son reproducibles (mismos datos → mismas figuras)

### Trazabilidad

```
analytics/nodes_hvrptw.csv      → src/baseline_hvrptw_ortools.py
analytics/arcs_with_variability.csv  → results/baseline_routes.csv
analytics/demand_calibrated.csv      → results/baseline_kpis.csv
                                         ↓
results/baseline_routes.csv     → src/montecarlo_hvrptw.py
                                → results/montecarlo_results_500.csv
                                → results/stochastic_kpis_500.csv
                                         ↓
results/montecarlo_results_500.csv → src/validacion_cientifica.py
                                   → results/convergence_analysis.csv
                                   → results/sensitivity_analysis.csv
                                   → results/capacity_experiments.csv
                                         ↓
results/*.csv                  → src/visualizaciones_cientificas_finales.py
                               → results/figures_final/ (48 archivos)
                               → results/final_tables/ (7 CSV)
                                         ↓
results/*.csv                  → src/paper_ready_figures.py
                               → results/figures_paper/ (16 archivos)
```

---

## Verificación

```bash
# Verificar datasets
make check

# Verificar calidad de figuras (300 DPI)
python -c "
from PIL import Image
import os
for d in ['results/figures_final', 'results/figures_paper']:
    for f in sorted(os.listdir(d)):
        if f.endswith('.png'):
            dpi = Image.open(os.path.join(d, f)).info.get('dpi', (0,0))
            print(f'{f}: {dpi[0]}x{dpi[1]} DPI')
"

# Verificar reproducibilidad
python src/baseline_hvrptw_ortools.py --time-limit 120
# Comparar results/baseline_kpis.csv con versión anterior
```

---

## Estructura del Repositorio

```
Trab_lab/
├── analytics/               # Datos maestros (NO generados)
│   ├── nodes_hvrptw.csv
│   ├── arcs_with_variability.csv
│   ├── vehicles_hvrptw.csv
│   ├── demand_calibrated.csv
│   └── sismed_raw/
├── src/                     # Código fuente
│   ├── baseline_hvrptw_ortools.py
│   ├── montecarlo_hvrptw.py
│   ├── validacion_cientifica.py
│   ├── visualizaciones_cientificas_finales.py
│   └── paper_ready_figures.py
├── results/                 # Resultados generados
│   ├── figures_final/       # 24 figuras (PNG+SVG)
│   ├── figures_paper/       # 8 figuras paper (PNG+PDF)
│   ├── final_tables/        # 7 tablas CSV
│   └── visual_gallery/      # Galería HTML
├── docs/                    # Documentación científica
├── .github/workflows/       # CI/CD
├── Makefile
└── requirements.txt
```
