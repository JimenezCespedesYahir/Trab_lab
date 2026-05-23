# GitHub Actions — Workflows CI/CD

## Arquitectura

El repositorio usa 4 workflows separados para mantener claridad y eficiencia:

| Workflow | Archivo | Trigger | Runtime |
|----------|---------|---------|---------|
| CI Liviana | `ci_light.yml` | Push / PR | <10 min |
| Full Pipeline | `full_pipeline.yml` | Manual | 45–90 min |
| Figuras | `figures.yml` | Manual | <5 min |
| Validación | `validation.yml` | Manual | 15–60 min |

---

## 1. CI Liviana (`ci_light.yml`)

**Trigger:** automático en cada push y PR

**Ejecuta:**

| Step | Descripción | Criterio |
|------|-------------|----------|
| Datasets | Existencia, formato, columnas | 4 CSVs, min rows, required cols |
| Geoespacial | Conectividad BFS desde depósito | 81/81 alcanzables |
| Baseline | OR-Tools GLS con 30s time-limit | Smoke test |
| MC mini | 10 escenarios con seed=42 | Sin errores |
| Figuras | Import de módulos de visualización | Sin errores |
| Seeds | Reproducibilidad de NumPy RNG | Determinismo |

**Runtime:** ~5–8 minutos

---

## 2. Full Pipeline (`full_pipeline.yml`)

**Trigger:** manual via `workflow_dispatch`

**Parámetros configurables:**

| Parámetro | Default | Opciones |
|-----------|---------|----------|
| `mc_scenarios` | 500 | 100–2000 |
| `solver_time_limit` | 120 | 30–300 |
| `run_convergence` | true | true/false |
| `run_fleet_experiments` | true | true/false |

**Etapas:**

```
A: Preprocessing     → Validar CSVs
B: Red vial          → BFS, distancias
C: Baseline HVRPTW   → OR-Tools GLS
D: Monte Carlo       → N escenarios, VaR/CVaR
E: Validación        → Convergencia, sensibilidad, flota
F: Figuras (24)      → PNG 300 DPI + SVG
G: Paper-ready (8)   → PNG 300 DPI + PDF
```

**Artefactos:** figuras, tablas y resultados CSV se suben automáticamente (retención 90 días).

**Cómo ejecutar:**
1. Ir a `Actions` > `Full Scientific Pipeline`
2. Click `Run workflow`
3. Configurar parámetros
4. Click `Run workflow`

---

## 3. Figuras (`figures.yml`)

**Trigger:** manual

**Uso:** regenerar figuras sin re-ejecutar baseline/MC (cuando se modifican estilos o datos existentes).

**Parámetros:**
- `paper_only`: si true, solo genera las 8 figuras paper-ready (más rápido)

**Runtime:** 2–5 minutos

---

## 4. Validación (`validation.yml`)

**Trigger:** manual

**Ejecuta:** auditoría exhaustiva de datasets, flota, y opcionalmente convergencia MC y sensibilidad item→kg.

**Parámetros:**
- `run_convergence`: análisis MC con 100/500/1000/2000 escenarios
- `run_sensitivity`: sensibilidad del factor de conversión items→kg

**Runtime:** 15–60 minutos (según opciones)

---

## Dependencias

Todos los workflows usan:
- `ubuntu-latest`
- `python 3.12`
- `pip cache` para acelerar instalación
- `requirements.txt` del repositorio

---

## Artefactos

| Workflow | Artefacto | Retención |
|----------|-----------|-----------|
| Full Pipeline | `scientific-figures` | 90 días |
| Full Pipeline | `scientific-tables` | 90 días |
| Full Pipeline | `scientific-results` | 90 días |
| Figures | `figures-{sha}` | 30 días |

Los artefactos se descargan desde la pestaña `Actions` de GitHub.

---

## Badges

Agregar al README.md:

```markdown
![CI](https://github.com/JimenezCespedesYahir/Trab_lab/actions/workflows/ci_light.yml/badge.svg)
```
