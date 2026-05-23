"""
Visualizaciones Científicas Finales — HVRPTW Estocástico DSRSLCC
================================================================
Genera las 24 visualizaciones obligatorias para tesis/paper,
organizadas en 5 categorías (A–E).

Uso: python src/visualizaciones_cientificas_finales.py
"""

import csv
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker
from matplotlib.patches import Patch, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize
from matplotlib import cm

# ──────────────────────────────────────────────
# Style — paper Q1 / tesis seria
# ──────────────────────────────────────────────
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 200,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures_final')
TABLES_DIR = os.path.join(RESULTS_DIR, 'final_tables')
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)

VEHICLE_COLORS = {
    'V1_FUSO_CANTER': '#2980B9',
    'V2_FIAT_DUCATO': '#8E44AD',
    'V3_NLR_35T': '#27AE60',
    'V4_TOYOTA_HILUX': '#C0392B',
}
VEHICLE_LABELS = {
    'V1_FUSO_CANTER': 'FUSO Canter 6T',
    'V2_FIAT_DUCATO': 'Fiat Ducato 3T (Refrig.)',
    'V3_NLR_35T': 'NLR 3.5T',
    'V4_TOYOTA_HILUX': 'Toyota Hilux 1T',
}
DEPOT_LAT = -4.906564
DEPOT_LON = -80.728434


# ──────────────────────────────────────────────
# Data loaders
# ──────────────────────────────────────────────
def load_csv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_nodes():
    return load_csv(os.path.join(ANALYTICS_DIR, 'nodes_hvrptw.csv'))


def load_arcs():
    return load_csv(os.path.join(ANALYTICS_DIR, 'arcs_with_variability.csv'))


def load_routes():
    return load_csv(os.path.join(RESULTS_DIR, 'baseline_routes.csv'))


def load_mc():
    return load_csv(os.path.join(RESULTS_DIR, 'montecarlo_results_500.csv'))


def load_convergence():
    return load_csv(os.path.join(RESULTS_DIR, 'convergence_analysis.csv'))


def load_sensitivity():
    return load_csv(os.path.join(RESULTS_DIR, 'sensitivity_analysis.csv'))


def load_conversion():
    return load_csv(os.path.join(RESULTS_DIR, 'sensitivity_conversion_factor.csv'))


def load_capacity():
    return load_csv(os.path.join(RESULTS_DIR, 'capacity_experiments.csv'))


def load_vehicles():
    return load_csv(os.path.join(ANALYTICS_DIR, 'vehicles_hvrptw.csv'))


def savefig(fig, name):
    for ext in ['png', 'svg']:
        fig.savefig(os.path.join(FIGURES_DIR, f'{name}.{ext}'))
    plt.close(fig)


def time_to_minutes(t_str):
    h, m = t_str.split(':')
    return int(h) * 60 + int(m)


# ──────────────────────────────────────────────
# A. MAPAS Y RED LOGÍSTICA
# ──────────────────────────────────────────────

def fig_A1_red_general():
    """A1: Mapa general de la red HVRPTW con depósito, IPRESS y rutas."""
    nodes = load_nodes()
    routes = load_routes()

    lats = [float(n['latitude']) for n in nodes]
    lons = [float(n['longitude']) for n in nodes]
    cats = [n['categoria'] for n in nodes]

    node_coords = {}
    for n in nodes:
        node_coords[n['node_id']] = (float(n['longitude']), float(n['latitude']))
    node_coords['DEPOT_DSRSLCC'] = (DEPOT_LON, DEPOT_LAT)

    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot arcs (sampled for readability)
    arcs = load_arcs()
    for arc in arcs[::3]:
        ax.plot([float(arc['origin_lon']), float(arc['destination_lon'])],
                [float(arc['origin_lat']), float(arc['destination_lat'])],
                color='#BDC3C7', linewidth=0.3, alpha=0.4, zorder=1)

    # Plot routes
    route_ids = sorted(set(r['route_id'] for r in routes))
    route_colors = plt.cm.tab10(np.linspace(0, 1, len(route_ids)))
    for idx, rid in enumerate(route_ids):
        stops = sorted([r for r in routes if r['route_id'] == rid],
                       key=lambda x: int(x['stop_sequence']))
        xs = []
        ys = []
        for s in stops:
            nid = s['node_id']
            if nid in node_coords:
                xs.append(node_coords[nid][0])
                ys.append(node_coords[nid][1])
        if xs:
            # Return to depot
            xs.append(DEPOT_LON)
            ys.append(DEPOT_LAT)
            ax.plot(xs, ys, color=route_colors[idx], linewidth=1.8, alpha=0.7,
                    zorder=2, label=f'Ruta {rid}')

    # Nodes by category
    cs_lats = [float(n['latitude']) for n in nodes if n['categoria'] == 'CENTRO DE SALUD']
    cs_lons = [float(n['longitude']) for n in nodes if n['categoria'] == 'CENTRO DE SALUD']
    ps_lats = [float(n['latitude']) for n in nodes if n['categoria'] != 'CENTRO DE SALUD']
    ps_lons = [float(n['longitude']) for n in nodes if n['categoria'] != 'CENTRO DE SALUD']

    ax.scatter(cs_lons, cs_lats, c='#2980B9', s=50, marker='s', zorder=3,
               edgecolors='black', linewidths=0.5, label=f'Centro de Salud (n={len(cs_lats)})')
    ax.scatter(ps_lons, ps_lats, c='#27AE60', s=30, marker='o', zorder=3,
               edgecolors='black', linewidths=0.5, label=f'Puesto de Salud (n={len(ps_lats)})')
    ax.scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=200, marker='*', zorder=5,
               edgecolors='black', linewidths=1.0, label='Depósito DSRSLCC')

    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Figura A1: Red HVRPTW — DSRSLCC Sullana\n'
                 '81 IPRESS, 820 arcos bidireccionales, 10 rutas baseline',
                 fontweight='bold')
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    ax.set_aspect('equal')
    savefig(fig, 'A1_red_general_hvrptw')


def fig_A2_mapa_vehiculos():
    """A2: Mapa por tipo de vehículo asignado."""
    routes = load_routes()
    nodes = load_nodes()

    node_coords = {}
    for n in nodes:
        node_coords[n['node_id']] = (float(n['longitude']), float(n['latitude']))
    node_coords['DEPOT_DSRSLCC'] = (DEPOT_LON, DEPOT_LAT)

    fig, ax = plt.subplots(figsize=(10, 10))

    # Background nodes
    for n in nodes:
        ax.scatter(float(n['longitude']), float(n['latitude']),
                   c='#D5D8DC', s=15, zorder=1, edgecolors='none')

    # Routes by vehicle type
    route_ids = sorted(set(r['route_id'] for r in routes))
    for rid in route_ids:
        stops = sorted([r for r in routes if r['route_id'] == rid],
                       key=lambda x: int(x['stop_sequence']))
        vid = stops[0]['vehicle_id']
        color = VEHICLE_COLORS.get(vid, 'gray')

        xs, ys = [], []
        for s in stops:
            nid = s['node_id']
            if nid in node_coords:
                xs.append(node_coords[nid][0])
                ys.append(node_coords[nid][1])
        if xs:
            xs.append(DEPOT_LON)
            ys.append(DEPOT_LAT)
            ax.plot(xs, ys, color=color, linewidth=2.0, alpha=0.7, zorder=2)

        # Plot stops
        for s in stops:
            nid = s['node_id']
            if nid in node_coords and nid != 'DEPOT_DSRSLCC':
                ax.scatter(node_coords[nid][0], node_coords[nid][1],
                           c=color, s=35, zorder=3, edgecolors='black', linewidths=0.5)

    ax.scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=200, marker='*', zorder=5,
               edgecolors='black', linewidths=1.0)

    legend_elements = [Line2D([0], [0], color=c, lw=3, label=VEHICLE_LABELS[v])
                       for v, c in VEHICLE_COLORS.items()]
    legend_elements.append(Line2D([0], [0], marker='*', color='red', lw=0,
                                   markersize=12, label='Depósito'))
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9, framealpha=0.9)
    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Figura A2: Asignación de Rutas por Tipo de Vehículo',
                 fontweight='bold')
    ax.set_aspect('equal')
    savefig(fig, 'A2_mapa_vehiculos')


