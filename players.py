from poke_env.player import RandomPlayer, Player, SimpleHeuristicsPlayer
from poke_env.data import GenData

from metrics import MetricsMixin

GEN_DATA = GenData.from_gen(9)


class TrackedRandomPlayer(MetricsMixin, RandomPlayer):
    pass


class TrackedHeuristicsPlayer(MetricsMixin, SimpleHeuristicsPlayer):
    pass


class MaxDamagePlayer(MetricsMixin, Player):
    def choose_move(self, battle):
        if battle.available_moves:
            opponent = battle.opponent_active_pokemon

            def move_score(move):
                if move.base_power == 0:
                    return 0
                return move.base_power * move.type.damage_multiplier(
                    opponent.type_1,
                    opponent.type_2,
                    type_chart=GEN_DATA.type_chart,
                )

            best_move = max(battle.available_moves, key=move_score)
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)