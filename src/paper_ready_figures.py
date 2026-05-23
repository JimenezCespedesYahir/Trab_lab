"""
Paper-Ready Figures — HVRPTW Estocástico DSRSLCC
=================================================
Genera las 8 figuras seleccionadas para paper Q1 con formato
estricto APA7/IEEE, tipografía optimizada, y layout publicable.

Uso: python src/paper_ready_figures.py
"""

import csv
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
from matplotlib import cm

# ──────────────────────────────────────────────
# Paper Q1 Style
# ──────────────────────────────────────────────
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'mathtext.fontset': 'dejavuserif',
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'axes.titleweight': 'bold',
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.grid': True,
    'grid.alpha': 0.25,
    'grid.linewidth': 0.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 6,
})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
ANALYTICS_DIR = os.path.join(BASE_DIR, 'analytics')
PAPER_DIR = os.path.join(RESULTS_DIR, 'figures_paper')
os.makedirs(PAPER_DIR, exist_ok=True)

DEPOT_LAT = -4.906564
DEPOT_LON = -80.728434


def load_csv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def savefig(fig, name):
    for ext in ['png', 'pdf']:
        fig.savefig(os.path.join(PAPER_DIR, f'{name}.{ext}'))
    plt.close(fig)


# ──────────────────────────────────────────────
# Fig. 1 — Network (single column, 3.5")
# ──────────────────────────────────────────────
def fig1_network():
    nodes = load_csv(os.path.join(ANALYTICS_DIR, 'nodes_hvrptw.csv'))
    routes = load_csv(os.path.join(RESULTS_DIR, 'baseline_routes.csv'))

    node_coords = {}
    for n in nodes:
        node_coords[n['node_id']] = (float(n['longitude']), float(n['latitude']))
    node_coords['DEPOT_DSRSLCC'] = (DEPOT_LON, DEPOT_LAT)

    fig, ax = plt.subplots(figsize=(3.5, 3.5))

    # Routes
    vcolors = {'V1_FUSO_CANTER': '#2980B9', 'V3_NLR_35T': '#27AE60', 'V4_TOYOTA_HILUX': '#C0392B'}
    route_ids = sorted(set(r['route_id'] for r in routes))
    for rid in route_ids:
        stops = sorted([r for r in routes if r['route_id'] == rid], key=lambda x: int(x['stop_sequence']))
        vid = stops[0]['vehicle_id']
        xs, ys = [], []
        for s in stops:
            if s['node_id'] in node_coords:
                xs.append(node_coords[s['node_id']][0])
                ys.append(node_coords[s['node_id']][1])
        xs.append(DEPOT_LON); ys.append(DEPOT_LAT)
        ax.plot(xs, ys, color=vcolors.get(vid, 'gray'), linewidth=0.8, alpha=0.6, zorder=2)

    # Nodes
    cs = [n for n in nodes if n['categoria'] == 'CENTRO DE SALUD']
    ps = [n for n in nodes if n['categoria'] != 'CENTRO DE SALUD']
    ax.scatter([float(n['longitude']) for n in cs], [float(n['latitude']) for n in cs],
               c='#2980B9', s=18, marker='s', zorder=3, edgecolors='black', linewidths=0.3,
               label=f'CS (n={len(cs)})')
    ax.scatter([float(n['longitude']) for n in ps], [float(n['latitude']) for n in ps],
               c='#27AE60', s=12, marker='o', zorder=3, edgecolors='black', linewidths=0.3,
               label=f'PS (n={len(ps)})')
    ax.scatter([DEPOT_LON], [DEPOT_LAT], c='red', s=60, marker='*', zorder=5,
               edgecolors='black', linewidths=0.5, label='Depot')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Fig. 1. HVRPTW network (81 IPRESS)')
    ax.legend(loc='upper left', fontsize=7, framealpha=0.9, handletextpad=0.3)
    ax.set_aspect('equal')
    ax.tick_params(labelsize=7)
    savefig(fig, 'fig01_network')


# ──────────────────────────────────────────────
# Fig. 2 — Cost distribution (single column)
# ──────────────────────────────────────────────
def fig2_cost_distribution():
    mc = load_csv(os.path.join(RESULTS_DIR, 'montecarlo_results_500.csv'))
    costs = [float(r['total_cost']) for r in mc]
    det = 5088.86

    from scipy.stats import gaussian_kde
    kde = gaussian_kde(costs)
    x = np.linspace(min(costs)*0.9, max(costs)*1.05, 300)

    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.hist(costs, bins=35, density=True, color='#3498DB', alpha=0.6,
            edgecolor='black', linewidth=0.3)
    ax.plot(x, kde(x), color='#1A5276', linewidth=1.5)
    ax.axvline(det, color='#C0392B', linewidth=1.5, linestyle='--', label=f'Det. S/{det:,.0f}')
    ax.axvline(np.mean(costs), color='#27AE60', linewidth=1.2, linestyle='-.',
               label=f'E[C] S/{np.mean(costs):,.0f}')
    ax.axvline(np.percentile(costs, 95), color='#E67E22', linewidth=1.2, linestyle=':',
               label=f'VaR₅% S/{np.percentile(costs, 95):,.0f}')

    ax.set_xlabel('Total Cost (S/)')
    ax.set_ylabel('Density')
    ax.set_title('Fig. 2. Cost distribution (500 MC scenarios)')
    ax.legend(fontsize=7, loc='upper right')
    savefig(fig, 'fig02_cost_distribution')