def fig_A3_cadena_frio():
    """A3: Mapa de cadena de frío (arquitectura preparada, demand=0)."""
    nodes = load_nodes()

    fig, ax = plt.subplots(figsize=(10, 10))

    cold = [n for n in nodes if float(n.get('cold_chain_demand', 0)) > 0]
    no_cold = [n for n in nodes if float(n.get('cold_chain_demand', 0)) == 0]

    ax.scatter([float(n['longitude']) for n in no_cold],
               [float(n['latitude']) for n in no_cold],
               c='#BDC3C7', s=25, marker='o', zorder=2,
               edgecolors='gray', linewidths=0.3,
               label=f'Sin demanda cold-chain (n={len(no_cold)})')

    if cold:
        ax.scatter([float(n['longitude']) for n in cold],
                   [float(n['latitude']) for n in cold],
                   c='#2980B9', s=60, marker='D', zorder=3,
                   edgecolors='black', linewidths=0.8,
                   label=f'Cold-chain activo (n={len(cold)})')

    # Show Ducato coverage zone
    ax.scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=200, marker='*', zorder=5,
               edgecolors='black', linewidths=1.0, label='Depósito DSRSLCC')

    # Add info box
    info_text = ('Estado Cadena de Frío:\n'
                 '  Fiat Ducato Refrigerada: 2 unid.\n'
                 '  cold_chain_demand: 0 (todos)\n'
                 '  Arquitectura: PREPARADA\n'
                 '  Activación: requiere SISMED\n'
                 '  Ventana: 08:00–13:00 (propuesta)')
    props = dict(boxstyle='round', facecolor='#EBF5FB', alpha=0.9)
    ax.text(0.02, 0.02, info_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='bottom', bbox=props)

    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Figura A3: Red de Cadena de Frío Farmacéutica\n'
                 'Arquitectura preparada — pendiente calibración SISMED',
                 fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.set_aspect('equal')
    savefig(fig, 'A3_cadena_frio')


def fig_A4_fragilidad_operacional():
    """A4: Mapa de fragilidad operacional por ruta."""
    routes = load_routes()
    nodes = load_nodes()

    node_coords = {}
    for n in nodes:
        node_coords[n['node_id']] = (float(n['longitude']), float(n['latitude']))
    node_coords['DEPOT_DSRSLCC'] = (DEPOT_LON, DEPOT_LAT)

    # Route utilization from first stop of each route
    route_info = {}
    for r in routes:
        rid = r['route_id']
        if rid not in route_info and r['stop_sequence'] == '0':
            route_info[rid] = {
                'vehicle_id': r['vehicle_id'],
                'capacity': float(r['capacity_kg']),
                'load': float(r['route_load_kg']),
                'util': float(r['utilization_pct']) / 100.0,
                'distance': float(r['route_distance_km']),
            }

    fig, ax = plt.subplots(figsize=(10, 10))

    # Background
    for n in nodes:
        ax.scatter(float(n['longitude']), float(n['latitude']),
                   c='#D5D8DC', s=10, zorder=1)

    route_ids = sorted(set(r['route_id'] for r in routes))
    norm = Normalize(vmin=0.4, vmax=1.0)
    cmap_frag = cm.RdYlGn_r

    for rid in route_ids:
        stops = sorted([r for r in routes if r['route_id'] == rid],
                       key=lambda x: int(x['stop_sequence']))
        info = route_info.get(rid, {})
        util = info.get('util', 0.5)

        xs, ys = [], []
        for s in stops:
            nid = s['node_id']
            if nid in node_coords:
                xs.append(node_coords[nid][0])
                ys.append(node_coords[nid][1])
        if xs:
            xs.append(DEPOT_LON)
            ys.append(DEPOT_LAT)
            color = cmap_frag(norm(util))
            lw = 3.5 if util > 0.9 else 1.8
            ax.plot(xs, ys, color=color, linewidth=lw, alpha=0.8, zorder=2)

        # Node markers sized by fragility
        for s in stops:
            nid = s['node_id']
            if nid in node_coords and nid != 'DEPOT_DSRSLCC':
                marker_s = 60 if util > 0.9 else 25
                ax.scatter(node_coords[nid][0], node_coords[nid][1],
                           c=[cmap_frag(norm(util))], s=marker_s, zorder=3,
                           edgecolors='black', linewidths=0.5)

    ax.scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=200, marker='*', zorder=5,
               edgecolors='black', linewidths=1.0)

    sm = cm.ScalarMappable(cmap=cmap_frag, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, label='Utilización de Capacidad')
    cbar.set_ticks([0.4, 0.6, 0.8, 0.9, 1.0])
    cbar.set_ticklabels(['40%', '60%', '80%', '90%\n(alto)', '100%\n(crítico)'])

    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Figura A4: Fragilidad Operacional por Ruta\n'
                 'Rutas Hilux (util >95%) en rojo — mayor grosor = mayor riesgo',
                 fontweight='bold')
    ax.set_aspect('equal')
    savefig(fig, 'A4_fragilidad_operacional')


