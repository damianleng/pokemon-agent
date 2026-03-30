import asyncio

from poke_env.player import RandomPlayer
from poke_env.player import Player
from poke_env.player import SimpleHeuristicsPlayer
from poke_env.data import GenData

GEN_DATA = GenData.from_gen(9)


class MaxDamagePlayer(Player):
    def choose_move(self, battle):
        if battle.available_moves:
            opponent = battle.opponent_active_pokemon

            def move_score(move):
                if move.base_power == 0:
                    return 0
                effectiveness = move.type.damage_multiplier(
                    opponent.type_1,
                    opponent.type_2,
                    type_chart=GEN_DATA.type_chart,
                )
                return move.base_power * effectiveness

            best_move = max(battle.available_moves, key=move_score)
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)

async def main():
    n = 100

    # Random vs Heuristics
    random_p = RandomPlayer(battle_format="gen9randombattle")
    heuristics_p = SimpleHeuristicsPlayer(battle_format="gen9randombattle")
    await random_p.battle_against(heuristics_p, n_battles=n)
    print(f"Random vs Heuristics:    {random_p.n_won_battles} / {n}")

    # Greedy vs Heuristics
    greedy_p = MaxDamagePlayer(battle_format="gen9randombattle")
    heuristics_p2 = SimpleHeuristicsPlayer(battle_format="gen9randombattle")
    await greedy_p.battle_against(heuristics_p2, n_battles=n)
    print(f"Greedy vs Heuristics:    {greedy_p.n_won_battles} / {n}")

    # Greedy vs Random
    greedy_p2 = MaxDamagePlayer(battle_format="gen9randombattle")
    random_p2 = RandomPlayer(battle_format="gen9randombattle")
    await greedy_p2.battle_against(random_p2, n_battles=n)
    print(f"Greedy vs Random:        {greedy_p2.n_won_battles} / {n}")


if __name__ == "__main__":
    asyncio.run(main())