# ──────────────────────────────────────────────
# Fig. 3 — MC Convergence (double column)
# ──────────────────────────────────────────────
def fig3_convergence():
    rows = load_csv(os.path.join(RESULTS_DIR, 'convergence_analysis.csv'))
    ns = [int(r['n_scenarios']) for r in rows]
    ecosts = [float(r['expected_cost']) for r in rows]
    ci_rels = [float(r['ci95_relative']) for r in rows]
    cvars = [float(r['CVaR_0.05']) for r in rows]
    rels = [float(r['reliability'])*100 for r in rows]

    fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.2))

    for ax in axes:
        ax.set_xscale('log')
        ax.set_xticks(ns)
        ax.get_xaxis().set_major_formatter(mticker.ScalarFormatter())
        ax.tick_params(labelsize=7)

    axes[0].plot(ns, ecosts, 'bo-', markersize=4)
    axes[0].set_ylabel('E[Cost] (S/)', fontsize=8)
    axes[0].set_title('(a) Expected cost', fontsize=8)

    axes[1].plot(ns, ci_rels, 'ro-', markersize=4)
    axes[1].axhline(5.0, color='green', linestyle='--', alpha=0.5, linewidth=0.8)
    axes[1].set_ylabel('CI 95% rel. (%)', fontsize=8)
    axes[1].set_title('(b) Convergence', fontsize=8)

    axes[2].plot(ns, cvars, 'go-', markersize=4)
    axes[2].set_ylabel('CVaR₅% (S/)', fontsize=8)
    axes[2].set_title('(c) CVaR 5%', fontsize=8)

    axes[3].plot(ns, rels, 'mo-', markersize=4)
    axes[3].set_ylabel('Reliability (%)', fontsize=8)
    axes[3].set_title('(d) Reliability', fontsize=8)
    axes[3].set_ylim([0, max(rels)*1.5+1])

    for ax in axes:
        ax.set_xlabel('N scenarios', fontsize=8)

    plt.suptitle('Fig. 3. Monte Carlo convergence analysis', fontweight='bold', fontsize=9, y=1.05)
    plt.tight_layout()
    savefig(fig, 'fig03_convergence')


# ──────────────────────────────────────────────
# Fig. 4 — Sensitivity heatmap (double column)
# ──────────────────────────────────────────────
def fig4_sensitivity():
    rows = load_csv(os.path.join(RESULTS_DIR, 'sensitivity_analysis.csv'))
    demand_cvs = sorted(set(float(r['demand_cv']) for r in rows))
    time_cvs = sorted(set(float(r['time_cv']) for r in rows))

    cost_m = np.zeros((len(demand_cvs), len(time_cvs)))
    rel_m = np.zeros((len(demand_cvs), len(time_cvs)))

    for r in rows:
        di = demand_cvs.index(float(r['demand_cv']))
        ti = time_cvs.index(float(r['time_cv']))
        cost_m[di, ti] = float(r['expected_cost'])
        rel_m[di, ti] = float(r['route_reliability']) * 100

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8))

    im0 = axes[0].imshow(cost_m, cmap='YlOrRd', aspect='auto')
    axes[0].set_xticks(range(len(time_cvs)))
    axes[0].set_xticklabels([f'{t:.1f}' for t in time_cvs], fontsize=7)
    axes[0].set_yticks(range(len(demand_cvs)))
    axes[0].set_yticklabels([f'{d:.1f}' for d in demand_cvs], fontsize=7)
    axes[0].set_xlabel('CV travel time', fontsize=8)
    axes[0].set_ylabel('CV demand', fontsize=8)
    axes[0].set_title('(a) E[Cost] (S/)', fontsize=8)
    for i in range(len(demand_cvs)):
        for j in range(len(time_cvs)):
            axes[0].text(j, i, f'{cost_m[i,j]:,.0f}', ha='center', va='center', fontsize=6)
    plt.colorbar(im0, ax=axes[0], shrink=0.8)

    im1 = axes[1].imshow(rel_m, cmap='RdYlGn', aspect='auto')
    axes[1].set_xticks(range(len(time_cvs)))
    axes[1].set_xticklabels([f'{t:.1f}' for t in time_cvs], fontsize=7)
    axes[1].set_yticks(range(len(demand_cvs)))
    axes[1].set_yticklabels([f'{d:.1f}' for d in demand_cvs], fontsize=7)
    axes[1].set_xlabel('CV travel time', fontsize=8)
    axes[1].set_ylabel('CV demand', fontsize=8)
    axes[1].set_title('(b) Route reliability (%)', fontsize=8)
    for i in range(len(demand_cvs)):
        for j in range(len(time_cvs)):
            axes[1].text(j, i, f'{rel_m[i,j]:.0f}', ha='center', va='center', fontsize=6)
    plt.colorbar(im1, ax=axes[1], shrink=0.8)

    plt.suptitle('Fig. 4. Cross-sensitivity: demand CV × travel time CV',
                 fontweight='bold', fontsize=9, y=1.05)
    plt.tight_layout()
    savefig(fig, 'fig04_sensitivity')