def fig_A5_congestion_tiempos():
    """A5: Mapa de congestión y variabilidad de tiempos de viaje."""
    arcs = load_arcs()
    nodes = load_nodes()

    fig, ax = plt.subplots(figsize=(10, 10))

    # Background nodes
    for n in nodes:
        ax.scatter(float(n['longitude']), float(n['latitude']),
                   c='#D5D8DC', s=12, zorder=1)

    # Arcs colored by travel_time_cv
    cvs = [float(a['travel_time_cv']) for a in arcs if a.get('travel_time_cv')]
    norm = Normalize(vmin=min(cvs), vmax=max(cvs) if max(cvs) > min(cvs) else min(cvs) + 0.1)
    cmap_cong = cm.YlOrRd

    for arc in arcs:
        cv = float(arc.get('travel_time_cv', 0.2))
        dur = float(arc.get('duration_min', 0))
        color = cmap_cong(norm(cv))
        lw = 0.5 + (dur / 60.0)
        ax.plot([float(arc['origin_lon']), float(arc['destination_lon'])],
                [float(arc['origin_lat']), float(arc['destination_lat'])],
                color=color, linewidth=min(lw, 2.5), alpha=0.6, zorder=2)

    ax.scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=200, marker='*', zorder=5,
               edgecolors='black', linewidths=1.0, label='Depósito')

    sm = cm.ScalarMappable(cmap=cmap_cong, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, label='CV Tiempo de Viaje')

    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title('Figura A5: Variabilidad de Tiempos de Viaje\n'
                 'Grosor ∝ duración, color ∝ CV temporal',
                 fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_aspect('equal')
    savefig(fig, 'A5_congestion_tiempos')


# ──────────────────────────────────────────────
# B. VISUALIZACIONES MONTE CARLO
# ──────────────────────────────────────────────

def fig_B6_distribucion_costos():
    """B6: Distribución de costos determinista vs estocástico."""
    mc = load_mc()
    costs = [float(r['total_cost']) for r in mc]
    det_cost = 5088.86

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(costs, bins=40, density=True, color='#3498DB', alpha=0.7,
            edgecolor='black', linewidth=0.5, label='Distribución estocástica (500 esc.)')

    # KDE
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(costs)
    x_range = np.linspace(min(costs) * 0.9, max(costs) * 1.05, 300)
    ax.plot(x_range, kde(x_range), color='#1A5276', linewidth=2.5, label='KDE')

    # Deterministic line
    ax.axvline(det_cost, color='#C0392B', linewidth=2.5, linestyle='--',
               label=f'Determinista: S/ {det_cost:,.0f}')
    # Mean
    mean_cost = np.mean(costs)
    ax.axvline(mean_cost, color='#27AE60', linewidth=2, linestyle='-.',
               label=f'E[Costo]: S/ {mean_cost:,.0f}')
    # VaR/CVaR
    var95 = np.percentile(costs, 95)
    ax.axvline(var95, color='#E67E22', linewidth=2, linestyle=':',
               label=f'VaR 5%: S/ {var95:,.0f}')

    ax.set_xlabel('Costo Total (S/)')
    ax.set_ylabel('Densidad')
    ax.set_title('Figura B6: Distribución de Costos — Determinista vs Estocástico\n'
                 f'Gap promedio: +{((mean_cost/det_cost)-1)*100:.0f}% | '
                 f'Skewness: {_skewness(costs):.2f}',
                 fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    savefig(fig, 'B6_distribucion_costos')


def _skewness(data):
    n = len(data)
    m = np.mean(data)
    s = np.std(data, ddof=1)
    return (n / ((n-1)*(n-2))) * np.sum(((np.array(data) - m) / s) ** 3)


def fig_B7_convergencia_mc():
    """B7: Convergencia Monte Carlo n=100,500,1000,2000."""
    rows = load_convergence()
    ns = [int(r['n_scenarios']) for r in rows]
    ecosts = [float(r['expected_cost']) for r in rows]
    ci_widths = [float(r['ci95_width']) for r in rows]
    ci_rels = [float(r['ci95_relative']) for r in rows]
    cvars = [float(r['CVaR_0.05']) for r in rows]
    rels = [float(r['reliability']) for r in rows]

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))

    # (a) E[cost]
    axes[0, 0].plot(ns, ecosts, 'bo-', markersize=8, linewidth=2)
    axes[0, 0].fill_between(ns,
                             [e - float(rows[i]['ci95_width'])/2 for i, e in enumerate(ecosts)],
                             [e + float(rows[i]['ci95_width'])/2 for i, e in enumerate(ecosts)],
                             alpha=0.2, color='blue')
    axes[0, 0].axhline(y=ecosts[-1], color='gray', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('N escenarios')
    axes[0, 0].set_ylabel('E[Costo] (S/)')
    axes[0, 0].set_title('(a) Costo Esperado con IC 95%')
    axes[0, 0].set_xscale('log')
    axes[0, 0].set_xticks(ns)
    axes[0, 0].get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # (b) CI relative width
    axes[0, 1].plot(ns, ci_rels, 'ro-', markersize=8, linewidth=2)
    axes[0, 1].axhline(y=5.0, color='green', linestyle='--', alpha=0.5, label='Umbral 5%')
    axes[0, 1].set_xlabel('N escenarios')
    axes[0, 1].set_ylabel('IC 95% relativo (%)')
    axes[0, 1].set_title('(b) Convergencia del IC')
    axes[0, 1].set_xscale('log')
    axes[0, 1].set_xticks(ns)
    axes[0, 1].get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    axes[0, 1].legend(fontsize=9)

    # (c) CVaR
    axes[1, 0].plot(ns, cvars, 'go-', markersize=8, linewidth=2)
    axes[1, 0].axhline(y=cvars[-1], color='gray', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('N escenarios')
    axes[1, 0].set_ylabel('CVaR 5% (S/)')
    axes[1, 0].set_title('(c) CVaR 5% — Estabilidad')
    axes[1, 0].set_xscale('log')
    axes[1, 0].set_xticks(ns)
    axes[1, 0].get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # (d) Reliability
    axes[1, 1].plot(ns, [r*100 for r in rels], 'mo-', markersize=8, linewidth=2)
    axes[1, 1].axhline(y=rels[-1]*100, color='gray', linestyle='--', alpha=0.5)
    axes[1, 1].set_xlabel('N escenarios')
    axes[1, 1].set_ylabel('Route Reliability (%)')
    axes[1, 1].set_title('(d) Reliability')
    axes[1, 1].set_xscale('log')
    axes[1, 1].set_xticks(ns)
    axes[1, 1].get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    axes[1, 1].set_ylim([0, max(r*100 for r in rels) * 1.5 + 1])

    plt.suptitle('Figura B7: Convergencia Monte Carlo (100–2000 escenarios)',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'B7_convergencia_montecarlo')


def fig_B8_distribucion_reliability():
    """B8: Distribución de reliability por escenario."""
    mc = load_mc()
    # Reliability per scenario: 1 if cap_violations==0 and tw_violations==0
    reliabilities = []
    for r in mc:
        cap_v = int(r['cap_violations'])
        tw_v = int(r['tw_violations'])
        reliabilities.append(1 if cap_v == 0 and tw_v == 0 else 0)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # (a) Pie chart of reliability
    rel_count = sum(reliabilities)
    fail_count = len(reliabilities) - rel_count
    axes[0].pie([rel_count, fail_count],
                labels=[f'Factible\n({rel_count}, {rel_count/len(reliabilities)*100:.1f}%)',
                        f'Infactible\n({fail_count}, {fail_count/len(reliabilities)*100:.1f}%)'],
                colors=['#27AE60', '#C0392B'],
                autopct='', startangle=90,
                wedgeprops=dict(edgecolor='black', linewidth=0.5))
    axes[0].set_title('(a) Factibilidad por Escenario')

    # (b) Violation count distribution
    cap_viols = [int(r['cap_violations']) for r in mc]
    tw_viols = [int(r['tw_violations']) for r in mc]
    max_v = max(max(cap_viols), max(tw_viols)) + 1
    bins = np.arange(-0.5, max_v + 0.5, 1)

    axes[1].hist(cap_viols, bins=bins, alpha=0.7, color='#E74C3C',
                 edgecolor='black', linewidth=0.5, label='Cap. violations')
    axes[1].hist(tw_viols, bins=bins, alpha=0.5, color='#3498DB',
                 edgecolor='black', linewidth=0.5, label='TW violations')
    axes[1].set_xlabel('Número de Violaciones')
    axes[1].set_ylabel('Frecuencia')
    axes[1].set_title('(b) Distribución de Violaciones')
    axes[1].legend()

    plt.suptitle('Figura B8: Reliability y Violaciones bajo Incertidumbre (500 escenarios)',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'B8_distribucion_reliability')


def fig_B9_distribucion_violaciones():
    """B9: Distribución detallada de violaciones de capacidad."""
    mc = load_mc()
    cap_excess = [float(r['cap_excess_kg']) for r in mc]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # (a) Histogram of excess
    excess_nonzero = [e for e in cap_excess if e > 0]
    if excess_nonzero:
        axes[0].hist(excess_nonzero, bins=30, color='#E74C3C', alpha=0.7,
                     edgecolor='black', linewidth=0.5)
        axes[0].axvline(np.mean(excess_nonzero), color='black', linestyle='--',
                        label=f'Media: {np.mean(excess_nonzero):.0f} kg')
        axes[0].axvline(np.median(excess_nonzero), color='blue', linestyle=':',
                        label=f'Mediana: {np.median(excess_nonzero):.0f} kg')
    axes[0].set_xlabel('Exceso de Capacidad (kg)')
    axes[0].set_ylabel('Frecuencia')
    axes[0].set_title('(a) Distribución de Exceso (escenarios con violación)')
    axes[0].legend(fontsize=9)

    # (b) CDF
    sorted_excess = np.sort(cap_excess)
    cdf = np.arange(1, len(sorted_excess) + 1) / len(sorted_excess)
    axes[1].plot(sorted_excess, cdf, color='#C0392B', linewidth=2)
    axes[1].axhline(0.95, color='gray', linestyle='--', alpha=0.5, label='95%')
    axes[1].set_xlabel('Exceso de Capacidad (kg)')
    axes[1].set_ylabel('P(X ≤ x)')
    axes[1].set_title('(b) CDF de Exceso de Capacidad')
    axes[1].legend()

    plt.suptitle('Figura B9: Violaciones de Capacidad bajo Incertidumbre',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'B9_violaciones_capacidad')


def fig_B10_boxplots():
    """B10: Boxplots de demanda, costos, reliability, utilización."""
    mc = load_mc()
    costs = [float(r['total_cost']) for r in mc]
    loads = [float(r['total_load_kg']) for r in mc]
    utils = [float(r['avg_utilization']) for r in mc]
    cap_viols = [int(r['cap_violations']) for r in mc]

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    bp1 = axes[0, 0].boxplot(costs, vert=True, patch_artist=True)
    bp1['boxes'][0].set_facecolor('#3498DB')
    axes[0, 0].axhline(5088.86, color='red', linestyle='--', label='Determinista')
    axes[0, 0].set_ylabel('S/')
    axes[0, 0].set_title('(a) Costo Total')
    axes[0, 0].set_xticklabels(['500 esc.'])
    axes[0, 0].legend(fontsize=9)

    bp2 = axes[0, 1].boxplot(loads, vert=True, patch_artist=True)
    bp2['boxes'][0].set_facecolor('#27AE60')
    axes[0, 1].axhline(16169, color='red', linestyle='--', label='Demanda nominal')
    axes[0, 1].set_ylabel('kg')
    axes[0, 1].set_title('(b) Carga Total')
    axes[0, 1].set_xticklabels(['500 esc.'])
    axes[0, 1].legend(fontsize=9)

    bp3 = axes[1, 0].boxplot(utils, vert=True, patch_artist=True)
    bp3['boxes'][0].set_facecolor('#E67E22')
    axes[1, 0].set_ylabel('Proporción')
    axes[1, 0].set_title('(c) Utilización Promedio')
    axes[1, 0].set_xticklabels(['500 esc.'])

    bp4 = axes[1, 1].boxplot(cap_viols, vert=True, patch_artist=True)
    bp4['boxes'][0].set_facecolor('#E74C3C')
    axes[1, 1].set_ylabel('Cantidad')
    axes[1, 1].set_title('(d) Violaciones de Capacidad')
    axes[1, 1].set_xticklabels(['500 esc.'])

    plt.suptitle('Figura B10: Distribución de KPIs bajo 500 Escenarios MC',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'B10_boxplots_kpis')


def fig_B11_heatmap_sensibilidad():
    """B11: Heatmap CV demanda × CV tiempo → costo esperado / reliability."""
    rows = load_sensitivity()

    demand_cvs = sorted(set(float(r['demand_cv']) for r in rows))
    time_cvs = sorted(set(float(r['time_cv']) for r in rows))

    # Build matrices
    cost_matrix = np.zeros((len(demand_cvs), len(time_cvs)))
    rel_matrix = np.zeros((len(demand_cvs), len(time_cvs)))
    cap_matrix = np.zeros((len(demand_cvs), len(time_cvs)))

    for r in rows:
        di = demand_cvs.index(float(r['demand_cv']))
        ti = time_cvs.index(float(r['time_cv']))
        cost_matrix[di, ti] = float(r['expected_cost'])
        rel_matrix[di, ti] = float(r['route_reliability']) * 100
        cap_matrix[di, ti] = float(r['cap_violation_rate']) * 100

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    xlabels = [f'{t:.1f}' for t in time_cvs]
    ylabels = [f'{d:.1f}' for d in demand_cvs]

    # Cost heatmap
    im0 = axes[0].imshow(cost_matrix, cmap='YlOrRd', aspect='auto')
    axes[0].set_xticks(range(len(time_cvs)))
    axes[0].set_xticklabels(xlabels)
    axes[0].set_yticks(range(len(demand_cvs)))
    axes[0].set_yticklabels(ylabels)
    axes[0].set_xlabel('CV Tiempo')
    axes[0].set_ylabel('CV Demanda')
    axes[0].set_title('(a) E[Costo] (S/)')
    for i in range(len(demand_cvs)):
        for j in range(len(time_cvs)):
            axes[0].text(j, i, f'{cost_matrix[i,j]:,.0f}', ha='center', va='center', fontsize=8)
    plt.colorbar(im0, ax=axes[0], shrink=0.8)

    # Reliability heatmap
    im1 = axes[1].imshow(rel_matrix, cmap='RdYlGn', aspect='auto')
    axes[1].set_xticks(range(len(time_cvs)))
    axes[1].set_xticklabels(xlabels)
    axes[1].set_yticks(range(len(demand_cvs)))
    axes[1].set_yticklabels(ylabels)
    axes[1].set_xlabel('CV Tiempo')
    axes[1].set_ylabel('CV Demanda')
    axes[1].set_title('(b) Reliability (%)')
    for i in range(len(demand_cvs)):
        for j in range(len(time_cvs)):
            axes[1].text(j, i, f'{rel_matrix[i,j]:.0f}%', ha='center', va='center', fontsize=8)
    plt.colorbar(im1, ax=axes[1], shrink=0.8)

    # Cap violations heatmap
    im2 = axes[2].imshow(cap_matrix, cmap='YlOrRd', aspect='auto')
    axes[2].set_xticks(range(len(time_cvs)))
    axes[2].set_xticklabels(xlabels)
    axes[2].set_yticks(range(len(demand_cvs)))
    axes[2].set_yticklabels(ylabels)
    axes[2].set_xlabel('CV Tiempo')
    axes[2].set_ylabel('CV Demanda')
    axes[2].set_title('(c) Cap Violation (%)')
    for i in range(len(demand_cvs)):
        for j in range(len(time_cvs)):
            axes[2].text(j, i, f'{cap_matrix[i,j]:.0f}%', ha='center', va='center', fontsize=8)
    plt.colorbar(im2, ax=axes[2], shrink=0.8)

    plt.suptitle('Figura B11: Sensibilidad Cruzada — CV Demanda × CV Tiempo',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'B11_heatmap_sensibilidad')


def fig_B12_var_cvar():
    """B12: Curvas VaR y CVaR por nivel de riesgo α."""
    mc = load_mc()
    costs = sorted([float(r['total_cost']) for r in mc])

    alphas = np.arange(0.01, 0.51, 0.01)
    vars_list = []
    cvars_list = []
    for a in alphas:
        idx = int(np.ceil((1 - a) * len(costs))) - 1
        var_val = costs[min(idx, len(costs)-1)]
        tail = [c for c in costs if c >= var_val]
        cvar_val = np.mean(tail) if tail else var_val
        vars_list.append(var_val)
        cvars_list.append(cvar_val)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(alphas * 100, vars_list, color='#2980B9', linewidth=2.5, label='VaR(α)')
    ax.plot(alphas * 100, cvars_list, color='#C0392B', linewidth=2.5, label='CVaR(α)')
    ax.fill_between(alphas * 100, vars_list, cvars_list, alpha=0.15, color='#E74C3C',
                    label='Exceso CVaR sobre VaR')

    # Annotate key points
    for a_key in [0.01, 0.05, 0.10]:
        idx_k = int(np.ceil((1 - a_key) * len(costs))) - 1
        var_k = costs[min(idx_k, len(costs)-1)]
        tail_k = [c for c in costs if c >= var_k]
        cvar_k = np.mean(tail_k) if tail_k else var_k
        ax.annotate(f'α={a_key:.0%}\nVaR={var_k:,.0f}\nCVaR={cvar_k:,.0f}',
                    xy=(a_key * 100, cvar_k),
                    xytext=(a_key * 100 + 5, cvar_k + 500),
                    fontsize=8, arrowprops=dict(arrowstyle='->', color='gray'),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.8))

    ax.axhline(5088.86, color='gray', linestyle=':', alpha=0.5, label='Costo determinista')
    ax.set_xlabel('Nivel de Riesgo α (%)')
    ax.set_ylabel('Costo (S/)')
    ax.set_title('Figura B12: Curvas VaR y CVaR por Nivel de Riesgo',
                 fontweight='bold')
    ax.legend(loc='lower left', fontsize=9)
    savefig(fig, 'B12_var_cvar_curvas')


# ──────────────────────────────────────────────
# C. FRAGILIDAD DE FLOTA
# ──────────────────────────────────────────────

def fig_C13_slack_variabilidad():
    """C13: Ratio slack/variabilidad — figura diagnóstica principal."""
    resources = ['Tiempo\n(Ventana 8h)', 'FUSO\nCanter 6T', 'NLR\n3.5T',
                 'Ducato\n3T (Refrig.)', 'Hilux\n1T']
    slacks = [3.5*60, 2400, 1200, 800, 46]     # minutes for time, kg for capacity
    variabilities = [0.8*60, 1500, 700, 650, 420]
    ratios = [s/v for s, v in zip(slacks, variabilities)]
    colors = ['#3498DB', '#27AE60', '#27AE60', '#F39C12', '#C0392B']

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # (a) Bar chart of ratios
    x = np.arange(len(resources))
    bars = axes[0].bar(x, ratios, color=colors, edgecolor='black', linewidth=0.8, width=0.6)
    axes[0].axhline(y=1.0, color='red', linewidth=2.5, linestyle='--',
                    label='Umbral de fragilidad (ratio = 1)')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(resources, fontsize=10)
    axes[0].set_ylabel('Ratio Slack / Variabilidad (1σ)')
    axes[0].set_title('(a) Ratio Slack/Variabilidad por Recurso')
    axes[0].legend(fontsize=9, loc='upper right')

    for bar, ratio in zip(bars, ratios):
        va = 'bottom' if ratio > 0.3 else 'bottom'
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
                     f'{ratio:.2f}', ha='center', va=va, fontweight='bold', fontsize=11)

    # Zone annotation
    axes[0].axhspan(0, 1, alpha=0.08, color='red', label='Zona de riesgo')
    axes[0].axhspan(1, max(ratios) * 1.2, alpha=0.05, color='green')

    # (b) Stacked decomposition
    axes[1].barh(x, slacks, color=[c + '80' for c in colors], edgecolor='black',
                 linewidth=0.5, label='Slack disponible')
    axes[1].barh(x, [-v for v in variabilities], color=colors, edgecolor='black',
                 linewidth=0.5, alpha=0.6, label='Variabilidad (1σ)')
    axes[1].set_yticks(x)
    axes[1].set_yticklabels(resources, fontsize=10)
    axes[1].set_xlabel('kg (capacidad) / min (tiempo)')
    axes[1].set_title('(b) Slack vs Variabilidad (1σ)')
    axes[1].axvline(0, color='black', linewidth=1)
    axes[1].legend(fontsize=9)

    plt.suptitle('Figura C13: Diagnóstico Slack/Variabilidad — Factor Clave de Fragilidad\n'
                 'Hilux ratio = 0.11 (40× peor que tiempo) — cuello de botella estructural',
                 fontweight='bold', y=1.03)
    plt.tight_layout()
    savefig(fig, 'C13_slack_variabilidad')


