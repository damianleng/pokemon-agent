import matplotlib.pyplot as plt
import numpy as np


def _label_bars(ax, bars, fmt):
    for bar in bars:
        val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, val + ax.get_ylim()[1] * 0.01,
                fmt.format(val), ha="center", va="bottom", fontsize=9)


def plot_results(matchups, wins, win_rates, avg_turns, avg_win_hp, avg_fainted, n):
    x = np.arange(len(matchups))
    width = 0.6
    colors = ["steelblue", "tomato", "seagreen", "mediumpurple", "darkorange"]
    c = colors[:len(matchups)]

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("AI Strategy Comparison (Gen 9 Random Battle)", fontsize=14)

    def setup(ax, title, ylabel, ylim=None):
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(matchups, rotation=12, ha="right")
        ax.set_ylabel(ylabel)
        if ylim:
            ax.set_ylim(*ylim)

    # Win rate
    bars = axes[0][0].bar(x, [r * 100 for r in win_rates], width, color=c)
    setup(axes[0][0], "Win Rate (%)", "Win Rate (%)", (0, 100))
    _label_bars(axes[0][0], bars, "{:.1f}%")

    # Avg turns
    bars = axes[0][1].bar(x, avg_turns, width, color=c)
    setup(axes[0][1], "Avg Turns per Battle", "Turns")
    _label_bars(axes[0][1], bars, "{:.1f}")

    # Avg win HP
    bars = axes[0][2].bar(x, [h * 100 for h in avg_win_hp], width, color=c)
    setup(axes[0][2], "Avg Team HP on Win (%)", "HP Remaining (%)", (0, 100))
    _label_bars(axes[0][2], bars, "{:.1f}%")

    # Win/loss stacked bar
    losses = [n - w for w in wins]
    axes[1][0].bar(x, wins, width, label="Wins", color="seagreen")
    axes[1][0].bar(x, losses, width, bottom=wins, label="Losses", color="tomato")
    setup(axes[1][0], "Win / Loss Breakdown", "Battles", (0, n))
    axes[1][0].legend()
    for i, (w, l) in enumerate(zip(wins, losses)):
        axes[1][0].text(i, w / 2, str(w), ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        axes[1][0].text(i, w + l / 2, str(l), ha="center", va="center", fontsize=9, color="white", fontweight="bold")

    # Avg fainted per battle
    bars = axes[1][1].bar(x, avg_fainted, width, color=c)
    setup(axes[1][1], "Avg Pokemon Fainted per Battle", "Fainted", (0, 6))
    _label_bars(axes[1][1], bars, "{:.1f}")

    axes[1][2].axis("off")

    plt.tight_layout()
    plt.savefig("results.png", dpi=150)
    plt.show()
    print("Plot saved to results.png")