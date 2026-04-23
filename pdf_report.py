"""Render the battle analysis to a PDF report (uses matplotlib's PdfPages)."""
import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from analysis_display import get_strategy_insights
from metrics import analyze_statistical_significance


def _text_page(pdf, lines, title=None):
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    y = 0.96
    if title:
        ax.text(0.5, y, title, ha="center", va="top",
                fontsize=16, fontweight="bold")
        y -= 0.05

    ax.text(0.06, y, "\n".join(lines), ha="left", va="top",
            fontsize=10, family="monospace")
    pdf.savefig(fig)
    plt.close(fig)


def _image_page(pdf, image_path, title):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor("white")
    fig.suptitle(title, fontsize=15, fontweight="bold")
    ax = fig.add_subplot(111)
    ax.imshow(mpimg.imread(image_path))
    ax.axis("off")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _significance_lines(battle_results, n):
    lines = [
        "*** = Statistically significant difference from random chance (p < 0.05)",
        "",
    ]
    significant = []
    for matchup, wins in battle_results:
        if analyze_statistical_significance(wins, n - wins, n):
            significant.append((matchup, wins / n * 100, wins))

    if significant:
        lines.append("Statistically significant performance differences detected:")
        for matchup, win_rate, w in significant:
            if win_rate >= 50:
                edge = "Strong" if win_rate > 70 else "Moderate" if win_rate > 60 else "Slight"
                label = f"{edge} advantage"
            else:
                edge = "Strong" if win_rate < 30 else "Moderate" if win_rate < 40 else "Slight"
                label = f"{edge} disadvantage"
            lines.append(f"  - {matchup}: {label} ({w}/{n} = {win_rate:.1f}%)")
    else:
        lines.append("No statistically significant differences detected.")
        lines.append("Consider increasing sample size (n) for more reliable results.")

    lines += [
        "",
        f"Sample size: {n} battles per matchup",
        "Confidence level: 95% (alpha = 0.05)",
    ]
    return lines


def _player_lines(summary):
    basic = summary["basic_stats"]
    streaks = summary["consistency"]
    moves = summary["move_patterns"]

    lines = [
        "Basic Stats",
        "-" * 60,
        f"Total battles: {basic['total_battles']}",
        f"Win rate:      {basic['win_rate']*100:.1f}% ({basic['wins']}/{basic['total_battles']})",
        f"Avg turns:     {basic['avg_turns']:.1f}",
        f"Avg win HP:    {basic['avg_win_hp']*100:.1f}%",
        f"Avg fainted:   {basic['avg_fainted']:.1f}",
        "",
        "Performance Consistency",
        "-" * 60,
        f"Longest win streak:  {streaks['longest_win_streak']:2d} battles",
        f"Longest loss streak: {streaks['longest_loss_streak']:2d} battles",
    ]
    if streaks["current_streak_type"]:
        label = "wins" if streaks["current_streak_type"] == "win" else "losses"
        lines.append(f"Current streak:      {streaks['current_streak']:2d} {label}")
    lines += [
        f"Average streak:      {streaks['avg_streak_length']:4.1f} battles",
        "",
        "Move Selection Patterns",
        "-" * 60,
        "Move categories:",
        f"  Offensive:          {moves['offensive_moves_pct']:5.1f}%",
        f"  Defensive:          {moves['defensive_moves_pct']:5.1f}%",
        f"  Status:             {moves['status_moves_pct']:5.1f}%",
        "Type effectiveness:",
        f"  Super effective:    {moves['super_effective_moves_pct']:5.1f}%",
        f"  Normal damage:      {moves['normal_effective_moves_pct']:5.1f}%",
        f"  Not very effective: {moves['not_very_effective_moves_pct']:5.1f}%",
        "Switching behavior:",
        f"  Switch frequency:   {moves['switch_frequency_pct']:5.1f}%",
    ]
    if moves["avg_turn_when_switching"] > 0:
        lines.append(f"  Avg switch timing:  Turn {moves['avg_turn_when_switching']:4.1f}")
    return lines


def _insights_lines(players_data):
    insights = get_strategy_insights(players_data)
    lines = []
    if insights:
        for ins in insights:
            lines.append(f"  - {ins}")
    else:
        lines.append("No notable patterns detected.")
    lines += [
        "",
        "Recommendations",
        "-" * 60,
        "- Focus on type effectiveness - high super-effective move %",
        "  correlates with better win rates.",
        "- Consistent players (lower streak variance) tend to perform",
        "  better over long sessions.",
        "- Strategic switching (5-15%) often indicates more sophisticated play.",
    ]
    return lines


def generate_pdf_report(
    players_data,
    battle_results,
    n,
    output_path="analysis_report.pdf",
    image_path="results.png",
):
    with PdfPages(output_path) as pdf:
        if os.path.exists(image_path):
            _image_page(pdf, image_path,
                        title="Pokemon AI Strategy Battle Analysis")

        _text_page(pdf, _significance_lines(battle_results, n),
                   title="Statistical Significance Analysis")

        for player_name, data in players_data.items():
            _text_page(pdf, _player_lines(data.get_performance_summary()),
                       title=f"{player_name} Detailed Analysis")

        _text_page(pdf, _insights_lines(players_data),
                   title="Strategic Insights & Recommendations")

    print(f"Analysis report saved to {output_path}")