# ──────────────────────────────────────────────
# Fig. 5 — Slack/variability (KEY — single column wide)
# ──────────────────────────────────────────────
def fig5_slack_variability():
    resources = ['Time\n(8h window)', 'FUSO\n6T', 'NLR\n3.5T', 'Ducato\n3T', 'Hilux\n1T']
    ratios = [4.38, 1.87, 1.71, 1.23, 0.11]
    colors = ['#3498DB', '#27AE60', '#27AE60', '#F39C12', '#C0392B']

    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    x = np.arange(len(resources))
    bars = ax.bar(x, ratios, color=colors, edgecolor='black', linewidth=0.5, width=0.55)

    ax.axhline(y=1.0, color='red', linewidth=1.5, linestyle='--', label='Fragility threshold')
    ax.axhspan(0, 1, alpha=0.06, color='red')

    ax.set_xticks(x)
    ax.set_xticklabels(resources, fontsize=8)
    ax.set_ylabel('Slack / Variability (1σ)')
    ax.set_title('Fig. 5. Slack-to-variability ratio')
    ax.legend(fontsize=7, loc='upper right')

    for bar, ratio in zip(bars, ratios):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06,
                f'{ratio:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=8)

    savefig(fig, 'fig05_slack_variability')


# ──────────────────────────────────────────────
# Fig. 6 — Fleet composition impact (double column)
# ──────────────────────────────────────────────
def fig6_fleet_impact():
    rows = load_csv(os.path.join(RESULTS_DIR, 'capacity_experiments.csv'))

    baseline = next(r for r in rows if r['experiment'] == 'baseline')
    no_nlr = next(r for r in rows if r['experiment'] == 'no_hilux_+NLR')
    no_fuso = next(r for r in rows if r['experiment'] == 'no_hilux_+FUSO')

    configs = ['With Hilux\n(Baseline)', 'Without Hilux\n(+NLR)', 'Without Hilux\n(+FUSO)']
    data = [baseline, no_nlr, no_fuso]
    colors_b = ['#C0392B', '#27AE60', '#2980B9']

    fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.5))

    metrics = [
        ('E[Cost] (S/)', 'expected_cost', False),
        ('Reliability (%)', 'reliability', True),
        ('Cap Viol. (%)', 'cap_violation_rate', True),
        ('CVaR₅% (S/)', 'CVaR_0.05', False),
    ]

    for idx, (label, key, pct) in enumerate(metrics):
        vals = [float(d[key]) * (100 if pct else 1) for d in data]
        x = np.arange(len(configs))
        bars = axes[idx].bar(x, vals, color=colors_b, edgecolor='black', linewidth=0.4, width=0.6)
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels(configs, fontsize=6)
        axes[idx].set_ylabel(label, fontsize=7)
        axes[idx].set_title(f'({chr(97+idx)})', fontsize=8)
        axes[idx].tick_params(labelsize=6)

        for bar, val in zip(bars, vals):
            fmt = f'{val:,.0f}' if not pct else f'{val:.0f}%'
            axes[idx].text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.01,
                           fmt, ha='center', va='bottom', fontsize=6, fontweight='bold')

    plt.suptitle('Fig. 6. Impact of Hilux elimination on risk metrics',
                 fontweight='bold', fontsize=9, y=1.08)
    plt.tight_layout()
    savefig(fig, 'fig06_fleet_impact')


