import matplotlib.pyplot as plt
import numpy as np
 
# Colour palette — cycles automatically for any number of matchups
PALETTE = [
    "steelblue", "tomato", "seagreen",
    "mediumpurple", "darkorange", "deeppink",
    "teal", "goldenrod",
]
 
 
def _label_bars(ax, bars, fmt):
    ylim_top = ax.get_ylim()[1]
    for bar in bars:
        val = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + ylim_top * 0.01,
            fmt.format(val),
            ha="center", va="bottom", fontsize=8,
        )
 
 
def plot_results(matchups, wins, win_rates, avg_turns, avg_win_hp, avg_fainted, n):
    m = len(matchups)
    x = np.arange(m)
    width = max(0.35, 0.6 - 0.04 * max(0, m - 3))
    colors = [PALETTE[i % len(PALETTE)] for i in range(m)]
 
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("AI Strategy Comparison — Gen 9 Random Battle", fontsize=15, fontweight="bold")
 
    def setup(ax, title, ylabel, ylim=None, rot=20):
        ax.set_title(title, fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(matchups, rotation=rot, ha="right", fontsize=8)
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(*ylim)
 
    # Win rate
    bars = axes[0][0].bar(x, [r * 100 for r in win_rates], width, color=colors)
    setup(axes[0][0], "Win Rate (%)", "Win Rate (%)", (0, 100))
    _label_bars(axes[0][0], bars, "{:.1f}%")
 
    # Avg turns
    bars = axes[0][1].bar(x, avg_turns, width, color=colors)
    setup(axes[0][1], "Avg Turns per Battle", "Turns")
    _label_bars(axes[0][1], bars, "{:.1f}")
 
    # Avg win HP
    bars = axes[0][2].bar(x, [h * 100 for h in avg_win_hp], width, color=colors)
    setup(axes[0][2], "Avg Team HP on Win (%)", "HP Remaining (%)", (0, 100))
    _label_bars(axes[0][2], bars, "{:.1f}%")
 
    # Win/loss stacked bar
    losses = [n - w for w in wins]
    axes[1][0].bar(x, wins,   width, label="Wins",   color="seagreen")
    axes[1][0].bar(x, losses, width, label="Losses", color="tomato", bottom=wins)
    setup(axes[1][0], "Win / Loss Breakdown", "Battles", (0, n))
    axes[1][0].legend(fontsize=9)
    for i, (w, lo) in enumerate(zip(wins, losses)):
        if w > 4:
            axes[1][0].text(i, w / 2,      str(w),  ha="center", va="center",
                            fontsize=8, color="white", fontweight="bold")
        if lo > 4:
            axes[1][0].text(i, w + lo / 2, str(lo), ha="center", va="center",
                            fontsize=8, color="white", fontweight="bold")
 
    # Avg fainted per battle
    bars = axes[1][1].bar(x, avg_fainted, width, color=colors)
    setup(axes[1][1], "Avg Pokemon Fainted per Battle", "Fainted", (0, 6))
    _label_bars(axes[1][1], bars, "{:.1f}")
 
    # Legend panel
    ax_legend = axes[1][2]
    ax_legend.axis("off")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(m)]
    ax_legend.legend(
        handles, matchups,
        loc="center", fontsize=9,
        title="Matchups (left player wins counted)",
        title_fontsize=9,
        frameon=True,
    )
 
    plt.tight_layout()
    plt.savefig("results.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved to results.png")
