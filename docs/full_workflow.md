# Workflow Completo — De Datos a Paper

## Guía Paso a Paso

Este documento describe cómo reproducir la investigación completa
desde cero, tanto localmente como via GitHub Actions.

---

## Opción 1: Ejecución Local (Makefile)

### Paso 1 — Setup
```bash
git clone https://github.com/JimenezCespedesYahir/Trab_lab.git
cd Trab_lab
make install
```

### Paso 2 — Baseline HVRPTW
```bash
make baseline
# Output: results/baseline_kpis.csv, results/baseline_routes.csv
# Runtime: ~2 min
```

### Paso 3 — Monte Carlo
```bash
make montecarlo MC_SCENARIOS=500
# Output: results/montecarlo_results_500.csv
# Runtime: ~10–15 min
```

### Paso 4 — Validación Científica
```bash
make validate
# Output: results/convergence_analysis.csv, results/capacity_experiments.csv
# Runtime: ~20–30 min
```

### Paso 5 — Figuras
```bash
make figures
# Output: results/figures_final/ (48 archivos)
# Runtime: ~2 min
```

### Paso 6 — Paper-Ready
```bash
make paper
# Output: results/figures_paper/ (16 archivos)
# Runtime: ~1 min
```

### Paso 7 — Verificar
```bash
make check
```

### Pipeline Completa (una línea)
```bash
make all
# Ejecuta steps 1–6 secuencialmente
# Runtime total: ~45–60 min
```

---

## Opción 2: GitHub Actions

### CI Automática
Cada push ejecuta automáticamente la CI liviana:
- Validación de datasets
- Conectividad geoespacial
- Baseline reducido (30s)
- MC mini (10 escenarios)
- Sanity checks

### Pipeline Completa (Manual)
1. Ir a [Actions](../../actions) → `Full Scientific Pipeline`
2. Click `Run workflow`
3. Configurar:
   - `mc_scenarios`: 500 (default) o 2000 (completo)
   - `solver_time_limit`: 120 (default)
4. Esperar ~60–90 min
5. Descargar artefactos:
   - `scientific-figures`: 24+8 figuras
   - `scientific-tables`: 7 tablas CSV
   - `scientific-results`: KPIs, MC, sensibilidad

### Regenerar Solo Figuras
1. [Actions](../../actions) → `Regenerate Figures`
2. `paper_only`: false (24+8) o true (solo 8 paper)
3. Descargar artefacto `figures-{sha}`

---

## Opción 3: Script por Script

```bash
# 1. Baseline
python src/baseline_hvrptw_ortools.py --time-limit 120

# 2. Monte Carlo
python -c "
import sys; sys.path.insert(0, 'src')
from montecarlo_hvrptw import run_montecarlo_evaluation
import csv
results = run_montecarlo_evaluation(n_scenarios=500, seed=42)
with open('results/montecarlo_results_500.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=results[0].keys())
    w.writeheader(); w.writerows(results)
"

# 3. Validación científica
cd src && python validacion_cientifica.py && cd ..

# 4. Figuras (24)
python src/visualizaciones_cientificas_finales.py

# 5. Paper-ready (8)
python src/paper_ready_figures.py
```

---

## Personalización

### Cambiar número de escenarios MC
```bash
make montecarlo MC_SCENARIOS=2000
```

### Cambiar semilla
```bash
make montecarlo SEED=123
```

### Cambiar time-limit del solver
```bash
make baseline SOLVER_TIME=300
```

### Usar Python específico
```bash
make all PYTHON=python3.12
```

---

## Outputs Esperados

| Carpeta | Contenido | Archivos |
|---------|-----------|----------|
| `results/` | KPIs, rutas, MC, sensibilidad | ~10 CSV |
| `results/figures_final/` | 24 figuras científicas | 48 (PNG+SVG) |
| `results/figures_paper/` | 8 figuras paper-ready | 16 (PNG+PDF) |
| `results/final_tables/` | 7 tablas publicables | 7 CSV |
| `results/visual_gallery/` | Galería HTML interactiva | 1 HTML |

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: ortools` | `pip install ortools>=9.8` |
| `FileNotFoundError: baseline_routes.csv` | Ejecutar `make baseline` primero |
| `Figuras vacías` | Verificar que existen CSVs en `results/` |
| `MC tarda mucho` | Reducir `MC_SCENARIOS=100` para prueba |
| `OR-Tools no converge` | Aumentar `SOLVER_TIME=300` |