def fig_C14_utilizacion_vehiculos():
    """C14: Utilización por tipo de vehículo."""
    routes = load_routes()

    # Get per-route info
    route_data = {}
    for r in routes:
        if r['stop_sequence'] == '0':
            route_data[r['route_id']] = {
                'vehicle': r['vehicle_name'],
                'vehicle_id': r['vehicle_id'],
                'capacity': float(r['capacity_kg']),
                'load': float(r['route_load_kg']),
                'util': float(r['utilization_pct']),
            }

    vehicles = sorted(route_data.values(), key=lambda x: x['util'], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    y = np.arange(len(vehicles))
    utils = [v['util'] for v in vehicles]
    labels = [f"R{list(route_data.keys())[list(route_data.values()).index(v)]}: {v['vehicle']}"
              for v in vehicles]
    colors = [VEHICLE_COLORS.get(v['vehicle_id'], 'gray') for v in vehicles]

    bars = ax.barh(y, utils, color=colors, edgecolor='black', linewidth=0.5)
    ax.axvline(85, color='orange', linewidth=2, linestyle='--', label='Umbral 85%')
    ax.axvline(95, color='red', linewidth=2, linestyle='--', label='Umbral crítico 95%')

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Utilización (%)')
    ax.set_title('Figura C14: Utilización de Capacidad por Ruta/Vehículo',
                 fontweight='bold')
    ax.legend(fontsize=9)

    for bar, util in zip(bars, utils):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{util:.1f}%', va='center', fontsize=9)

    savefig(fig, 'C14_utilizacion_vehiculos')


def fig_C15_con_sin_hilux():
    """C15: Comparación con Hilux vs sin Hilux."""
    rows = load_capacity()

    baseline = None
    no_hilux_nlr = None
    no_hilux_fuso = None

    for r in rows:
        if r['experiment'] == 'baseline':
            baseline = r
        elif r['experiment'] == 'no_hilux_+NLR':
            no_hilux_nlr = r
        elif r['experiment'] == 'no_hilux_+FUSO':
            no_hilux_fuso = r

    if not all([baseline, no_hilux_nlr, no_hilux_fuso]):
        print("  WARNING: Missing capacity experiment data for C15")
        return

    configs = ['Con Hilux\n(Baseline)', 'Sin Hilux\n+NLR', 'Sin Hilux\n+FUSO']
    data_list = [baseline, no_hilux_nlr, no_hilux_fuso]

    metrics = {
        'E[Costo] (S/)': [float(d['expected_cost']) for d in data_list],
        'Reliability (%)': [float(d['reliability'])*100 for d in data_list],
        'Cap Viol (%)': [float(d['cap_violation_rate'])*100 for d in data_list],
        'CVaR 5% (S/)': [float(d['CVaR_0.05']) for d in data_list],
    }

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.flatten()
    colors_bar = ['#C0392B', '#27AE60', '#2980B9']

    for idx, (metric, values) in enumerate(metrics.items()):
        x = np.arange(len(configs))
        bars = axes[idx].bar(x, values, color=colors_bar, edgecolor='black', linewidth=0.5)
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels(configs, fontsize=10)
        axes[idx].set_ylabel(metric)
        axes[idx].set_title(f'({chr(97+idx)}) {metric}')

        for bar, val in zip(bars, values):
            fmt = f'{val:,.0f}' if 'S/' in metric else f'{val:.1f}%'
            axes[idx].text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
                           fmt, ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.suptitle('Figura C15: Impacto de Eliminación de Hilux en Métricas de Riesgo\n'
                 'Reliability pasa de 6.5% a 95–98% al reemplazar Hilux',
                 fontweight='bold', y=1.03)
    plt.tight_layout()
    savefig(fig, 'C15_con_sin_hilux')


def fig_C16_matriz_robustez():
    """C16: Matriz de robustez operacional (10 configuraciones)."""
    rows = load_capacity()
    rows = [r for r in rows if r.get('feasible', 'True') == 'True']

    exps = [r['experiment'] for r in rows]
    rels = [float(r['reliability']) * 100 for r in rows]
    costs = [float(r['expected_cost']) for r in rows]
    cap_viols = [float(r['cap_violation_rate']) * 100 for r in rows]

    fig, ax = plt.subplots(figsize=(10, 7))

    colors = []
    for e in exps:
        if e == 'baseline':
            colors.append('#C0392B')
        elif 'hilux' in e.lower():
            colors.append('#27AE60')
        elif 'buffer' in e:
            colors.append('#F39C12')
        else:
            colors.append('#2980B9')

    scatter = ax.scatter(costs, rels, c=colors, s=[max(150, cv*3) for cv in cap_viols],
                         edgecolors='black', linewidths=0.8, zorder=3)

    for i, exp in enumerate(exps):
        ax.annotate(exp, (costs[i], rels[i]),
                    textcoords="offset points", xytext=(8, 5),
                    fontsize=8, alpha=0.9)

    ax.axhline(85, color='green', linestyle='--', alpha=0.4, label='Target Reliability 85%')
    ax.set_xlabel('E[Costo] (S/)')
    ax.set_ylabel('Route Reliability (%)')
    ax.set_title('Figura C16: Matriz de Robustez — Costo vs Reliability\n'
                 'Tamaño ∝ tasa de violación de capacidad',
                 fontweight='bold')
    ax.legend(fontsize=9)

    # Quadrant labels
    ax.text(0.02, 0.98, 'IDEAL\n(bajo costo,\nalta reliability)',
            transform=ax.transAxes, fontsize=8, va='top', color='green', alpha=0.6)
    ax.text(0.85, 0.02, 'PEOR\n(alto costo,\nbaja reliability)',
            transform=ax.transAxes, fontsize=8, va='bottom', color='red', alpha=0.6)

    savefig(fig, 'C16_matriz_robustez')


def fig_C17_violaciones_por_vehiculo():
    """C17: Violaciones por tipo de vehículo (Monte Carlo)."""
    routes = load_routes()

    # Identify Hilux vs non-Hilux routes
    hilux_routes = []
    other_routes = []
    for r in routes:
        if r['stop_sequence'] == '0':
            if r['vehicle_id'] == 'V4_TOYOTA_HILUX':
                hilux_routes.append(r['route_id'])
            else:
                other_routes.append(r['route_id'])

    # From baseline route info
    route_info = {}
    for r in routes:
        if r['stop_sequence'] == '0':
            route_info[r['route_id']] = {
                'vehicle': r['vehicle_name'],
                'vehicle_id': r['vehicle_id'],
                'capacity': float(r['capacity_kg']),
                'load': float(r['route_load_kg']),
                'util': float(r['utilization_pct']),
                'slack_kg': float(r['capacity_kg']) - float(r['route_load_kg']),
            }

    vehicles_types = ['FUSO Canter 6T', 'NLR 3.5 TON', 'Toyota Hilux']
    slacks = []
    utils_det = []
    n_routes = []

    for vt in vehicles_types:
        matching = [ri for ri in route_info.values() if ri['vehicle'] == vt]
        slacks.append(np.mean([m['slack_kg'] for m in matching]) if matching else 0)
        utils_det.append(np.mean([m['util'] for m in matching]) if matching else 0)
        n_routes.append(len(matching))

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    x = np.arange(len(vehicles_types))
    colors_v = ['#2980B9', '#27AE60', '#C0392B']

    # (a) Deterministic slack
    bars = axes[0].bar(x, slacks, color=colors_v, edgecolor='black', linewidth=0.5)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(vehicles_types, fontsize=9)
    axes[0].set_ylabel('Slack (kg)')
    axes[0].set_title('(a) Slack Determinista Promedio')
    for bar, s in zip(bars, slacks):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                     f'{s:.0f} kg', ha='center', fontsize=9)

    # (b) Deterministic utilization
    bars = axes[1].bar(x, utils_det, color=colors_v, edgecolor='black', linewidth=0.5)
    axes[1].axhline(85, color='orange', linestyle='--', label='85%')
    axes[1].axhline(95, color='red', linestyle='--', label='95%')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(vehicles_types, fontsize=9)
    axes[1].set_ylabel('Utilización (%)')
    axes[1].set_title('(b) Utilización Determinista')
    axes[1].legend(fontsize=8)
    for bar, u in zip(bars, utils_det):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                     f'{u:.1f}%', ha='center', fontsize=9)

    # (c) Number of routes
    bars = axes[2].bar(x, n_routes, color=colors_v, edgecolor='black', linewidth=0.5)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(vehicles_types, fontsize=9)
    axes[2].set_ylabel('Número de Rutas')
    axes[2].set_title('(c) Rutas Asignadas')
    for bar, nr in zip(bars, n_routes):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     str(nr), ha='center', fontsize=11, fontweight='bold')

    plt.suptitle('Figura C17: Perfil de Vulnerabilidad por Tipo de Vehículo',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'C17_violaciones_por_vehiculo')


