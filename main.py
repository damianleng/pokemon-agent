import asyncio

from players import TrackedRandomPlayer, TrackedHeuristicsPlayer, MaxDamagePlayer
from visualize import plot_results


async def main():
    n = 100

    # Random vs Heuristics
    random_p = TrackedRandomPlayer(battle_format="gen9randombattle")
    heuristics_p = TrackedHeuristicsPlayer(battle_format="gen9randombattle")
    await random_p.battle_against(heuristics_p, n_battles=n)
    print(f"Random vs Heuristics:  {random_p.n_won_battles}/{n} wins | "
          f"avg turns: {random_p.avg_turns:.1f} | "
          f"avg win HP: {random_p.avg_win_hp*100:.1f}% | "
          f"avg fainted: {random_p.avg_fainted:.1f}")

    # Greedy vs Heuristics
    greedy_p = MaxDamagePlayer(battle_format="gen9randombattle")
    heuristics_p2 = TrackedHeuristicsPlayer(battle_format="gen9randombattle")
    await greedy_p.battle_against(heuristics_p2, n_battles=n)
    print(f"Greedy vs Heuristics:  {greedy_p.n_won_battles}/{n} wins | "
          f"avg turns: {greedy_p.avg_turns:.1f} | "
          f"avg win HP: {greedy_p.avg_win_hp*100:.1f}% | "
          f"avg fainted: {greedy_p.avg_fainted:.1f}")

    # Greedy vs Random
    greedy_p2 = MaxDamagePlayer(battle_format="gen9randombattle")
    random_p2 = TrackedRandomPlayer(battle_format="gen9randombattle")
    await greedy_p2.battle_against(random_p2, n_battles=n)
    print(f"Greedy vs Random:      {greedy_p2.n_won_battles}/{n} wins | "
          f"avg turns: {greedy_p2.avg_turns:.1f} | "
          f"avg win HP: {greedy_p2.avg_win_hp*100:.1f}% | "
          f"avg fainted: {greedy_p2.avg_fainted:.1f}")

    matchups    = ["Random\nvs Heuristics", "Greedy\nvs Heuristics", "Greedy\nvs Random"]
    wins        = [random_p.n_won_battles, greedy_p.n_won_battles, greedy_p2.n_won_battles]
    win_rates   = [random_p.n_won_battles / n, greedy_p.n_won_battles / n, greedy_p2.n_won_battles / n]
    avg_turns   = [random_p.avg_turns, greedy_p.avg_turns, greedy_p2.avg_turns]
    avg_win_hp  = [random_p.avg_win_hp, greedy_p.avg_win_hp, greedy_p2.avg_win_hp]
    avg_fainted = [random_p.avg_fainted, greedy_p.avg_fainted, greedy_p2.avg_fainted]

    plot_results(matchups, wins, win_rates, avg_turns, avg_win_hp, avg_fainted, n)


if __name__ == "__main__":
    asyncio.run(main())