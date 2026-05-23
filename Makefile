###############################################################################
# Makefile — Pipeline Científico HVRPTW DSRSLCC
#
# Uso:
#   make install        Instalar dependencias
#   make baseline       Ejecutar baseline HVRPTW determinista
#   make montecarlo     Monte Carlo completo (500 escenarios)
#   make validate       Validación científica completa
#   make figures        Generar 24 figuras + 7 tablas
#   make paper          Generar 8 figuras paper-ready (PDF+PNG)
#   make all            Pipeline completa A→G
#   make clean          Limpiar resultados generados
#   make check          Sanity checks rápidos
###############################################################################

PYTHON ?= python3
SEED ?= 42
MC_SCENARIOS ?= 500
SOLVER_TIME ?= 120

.PHONY: all install baseline montecarlo validate figures paper clean check help

help:  ## Mostrar ayuda
	@echo "╔══════════════════════════════════════════╗"
	@echo "║  HVRPTW Estocástico DSRSLCC — Makefile   ║"
	@echo "╚══════════════════════════════════════════╝"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Instalar dependencias
	$(PYTHON) -m pip install -r requirements.txt

# ─── Etapa C: Baseline ───
baseline: results/baseline_kpis.csv  ## Ejecutar baseline HVRPTW

results/baseline_kpis.csv: src/baseline_hvrptw_ortools.py analytics/nodes_hvrptw.csv
	$(PYTHON) src/baseline_hvrptw_ortools.py --time-limit $(SOLVER_TIME)

# ─── Etapa D: Monte Carlo ───
montecarlo: results/montecarlo_results_$(MC_SCENARIOS).csv  ## Monte Carlo (MC_SCENARIOS=500)

results/montecarlo_results_$(MC_SCENARIOS).csv: src/montecarlo_hvrptw.py results/baseline_routes.csv
	$(PYTHON) -c "\
	import sys; sys.path.insert(0, 'src'); \
	from montecarlo_hvrptw import run_montecarlo_evaluation; \
	import csv, os; \
	results = run_montecarlo_evaluation(n_scenarios=$(MC_SCENARIOS), seed=$(SEED)); \
	os.makedirs('results', exist_ok=True); \
	f = open('results/montecarlo_results_$(MC_SCENARIOS).csv', 'w', newline=''); \
	w = csv.DictWriter(f, fieldnames=results[0].keys()); \
	w.writeheader(); w.writerows(results); f.close(); \
	print(f'MC done: {len(results)} scenarios')"

# ─── Etapa E: Validación ───
validate:  ## Validación científica completa
	cd src && $(PYTHON) validacion_cientifica.py

# ─── Etapa F: Figuras ───
figures:  ## Generar 24 figuras + 7 tablas (300 DPI)
	$(PYTHON) src/visualizaciones_cientificas_finales.py

# ─── Etapa G: Paper ───
paper:  ## Generar 8 figuras paper-ready (PDF+PNG)
	$(PYTHON) src/paper_ready_figures.py

# ─── Pipeline completa ───
all: install baseline montecarlo validate figures paper  ## Pipeline completa A→G
	@echo ""
	@echo "╔══════════════════════════════════════════╗"
	@echo "║  Pipeline Científica Completa — DONE     ║"
	@echo "║  Baseline → MC → Validación → Figuras    ║"
	@echo "╚══════════════════════════════════════════╝"

# ─── Sanity checks ───
check:  ## Sanity checks rápidos
	@echo "=== Dataset validation ==="
	@$(PYTHON) -c "import csv; \
	for f in ['analytics/nodes_hvrptw.csv','analytics/arcs_with_variability.csv','analytics/vehicles_hvrptw.csv']: \
	    rows = list(csv.DictReader(open(f))); print(f'  {f}: {len(rows)} rows')"
	@echo "=== Results check ==="
	@ls -la results/*.csv 2>/dev/null || echo "  No results yet (run 'make baseline')"
	@echo "=== Figures check ==="
	@ls results/figures_final/*.png 2>/dev/null | wc -l | xargs -I{} echo "  figures_final: {} PNGs"
	@ls results/figures_paper/*.png 2>/dev/null | wc -l | xargs -I{} echo "  figures_paper: {} PNGs"
	@echo "=== Done ==="

# ─── Limpieza ───
clean:  ## Limpiar resultados generados (NO borra datos)
	rm -rf results/figures_final/* results/figures_paper/* results/final_tables/*
	@echo "Cleaned generated outputs (data preserved)"
