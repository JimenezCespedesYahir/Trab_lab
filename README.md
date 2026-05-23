# HVRPTW Estocástico — DSRSLCC Sullana

![CI](https://github.com/JimenezCespedesYahir/Trab_lab/actions/workflows/ci_light.yml/badge.svg)

> **Fragilidad Operacional de Flota bajo Incertidumbre Dual en un HVRPTW Farmacéutico: Caso DSRSLCC–Sullana**

Investigación en Optimización Estocástica aplicada a logística farmacéutica pública.
Framework reproducible: SISMED → OSRM → OR-Tools → Monte Carlo → Visualización científica.

## Hallazgo Principal

La optimización determinista de costo asigna Toyota Hilux (S/ 1.5/km) a 50% de las rutas,
operando al 95%+ de capacidad. Bajo incertidumbre SISMED (CV=0.42), la route reliability
colapsa al 6%. Reemplazar Hilux por NLR: reliability 6% → 96%, costo +6%.

**Ratio slack/variabilidad**: Hilux = 0.11 (40× peor que la dimensión temporal = 4.38).

## Ejecución Rápida

```bash
pip install -r requirements.txt

# Pipeline completa (~60 min)
make all

# Solo baseline (~2 min)
make baseline

# Solo figuras (~2 min)
make figures
```

## Estructura

```
analytics/          Datos maestros (IPRESS, arcos, flota, demanda SISMED)
src/                Código fuente (baseline, MC, validación, visualización)
results/            Resultados generados (KPIs, figuras, tablas)
docs/               Documentación científica
.github/workflows/  CI liviana + pipeline completa + figuras + validación
```

## Workflows GitHub Actions

| Workflow | Trigger | Descripción |
|----------|---------|-------------|
| `ci_light.yml` | Push/PR | Validación rápida (<10 min) |
| `full_pipeline.yml` | Manual | Pipeline completa A→G (~60 min) |
| `figures.yml` | Manual | Regenerar figuras |
| `validation.yml` | Manual | Auditoría científica |

## Documentación

- [`docs/reproducibility_pipeline.md`](docs/reproducibility_pipeline.md) — Cómo reproducir la investigación
- [`docs/figure_index.md`](docs/figure_index.md) — Índice maestro de 24 figuras
- [`docs/scientific_contribution.md`](docs/scientific_contribution.md) — Contribución científica
- [`docs/full_workflow.md`](docs/full_workflow.md) — Guía paso a paso

## Datasets

| Dataset | Registros | Fuente |
|---------|-----------|--------|
| IPRESS | 81 nodos | Nominatim geocoding |
| Red vial | 820 arcos | OSRM distances |
| Flota | 16 vehículos (4 tipos) | DSRSLCC inventario |
| Demanda | SISMED calibrada | PowerBI DSRSLCC |

## Resultados

| Métrica | Determinista | Estocástico |
|---------|-------------|-------------|
| Costo | S/ 5,089 | S/ 8,160 (+61%) |
| Reliability | 100% | 5.9% |
| CVaR 5% | — | S/ 14,021 |
| Cap violations | 0% | 93.5% |
