import asyncio
 
from players import TrackedRandomPlayer, TrackedHeuristicsPlayer, MaxDamagePlayer, LookaheadPlayer
from visualize import plot_results
 
 
def _fmt(label, player, n):
    print(f"{label:<30} {player.n_won_battles}/{n} wins | "
          f"avg turns: {player.avg_turns:.1f} | "
          f"avg win HP: {player.avg_win_hp*100:.1f}% | "
          f"avg fainted: {player.avg_fainted:.1f}")
 
 
async def main():
    n = 100
 
    # Random vs Heuristics
    random_p = TrackedRandomPlayer(battle_format="gen9randombattle")
    heuristics_p = TrackedHeuristicsPlayer(battle_format="gen9randombattle")
    await random_p.battle_against(heuristics_p, n_battles=n)
    _fmt("Random vs Heuristics:", random_p, n)
 
    # Greedy vs Heuristics
    greedy_p = MaxDamagePlayer(battle_format="gen9randombattle")
    heuristics_p2 = TrackedHeuristicsPlayer(battle_format="gen9randombattle")
    await greedy_p.battle_against(heuristics_p2, n_battles=n)
    _fmt("Greedy vs Heuristics:", greedy_p, n)
 
    # Greedy vs Random
    greedy_p2 = MaxDamagePlayer(battle_format="gen9randombattle")
    random_p2 = TrackedRandomPlayer(battle_format="gen9randombattle")
    await greedy_p2.battle_against(random_p2, n_battles=n)
    _fmt("Greedy vs Random:", greedy_p2, n)
 
    # Lookahead vs Random
    lookahead_p = LookaheadPlayer(battle_format="gen9randombattle", depth=2)
    random_p3 = TrackedRandomPlayer(battle_format="gen9randombattle")
    await lookahead_p.battle_against(random_p3, n_battles=n)
    _fmt("Lookahead vs Random:", lookahead_p, n)
 
    # Lookahead vs Greedy
    lookahead_p2 = LookaheadPlayer(battle_format="gen9randombattle", depth=2)
    greedy_p3 = MaxDamagePlayer(battle_format="gen9randombattle")
    await lookahead_p2.battle_against(greedy_p3, n_battles=n)
    _fmt("Lookahead vs Greedy:", lookahead_p2, n)
 
    # Lookahead vs Heuristics
    lookahead_p3 = LookaheadPlayer(battle_format="gen9randombattle", depth=2)
    heuristics_p3 = TrackedHeuristicsPlayer(battle_format="gen9randombattle")
    await lookahead_p3.battle_against(heuristics_p3, n_battles=n)
    _fmt("Lookahead vs Heuristics:", lookahead_p3, n)
 
    matchups = [
        "Random\nvs Heuristics",
        "Greedy\nvs Heuristics",
        "Greedy\nvs Random",
        "Lookahead\nvs Random",
        "Lookahead\nvs Greedy",
        "Lookahead\nvs Heuristics",
    ]
    players = [random_p, greedy_p, greedy_p2, lookahead_p, lookahead_p2, lookahead_p3]
 
    wins        = [p.n_won_battles for p in players]
    win_rates   = [p.n_won_battles / n for p in players]
    avg_turns   = [p.avg_turns for p in players]
    avg_win_hp  = [p.avg_win_hp for p in players]
    avg_fainted = [p.avg_fainted for p in players]
 
    plot_results(matchups, wins, win_rates, avg_turns, avg_win_hp, avg_fainted, n)
 
 
if __name__ == "__main__":
    asyncio.run(main())