def fig_C18_cuello_botella():
    """C18: Análisis de cuello de botella — por qué Hilux falla."""
    fig = plt.figure(figsize=(12, 7))
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)

    # (a) Capacity comparison
    ax1 = fig.add_subplot(gs[0, 0])
    vehicles = ['FUSO\n6T', 'NLR\n3.5T', 'Ducato\n3T', 'Hilux\n1T']
    caps = [6000, 3500, 3000, 1000]
    colors_v = ['#2980B9', '#27AE60', '#F39C12', '#C0392B']
    ax1.bar(range(len(vehicles)), caps, color=colors_v, edgecolor='black', linewidth=0.5)
    ax1.set_xticks(range(len(vehicles)))
    ax1.set_xticklabels(vehicles, fontsize=9)
    ax1.set_ylabel('Capacidad (kg)')
    ax1.set_title('(a) Capacidad Nominal')

    # (b) Cost per km
    ax2 = fig.add_subplot(gs[0, 1])
    costs_km = [2.5, 2.0, 3.0, 1.5]
    ax2.bar(range(len(vehicles)), costs_km, color=colors_v, edgecolor='black', linewidth=0.5)
    ax2.set_xticks(range(len(vehicles)))
    ax2.set_xticklabels(vehicles, fontsize=9)
    ax2.set_ylabel('S/ / km')
    ax2.set_title('(b) Costo por km')

    # (c) Ratio costo/capacidad
    ax3 = fig.add_subplot(gs[0, 2])
    ratios_ck = [c/k for c, k in zip(costs_km, caps)]
    ax3.bar(range(len(vehicles)), [r*1000 for r in ratios_ck], color=colors_v,
            edgecolor='black', linewidth=0.5)
    ax3.set_xticks(range(len(vehicles)))
    ax3.set_xticklabels(vehicles, fontsize=9)
    ax3.set_ylabel('S/ / (km·ton) ×10³')
    ax3.set_title('(c) Eficiencia Costo/Capacidad')

    # (d) Root cause diagram
    ax4 = fig.add_subplot(gs[1, :])
    ax4.axis('off')

    flow_text = (
        '┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐    ┌──────────────────┐\n'
        '│  Solver OR-Tools │───▶│ Minimiza costo/km│───▶│  Asigna 5 rutas  │───▶│ Utilización >95% │\n'
        '│  determinista    │    │ Hilux = S/1.5/km │    │  a Hilux (1T)    │    │ Slack = 46 kg    │\n'
        '└─────────────────┘    └──────────────────┘    └───────────────────┘    └──────────────────┘\n'
        '                                                                              │\n'
        '                                                                              ▼\n'
        '┌─────────────────┐    ┌──────────────────┐    ┌───────────────────┐    ┌──────────────────┐\n'
        '│  Reliability     │◀───│ 93.5% escenarios │◀───│ σ demanda = 420kg│◀───│ CV SISMED = 0.42 │\n'
        '│  colapsa a 5.9% │    │ violan capacidad │    │ >> 46 kg slack   │    │ (incertidumbre)  │\n'
        '└─────────────────┘    └──────────────────┘    └───────────────────┘    └──────────────────┘'
    )
    ax4.text(0.5, 0.5, flow_text, transform=ax4.transAxes,
             fontsize=8, fontfamily='monospace', ha='center', va='center',
             bbox=dict(boxstyle='round', facecolor='#FEF9E7', alpha=0.9))
    ax4.set_title('(d) Cadena Causal: Por qué el Solver Determinista Induce Fragilidad',
                  fontweight='bold')

    plt.suptitle('Figura C18: Análisis de Cuello de Botella — Toyota Hilux',
                 fontweight='bold', y=1.02)
    savefig(fig, 'C18_cuello_botella')


