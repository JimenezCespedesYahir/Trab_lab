"""
Figuras Publicables — HVRPTW Estocástico DSRSLCC
=================================================
Genera figuras de calidad académica para tesis/paper.
"""

import csv
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker

# Style
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
    'axes.grid': True,
    'grid.alpha': 0.3,
})

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(RESULTS_DIR, 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)


def load_csv(filename):
    with open(os.path.join(RESULTS_DIR, filename), encoding='utf-8') as f:
        return list(csv.DictReader(f))


def fig_table_det_vs_stoch():
    """Table figure: deterministic vs stochastic comparison."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')

    data = [
        ['KPI', 'Determinista', 'Estocástico (2000 esc.)', 'Gap'],
        ['E[Costo]', 'S/ 5,089', 'S/ 8,160', '+61%'],
        ['Route Reliability', '100%', '5.9%', '-94 pp'],
        ['Cap Violation Rate', '0%', '93.5%', '+93.5 pp'],
        ['TW Violation Rate', '0%', '9.6%', '+9.6 pp'],
        ['CVaR 5%', 'S/ 5,089', 'S/ 14,021', '+175%'],
        ['Service Level', '100%', '100%', '0%'],
    ]

    table = ax.table(cellText=data[1:], colLabels=data[0],
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.5)

    # Style header
    for j in range(4):
        table[0, j].set_facecolor('#2C3E50')
        table[0, j].set_text_props(color='white', fontweight='bold')

    # Alternate row colors
    for i in range(1, 7):
        color = '#F8F9FA' if i % 2 == 0 else '#FFFFFF'
        for j in range(4):
            table[i, j].set_facecolor(color)

    # Highlight gap column
    for i in range(1, 7):
        table[i, 3].set_text_props(fontweight='bold')

    plt.title('Tabla 4: Comparación Determinista vs Estocástico', fontweight='bold', pad=20)
    plt.savefig(os.path.join(FIGURES_DIR, 'table_det_vs_stoch.png'))
    plt.close()


def fig_convergence():
    """Convergence analysis figure."""
    rows = load_csv('convergence_analysis.csv')
    ns = [int(r['n_scenarios']) for r in rows]
    ecosts = [float(r['expected_cost']) for r in rows]
    ci_widths = [float(r['ci95_width']) for r in rows]
    cvars = [float(r['CVaR_0.05']) for r in rows]
    rels = [float(r['reliability']) for r in rows]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # E[cost] convergence
    axes[0, 0].plot(ns, ecosts, 'bo-', markersize=8, linewidth=2)
    axes[0, 0].axhline(y=ecosts[-1], color='gray', linestyle='--', alpha=0.5)
    axes[0, 0].set_xlabel('N escenarios')
    axes[0, 0].set_ylabel('E[Costo] (S/)')
    axes[0, 0].set_title('(a) Costo Esperado')
    axes[0, 0].set_xscale('log')
    axes[0, 0].set_xticks(ns)
    axes[0, 0].get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # CI width
    axes[0, 1].plot(ns, ci_widths, 'ro-', markersize=8, linewidth=2)
    axes[0, 1].set_xlabel('N escenarios')
    axes[0, 1].set_ylabel('Ancho IC 95% (S/)')
    axes[0, 1].set_title('(b) Intervalo de Confianza')
    axes[0, 1].set_xscale('log')
    axes[0, 1].set_xticks(ns)
    axes[0, 1].get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # CVaR convergence
    axes[1, 0].plot(ns, cvars, 'go-', markersize=8, linewidth=2)
    axes[1, 0].axhline(y=cvars[-1], color='gray', linestyle='--', alpha=0.5)
    axes[1, 0].set_xlabel('N escenarios')
    axes[1, 0].set_ylabel('CVaR 5% (S/)')
    axes[1, 0].set_title('(c) CVaR 5%')
    axes[1, 0].set_xscale('log')
    axes[1, 0].set_xticks(ns)
    axes[1, 0].get_xaxis().set_major_formatter(mticker.ScalarFormatter())

    # Reliability convergence
    axes[1, 1].plot(ns, rels, 'mo-', markersize=8, linewidth=2)
    axes[1, 1].axhline(y=rels[-1], color='gray', linestyle='--', alpha=0.5)
    axes[1, 1].set_xlabel('N escenarios')
    axes[1, 1].set_ylabel('Route Reliability')
    axes[1, 1].set_title('(d) Reliability')
    axes[1, 1].set_xscale('log')
    axes[1, 1].set_xticks(ns)
    axes[1, 1].get_xaxis().set_major_formatter(mticker.ScalarFormatter())
    axes[1, 1].set_ylim([0, max(rels) * 1.5 + 0.01])

    plt.suptitle('Figura 3: Convergencia Monte Carlo', fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'pub_convergence.png'))
    plt.close()


def fig_sensitivity_conversion():
    """Conversion factor sensitivity figure."""
    rows = load_csv('sensitivity_conversion_factor.csv')
    rows = [r for r in rows if r.get('feasible') == 'True']

    labels = [r['conversion'] for r in rows]
    costs = [float(r['expected_cost']) for r in rows]
    rels = [float(r['reliability']) for r in rows]
    caps = [float(r['cap_violation_rate']) for r in rows]
    tws = [float(r['tw_violation_rate']) for r in rows]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    x = np.arange(len(labels))
    colors = ['#27AE60', '#2980B9', '#E67E22', '#C0392B']

    # Cost
    bars = axes[0].bar(x, costs, color=colors, edgecolor='black', linewidth=0.5)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel('E[Costo] (S/)')
    axes[0].set_title('(a) Costo Esperado')
    for bar, cost in zip(bars, costs):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                     f'S/ {cost:,.0f}', ha='center', va='bottom', fontsize=9)

    # Reliability
    bars = axes[1].bar(x, [r*100 for r in rels], color=colors, edgecolor='black', linewidth=0.5)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels)
    axes[1].set_ylabel('Reliability (%)')
    axes[1].set_title('(b) Route Reliability')
    axes[1].set_ylim([0, 100])

    # Violations comparison
    w = 0.35
    axes[2].bar(x - w/2, [c*100 for c in caps], w, label='Cap Violations', color='#E74C3C', edgecolor='black', linewidth=0.5)
    axes[2].bar(x + w/2, [t*100 for t in tws], w, label='TW Violations', color='#3498DB', edgecolor='black', linewidth=0.5)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels)
    axes[2].set_ylabel('Tasa de Violación (%)')
    axes[2].set_title('(c) Cap vs TW Violations')
    axes[2].legend()
    axes[2].set_ylim([0, 110])

    plt.suptitle('Figura 6: Sensibilidad del Factor de Conversión item→kg', fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'pub_sensitivity_conversion.png'))
    plt.close()


def fig_capacity_experiments():
    """Capacity/fleet experiments figure."""
    rows = load_csv('capacity_experiments.csv')
    rows = [r for r in rows if r.get('feasible') == 'True']

    exps = [r['experiment'] for r in rows]
    rels = [float(r['reliability'])*100 for r in rows]
    costs = [float(r['expected_cost']) for r in rows]
    cap_viols = [float(r['cap_violation_rate'])*100 for r in rows]

    # Sort by reliability
    sorted_data = sorted(zip(exps, rels, costs, cap_viols), key=lambda x: x[1])
    exps, rels, costs, cap_viols = zip(*sorted_data)

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    y = np.arange(len(exps))

    # Color by category
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

    # Reliability
    axes[0].barh(y, rels, color=colors, edgecolor='black', linewidth=0.5)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(exps, fontsize=9)
    axes[0].set_xlabel('Reliability (%)')
    axes[0].set_title('(a) Route Reliability')
    axes[0].axvline(x=85, color='green', linestyle='--', alpha=0.5, label='Target 85%')
    axes[0].legend(fontsize=8)

    # E[cost]
    axes[1].barh(y, costs, color=colors, edgecolor='black', linewidth=0.5)
    axes[1].set_yticks(y)
    axes[1].set_yticklabels(exps, fontsize=9)
    axes[1].set_xlabel('E[Costo] (S/)')
    axes[1].set_title('(b) Costo Esperado')

    # Cap violations
    axes[2].barh(y, cap_viols, color=colors, edgecolor='black', linewidth=0.5)
    axes[2].set_yticks(y)
    axes[2].set_yticklabels(exps, fontsize=9)
    axes[2].set_xlabel('Cap Violation Rate (%)')
    axes[2].set_title('(c) Violaciones de Capacidad')

    plt.suptitle('Figura 7: Experimentos de Capacidad y Flota', fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'pub_capacity_experiments.png'))
    plt.close()


def fig_factor_impact():
    """Relative factor impact figure."""
    # Data from experiments
    factors = ['Determinista', 'Solo Demanda\n(CV=0.20)', 'Solo Demanda\n(CV=0.42)',
               'Solo Demanda\n(CV=0.60)', 'Solo Tiempo\n(CV=0.10)',
               'Solo Tiempo\n(CV=0.20)', 'Solo Tiempo\n(CV=0.30)',
               'Ambos\n(SISMED)', 'Ambos\n(Alto)']
    deltas = [0, 19.3, 35.5, 95.2, 0.0, 0.1, 0.3, 59.1, 95.5]
    colors_map = ['#95A5A6', '#3498DB', '#2980B9', '#1A5276',
                  '#E67E22', '#E67E22', '#E67E22',
                  '#8E44AD', '#6C3483']

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(factors))
    bars = ax.bar(x, deltas, color=colors_map, edgecolor='black', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(factors, fontsize=9)
    ax.set_ylabel('ΔE[Costo] vs Determinista (%)')
    ax.set_title('Figura 9: Impacto Relativo de Factores de Incertidumbre', fontweight='bold')

    # Annotations
    for bar, delta in zip(bars, deltas):
        if delta > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'+{delta:.1f}%', ha='center', va='bottom', fontsize=9)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2980B9', label='Solo Demanda'),
        Patch(facecolor='#E67E22', label='Solo Tiempo'),
        Patch(facecolor='#8E44AD', label='Ambos'),
    ]
    ax.legend(handles=legend_elements, loc='upper left')

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'pub_factor_impact.png'))
    plt.close()


def fig_slack_variability():
    """Slack/variability ratio figure (key diagnostic)."""
    vehicles = ['Tiempo\n(Ventana 8h)', 'FUSO 6T', 'NLR 3.5T', 'Ducato 3T', 'Hilux 1T']
    ratios = [4.5, 1.6, 1.7, 1.2, 0.11]
    colors = ['#3498DB', '#27AE60', '#27AE60', '#F39C12', '#C0392B']

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(vehicles))
    bars = ax.bar(x, ratios, color=colors, edgecolor='black', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(vehicles)
    ax.set_ylabel('Ratio Slack / Variabilidad (σ)')
    ax.set_title('Figura 8: Ratio Slack/Variabilidad por Recurso', fontweight='bold')
    ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Umbral de fragilidad')
    ax.legend()

    for bar, ratio in zip(bars, ratios):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{ratio:.2f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, 'pub_slack_variability.png'))
    plt.close()


def fig_summary_table():
    """Summary results table for thesis/paper."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')

    data = [
        ['Experimento', 'Veh.', 'Rutas', 'E[Costo]', 'Reliability', 'Cap Viol', 'D/C'],
        ['Baseline', '16', '10', 'S/ 8,150', '6.5%', '93.5%', '0.323'],
        ['+10% cap', '16', '11', 'S/ 7,780', '14.5%', '84.5%', '0.294'],
        ['+20% cap', '16', '9', 'S/ 7,218', '11.0%', '88.0%', '0.269'],
        ['Buffer 85%', '16', '9', 'S/ 6,517', '25.0%', '75.0%', '0.380'],
        ['Buffer 75%', '16', '9', 'S/ 6,194', '43.0%', '55.5%', '0.431'],
        ['−Hilux +NLR', '16', '9', 'S/ 5,386', '95.5%', '3.5%', '0.249'],
        ['−Hilux +FUSO', '16', '9', 'S/ 5,818', '98.0%', '0.0%', '0.202'],
        ['+Ducato', '18', '10', 'S/ 7,803', '12.0%', '88.0%', '0.289'],
        ['+NLR', '20', '9', 'S/ 7,002', '16.0%', '84.0%', '0.253'],
    ]

    table = ax.table(cellText=data[1:], colLabels=data[0],
                     cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.4)

    # Style header
    for j in range(7):
        table[0, j].set_facecolor('#2C3E50')
        table[0, j].set_text_props(color='white', fontweight='bold')

    # Highlight best results
    for i in range(1, 10):
        color = '#F8F9FA' if i % 2 == 0 else '#FFFFFF'
        for j in range(7):
            table[i, j].set_facecolor(color)

    # Highlight no_hilux rows
    for j in range(7):
        table[6, j].set_facecolor('#D5F5E3')
        table[7, j].set_facecolor('#D5F5E3')

    # Highlight baseline
    for j in range(7):
        table[1, j].set_facecolor('#FADBD8')

    plt.title('Tabla 8: Experimentos de Capacidad y Flota (200 escenarios)', fontweight='bold', pad=20)
    plt.savefig(os.path.join(FIGURES_DIR, 'pub_table_capacity.png'))
    plt.close()


def main():
    print("Generando figuras publicables...")
    fig_table_det_vs_stoch()
    print("  [1/7] Tabla det vs stoch")
    fig_convergence()
    print("  [2/7] Convergencia MC")
    fig_sensitivity_conversion()
    print("  [3/7] Sensibilidad conversión")
    fig_capacity_experiments()
    print("  [4/7] Experimentos de capacidad")
    fig_factor_impact()
    print("  [5/7] Impacto de factores")
    fig_slack_variability()
    print("  [6/7] Slack/variabilidad")
    fig_summary_table()
    print("  [7/7] Tabla resumen de capacidad")
    print("\nFiguras generadas en results/figures/pub_*.png")


if __name__ == '__main__':
    main()
