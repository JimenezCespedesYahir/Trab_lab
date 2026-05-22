"""
Baseline HVRPTW Determinista — OR-Tools
========================================
Fase A del roadmap HVRPTW robusto-estocástico DSRSLCC.

Implementa:
- HVRPTW determinista con flota heterogénea
- Capacidad por tipo de vehículo
- Ventanas de tiempo
- Costos variables (por km) y fijos (por vehículo)
- Distancias y tiempos OSRM reales
- Múltiples vehículos con retorno al depósito

Datasets:
- analytics/nodes_hvrptw.csv (81 nodos + depósito)
- analytics/vehicles_hvrptw.csv (4 tipos, 16 vehículos)
- analytics/arcs_with_variability.csv (820 arcos)
- analytics/time_windows.csv (82 registros)
- analytics/demand_aggregated.csv (81 nodos)

Resultados:
- results/baseline_kpis.csv
- results/baseline_routes.csv
"""

import csv
import json
import math
import os
import sys
import time
from collections import defaultdict

from ortools.constraint_solver import routing_enums_pb2, pywrapcp


def load_data(base_dir):
    """Load all datasets and build the data model."""
    # --- Nodes ---
    nodes = []
    with open(os.path.join(base_dir, 'analytics', 'nodes_hvrptw.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            nodes.append(r)

    depot_lat, depot_lon = -4.906564, -80.728434
    all_locations = [{'node_id': 'DEPOT_DSRSLCC', 'nombre': 'DEPOSITO DSRSLCC',
                      'latitude': depot_lat, 'longitude': depot_lon,
                      'categoria': 'DEPOT', 'demand_mean': 0, 'service_time': 0,
                      'tw_start': '08:00', 'tw_end': '16:00'}]
    for n in nodes:
        all_locations.append({
            'node_id': n['node_id'],
            'nombre': n['nombre'],
            'latitude': float(n['latitude']),
            'longitude': float(n['longitude']),
            'categoria': n['categoria'],
            'demand_mean': float(n['demand_mean']),
            'service_time': float(n['service_time']),
            'tw_start': n['tw_start'],
            'tw_end': n['tw_end']
        })
    num_locations = len(all_locations)

    # --- Vehicles ---
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
    num_vehicles = len(vehicles)

    # --- Distance/Time Matrix ---
    arcs = {}
    with open(os.path.join(base_dir, 'analytics', 'arcs_with_variability.csv'),
              encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            arcs[(r['origin_id'], r['destination_id'])] = {
                'distance_km': float(r['distance_km']),
                'duration_min': float(r['duration_min'])
            }
            if r.get('bidirectional') == 'True':
                arcs[(r['destination_id'], r['origin_id'])] = {
                    'distance_km': float(r['distance_km']),
                    'duration_min': float(r['duration_min'])
                }

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.asin(math.sqrt(a))

    # Build full distance and time matrices
    distance_matrix = [[0] * num_locations for _ in range(num_locations)]
    time_matrix = [[0] * num_locations for _ in range(num_locations)]

    for i in range(num_locations):
        for j in range(num_locations):
            if i == j:
                continue
            oid = all_locations[i]['node_id']
            did = all_locations[j]['node_id']
            if (oid, did) in arcs:
                arc = arcs[(oid, did)]
                distance_matrix[i][j] = int(arc['distance_km'] * 1000)  # meters
                time_matrix[i][j] = int(arc['duration_min'] * 60)  # seconds
            else:
                # Estimate from haversine
                d = haversine(
                    float(all_locations[i]['latitude']),
                    float(all_locations[i]['longitude']),
                    float(all_locations[j]['latitude']),
                    float(all_locations[j]['longitude'])
                )
                distance_matrix[i][j] = int(d * 1000)  # meters
                avg_speed = 50  # km/h for unknown arcs
                time_matrix[i][j] = int(d / avg_speed * 3600)  # seconds

    # Add service times to time matrix
    service_times = [0] * num_locations
    for i, loc in enumerate(all_locations):
        service_times[i] = int(float(loc['service_time']) * 60)  # seconds

    # --- Demands ---
    demands = [0] * num_locations  # depot = 0
    for i, loc in enumerate(all_locations):
        demands[i] = int(float(loc['demand_mean']))  # kg

    # --- Time Windows ---
    def time_to_seconds(t):
        h, m = t.split(':')
        return int(h) * 3600 + int(m) * 60

    time_windows = []
    for loc in all_locations:
        tw_start = time_to_seconds(loc['tw_start'])
        tw_end = time_to_seconds(loc['tw_end'])
        time_windows.append((tw_start, tw_end))

    return {
        'locations': all_locations,
        'vehicles': vehicles,
        'distance_matrix': distance_matrix,
        'time_matrix': time_matrix,
        'service_times': service_times,
        'demands': demands,
        'time_windows': time_windows,
        'num_locations': num_locations,
        'num_vehicles': num_vehicles,
        'depot': 0
    }


def create_model(data):
    """Create and solve the HVRPTW model using OR-Tools."""
    manager = pywrapcp.RoutingIndexManager(
        data['num_locations'],
        data['num_vehicles'],
        data['depot']
    )
    routing = pywrapcp.RoutingModel(manager)

    # --- Distance callback (per vehicle type for cost) ---
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # --- Time callback (travel time + service time) ---
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel = data['time_matrix'][from_node][to_node]
        service = data['service_times'][from_node]
        return travel + service

    time_callback_index = routing.RegisterTransitCallback(time_callback)

    # --- Cost per vehicle type ---
    cost_callbacks = []
    for v_idx, v in enumerate(data['vehicles']):
        cost_per_m = v['cost_per_km'] / 1000  # cost per meter

        def make_cost_callback(cost_rate):
            def cost_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                dist = data['distance_matrix'][from_node][to_node]
                return int(dist * cost_rate * 100)  # cents
            return cost_callback

        cb_idx = routing.RegisterTransitCallback(make_cost_callback(cost_per_m))
        cost_callbacks.append(cb_idx)
        routing.SetArcCostEvaluatorOfVehicle(cb_idx, v_idx)

    # --- Fixed costs ---
    for v_idx, v in enumerate(data['vehicles']):
        routing.SetFixedCostOfVehicle(int(v['fixed_cost'] * 100), v_idx)  # cents

    # --- Capacity constraint ---
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    vehicle_capacities = [int(v['capacity_kg']) for v in data['vehicles']]
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # slack
        vehicle_capacities,
        True,  # start cumul to zero
        'Capacity'
    )

    # --- Time windows ---
    # Time is measured in seconds from midnight.
    # Depot opens at 08:00 (28800s), closes at 16:00 (57600s).
    # Max cumul must accommodate the latest possible time (16:00 = 57600s).
    routing.AddDimension(
        time_callback_index,
        7200,  # allow waiting up to 2 hours
        57600,  # max absolute time = 16:00 in seconds from midnight
        False,  # don't force start cumul to zero
        'Time'
    )
    time_dimension = routing.GetDimensionOrDie('Time')

    for location_idx in range(data['num_locations']):
        index = manager.NodeToIndex(location_idx)
        tw = data['time_windows'][location_idx]
        time_dimension.CumulVar(index).SetRange(tw[0], tw[1])

    # Set depot time windows for each vehicle
    depot_tw = data['time_windows'][0]
    for v_idx in range(data['num_vehicles']):
        start_index = routing.Start(v_idx)
        end_index = routing.End(v_idx)
        time_dimension.CumulVar(start_index).SetRange(depot_tw[0], depot_tw[1])
        time_dimension.CumulVar(end_index).SetRange(depot_tw[0], depot_tw[1])

    # Allow dropping visits with a penalty
    penalty = 100000  # high penalty per dropped node (in cents)
    for node in range(1, data['num_locations']):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    # --- Search parameters ---
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(120)
    search_parameters.log_search = True

    return manager, routing, search_parameters


def extract_solution(data, manager, routing, solution):
    """Extract routes and KPIs from the solution."""
    routes = []
    total_distance = 0
    total_cost_variable = 0
    total_cost_fixed = 0
    vehicles_used = 0
    total_load = 0
    total_service_time = 0
    dropped_nodes = []

    time_dimension = routing.GetDimensionOrDie('Time')

    # Check for dropped nodes
    for node in range(1, data['num_locations']):
        index = manager.NodeToIndex(node)
        if solution.Value(routing.NextVar(index)) == index:
            dropped_nodes.append(data['locations'][node]['node_id'])

    for v_idx in range(data['num_vehicles']):
        index = routing.Start(v_idx)
        route_nodes = []
        route_distance = 0
        route_load = 0
        route_time = 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            arrival = solution.Min(time_var)

            route_nodes.append({
                'node_id': data['locations'][node]['node_id'],
                'nombre': data['locations'][node]['nombre'],
                'demand': data['demands'][node],
                'arrival_time': f"{arrival // 3600:02d}:{(arrival % 3600) // 60:02d}",
                'service_time_min': data['service_times'][node] // 60
            })
            route_load += data['demands'][node]

            prev_index = index
            index = solution.Value(routing.NextVar(index))
            if not routing.IsEnd(index):
                route_distance += data['distance_matrix'][
                    manager.IndexToNode(prev_index)][manager.IndexToNode(index)]
            else:
                end_node = manager.IndexToNode(prev_index)
                route_distance += data['distance_matrix'][end_node][0]

        if len(route_nodes) > 1:
            vehicle = data['vehicles'][v_idx]
            cost_var = route_distance / 1000 * vehicle['cost_per_km']
            cost_fix = vehicle['fixed_cost']

            routes.append({
                'vehicle_idx': v_idx,
                'vehicle_id': vehicle['vehicle_id'],
                'vehicle_name': vehicle['vehicle_name'],
                'capacity_kg': vehicle['capacity_kg'],
                'nodes_visited': len(route_nodes) - 1,
                'route_distance_km': round(route_distance / 1000, 2),
                'route_load_kg': route_load,
                'utilization_pct': round(route_load / vehicle['capacity_kg'] * 100, 1),
                'cost_variable': round(cost_var, 2),
                'cost_fixed': round(cost_fix, 2),
                'cost_total': round(cost_var + cost_fix, 2),
                'stops': route_nodes
            })

            total_distance += route_distance
            total_cost_variable += cost_var
            total_cost_fixed += cost_fix
            total_load += route_load
            vehicles_used += 1

    return {
        'routes': routes,
        'kpis': {
            'total_distance_km': round(total_distance / 1000, 2),
            'total_cost_variable': round(total_cost_variable, 2),
            'total_cost_fixed': round(total_cost_fixed, 2),
            'total_cost': round(total_cost_variable + total_cost_fixed, 2),
            'vehicles_used': vehicles_used,
            'vehicles_available': data['num_vehicles'],
            'nodes_served': sum(r['nodes_visited'] for r in routes),
            'nodes_total': data['num_locations'] - 1,
            'nodes_dropped': len(dropped_nodes),
            'dropped_node_ids': dropped_nodes,
            'total_load_kg': total_load,
            'total_demand_kg': sum(data['demands']),
            'avg_utilization_pct': round(
                sum(r['utilization_pct'] for r in routes) / max(len(routes), 1), 1),
            'avg_route_distance_km': round(
                total_distance / 1000 / max(vehicles_used, 1), 2),
            'avg_nodes_per_route': round(
                sum(r['nodes_visited'] for r in routes) / max(vehicles_used, 1), 1),
            'num_routes': len(routes)
        }
    }


def save_results(result, base_dir):
    """Save results to CSV files."""
    results_dir = os.path.join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # KPIs
    kpis = result['kpis']
    with open(os.path.join(results_dir, 'baseline_kpis.csv'), 'w',
              newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['metric', 'value', 'unit'])
        writer.writerow(['total_distance', kpis['total_distance_km'], 'km'])
        writer.writerow(['total_cost_variable', kpis['total_cost_variable'], 'S/'])
        writer.writerow(['total_cost_fixed', kpis['total_cost_fixed'], 'S/'])
        writer.writerow(['total_cost', kpis['total_cost'], 'S/'])
        writer.writerow(['vehicles_used', kpis['vehicles_used'], 'units'])
        writer.writerow(['vehicles_available', kpis['vehicles_available'], 'units'])
        writer.writerow(['nodes_served', kpis['nodes_served'], 'nodes'])
        writer.writerow(['nodes_total', kpis['nodes_total'], 'nodes'])
        writer.writerow(['nodes_dropped', kpis['nodes_dropped'], 'nodes'])
        writer.writerow(['total_load', kpis['total_load_kg'], 'kg'])
        writer.writerow(['total_demand', kpis['total_demand_kg'], 'kg'])
        writer.writerow(['avg_utilization', kpis['avg_utilization_pct'], '%'])
        writer.writerow(['avg_route_distance', kpis['avg_route_distance_km'], 'km'])
        writer.writerow(['avg_nodes_per_route', kpis['avg_nodes_per_route'], 'nodes'])
        writer.writerow(['num_routes', kpis['num_routes'], 'routes'])

    # Routes
    with open(os.path.join(results_dir, 'baseline_routes.csv'), 'w',
              newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['route_id', 'vehicle_id', 'vehicle_name', 'capacity_kg',
                          'stop_sequence', 'node_id', 'nombre', 'demand_kg',
                          'arrival_time', 'service_time_min', 'route_distance_km',
                          'route_load_kg', 'utilization_pct'])
        for r_idx, route in enumerate(result['routes']):
            for s_idx, stop in enumerate(route['stops']):
                writer.writerow([
                    r_idx + 1,
                    route['vehicle_id'],
                    route['vehicle_name'],
                    route['capacity_kg'],
                    s_idx,
                    stop['node_id'],
                    stop['nombre'],
                    stop['demand'],
                    stop['arrival_time'],
                    stop['service_time_min'],
                    route['route_distance_km'] if s_idx == 0 else '',
                    route['route_load_kg'] if s_idx == 0 else '',
                    route['utilization_pct'] if s_idx == 0 else ''
                ])

    return kpis


def main():
    """Main execution."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("=" * 60)
    print("BASELINE HVRPTW DETERMINISTA — OR-Tools")
    print("Fase A: DSRSLCC Logística Farmacéutica")
    print("=" * 60)

    # Load data
    print("\n[1/4] Cargando datos...")
    t0 = time.time()
    data = load_data(base_dir)
    t_load = time.time() - t0
    print(f"  Nodos: {data['num_locations']} (1 depósito + {data['num_locations'] - 1} clientes)")
    print(f"  Vehículos: {data['num_vehicles']}")
    print(f"  Demanda total: {sum(data['demands'])} kg")
    print(f"  Capacidad total: {sum(v['capacity_kg'] for v in data['vehicles'])} kg")
    print(f"  Tiempo de carga: {t_load:.2f}s")

    # Create and solve model
    print("\n[2/4] Creando modelo OR-Tools...")
    t1 = time.time()
    manager, routing, search_parameters = create_model(data)
    t_model = time.time() - t1
    print(f"  Modelo creado en {t_model:.2f}s")

    print("\n[3/4] Resolviendo (límite: 120s)...")
    t2 = time.time()
    solution = routing.SolveWithParameters(search_parameters)
    t_solve = time.time() - t2
    print(f"  Tiempo de resolución: {t_solve:.2f}s")
    print(f"  Status: {routing.status()}")

    if solution:
        # Extract results
        print("\n[4/4] Extrayendo resultados...")
        result = extract_solution(data, manager, routing, solution)
        result['kpis']['runtime_load_s'] = round(t_load, 2)
        result['kpis']['runtime_model_s'] = round(t_model, 2)
        result['kpis']['runtime_solve_s'] = round(t_solve, 2)
        result['kpis']['runtime_total_s'] = round(t_load + t_model + t_solve, 2)

        # Save
        kpis = save_results(result, base_dir)

        # Print summary
        print("\n" + "=" * 60)
        print("RESULTADOS BASELINE")
        print("=" * 60)
        print(f"  Rutas generadas:        {kpis['num_routes']}")
        print(f"  Vehículos utilizados:    {kpis['vehicles_used']}/{kpis['vehicles_available']}")
        print(f"  Nodos servidos:          {kpis['nodes_served']}/{kpis['nodes_total']}")
        print(f"  Nodos no servidos:       {kpis['nodes_dropped']}")
        print(f"  Distancia total:         {kpis['total_distance_km']:.1f} km")
        print(f"  Costo total:             S/ {kpis['total_cost']:.2f}")
        print(f"    - Variable:            S/ {kpis['total_cost_variable']:.2f}")
        print(f"    - Fijo:                S/ {kpis['total_cost_fixed']:.2f}")
        print(f"  Carga total:             {kpis['total_load_kg']} kg")
        print(f"  Utilización promedio:    {kpis['avg_utilization_pct']:.1f}%")
        print(f"  Distancia media/ruta:    {kpis['avg_route_distance_km']:.1f} km")
        print(f"  Nodos promedio/ruta:     {kpis['avg_nodes_per_route']:.1f}")
        print(f"  Tiempo total:            {result['kpis']['runtime_total_s']:.2f}s")

        if kpis['nodes_dropped'] > 0:
            print(f"\n  ADVERTENCIA: {kpis['nodes_dropped']} nodos no servidos:")
            for nid in kpis['dropped_node_ids']:
                print(f"    - {nid}")

        print(f"\n  Resultados guardados en: results/baseline_kpis.csv, results/baseline_routes.csv")

        # Per-route summary
        print("\n" + "-" * 60)
        print("DETALLE POR RUTA")
        print("-" * 60)
        for route in result['routes']:
            stops = [s['node_id'] for s in route['stops'][1:]]  # skip depot
            print(f"  Ruta {route['vehicle_idx'] + 1} [{route['vehicle_name']}]: "
                  f"{route['nodes_visited']} nodos, "
                  f"{route['route_distance_km']:.1f} km, "
                  f"{route['route_load_kg']} kg "
                  f"({route['utilization_pct']:.0f}% cap)")
    else:
        print("\n  ERROR: No se encontró solución factible.")
        print("  Posibles causas:")
        print("    - Demanda total excede capacidad de flota")
        print("    - Ventanas de tiempo demasiado restrictivas")
        print("    - Tiempo de resolución insuficiente")
        sys.exit(1)


if __name__ == '__main__':
    main()