# ──────────────────────────────────────────────
# D. RESULTADOS HVRPTW
# ──────────────────────────────────────────────

def fig_D19_kpi_dashboard():
    """D19: KPI dashboard científico."""
    fig = plt.figure(figsize=(14, 8))
    gs = GridSpec(2, 4, figure=fig, hspace=0.5, wspace=0.4)

    kpis = [
        ('Costo Det.', 'S/ 5,089', '#3498DB'),
        ('E[Costo] MC', 'S/ 8,160', '#E74C3C'),
        ('Reliability', '5.9%', '#C0392B'),
        ('CVaR 5%', 'S/ 14,021', '#8E44AD'),
        ('Rutas', '10', '#27AE60'),
        ('Nodos', '81/81', '#2980B9'),
        ('Distancia', '1,962 km', '#F39C12'),
        ('Util. Media', '71.8%', '#1ABC9C'),
    ]

    for idx, (label, value, color) in enumerate(kpis):
        row = idx // 4
        col = idx % 4
        ax = fig.add_subplot(gs[row, col])
        ax.axis('off')

        ax.add_patch(plt.Rectangle((0.05, 0.1), 0.9, 0.8, transform=ax.transAxes,
                     facecolor=color, alpha=0.15, edgecolor=color, linewidth=2,
                     clip_on=False))
        ax.text(0.5, 0.65, value, transform=ax.transAxes,
                fontsize=20, fontweight='bold', ha='center', va='center', color=color)
        ax.text(0.5, 0.25, label, transform=ax.transAxes,
                fontsize=11, ha='center', va='center', color='#2C3E50')

    plt.suptitle('Figura D19: Dashboard de KPIs — HVRPTW DSRSLCC\n'
                 'Baseline determinista vs evaluación estocástica (2000 escenarios)',
                 fontweight='bold', y=1.02)
    savefig(fig, 'D19_kpi_dashboard')


def fig_D20_gantt_rutas():
    """D20: Gantt chart de rutas baseline."""
    routes = load_routes()

    fig, ax = plt.subplots(figsize=(14, 7))

    route_ids = sorted(set(r['route_id'] for r in routes), key=int)
    y_positions = {rid: idx for idx, rid in enumerate(route_ids)}

    for rid in route_ids:
        stops = sorted([r for r in routes if r['route_id'] == rid],
                       key=lambda x: int(x['stop_sequence']))
        vid = stops[0]['vehicle_id']
        color = VEHICLE_COLORS.get(vid, 'gray')

        for i, stop in enumerate(stops):
            if stop['arrival_time']:
                start_min = time_to_minutes(stop['arrival_time'])
                svc = int(stop['service_time_min']) if stop['service_time_min'] else 0
                y = y_positions[rid]

                # Travel segment
                if i > 0:
                    prev_end = time_to_minutes(stops[i-1]['arrival_time']) + int(stops[i-1].get('service_time_min', 0) or 0)
                    ax.barh(y, start_min - prev_end, left=prev_end, height=0.4,
                            color=color, alpha=0.3, edgecolor='none')

                # Service segment
                ax.barh(y, svc, left=start_min, height=0.6,
                        color=color, alpha=0.8, edgecolor='black', linewidth=0.3)

    ax.set_yticks(range(len(route_ids)))
    ax.set_yticklabels([f'Ruta {rid} ({[r["vehicle_name"] for r in routes if r["route_id"]==rid][0]})'
                        for rid in route_ids], fontsize=9)

    # Time axis
    hours = list(range(8, 17))
    ax.set_xticks([h * 60 for h in hours])
    ax.set_xticklabels([f'{h}:00' for h in hours])
    ax.set_xlabel('Hora del día')
    ax.set_xlim(7.5*60, 16.5*60)
    ax.axvline(16*60, color='red', linestyle='--', alpha=0.5, label='Cierre ventana (16:00)')
    ax.axvline(8*60, color='green', linestyle='--', alpha=0.5, label='Apertura ventana (08:00)')

    legend_elements = [Line2D([0], [0], color=c, lw=6, label=VEHICLE_LABELS[v])
                       for v, c in VEHICLE_COLORS.items() if v != 'V2_FIAT_DUCATO']
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    ax.set_title('Figura D20: Diagrama Gantt de Rutas Baseline\n'
                 'Barras opacas = servicio en nodo, barras translúcidas = tránsito',
                 fontweight='bold')
    ax.invert_yaxis()
    savefig(fig, 'D20_gantt_rutas')


