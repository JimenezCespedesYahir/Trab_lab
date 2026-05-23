"""
Validación Científica — HVRPTW DSRSLCC
========================================
1. Sensibilidad de conversión item→kg (5g, 10g, 20g, 50g)
2. Convergencia Monte Carlo (100, 500, 1000, 2000)
3. Experimentos de capacidad (+10%, +20%, -Hilux, +Ducato, buffers)
4. Análisis de distribuciones (skewness, kurtosis)
5. Impacto relativo de factores
"""

import csv
import math
import os
import sys
import time
import copy
from collections import defaultdict

import numpy as np
from scipy import stats as sp_stats

# Reuse core functions from montecarlo module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from montecarlo_hvrptw import (
    load_base_data, build_matrices, haversine,
    generate_demand_scenarios, generate_travel_time_scenarios,
    solve_hvrptw, evaluate_scenario, compute_stochastic_kpis
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)


# ─── Helpers ────────────────────────────────────────────────

def time_to_seconds(t):
    h, m = t.split(':')
    return int(h) * 3600 + int(m) * 60


def run_mc_evaluation(locations, vehicles, arcs, n_scenarios, seed=42,
                      demand_cv=None, time_cv=None, demand_scale=1.0,
                      capacity_scale=1.0, solver_time=60):
    """Run full MC: solve baseline + evaluate n_scenarios."""
    dist_matrix, time_matrix, time_cv_matrix = build_matrices(locations, arcs)
    n = len(locations)

    tw_seconds = [(time_to_seconds(loc['tw_start']), time_to_seconds(loc['tw_end']))
                  for loc in locations]
    service_times_s = [int(loc['service_time'] * 60) for loc in locations]

    # Scale demands
    scaled_locations = []
    for loc in locations:
        sl = dict(loc)
        sl['demand_mean'] = loc['demand_mean'] * demand_scale
        sl['demand_std'] = loc['demand_std'] * demand_scale
        scaled_locations.append(sl)

    # Scale vehicle capacities
    scaled_vehicles = []
    for v in vehicles:
        sv = dict(v)
        sv['capacity_kg'] = v['capacity_kg'] * capacity_scale
        scaled_vehicles.append(sv)

    demands_det = [int(sl['demand_mean']) for sl in scaled_locations]
    dist_m = (dist_matrix * 1000).astype(int)
    time_s = (time_matrix * 60).astype(int)
    caps = [int(sv['capacity_kg']) for sv in scaled_vehicles]

    routes = solve_hvrptw(scaled_locations, scaled_vehicles, dist_m, time_s,
                          demands_det, service_times_s, tw_seconds,
                          time_limit=solver_time)
    if not routes:
        return None, None

    rng = np.random.default_rng(seed)
    demand_scenarios = generate_demand_scenarios(
        scaled_locations, n_scenarios, cv_override=demand_cv, rng=rng)
    time_scenarios = generate_travel_time_scenarios(
        time_matrix, time_cv_matrix, n_scenarios, cv_override=time_cv, rng=rng)

    results = []
    for s in range(n_scenarios):
        res = evaluate_scenario(
            routes, scaled_vehicles, scaled_locations,
            demand_scenarios[s].astype(int), time_scenarios[s],
            dist_matrix, service_times_s, tw_seconds)
        res['scenario'] = s
        results.append(res)

    return results, routes


# ═══════════════════════════════════════════════════════════
# 1. CONVERSION FACTOR SENSITIVITY (item→kg)
# ═══════════════════════════════════════════════════════════

