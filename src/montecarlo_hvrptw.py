"""
Monte Carlo Simulation — HVRPTW Estocástico
=============================================
Evaluación del baseline determinista bajo incertidumbre dual:
- Demanda ~ Normal truncada (μ, σ de SISMED)
- Tiempos de viaje ~ LogNormal (μ, σ de arcos OSRM)

Genera escenarios estocásticos y evalúa:
- Costo total, violaciones TW, violaciones capacidad
- Service level, route reliability, utilización
- VaR, CVaR, intervalos de confianza

Incluye análisis de sensibilidad sobre CV demanda y CV tiempos.
"""

import csv
import json
import math
import os
import sys
import time
from collections import defaultdict

import numpy as np

from ortools.constraint_solver import routing_enums_pb2, pywrapcp


# ─── Data Loading ───────────────────────────────────────────

def load_base_data(base_dir):
    """Load datasets and return structured data model."""
    nodes = []
    with open(os.path.join(base_dir, 'analytics', 'nodes_hvrptw.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            nodes.append(r)

    depot_lat, depot_lon = -4.906564, -80.728434
    all_locations = [{'node_id': 'DEPOT_DSRSLCC', 'nombre': 'DEPOSITO DSRSLCC',
                      'latitude': depot_lat, 'longitude': depot_lon,
                      'categoria': 'DEPOT',
                      'demand_mean': 0, 'demand_std': 0, 'demand_cv': 0,
                      'service_time': 0,
                      'tw_start': '08:00', 'tw_end': '16:00'}]
    for n in nodes:
        all_locations.append({
            'node_id': n['node_id'],
            'nombre': n['nombre'],
            'latitude': float(n['latitude']),
            'longitude': float(n['longitude']),
            'categoria': n['categoria'],
            'demand_mean': float(n['demand_mean']),
            'demand_std': float(n['demand_std']),
            'demand_cv': float(n['demand_cv']),
            'service_time': float(n['service_time']),
            'tw_start': n['tw_start'],
            'tw_end': n['tw_end']
        })

    vehicles = []
    with open(os.path.join(base_dir, 'analytics', 'vehicles_hvrptw.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            qty = int(r['quantity'])
            for _ in range(qty):
                vehicles.append({
                    'vehicle_id': r['vehicle_id'],
                    'vehicle_name': r['vehicle_name'],
                    'capacity_kg': float(r['capacity_kg']),
                    'cost_per_km': float(r['cost_per_km']),
                    'fixed_cost': float(r['fixed_cost']),
                    'speed_kmh': float(r['speed_kmh']),
                    'autonomy_km': float(r['autonomy_km']),
                    'refrigeration': r['refrigeration'] == 'Yes'
                })

    arcs = {}
    with open(os.path.join(base_dir, 'analytics', 'arcs_with_variability.csv'),
              encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            arc_data = {
                'distance_km': float(r['distance_km']),
                'duration_min': float(r['duration_min']),
                'travel_time_cv': float(r.get('travel_time_cv', 0.2))
            }
            arcs[(r['origin_id'], r['destination_id'])] = arc_data
            if r.get('bidirectional') == 'True':
                arcs[(r['destination_id'], r['origin_id'])] = arc_data

    return all_locations, vehicles, arcs


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def build_matrices(locations, arcs):
    """Build distance and time matrices."""
    n = len(locations)
    dist_matrix = np.zeros((n, n))
    time_matrix = np.zeros((n, n))
    time_cv_matrix = np.full((n, n), 0.2)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            oid = locations[i]['node_id']
            did = locations[j]['node_id']
            if (oid, did) in arcs:
                arc = arcs[(oid, did)]
                dist_matrix[i, j] = arc['distance_km']
                time_matrix[i, j] = arc['duration_min']
                time_cv_matrix[i, j] = arc['travel_time_cv']
            else:
                d = haversine(
                    locations[i]['latitude'], locations[i]['longitude'],
                    locations[j]['latitude'], locations[j]['longitude']
                )
                dist_matrix[i, j] = d
                time_matrix[i, j] = d / 50 * 60
                time_cv_matrix[i, j] = 0.2

    return dist_matrix, time_matrix, time_cv_matrix


# ─── Scenario Generation ───────────────────────────────────

def generate_demand_scenarios(locations, n_scenarios, cv_override=None, rng=None):
    """Generate stochastic demand scenarios using truncated Normal."""
    if rng is None:
        rng = np.random.default_rng(42)

    n = len(locations)
    scenarios = np.zeros((n_scenarios, n))

    for i, loc in enumerate(locations):
        mu = loc['demand_mean']
        if mu == 0:
            continue
        cv = cv_override if cv_override is not None else loc['demand_cv']
        sigma = mu * cv if cv > 0 else mu * 0.2

        samples = rng.normal(mu, sigma, n_scenarios)
        samples = np.maximum(samples, mu * 0.1)  # truncate at 10% of mean
        scenarios[:, i] = samples

    return scenarios


def generate_travel_time_scenarios(time_matrix, time_cv_matrix, n_scenarios,
                                   cv_override=None, rng=None):
    """Generate stochastic travel time scenarios using LogNormal."""
    if rng is None:
        rng = np.random.default_rng(42)

    n = time_matrix.shape[0]
    scenarios = np.zeros((n_scenarios, n, n))

    for i in range(n):
        for j in range(n):
            if i == j or time_matrix[i, j] == 0:
                continue
            mu_real = time_matrix[i, j]
            cv = cv_override if cv_override is not None else time_cv_matrix[i, j]
            sigma_real = mu_real * cv

            # LogNormal parameters
            sigma_ln = np.sqrt(np.log(1 + (sigma_real / mu_real) ** 2))
            mu_ln = np.log(mu_real) - 0.5 * sigma_ln ** 2

            samples = rng.lognormal(mu_ln, sigma_ln, n_scenarios)
            scenarios[:, i, j] = samples

    return scenarios


# ─── Solver ─────────────────────────────────────────────────

def solve_hvrptw(locations, vehicles, dist_matrix_m, time_matrix_s,
                 demands, service_times, time_windows, time_limit=30):
    """Solve a single HVRPTW instance with OR-Tools."""
    n = len(locations)
    n_vehicles = len(vehicles)

    manager = pywrapcp.RoutingIndexManager(n, n_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        i = manager.IndexToNode(from_index)
        j = manager.IndexToNode(to_index)
        return int(dist_matrix_m[i, j])

    transit_cb = routing.RegisterTransitCallback(distance_callback)

    def time_callback(from_index, to_index):
        i = manager.IndexToNode(from_index)
        j = manager.IndexToNode(to_index)
        return int(time_matrix_s[i, j]) + service_times[i]

    time_cb = routing.RegisterTransitCallback(time_callback)

    for v_idx, v in enumerate(vehicles):
        cost_rate = v['cost_per_km'] / 1000

        def make_cb(rate):
            def cb(fi, ti):
                i = manager.IndexToNode(fi)
                j = manager.IndexToNode(ti)
                return int(dist_matrix_m[i, j] * rate * 100)
            return cb

        cb_idx = routing.RegisterTransitCallback(make_cb(cost_rate))
        routing.SetArcCostEvaluatorOfVehicle(cb_idx, v_idx)
        routing.SetFixedCostOfVehicle(int(v['fixed_cost'] * 100), v_idx)

    def demand_callback(from_index):
        return demands[manager.IndexToNode(from_index)]

    demand_cb = routing.RegisterUnaryTransitCallback(demand_callback)
    caps = [int(v['capacity_kg']) for v in vehicles]
    routing.AddDimensionWithVehicleCapacity(demand_cb, 0, caps, True, 'Capacity')

    routing.AddDimension(time_cb, 7200, 57600, False, 'Time')
    time_dim = routing.GetDimensionOrDie('Time')

    for idx in range(n):
        index = manager.NodeToIndex(idx)
        time_dim.CumulVar(index).SetRange(time_windows[idx][0], time_windows[idx][1])

    depot_tw = time_windows[0]
    for v_idx in range(n_vehicles):
        time_dim.CumulVar(routing.Start(v_idx)).SetRange(depot_tw[0], depot_tw[1])
        time_dim.CumulVar(routing.End(v_idx)).SetRange(depot_tw[0], depot_tw[1])

    penalty = 100000
    for node in range(1, n):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(time_limit)

    solution = routing.SolveWithParameters(params)

    if not solution:
        return None

    # Extract solution
    routes = []
    time_dim = routing.GetDimensionOrDie('Time')

    for v_idx in range(n_vehicles):
        route_nodes = []
        index = routing.Start(v_idx)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route_nodes.append(node)
            index = solution.Value(routing.NextVar(index))
        if len(route_nodes) > 1:
            routes.append({
                'vehicle_idx': v_idx,
                'nodes': route_nodes,
                'capacity_kg': vehicles[v_idx]['capacity_kg']
            })

    return routes


def evaluate_scenario(routes, vehicles, locations, demands_scenario,
                      time_scenario_min, dist_matrix, service_times_min, tw_seconds):
    """Evaluate a fixed route plan under a stochastic scenario.
    
    Cost includes:
    - Variable cost (distance × cost_per_km) using stochastic travel distances
    - Fixed cost per vehicle used
    - Penalty for TW violations (S/ 50 per violation)
    - Penalty for capacity violations (S/ 10 per excess kg)
    """
    PENALTY_TW = 50.0       # S/ per TW violation
    PENALTY_CAP = 10.0      # S/ per excess kg

    total_cost_var = 0
    total_cost_fix = 0
    total_cost_penalty = 0
    total_distance = 0
    tw_violations = 0
    cap_violations = 0
    cap_excess_kg = 0
    total_nodes = len(locations) - 1
    total_load = 0

    served_set = set()

    for route in routes:
        v_idx = route['vehicle_idx']
        v = vehicles[v_idx]
        route_nodes = route['nodes']

        route_load = sum(demands_scenario[n] for n in route_nodes if n > 0)

        # Compute route distance using stochastic travel times
        # Distance doesn't change (geography), but time does (stochastic)
        route_dist = 0
        for k in range(len(route_nodes) - 1):
            i, j = route_nodes[k], route_nodes[k + 1]
            route_dist += dist_matrix[i, j]
        last = route_nodes[-1]
        route_dist += dist_matrix[last, 0]

        # Check TW violations using stochastic times
        cumul_time = tw_seconds[0][0]
        route_tw_viol = 0
        for k, node in enumerate(route_nodes):
            if k > 0:
                prev = route_nodes[k - 1]
                cumul_time += time_scenario_min[prev, node] * 60 + service_times_min[prev]
            tw_end = tw_seconds[node][1]
            if cumul_time > tw_end:
                route_tw_viol += 1
                # Apply TW penalty
                total_cost_penalty += PENALTY_TW

        # Check capacity violation
        cap_excess = max(0, route_load - v['capacity_kg'])
        if cap_excess > 0:
            cap_violations += 1
            cap_excess_kg += cap_excess
            total_cost_penalty += cap_excess * PENALTY_CAP

        cost_var = route_dist * v['cost_per_km']
        cost_fix = v['fixed_cost']

        total_cost_var += cost_var
        total_cost_fix += cost_fix
        total_distance += route_dist
        tw_violations += route_tw_viol
        total_load += route_load

        for n in route_nodes:
            if n > 0:
                served_set.add(n)

    nodes_served = len(served_set)
    base_cost = total_cost_var + total_cost_fix

    return {
        'total_cost': base_cost + total_cost_penalty,
        'base_cost': base_cost,
        'cost_variable': total_cost_var,
        'cost_fixed': total_cost_fix,
        'cost_penalty': total_cost_penalty,
        'total_distance_km': total_distance,
        'tw_violations': tw_violations,
        'cap_violations': cap_violations,
        'cap_excess_kg': cap_excess_kg,
        'nodes_served': nodes_served,
        'nodes_total': total_nodes,
        'service_level': nodes_served / total_nodes if total_nodes > 0 else 1.0,
        'total_load_kg': total_load,
        'n_routes': len(routes),
        'avg_utilization': (total_load / sum(r['capacity_kg'] for r in routes)
                           if routes else 0)
    }


# ─── Main Monte Carlo ──────────────────────────────────────

def run_montecarlo(base_dir, n_scenarios=100, demand_cv=None, time_cv=None,
                   seed=42, solver_time=30, label='default'):
    """Run Monte Carlo simulation."""
    rng = np.random.default_rng(seed)

    locations, vehicles, arcs = load_base_data(base_dir)
    dist_matrix, time_matrix, time_cv_matrix = build_matrices(locations, arcs)

    n = len(locations)

    # Time windows
    def time_to_seconds(t):
        h, m = t.split(':')
        return int(h) * 3600 + int(m) * 60

    tw_seconds = [(time_to_seconds(loc['tw_start']), time_to_seconds(loc['tw_end']))
                  for loc in locations]

    service_times_s = [int(loc['service_time'] * 60) for loc in locations]

    # Solve deterministic baseline once
    demands_det = [int(loc['demand_mean']) for loc in locations]
    dist_m = (dist_matrix * 1000).astype(int)
    time_s = (time_matrix * 60).astype(int)

    routes = solve_hvrptw(locations, vehicles, dist_m, time_s,
                          demands_det, service_times_s, tw_seconds,
                          time_limit=solver_time)

    if not routes:
        print("ERROR: No baseline solution found")
        return None

    print(f"  Baseline: {len(routes)} routes, "
          f"{sum(1 for r in routes for n in r['nodes'] if n > 0)} nodes served")

    # Generate scenarios
    demand_scenarios = generate_demand_scenarios(
        locations, n_scenarios, cv_override=demand_cv, rng=rng)
    time_scenarios = generate_travel_time_scenarios(
        time_matrix, time_cv_matrix, n_scenarios, cv_override=time_cv, rng=rng)

    # Evaluate each scenario
    results = []
    for s in range(n_scenarios):
        demands_s = demand_scenarios[s].astype(int)
        time_s_mat = time_scenarios[s]

        res = evaluate_scenario(
            routes, vehicles, locations, demands_s,
            time_s_mat, dist_matrix, service_times_s, tw_seconds
        )
        res['scenario'] = s
        results.append(res)

    return results, routes


def compute_stochastic_kpis(results, alpha_levels=None):
    """Compute stochastic KPIs from Monte Carlo results."""
    if alpha_levels is None:
        alpha_levels = [0.01, 0.05, 0.10]

    costs = np.array([r['total_cost'] for r in results])
    distances = np.array([r['total_distance_km'] for r in results])
    tw_viols = np.array([r['tw_violations'] for r in results])
    cap_viols = np.array([r['cap_violations'] for r in results])
    service_levels = np.array([r['service_level'] for r in results])
    utilizations = np.array([r['avg_utilization'] for r in results])
    loads = np.array([r['total_load_kg'] for r in results])

    n = len(results)

    kpis = {
        'n_scenarios': n,
        'expected_cost': float(np.mean(costs)),
        'std_cost': float(np.std(costs)),
        'cv_cost': float(np.std(costs) / np.mean(costs)) if np.mean(costs) > 0 else 0,
        'min_cost': float(np.min(costs)),
        'max_cost': float(np.max(costs)),
        'median_cost': float(np.median(costs)),
        'expected_distance_km': float(np.mean(distances)),
        'expected_load_kg': float(np.mean(loads)),
        'service_level_mean': float(np.mean(service_levels)),
        'service_level_min': float(np.min(service_levels)),
        'tw_violation_rate': float(np.mean(tw_viols > 0)),
        'tw_violations_mean': float(np.mean(tw_viols)),
        'cap_violation_rate': float(np.mean(cap_viols > 0)),
        'cap_violations_mean': float(np.mean(cap_viols)),
        'utilization_mean': float(np.mean(utilizations)),
        'utilization_std': float(np.std(utilizations)),
        'route_reliability': float(np.mean((tw_viols == 0) & (cap_viols == 0))),
    }

    # VaR and CVaR at multiple alpha levels
    for alpha in alpha_levels:
        var_idx = int(np.ceil((1 - alpha) * n)) - 1
        sorted_costs = np.sort(costs)
        var_val = sorted_costs[var_idx]
        cvar_val = np.mean(sorted_costs[var_idx:])
        kpis[f'VaR_{alpha}'] = float(var_val)
        kpis[f'CVaR_{alpha}'] = float(cvar_val)

    # 95% confidence interval for expected cost
    se = np.std(costs) / np.sqrt(n)
    kpis['ci95_lower'] = float(np.mean(costs) - 1.96 * se)
    kpis['ci95_upper'] = float(np.mean(costs) + 1.96 * se)

    return kpis


# ─── Sensitivity Analysis ──────────────────────────────────

def run_sensitivity(base_dir, n_scenarios=100, solver_time=30):
    """Run sensitivity analysis varying CV demand and CV time."""
    demand_cvs = [0.10, 0.20, 0.30, 0.40]
    time_cvs = [0.10, 0.20, 0.30]
    alpha_levels = [0.01, 0.05, 0.10]

    all_results = []

    for dcv in demand_cvs:
        for tcv in time_cvs:
            label = f"dcv{dcv}_tcv{tcv}"
            print(f"\n  Sensitivity: demand_CV={dcv}, time_CV={tcv}")
            results, _ = run_montecarlo(
                base_dir, n_scenarios=n_scenarios,
                demand_cv=dcv, time_cv=tcv,
                seed=42, solver_time=solver_time, label=label
            )
            if results:
                kpis = compute_stochastic_kpis(results, alpha_levels)
                kpis['demand_cv'] = dcv
                kpis['time_cv'] = tcv
                all_results.append(kpis)

    return all_results


# ─── Output ────────────────────────────────────────────────

def save_montecarlo_results(results, kpis, base_dir, label=''):
    """Save Monte Carlo results and KPIs."""
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    suffix = f'_{label}' if label else ''

    # Scenario-level results
    with open(os.path.join(results_dir, f'montecarlo_results{suffix}.csv'),
              'w', newline='', encoding='utf-8') as f:
        fields = ['scenario', 'total_cost', 'base_cost', 'cost_variable', 'cost_fixed',
                  'cost_penalty', 'total_distance_km', 'tw_violations', 'cap_violations',
                  'cap_excess_kg', 'nodes_served', 'nodes_total', 'service_level',
                  'total_load_kg', 'n_routes', 'avg_utilization']
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r[k] for k in fields})

    # KPIs
    with open(os.path.join(results_dir, f'stochastic_kpis{suffix}.csv'),
              'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value'])
        for k, v in kpis.items():
            writer.writerow([k, v])


def save_sensitivity_results(sensitivity_results, base_dir):
    """Save sensitivity analysis results."""
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    with open(os.path.join(results_dir, 'sensitivity_analysis.csv'),
              'w', newline='', encoding='utf-8') as f:
        if not sensitivity_results:
            return
        fields = list(sensitivity_results[0].keys())
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sensitivity_results)


def generate_figures(results, kpis, sensitivity_results, base_dir):
    """Generate scientific visualization figures."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig_dir = os.path.join(base_dir, 'results', 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    costs = [r['total_cost'] for r in results]
    tw_viols = [r['tw_violations'] for r in results]
    cap_viols = [r['cap_violations'] for r in results]
    utils = [r['avg_utilization'] for r in results]
    distances = [r['total_distance_km'] for r in results]

    # 1. Cost Distribution
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].hist(costs, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0].axvline(np.mean(costs), color='red', linestyle='--', label=f'Mean: S/{np.mean(costs):,.0f}')
    axes[0].axvline(kpis.get('VaR_0.05', 0), color='orange', linestyle=':',
                     label=f'VaR 5%: S/{kpis.get("VaR_0.05", 0):,.0f}')
    axes[0].set_xlabel('Total Cost (S/)')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Cost Distribution')
    axes[0].legend(fontsize=8)

    axes[1].boxplot([costs, distances], labels=['Cost (S/)', 'Distance (km)'])
    axes[1].set_title('Cost & Distance Boxplots')

    axes[2].hist(utils, bins=20, color='green', edgecolor='black', alpha=0.7)
    axes[2].set_xlabel('Average Utilization')
    axes[2].set_ylabel('Frequency')
    axes[2].set_title('Fleet Utilization Distribution')

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'cost_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Robustness
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    tw_vals = [r['tw_violations'] for r in results]
    cap_vals = [r['cap_violations'] for r in results]
    reliability = [(1 if r['tw_violations'] == 0 and r['cap_violations'] == 0 else 0)
                    for r in results]

    axes[0].hist(tw_vals, bins=max(1, max(tw_vals) - min(tw_vals) + 1) if tw_vals else 1,
                  color='coral', edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('TW Violations per Scenario')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Time Window Violations')

    # Running reliability
    cum_rel = np.cumsum(reliability) / np.arange(1, len(reliability) + 1)
    axes[1].plot(cum_rel, color='navy')
    axes[1].set_xlabel('Scenario')
    axes[1].set_ylabel('Cumulative Reliability')
    axes[1].set_title('Route Reliability Convergence')
    axes[1].set_ylim([0, 1.05])
    axes[1].axhline(y=np.mean(reliability), color='red', linestyle='--',
                     label=f'Final: {np.mean(reliability):.3f}')
    axes[1].legend()

    # Service level
    sl = [r['service_level'] for r in results]
    axes[2].hist(sl, bins=20, color='teal', edgecolor='black', alpha=0.7)
    axes[2].set_xlabel('Service Level')
    axes[2].set_ylabel('Frequency')
    axes[2].set_title('Service Level Distribution')

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'robustness_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Sensitivity Analysis
    if sensitivity_results:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        demand_cvs = sorted(set(r['demand_cv'] for r in sensitivity_results))
        time_cvs = sorted(set(r['time_cv'] for r in sensitivity_results))

        # Expected cost heatmap
        cost_grid = np.zeros((len(demand_cvs), len(time_cvs)))
        for r in sensitivity_results:
            di = demand_cvs.index(r['demand_cv'])
            ti = time_cvs.index(r['time_cv'])
            cost_grid[di, ti] = r['expected_cost']

        im = axes[0, 0].imshow(cost_grid, cmap='YlOrRd', aspect='auto')
        axes[0, 0].set_xticks(range(len(time_cvs)))
        axes[0, 0].set_xticklabels([f'{cv:.2f}' for cv in time_cvs])
        axes[0, 0].set_yticks(range(len(demand_cvs)))
        axes[0, 0].set_yticklabels([f'{cv:.2f}' for cv in demand_cvs])
        axes[0, 0].set_xlabel('Time CV')
        axes[0, 0].set_ylabel('Demand CV')
        axes[0, 0].set_title('Expected Cost (S/)')
        for i in range(len(demand_cvs)):
            for j in range(len(time_cvs)):
                axes[0, 0].text(j, i, f'{cost_grid[i, j]:,.0f}',
                               ha='center', va='center', fontsize=8)

        # CVaR 5% heatmap
        cvar_grid = np.zeros((len(demand_cvs), len(time_cvs)))
        for r in sensitivity_results:
            di = demand_cvs.index(r['demand_cv'])
            ti = time_cvs.index(r['time_cv'])
            cvar_grid[di, ti] = r.get('CVaR_0.05', 0)

        im2 = axes[0, 1].imshow(cvar_grid, cmap='YlOrRd', aspect='auto')
        axes[0, 1].set_xticks(range(len(time_cvs)))
        axes[0, 1].set_xticklabels([f'{cv:.2f}' for cv in time_cvs])
        axes[0, 1].set_yticks(range(len(demand_cvs)))
        axes[0, 1].set_yticklabels([f'{cv:.2f}' for cv in demand_cvs])
        axes[0, 1].set_xlabel('Time CV')
        axes[0, 1].set_ylabel('Demand CV')
        axes[0, 1].set_title('CVaR 5% (S/)')
        for i in range(len(demand_cvs)):
            for j in range(len(time_cvs)):
                axes[0, 1].text(j, i, f'{cvar_grid[i, j]:,.0f}',
                               ha='center', va='center', fontsize=8)

        # Reliability heatmap
        rel_grid = np.zeros((len(demand_cvs), len(time_cvs)))
        for r in sensitivity_results:
            di = demand_cvs.index(r['demand_cv'])
            ti = time_cvs.index(r['time_cv'])
            rel_grid[di, ti] = r['route_reliability']

        im3 = axes[1, 0].imshow(rel_grid, cmap='RdYlGn', aspect='auto')
        axes[1, 0].set_xticks(range(len(time_cvs)))
        axes[1, 0].set_xticklabels([f'{cv:.2f}' for cv in time_cvs])
        axes[1, 0].set_yticks(range(len(demand_cvs)))
        axes[1, 0].set_yticklabels([f'{cv:.2f}' for cv in demand_cvs])
        axes[1, 0].set_xlabel('Time CV')
        axes[1, 0].set_ylabel('Demand CV')
        axes[1, 0].set_title('Route Reliability')
        for i in range(len(demand_cvs)):
            for j in range(len(time_cvs)):
                axes[1, 0].text(j, i, f'{rel_grid[i, j]:.3f}',
                               ha='center', va='center', fontsize=8)

        # Cost sensitivity curves
        for tcv in time_cvs:
            costs_line = [r['expected_cost'] for r in sensitivity_results
                         if r['time_cv'] == tcv]
            axes[1, 1].plot(demand_cvs, costs_line, marker='o', label=f'Time CV={tcv}')

        axes[1, 1].set_xlabel('Demand CV')
        axes[1, 1].set_ylabel('Expected Cost (S/)')
        axes[1, 1].set_title('Cost Sensitivity to Demand CV')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(fig_dir, 'sensitivity_analysis.png'), dpi=150, bbox_inches='tight')
        plt.close()

    # 4. Monte Carlo convergence
    fig, ax = plt.subplots(figsize=(10, 5))
    cum_mean = np.cumsum(costs) / np.arange(1, len(costs) + 1)
    ax.plot(cum_mean, color='navy', label='Running Mean Cost')
    ax.fill_between(
        range(len(costs)),
        [np.mean(costs[:i+1]) - 1.96 * np.std(costs[:i+1]) / np.sqrt(i+1)
         for i in range(len(costs))],
        [np.mean(costs[:i+1]) + 1.96 * np.std(costs[:i+1]) / np.sqrt(i+1)
         for i in range(len(costs))],
        alpha=0.2, color='navy', label='95% CI'
    )
    ax.set_xlabel('Scenario')
    ax.set_ylabel('Expected Cost (S/)')
    ax.set_title('Monte Carlo Convergence')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'montecarlo_convergence.png'), dpi=150, bbox_inches='tight')
    plt.close()

    return fig_dir


# ─── Main ──────────────────────────────────────────────────

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("MONTE CARLO — HVRPTW ESTOCÁSTICO DSRSLCC")
    print("=" * 60)

    # Phase 1: 100 scenarios pilot
    print("\n[1/4] Monte Carlo piloto (100 escenarios)...")
    t0 = time.time()
    results_100, routes = run_montecarlo(base_dir, n_scenarios=100, solver_time=60)
    t1 = time.time()
    kpis_100 = compute_stochastic_kpis(results_100)
    print(f"  Tiempo: {t1 - t0:.1f}s")
    print(f"  E[cost]: S/ {kpis_100['expected_cost']:,.2f}")
    print(f"  Route reliability: {kpis_100['route_reliability']:.3f}")
    print(f"  Service level: {kpis_100['service_level_mean']:.3f}")
    print(f"  CVaR 5%: S/ {kpis_100['CVaR_0.05']:,.2f}")

    save_montecarlo_results(results_100, kpis_100, base_dir)

    # Phase 2: 500 scenarios
    print("\n[2/4] Monte Carlo 500 escenarios...")
    t2 = time.time()
    results_500, _ = run_montecarlo(base_dir, n_scenarios=500, solver_time=60, seed=123)
    t3 = time.time()
    kpis_500 = compute_stochastic_kpis(results_500)
    print(f"  Tiempo: {t3 - t2:.1f}s")
    print(f"  E[cost]: S/ {kpis_500['expected_cost']:,.2f}")
    print(f"  Route reliability: {kpis_500['route_reliability']:.3f}")
    print(f"  CVaR 5%: S/ {kpis_500['CVaR_0.05']:,.2f}")

    save_montecarlo_results(results_500, kpis_500, base_dir, label='500')

    # Phase 3: Sensitivity analysis
    print("\n[3/4] Análisis de sensibilidad (12 combinaciones × 100 escenarios)...")
    t4 = time.time()
    sensitivity_results = run_sensitivity(base_dir, n_scenarios=100, solver_time=60)
    t5 = time.time()
    print(f"  Tiempo total sensibilidad: {t5 - t4:.1f}s")
    save_sensitivity_results(sensitivity_results, base_dir)

    # Phase 4: Visualizations
    print("\n[4/4] Generando figuras...")
    fig_dir = generate_figures(results_500, kpis_500, sensitivity_results, base_dir)
    print(f"  Figuras guardadas en: {fig_dir}/")

    # Summary
    print("\n" + "=" * 60)
    print("RESUMEN MONTE CARLO")
    print("=" * 60)
    print(f"\n  {'Metric':<30} {'100 esc.':<15} {'500 esc.'}")
    print(f"  {'─'*30} {'─'*15} {'─'*15}")
    print(f"  {'E[cost]':<30} S/ {kpis_100['expected_cost']:>10,.2f}  S/ {kpis_500['expected_cost']:>10,.2f}")
    print(f"  {'Std[cost]':<30} S/ {kpis_100['std_cost']:>10,.2f}  S/ {kpis_500['std_cost']:>10,.2f}")
    print(f"  {'CV[cost]':<30} {kpis_100['cv_cost']:>13.4f}  {kpis_500['cv_cost']:>13.4f}")
    print(f"  {'VaR 5%':<30} S/ {kpis_100['VaR_0.05']:>10,.2f}  S/ {kpis_500['VaR_0.05']:>10,.2f}")
    print(f"  {'CVaR 5%':<30} S/ {kpis_100['CVaR_0.05']:>10,.2f}  S/ {kpis_500['CVaR_0.05']:>10,.2f}")
    print(f"  {'Route reliability':<30} {kpis_100['route_reliability']:>13.3f}  {kpis_500['route_reliability']:>13.3f}")
    print(f"  {'Service level':<30} {kpis_100['service_level_mean']:>13.3f}  {kpis_500['service_level_mean']:>13.3f}")
    print(f"  {'TW violation rate':<30} {kpis_100['tw_violation_rate']:>13.3f}  {kpis_500['tw_violation_rate']:>13.3f}")
    print(f"  {'Cap violation rate':<30} {kpis_100['cap_violation_rate']:>13.3f}  {kpis_500['cap_violation_rate']:>13.3f}")
    print(f"  {'95% CI lower':<30} S/ {kpis_100['ci95_lower']:>10,.2f}  S/ {kpis_500['ci95_lower']:>10,.2f}")
    print(f"  {'95% CI upper':<30} S/ {kpis_100['ci95_upper']:>10,.2f}  S/ {kpis_500['ci95_upper']:>10,.2f}")

    total_time = time.time() - t0
    print(f"\n  Tiempo total: {total_time:.1f}s")
    print(f"  Archivos generados:")
    print(f"    results/montecarlo_results.csv (100 esc.)")
    print(f"    results/montecarlo_results_500.csv")
    print(f"    results/stochastic_kpis.csv")
    print(f"    results/stochastic_kpis_500.csv")
    print(f"    results/sensitivity_analysis.csv")
    print(f"    results/figures/*.png")


if __name__ == '__main__':
    main()