def fig_D21_carga_por_ruta():
    """D21: Carga por ruta vs capacidad."""
    routes = load_routes()

    route_data = {}
    for r in routes:
        if r['stop_sequence'] == '0':
            route_data[r['route_id']] = {
                'vehicle': r['vehicle_name'],
                'vehicle_id': r['vehicle_id'],
                'capacity': float(r['capacity_kg']),
                'load': float(r['route_load_kg']),
                'util': float(r['utilization_pct']),
            }

    rids = sorted(route_data.keys(), key=int)

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(rids))
    width = 0.35

    loads = [route_data[rid]['load'] for rid in rids]
    caps = [route_data[rid]['capacity'] for rid in rids]
    colors = [VEHICLE_COLORS.get(route_data[rid]['vehicle_id'], 'gray') for rid in rids]

    ax.bar(x - width/2, caps, width, label='Capacidad', color='#BDC3C7',
           edgecolor='black', linewidth=0.5)
    bars = ax.bar(x + width/2, loads, width, label='Carga asignada',
                  color=colors, edgecolor='black', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([f'R{rid}\n{route_data[rid]["vehicle"][:8]}' for rid in rids],
                       fontsize=8)
    ax.set_ylabel('Peso (kg)')
    ax.set_title('Figura D21: Carga Asignada vs Capacidad por Ruta',
                 fontweight='bold')
    ax.legend(fontsize=10)

    for bar, load, cap in zip(bars, loads, caps):
        util = load/cap * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f'{util:.0f}%', ha='center', fontsize=8, fontweight='bold')

    savefig(fig, 'D21_carga_por_ruta')


def fig_D22_distancia_por_vehiculo():
    """D22: Distancia por ruta/vehículo."""
    routes = load_routes()

    route_data = {}
    for r in routes:
        if r['stop_sequence'] == '0':
            route_data[r['route_id']] = {
                'vehicle': r['vehicle_name'],
                'vehicle_id': r['vehicle_id'],
                'distance': float(r['route_distance_km']),
            }

    rids = sorted(route_data.keys(), key=int)

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(rids))
    distances = [route_data[rid]['distance'] for rid in rids]
    colors = [VEHICLE_COLORS.get(route_data[rid]['vehicle_id'], 'gray') for rid in rids]

    bars = ax.bar(x, distances, color=colors, edgecolor='black', linewidth=0.5)
    ax.axhline(np.mean(distances), color='gray', linestyle='--',
               label=f'Promedio: {np.mean(distances):.0f} km')

    ax.set_xticks(x)
    ax.set_xticklabels([f'R{rid}\n{route_data[rid]["vehicle"][:8]}' for rid in rids],
                       fontsize=8)
    ax.set_ylabel('Distancia (km)')
    ax.set_title('Figura D22: Distancia por Ruta',
                 fontweight='bold')
    ax.legend(fontsize=10)

    for bar, d in zip(bars, distances):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                f'{d:.0f}', ha='center', fontsize=9)

    savefig(fig, 'D22_distancia_por_vehiculo')


def fig_D23_tiempo_por_ruta():
    """D23: Tiempo total por ruta (tránsito + servicio)."""
    routes = load_routes()

    route_ids = sorted(set(r['route_id'] for r in routes), key=int)
    route_times = {}

    for rid in route_ids:
        stops = sorted([r for r in routes if r['route_id'] == rid],
                       key=lambda x: int(x['stop_sequence']))
        first_arrival = time_to_minutes(stops[0]['arrival_time'])
        last_stop = stops[-1]
        last_arrival = time_to_minutes(last_stop['arrival_time'])
        last_svc = int(last_stop['service_time_min']) if last_stop['service_time_min'] else 0
        total_time = (last_arrival + last_svc) - first_arrival

        total_svc = sum(int(s['service_time_min']) for s in stops if s['service_time_min'])
        total_transit = total_time - total_svc

        route_times[rid] = {
            'total': total_time,
            'service': total_svc,
            'transit': total_transit,
            'vehicle': stops[0]['vehicle_name'],
            'vehicle_id': stops[0]['vehicle_id'],
        }

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(route_ids))
    svcs = [route_times[rid]['service'] for rid in route_ids]
    transits = [route_times[rid]['transit'] for rid in route_ids]
    colors = [VEHICLE_COLORS.get(route_times[rid]['vehicle_id'], 'gray') for rid in route_ids]

    ax.bar(x, svcs, label='Servicio', color=colors, edgecolor='black', linewidth=0.5, alpha=0.8)
    ax.bar(x, transits, bottom=svcs, label='Tránsito', color=colors,
           edgecolor='black', linewidth=0.5, alpha=0.4)

    ax.axhline(8*60, color='red', linestyle='--', alpha=0.5, label='Ventana máxima (8h)')

    ax.set_xticks(x)
    ax.set_xticklabels([f'R{rid}\n{route_times[rid]["vehicle"][:8]}' for rid in route_ids],
                       fontsize=8)
    ax.set_ylabel('Minutos')
    ax.set_title('Figura D23: Tiempo Total por Ruta (Servicio + Tránsito)',
                 fontweight='bold')
    ax.legend(fontsize=9)

    for i, rid in enumerate(route_ids):
        total = route_times[rid]['total']
        ax.text(i, total + 5, f'{total//60}h{total%60:02d}m',
                ha='center', fontsize=8)

    savefig(fig, 'D23_tiempo_por_ruta')


def fig_D24_utilizacion_espacial():
    """D24: Utilización espacial — demanda geográfica vs asignación."""
    nodes = load_nodes()
    routes = load_routes()

    node_coords = {}
    node_demand = {}
    for n in nodes:
        nid = n['node_id']
        node_coords[nid] = (float(n['longitude']), float(n['latitude']))
        node_demand[nid] = float(n['demand_mean'])

    # Assign vehicle to each node based on routes
    node_vehicle = {}
    for r in routes:
        nid = r['node_id']
        if nid != 'DEPOT_DSRSLCC':
            node_vehicle[nid] = r['vehicle_id']

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # (a) Demand heat
    demands = [node_demand.get(n['node_id'], 0) for n in nodes]
    norm_d = Normalize(vmin=min(demands), vmax=max(demands))

    sc = axes[0].scatter([float(n['longitude']) for n in nodes],
                         [float(n['latitude']) for n in nodes],
                         c=demands, cmap='YlOrRd', s=50,
                         edgecolors='black', linewidths=0.3, norm=norm_d, zorder=3)
    axes[0].scatter([DEPOT_LON], [DEPOT_LAT], c='blue', s=200, marker='*',
                    zorder=5, edgecolors='black')
    plt.colorbar(sc, ax=axes[0], shrink=0.7, label='Demanda (kg/mes)')
    axes[0].set_xlabel('Longitud')
    axes[0].set_ylabel('Latitud')
    axes[0].set_title('(a) Distribución Geográfica de Demanda')
    axes[0].set_aspect('equal')

    # (b) Vehicle assignment
    for n in nodes:
        nid = n['node_id']
        vid = node_vehicle.get(nid, 'UNKNOWN')
        color = VEHICLE_COLORS.get(vid, '#BDC3C7')
        axes[1].scatter(float(n['longitude']), float(n['latitude']),
                        c=color, s=40, edgecolors='black', linewidths=0.3, zorder=3)
    axes[1].scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=200, marker='*',
                    zorder=5, edgecolors='black')

    legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=c,
                              markersize=10, label=VEHICLE_LABELS[v])
                       for v, c in VEHICLE_COLORS.items()]
    axes[1].legend(handles=legend_elements, loc='upper left', fontsize=8)
    axes[1].set_xlabel('Longitud')
    axes[1].set_ylabel('Latitud')
    axes[1].set_title('(b) Asignación de Vehículos a IPRESS')
    axes[1].set_aspect('equal')

    plt.suptitle('Figura D24: Utilización Espacial — Demanda vs Asignación Vehicular',
                 fontweight='bold', y=1.02)
    plt.tight_layout()
    savefig(fig, 'D24_utilizacion_espacial')


# ──────────────────────────────────────────────
# E. TABLAS FINALES (CSV + Figure tables)
# ──────────────────────────────────────────────