def experiment_conversion_sensitivity():
    """Test how different item→kg conversion factors affect results."""
    print("\n" + "=" * 70)
    print("EXPERIMENTO 1: Sensibilidad del Factor de Conversión (item→kg)")
    print("=" * 70)

    # The current calibration uses 10g/item.
    # Factors are relative to the 10g baseline.
    # 5g = 0.5x, 10g = 1.0x, 20g = 2.0x, 50g = 5.0x
    conversion_factors = {
        '5g': 0.5,
        '10g': 1.0,
        '20g': 2.0,
        '50g': 5.0,
    }

    locations, vehicles, arcs = load_base_data(BASE_DIR)
    all_results = []

    for label, scale in conversion_factors.items():
        print(f"\n  Factor: {label}/item (scale={scale}x)...")
        results, routes = run_mc_evaluation(
            locations, vehicles, arcs,
            n_scenarios=200, seed=42, demand_scale=scale, solver_time=60)

        if results is None:
            print(f"    NO SOLUTION for {label}")
            all_results.append({
                'conversion': label, 'scale': scale,
                'feasible': False, 'n_routes': 0,
                'expected_cost': float('nan'), 'std_cost': float('nan'),
                'reliability': float('nan'), 'cap_violation_rate': float('nan'),
                'tw_violation_rate': float('nan'), 'CVaR_0.05': float('nan'),
                'total_demand_kg': 0, 'demand_capacity_ratio': 0,
                'utilization_mean': float('nan'),
            })
            continue

        kpis = compute_stochastic_kpis(results)
        n_routes = results[0]['n_routes']

        # Compute deterministic metrics
        total_demand = sum(loc['demand_mean'] * scale for loc in locations)
        total_cap = sum(v['capacity_kg'] for v in vehicles)

        row = {
            'conversion': label,
            'scale': scale,
            'feasible': True,
            'n_routes': n_routes,
            'expected_cost': kpis['expected_cost'],
            'std_cost': kpis['std_cost'],
            'cv_cost': kpis['cv_cost'],
            'reliability': kpis['route_reliability'],
            'cap_violation_rate': kpis['cap_violation_rate'],
            'tw_violation_rate': kpis['tw_violation_rate'],
            'CVaR_0.05': kpis['CVaR_0.05'],
            'VaR_0.05': kpis['VaR_0.05'],
            'total_demand_kg': total_demand,
            'demand_capacity_ratio': total_demand / total_cap,
            'utilization_mean': kpis['utilization_mean'],
            'service_level': kpis['service_level_mean'],
            'cap_excess_mean': np.mean([r['cap_excess_kg'] for r in results]),
        }
        all_results.append(row)

        print(f"    Routes: {n_routes}, E[cost]: S/ {kpis['expected_cost']:,.0f}, "
              f"Reliability: {kpis['route_reliability']:.3f}, "
              f"Cap viol: {kpis['cap_violation_rate']:.3f}, "
              f"D/C ratio: {total_demand/total_cap:.3f}")

    # Save results
    fields = list(all_results[0].keys())
    with open(os.path.join(RESULTS_DIR, 'sensitivity_conversion_factor.csv'),
              'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_results)

    print("\n  Resumen de Robustez del Hallazgo 'Capacity-Driven Risk':")
    for r in all_results:
        cvr = r['cap_violation_rate']
        twr = r['tw_violation_rate']
        dominant = "CAPACIDAD" if cvr > twr else ("TIEMPO" if twr > cvr else "AMBOS")
        print(f"    {r['conversion']}: cap_viol={cvr:.3f}, tw_viol={twr:.3f} → dominante: {dominant}")

    return all_results


# ═══════════════════════════════════════════════════════════
# 2. MONTE CARLO CONVERGENCE
# ═══════════════════════════════════════════════════════════

def experiment_convergence():
    """Test MC convergence at 100, 500, 1000, 2000 scenarios."""
    print("\n" + "=" * 70)
    print("EXPERIMENTO 2: Convergencia Monte Carlo")
    print("=" * 70)

    scenario_counts = [100, 500, 1000, 2000]
    locations, vehicles, arcs = load_base_data(BASE_DIR)

    convergence_results = []

    # Solve baseline once with longest scenario count
    max_n = max(scenario_counts)
    print(f"\n  Generando {max_n} escenarios (superset)...")
    results_full, routes = run_mc_evaluation(
        locations, vehicles, arcs,
        n_scenarios=max_n, seed=42, solver_time=60)

    if results_full is None:
        print("  ERROR: No baseline solution")
        return []

    costs_full = np.array([r['total_cost'] for r in results_full])

    for n in scenario_counts:
        subset = results_full[:n]
        kpis = compute_stochastic_kpis(subset)
        costs = costs_full[:n]
        se = np.std(costs) / np.sqrt(n)

        row = {
            'n_scenarios': n,
            'expected_cost': kpis['expected_cost'],
            'std_cost': kpis['std_cost'],
            'cv_cost': kpis['cv_cost'],
            'VaR_0.05': kpis['VaR_0.05'],
            'CVaR_0.05': kpis['CVaR_0.05'],
            'reliability': kpis['route_reliability'],
            'ci95_width': 2 * 1.96 * se,
            'ci95_relative': 2 * 1.96 * se / kpis['expected_cost'] * 100,
            'cap_violation_rate': kpis['cap_violation_rate'],
            'tw_violation_rate': kpis['tw_violation_rate'],
            'service_level': kpis['service_level_mean'],
            'skewness': float(sp_stats.skew(costs)),
            'kurtosis': float(sp_stats.kurtosis(costs)),
        }
        convergence_results.append(row)

        print(f"  n={n:>5}: E[cost]=S/ {kpis['expected_cost']:>10,.2f}, "
              f"CI95 width=S/ {2*1.96*se:>8,.2f} ({2*1.96*se/kpis['expected_cost']*100:.2f}%), "
              f"CVaR5%=S/ {kpis['CVaR_0.05']:>10,.2f}, "
              f"Reliability={kpis['route_reliability']:.3f}")

    # Save
    fields = list(convergence_results[0].keys())
    with open(os.path.join(RESULTS_DIR, 'convergence_analysis.csv'),
              'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(convergence_results)

    # Distribution analysis
    print("\n  Análisis de Distribución (2000 escenarios):")
    print(f"    Skewness:  {sp_stats.skew(costs_full):.4f}")
    print(f"    Kurtosis:  {sp_stats.kurtosis(costs_full):.4f}")
    print(f"    Shapiro-Wilk p-value: {sp_stats.shapiro(costs_full[:500])[1]:.6f}")
    print(f"    Min: S/ {costs_full.min():,.2f}")
    print(f"    Max: S/ {costs_full.max():,.2f}")
    print(f"    Range: S/ {costs_full.max() - costs_full.min():,.2f}")

    return convergence_results, results_full


# ═══════════════════════════════════════════════════════════
# 3. CAPACITY EXPERIMENTS
# ═══════════════════════════════════════════════════════════

def experiment_capacity():
    """Test fleet configurations and capacity buffers."""
    print("\n" + "=" * 70)
    print("EXPERIMENTO 3: Capacidad y Configuración de Flota")
    print("=" * 70)

    locations, vehicles_base, arcs = load_base_data(BASE_DIR)

    experiments = {
        'baseline': {'vehicles': vehicles_base, 'cap_scale': 1.0},
        'cap_+10%': {'vehicles': vehicles_base, 'cap_scale': 1.10},
        'cap_+20%': {'vehicles': vehicles_base, 'cap_scale': 1.20},
        'cap_+50%': {'vehicles': vehicles_base, 'cap_scale': 1.50},
        'buffer_85%': {'vehicles': vehicles_base, 'cap_scale': 0.85},  # 15% buffer
        'buffer_75%': {'vehicles': vehicles_base, 'cap_scale': 0.75},  # 25% buffer
    }

    # Special fleet configs: no Hilux, extra Ducato, extra NLR
    # Build custom vehicle lists
    def build_fleet(fuso=4, ducato=2, nlr=4, hilux=6):
        fleet = []
        specs = {
            'FUSO': {'id': 'V1', 'name': 'FUSO Canter 6T', 'cap': 6000,
                     'cpk': 2.5, 'fixed': 150, 'speed': 60, 'aut': 400, 'ref': False},
            'DUCATO': {'id': 'V2', 'name': 'Fiat Ducato Refrigerada', 'cap': 3000,
                       'cpk': 3.0, 'fixed': 200, 'speed': 50, 'aut': 350, 'ref': True},
            'NLR': {'id': 'V3', 'name': 'NLR 3.5 TON', 'cap': 3500,
                    'cpk': 2.2, 'fixed': 120, 'speed': 55, 'aut': 380, 'ref': False},
            'HILUX': {'id': 'V4', 'name': 'Toyota Hilux', 'cap': 1000,
                      'cpk': 1.8, 'fixed': 80, 'speed': 70, 'aut': 500, 'ref': False},
        }
        for vtype, qty in [('FUSO', fuso), ('DUCATO', ducato), ('NLR', nlr), ('HILUX', hilux)]:
            s = specs[vtype]
            for _ in range(qty):
                fleet.append({
                    'vehicle_id': s['id'], 'vehicle_name': s['name'],
                    'capacity_kg': s['cap'], 'cost_per_km': s['cpk'],
                    'fixed_cost': s['fixed'], 'speed_kmh': s['speed'],
                    'autonomy_km': s['aut'], 'refrigeration': s['ref']
                })
        return fleet

    experiments['no_hilux_+NLR'] = {
        'vehicles': build_fleet(fuso=4, ducato=2, nlr=10, hilux=0),
        'cap_scale': 1.0
    }
    experiments['no_hilux_+FUSO'] = {
        'vehicles': build_fleet(fuso=10, ducato=2, nlr=4, hilux=0),
        'cap_scale': 1.0
    }
    experiments['extra_ducato'] = {
        'vehicles': build_fleet(fuso=4, ducato=4, nlr=4, hilux=6),
        'cap_scale': 1.0
    }
    experiments['extra_NLR'] = {
        'vehicles': build_fleet(fuso=4, ducato=2, nlr=8, hilux=6),
        'cap_scale': 1.0
    }

    all_results = []
    for exp_name, config in experiments.items():
        print(f"\n  Experimento: {exp_name}")
        veh = config['vehicles']
        cap_scale = config['cap_scale']

        total_cap = sum(v['capacity_kg'] * cap_scale for v in veh)
        n_veh = len(veh)

        results, routes = run_mc_evaluation(
            locations, veh, arcs,
            n_scenarios=200, seed=42,
            capacity_scale=cap_scale, solver_time=60)

        if results is None:
            print(f"    NO SOLUTION")
            all_results.append({
                'experiment': exp_name, 'feasible': False,
                'n_vehicles': n_veh, 'total_capacity_kg': total_cap,
            })
            continue

        kpis = compute_stochastic_kpis(results)
        total_demand = sum(loc['demand_mean'] for loc in locations)

        row = {
            'experiment': exp_name,
            'feasible': True,
            'n_vehicles': n_veh,
            'total_capacity_kg': total_cap,
            'n_routes': results[0]['n_routes'],
            'expected_cost': kpis['expected_cost'],
            'std_cost': kpis['std_cost'],
            'reliability': kpis['route_reliability'],
            'cap_violation_rate': kpis['cap_violation_rate'],
            'tw_violation_rate': kpis['tw_violation_rate'],
            'CVaR_0.05': kpis['CVaR_0.05'],
            'utilization_mean': kpis['utilization_mean'],
            'service_level': kpis['service_level_mean'],
            'demand_capacity_ratio': total_demand / total_cap,
            'cap_excess_mean': np.mean([r['cap_excess_kg'] for r in results]),
        }
        all_results.append(row)

        print(f"    Routes: {row['n_routes']}, E[cost]: S/ {row['expected_cost']:,.0f}, "
              f"Reliability: {row['reliability']:.3f}, "
              f"Cap viol: {row['cap_violation_rate']:.3f}, "
              f"D/C: {row['demand_capacity_ratio']:.3f}")

    # Save
    fields = list(all_results[0].keys())
    with open(os.path.join(RESULTS_DIR, 'capacity_experiments.csv'),
              'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in all_results:
            row_out = {k: r.get(k, '') for k in fields}
            writer.writerow(row_out)

    return all_results


# ═══════════════════════════════════════════════════════════
# 4. RELATIVE FACTOR IMPACT
# ═══════════════════════════════════════════════════════════

def experiment_factor_impact():
    """Determine relative importance of each uncertainty factor."""
    print("\n" + "=" * 70)
    print("EXPERIMENTO 4: Impacto Relativo de Factores")
    print("=" * 70)

    locations, vehicles, arcs = load_base_data(BASE_DIR)

    # Scenarios: isolate each factor
    configs = {
        'deterministic': {'demand_cv': 0.001, 'time_cv': 0.001},
        'demand_only_low': {'demand_cv': 0.20, 'time_cv': 0.001},
        'demand_only_med': {'demand_cv': 0.42, 'time_cv': 0.001},
        'demand_only_high': {'demand_cv': 0.60, 'time_cv': 0.001},
        'time_only_low': {'demand_cv': 0.001, 'time_cv': 0.10},
        'time_only_med': {'demand_cv': 0.001, 'time_cv': 0.20},
        'time_only_high': {'demand_cv': 0.001, 'time_cv': 0.30},
        'both_sismed': {'demand_cv': 0.42, 'time_cv': 0.20},
        'both_high': {'demand_cv': 0.60, 'time_cv': 0.30},
    }

    all_results = []
    for name, cfg in configs.items():
        print(f"  Config: {name} (demand_cv={cfg['demand_cv']}, time_cv={cfg['time_cv']})...")
        results, _ = run_mc_evaluation(
            locations, vehicles, arcs,
            n_scenarios=200, seed=42,
            demand_cv=cfg['demand_cv'], time_cv=cfg['time_cv'],
            solver_time=60)

        if results is None:
            continue

        kpis = compute_stochastic_kpis(results)
        costs = [r['total_cost'] for r in results]

        row = {
            'config': name,
            'demand_cv': cfg['demand_cv'],
            'time_cv': cfg['time_cv'],
            'expected_cost': kpis['expected_cost'],
            'std_cost': kpis['std_cost'],
            'reliability': kpis['route_reliability'],
            'cap_violation_rate': kpis['cap_violation_rate'],
            'tw_violation_rate': kpis['tw_violation_rate'],
            'CVaR_0.05': kpis['CVaR_0.05'],
            'cost_range': max(costs) - min(costs),
        }
        all_results.append(row)

    # Compute relative impact
    if all_results:
        det_cost = next((r['expected_cost'] for r in all_results if r['config'] == 'deterministic'), None)
        if det_cost:
            print(f"\n  Impacto Relativo (vs deterministic E[cost]=S/ {det_cost:,.0f}):")
            for r in all_results:
                delta = r['expected_cost'] - det_cost
                delta_pct = delta / det_cost * 100
                print(f"    {r['config']:<25}: ΔE[cost]=S/ {delta:>8,.0f} ({delta_pct:>+6.1f}%), "
                      f"reliability={r['reliability']:.3f}")

    return all_results


# ═══════════════════════════════════════════════════════════
# 5. FIGURES
# ═══════════════════════════════════════════════════════════

def generate_all_figures(conv_results, conv_analysis, cap_results, mc_results_full):
    """Generate all scientific figures."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    # ── Figure 1: Conversion Factor Sensitivity ──
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    feasible = [r for r in conv_results if r.get('feasible', False)]
    labels = [r['conversion'] for r in feasible]
    x = range(len(labels))

    costs = [r['expected_cost'] for r in feasible]
    rels = [r['reliability'] for r in feasible]
    caps = [r['cap_violation_rate'] for r in feasible]

    axes[0].bar(x, costs, color=['green', 'steelblue', 'orange', 'red'])
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel('E[Cost] (S/)')
    axes[0].set_title('Expected Cost by Conversion Factor')

    axes[1].bar(x, rels, color=['green', 'steelblue', 'orange', 'red'])
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel('Route Reliability')
    axes[1].set_title('Reliability by Conversion Factor')
    axes[1].set_ylim([0, 1])

    axes[2].bar(x, caps, color=['green', 'steelblue', 'orange', 'red'])
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels)
    axes[2].set_ylabel('Cap Violation Rate')
    axes[2].set_title('Capacity Violations by Conv. Factor')
    axes[2].set_ylim([0, 1])

    plt.suptitle('Sensibilidad del Factor de Conversión item→kg', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'sensitivity_conversion.png'), dpi=150)
    plt.close()

    # ── Figure 2: MC Convergence ──
    if conv_analysis:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        ns = [r['n_scenarios'] for r in conv_analysis]
        e_costs = [r['expected_cost'] for r in conv_analysis]
        ci_widths = [r['ci95_width'] for r in conv_analysis]
        cvars = [r['CVaR_0.05'] for r in conv_analysis]
        rels_c = [r['reliability'] for r in conv_analysis]

        axes[0, 0].plot(ns, e_costs, 'bo-')
        axes[0, 0].set_xlabel('N scenarios')
        axes[0, 0].set_ylabel('E[Cost] (S/)')
        axes[0, 0].set_title('Expected Cost Convergence')
        axes[0, 0].grid(True, alpha=0.3)

        axes[0, 1].plot(ns, ci_widths, 'ro-')
        axes[0, 1].set_xlabel('N scenarios')
        axes[0, 1].set_ylabel('CI 95% Width (S/)')
        axes[0, 1].set_title('Confidence Interval Width')
        axes[0, 1].grid(True, alpha=0.3)

        axes[1, 0].plot(ns, cvars, 'go-')
        axes[1, 0].set_xlabel('N scenarios')
        axes[1, 0].set_ylabel('CVaR 5% (S/)')
        axes[1, 0].set_title('CVaR 5% Convergence')
        axes[1, 0].grid(True, alpha=0.3)

        axes[1, 1].plot(ns, rels_c, 'mo-')
        axes[1, 1].set_xlabel('N scenarios')
        axes[1, 1].set_ylabel('Route Reliability')
        axes[1, 1].set_title('Reliability Convergence')
        axes[1, 1].set_ylim([0, max(rels_c) * 1.5 + 0.01])
        axes[1, 1].grid(True, alpha=0.3)

        plt.suptitle('Convergencia Monte Carlo', fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, 'convergence_montecarlo.png'), dpi=150)
        plt.close()

    # ── Figure 3: Capacity Experiments ──
    if cap_results:
        feasible_cap = [r for r in cap_results if r.get('feasible', False)]
        fig, axes = plt.subplots(1, 3, figsize=(16, 6))

        exp_names = [r['experiment'] for r in feasible_cap]
        x = range(len(exp_names))

        costs_c = [r['expected_cost'] for r in feasible_cap]
        rels_e = [r['reliability'] for r in feasible_cap]
        cap_viol_e = [r['cap_violation_rate'] for r in feasible_cap]

        colors = ['steelblue'] * len(exp_names)
        if 'baseline' in exp_names:
            colors[exp_names.index('baseline')] = 'red'

        axes[0].barh(x, costs_c, color=colors)
        axes[0].set_yticks(x)
        axes[0].set_yticklabels(exp_names, fontsize=8)
        axes[0].set_xlabel('E[Cost] (S/)')
        axes[0].set_title('Expected Cost')

        axes[1].barh(x, rels_e, color=colors)
        axes[1].set_yticks(x)
        axes[1].set_yticklabels(exp_names, fontsize=8)
        axes[1].set_xlabel('Reliability')
        axes[1].set_title('Route Reliability')

        axes[2].barh(x, cap_viol_e, color=colors)
        axes[2].set_yticks(x)
        axes[2].set_yticklabels(exp_names, fontsize=8)
        axes[2].set_xlabel('Cap Violation Rate')
        axes[2].set_title('Capacity Violations')

        plt.suptitle('Experimentos de Capacidad y Flota', fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, 'capacity_experiments.png'), dpi=150)
        plt.close()

    # ── Figure 4: Distribution Analysis ──
    if mc_results_full:
        costs_full = np.array([r['total_cost'] for r in mc_results_full])
        cap_excess = np.array([r['cap_excess_kg'] for r in mc_results_full])
        tw_viols = np.array([r['tw_violations'] for r in mc_results_full])

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        axes[0, 0].hist(costs_full, bins=50, color='steelblue', edgecolor='black', alpha=0.7, density=True)
        # Overlay KDE
        xmin, xmax = costs_full.min(), costs_full.max()
        x_kde = np.linspace(xmin, xmax, 200)
        kde = sp_stats.gaussian_kde(costs_full)
        axes[0, 0].plot(x_kde, kde(x_kde), 'r-', linewidth=2, label='KDE')
        axes[0, 0].set_xlabel('Total Cost (S/)')
        axes[0, 0].set_ylabel('Density')
        axes[0, 0].set_title(f'Cost Distribution (n={len(costs_full)})')
        axes[0, 0].legend()

        # Q-Q plot
        sp_stats.probplot(costs_full, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot (Normal)')

        # Capacity excess distribution
        axes[1, 0].hist(cap_excess, bins=40, color='coral', edgecolor='black', alpha=0.7)
        axes[1, 0].set_xlabel('Capacity Excess (kg)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Capacity Excess Distribution')

        # Running statistics
        n_pts = len(costs_full)
        running_mean = np.cumsum(costs_full) / np.arange(1, n_pts + 1)
        running_std = [np.std(costs_full[:i+1]) for i in range(n_pts)]
        axes[1, 1].plot(running_mean, 'b-', label='Running Mean', linewidth=1)
        axes[1, 1].fill_between(
            range(n_pts),
            running_mean - 1.96 * np.array(running_std) / np.sqrt(np.arange(1, n_pts + 1)),
            running_mean + 1.96 * np.array(running_std) / np.sqrt(np.arange(1, n_pts + 1)),
            alpha=0.2, color='blue')
        axes[1, 1].set_xlabel('Scenario')
        axes[1, 1].set_ylabel('E[Cost] (S/)')
        axes[1, 1].set_title('Monte Carlo Running Mean (2000 esc.)')
        axes[1, 1].legend()

        plt.suptitle('Análisis de Distribución y Convergencia', fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, 'distribution_analysis.png'), dpi=150)
        plt.close()


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    t_start = time.time()

    print("=" * 70)
    print("VALIDACIÓN CIENTÍFICA — HVRPTW DSRSLCC")
    print("Consolidación, Robustez y Análisis Crítico")
    print("=" * 70)

    # 1. Conversion sensitivity
    conv_results = experiment_conversion_sensitivity()

    # 2. Convergence
    conv_analysis, mc_full = experiment_convergence()

    # 3. Capacity experiments
    cap_results = experiment_capacity()

    # 4. Factor impact
    factor_results = experiment_factor_impact()

    # 5. Figures
    print("\n[5/5] Generando figuras...")
    generate_all_figures(conv_results, conv_analysis, cap_results, mc_full)

    total_time = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"TOTAL TIME: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"{'=' * 70}")
    print(f"  Archivos generados:")
    print(f"    results/sensitivity_conversion_factor.csv")
    print(f"    results/convergence_analysis.csv")
    print(f"    results/capacity_experiments.csv")
    print(f"    results/figures/sensitivity_conversion.png")
    print(f"    results/figures/convergence_montecarlo.png")
    print(f"    results/figures/capacity_experiments.png")
    print(f"    results/figures/distribution_analysis.png")


if __name__ == '__main__':
    main()