# ──────────────────────────────────────────────
# Fig. 7 — Robustness frontier (single column)
# ──────────────────────────────────────────────
def fig7_robustness():
    rows = load_csv(os.path.join(RESULTS_DIR, 'capacity_experiments.csv'))
    rows = [r for r in rows if r.get('feasible', 'True') == 'True']

    exps = [r['experiment'] for r in rows]
    rels = [float(r['reliability'])*100 for r in rows]
    costs = [float(r['expected_cost']) for r in rows]
    cap_viols = [float(r['cap_violation_rate'])*100 for r in rows]

    colors = []
    for e in exps:
        if e == 'baseline': colors.append('#C0392B')
        elif 'hilux' in e.lower(): colors.append('#27AE60')
        elif 'buffer' in e: colors.append('#F39C12')
        else: colors.append('#2980B9')

    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    ax.scatter(costs, rels, c=colors, s=[max(30, cv*1.5) for cv in cap_viols],
               edgecolors='black', linewidths=0.5, zorder=3)

    for i, exp in enumerate(exps):
        short = exp.replace('no_hilux_', '−H ').replace('cap_', '').replace('buffer_', 'buf ')
        ax.annotate(short, (costs[i], rels[i]), textcoords="offset points",
                    xytext=(5, 3), fontsize=5.5, alpha=0.85)

    ax.axhline(85, color='green', linestyle='--', alpha=0.3, linewidth=0.8)
    ax.set_xlabel('E[Cost] (S/)')
    ax.set_ylabel('Route Reliability (%)')
    ax.set_title('Fig. 7. Cost-reliability frontier')

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#C0392B', markersize=6, label='Baseline'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#27AE60', markersize=6, label='No-Hilux'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#F39C12', markersize=6, label='Buffer'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2980B9', markersize=6, label='Capacity+'),
    ]
    ax.legend(handles=legend_elements, fontsize=6, loc='center left')
    savefig(fig, 'fig07_robustness_frontier')


# ──────────────────────────────────────────────
# Fig. 8 — Causal chain (double column)
# ──────────────────────────────────────────────
def fig8_causal():
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5))

    # (a) Capacity
    vehicles = ['FUSO\n6T', 'NLR\n3.5T', 'Ducato\n3T', 'Hilux\n1T']
    caps = [6000, 3500, 3000, 1000]
    colors_v = ['#2980B9', '#27AE60', '#F39C12', '#C0392B']

    axes[0].bar(range(4), caps, color=colors_v, edgecolor='black', linewidth=0.4)
    axes[0].set_xticks(range(4))
    axes[0].set_xticklabels(vehicles, fontsize=7)
    axes[0].set_ylabel('Capacity (kg)', fontsize=8)
    axes[0].set_title('(a) Nominal capacity', fontsize=8)
    axes[0].tick_params(labelsize=6)

    # (b) Cost/km
    costs_km = [2.5, 2.0, 3.0, 1.5]
    axes[1].bar(range(4), costs_km, color=colors_v, edgecolor='black', linewidth=0.4)
    axes[1].set_xticks(range(4))
    axes[1].set_xticklabels(vehicles, fontsize=7)
    axes[1].set_ylabel('S/ per km', fontsize=8)
    axes[1].set_title('(b) Cost per km', fontsize=8)
    axes[1].tick_params(labelsize=6)

    # (c) Utilization
    utils = [53.2, 58.4, 0, 95.7]
    axes[2].bar(range(4), utils, color=colors_v, edgecolor='black', linewidth=0.4)
    axes[2].axhline(85, color='orange', linestyle='--', linewidth=0.8, label='85%')
    axes[2].axhline(95, color='red', linestyle='--', linewidth=0.8, label='95%')
    axes[2].set_xticks(range(4))
    axes[2].set_xticklabels(vehicles, fontsize=7)
    axes[2].set_ylabel('Utilization (%)', fontsize=8)
    axes[2].set_title('(c) Deterministic util.', fontsize=8)
    axes[2].legend(fontsize=6)
    axes[2].tick_params(labelsize=6)

    plt.suptitle('Fig. 8. Bottleneck analysis: why Hilux induces fragility',
                 fontweight='bold', fontsize=9, y=1.05)
    plt.tight_layout()
    savefig(fig, 'fig08_bottleneck')


def main():
    print("Generating paper-ready figures (8 × PNG + PDF)...")
    funcs = [
        ('Fig.1', 'Network', fig1_network),
        ('Fig.2', 'Cost distribution', fig2_cost_distribution),
        ('Fig.3', 'MC Convergence', fig3_convergence),
        ('Fig.4', 'Sensitivity', fig4_sensitivity),
        ('Fig.5', 'Slack/Variability', fig5_slack_variability),
        ('Fig.6', 'Fleet impact', fig6_fleet_impact),
        ('Fig.7', 'Robustness frontier', fig7_robustness),
        ('Fig.8', 'Bottleneck', fig8_causal),
    ]
    for code, name, func in funcs:
        try:
            func()
            print(f"  [{code}] {name} — OK")
        except Exception as e:
            print(f"  [{code}] {name} — ERROR: {e}")

    print(f"\nPaper figures: {PAPER_DIR}")
    print(f"Total: {len(funcs)} × 2 formats (PNG 300dpi + PDF)")


if __name__ == '__main__':
    main()