def generate_final_tables():
    """Generate CSV/Excel tables for publication."""
    import csv as csv_mod

    # Table 1: KPI Summary
    with open(os.path.join(TABLES_DIR, 'tabla_01_kpi_resumen.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['KPI', 'Determinista', 'Estocástico (2000 esc.)', 'Gap'])
        w.writerow(['Costo total (S/)', '5,089', '8,160', '+60.4%'])
        w.writerow(['Route Reliability', '100%', '5.9%', '-94.1 pp'])
        w.writerow(['Cap Violation Rate', '0%', '93.5%', '+93.5 pp'])
        w.writerow(['TW Violation Rate', '0%', '9.6%', '+9.6 pp'])
        w.writerow(['CVaR 5% (S/)', '5,089', '14,021', '+175.5%'])
        w.writerow(['Service Level', '100%', '100%', '0%'])
        w.writerow(['Rutas', '10', '10', '—'])
        w.writerow(['Distancia (km)', '1,962', '1,962', '—'])
        w.writerow(['Utilización media', '71.8%', '64.5%', '-7.3 pp'])

    # Table 2: Sensitivity conversion factor
    with open(os.path.join(TABLES_DIR, 'tabla_02_sensibilidad_conversion.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['Factor', 'Demanda Total (kg)', 'E[Costo] (S/)', 'Reliability (%)',
                     'Cap Violation (%)', 'TW Violation (%)', 'CVaR 5% (S/)', 'Dominante'])
        rows = load_conversion()
        for r in rows:
            if r.get('feasible') == 'True':
                w.writerow([r['conversion'], f"{float(r['total_demand_kg']):,.0f}",
                           f"{float(r['expected_cost']):,.0f}",
                           f"{float(r['reliability'])*100:.1f}",
                           f"{float(r['cap_violation_rate'])*100:.1f}",
                           f"{float(r['tw_violation_rate'])*100:.1f}",
                           f"{float(r['CVaR_0.05']):,.0f}", 'CAPACIDAD'])

    # Table 3: Fleet experiments
    with open(os.path.join(TABLES_DIR, 'tabla_03_experimentos_flota.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['Experimento', 'Vehículos', 'Capacidad (kg)', 'Rutas',
                     'E[Costo] (S/)', 'Reliability (%)', 'Cap Viol (%)',
                     'CVaR 5% (S/)', 'D/C Ratio'])
        rows = load_capacity()
        for r in rows:
            if r.get('feasible', 'True') == 'True':
                w.writerow([r['experiment'], r['n_vehicles'], f"{float(r['total_capacity_kg']):,.0f}",
                           r['n_routes'], f"{float(r['expected_cost']):,.0f}",
                           f"{float(r['reliability'])*100:.1f}",
                           f"{float(r['cap_violation_rate'])*100:.1f}",
                           f"{float(r['CVaR_0.05']):,.0f}",
                           f"{float(r['demand_capacity_ratio']):.3f}"])

    # Table 4: Convergence
    with open(os.path.join(TABLES_DIR, 'tabla_04_convergencia_mc.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['N Escenarios', 'E[Costo] (S/)', 'Std (S/)', 'CV',
                     'CVaR 5% (S/)', 'Reliability (%)', 'IC 95% Relativo (%)'])
        rows = load_convergence()
        for r in rows:
            w.writerow([r['n_scenarios'], f"{float(r['expected_cost']):,.0f}",
                       f"{float(r['std_cost']):,.0f}", f"{float(r['cv_cost']):.3f}",
                       f"{float(r['CVaR_0.05']):,.0f}",
                       f"{float(r['reliability'])*100:.1f}",
                       f"{float(r['ci95_relative']):.1f}"])

    # Table 5: Sensitivity matrix
    with open(os.path.join(TABLES_DIR, 'tabla_05_sensibilidad_cruzada.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['CV Demanda', 'CV Tiempo', 'E[Costo] (S/)', 'Reliability (%)',
                     'Cap Viol (%)', 'CVaR 5% (S/)'])
        rows = load_sensitivity()
        for r in rows:
            w.writerow([r['demand_cv'], r['time_cv'],
                       f"{float(r['expected_cost']):,.0f}",
                       f"{float(r['route_reliability'])*100:.1f}",
                       f"{float(r['cap_violation_rate'])*100:.1f}",
                       f"{float(r['CVaR_0.05']):,.0f}"])

    # Table 6: Route details
    with open(os.path.join(TABLES_DIR, 'tabla_06_rutas_baseline.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['Ruta', 'Vehículo', 'Capacidad (kg)', 'Carga (kg)',
                     'Utilización (%)', 'Distancia (km)', 'Paradas', 'Slack (kg)'])
        routes = load_routes()
        for rid in sorted(set(r['route_id'] for r in routes), key=int):
            stops = [r for r in routes if r['route_id'] == rid]
            first = [r for r in stops if r['stop_sequence'] == '0'][0]
            n_stops = len(stops) - 1
            cap = float(first['capacity_kg'])
            load = float(first['route_load_kg'])
            w.writerow([rid, first['vehicle_name'], f"{cap:.0f}", f"{load:.0f}",
                       f"{float(first['utilization_pct']):.1f}",
                       f"{float(first['route_distance_km']):.1f}",
                       n_stops, f"{cap-load:.0f}"])

    # Table 7: Slack/variability ratios
    with open(os.path.join(TABLES_DIR, 'tabla_07_slack_variabilidad.csv'), 'w', newline='') as f:
        w = csv_mod.writer(f)
        w.writerow(['Recurso', 'Slack Disponible', 'Variabilidad (1σ)',
                     'Ratio', 'Clasificación'])
        w.writerow(['Tiempo (Ventana 8h)', '210 min', '48 min', '4.38', 'SEGURO'])
        w.writerow(['FUSO Canter 6T', '2,810 kg', '1,500 kg', '1.87', 'ACEPTABLE'])
        w.writerow(['NLR 3.5T', '1,200 kg', '700 kg', '1.71', 'ACEPTABLE'])
        w.writerow(['Ducato 3T (Refrig.)', '800 kg', '650 kg', '1.23', 'MARGINAL'])
        w.writerow(['Toyota Hilux 1T', '46 kg', '420 kg', '0.11', 'CRÍTICO'])

    print(f"  Tablas generadas en {TABLES_DIR}")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    print("=" * 60)
    print("GENERANDO VISUALIZACIONES CIENTÍFICAS FINALES")
    print("HVRPTW Estocástico — DSRSLCC Sullana")
    print("=" * 60)

    figures = [
        ('A1', 'Red General HVRPTW', fig_A1_red_general),
        ('A2', 'Mapa por Tipo de Vehículo', fig_A2_mapa_vehiculos),
        ('A3', 'Cadena de Frío', fig_A3_cadena_frio),
        ('A4', 'Fragilidad Operacional', fig_A4_fragilidad_operacional),
        ('A5', 'Congestión / Tiempos', fig_A5_congestion_tiempos),
        ('B6', 'Distribución de Costos', fig_B6_distribucion_costos),
        ('B7', 'Convergencia MC', fig_B7_convergencia_mc),
        ('B8', 'Distribución Reliability', fig_B8_distribucion_reliability),
        ('B9', 'Violaciones Capacidad', fig_B9_distribucion_violaciones),
        ('B10', 'Boxplots KPIs', fig_B10_boxplots),
        ('B11', 'Heatmap Sensibilidad', fig_B11_heatmap_sensibilidad),
        ('B12', 'Curvas VaR/CVaR', fig_B12_var_cvar),
        ('C13', 'Slack/Variabilidad (KEY)', fig_C13_slack_variabilidad),
        ('C14', 'Utilización por Vehículo', fig_C14_utilizacion_vehiculos),
        ('C15', 'Con/Sin Hilux', fig_C15_con_sin_hilux),
        ('C16', 'Matriz de Robustez', fig_C16_matriz_robustez),
        ('C17', 'Violaciones por Vehículo', fig_C17_violaciones_por_vehiculo),
        ('C18', 'Cuello de Botella', fig_C18_cuello_botella),
        ('D19', 'KPI Dashboard', fig_D19_kpi_dashboard),
        ('D20', 'Gantt de Rutas', fig_D20_gantt_rutas),
        ('D21', 'Carga por Ruta', fig_D21_carga_por_ruta),
        ('D22', 'Distancia por Vehículo', fig_D22_distancia_por_vehiculo),
        ('D23', 'Tiempo por Ruta', fig_D23_tiempo_por_ruta),
        ('D24', 'Utilización Espacial', fig_D24_utilizacion_espacial),
    ]

    for code, name, func in figures:
        try:
            func()
            print(f"  [{code}] {name} — OK")
        except Exception as e:
            print(f"  [{code}] {name} — ERROR: {e}")

    print("\nGenerando tablas finales...")
    generate_final_tables()

    print(f"\n{'='*60}")
    print(f"  Figuras: {FIGURES_DIR}")
    print(f"  Tablas:  {TABLES_DIR}")
    print(f"  Total figuras: {len(figures)} × 2 formatos (PNG + SVG)")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
