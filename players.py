from poke_env.player import RandomPlayer, Player, SimpleHeuristicsPlayer
from poke_env.data import GenData
 
from metrics import MetricsMixin
 
GEN_DATA = GenData.from_gen(9)
 
 
class TrackedRandomPlayer(MetricsMixin, RandomPlayer):
    def choose_move(self, battle):
        chosen_order = super().choose_move(battle)
        self._track_move_selection(battle, chosen_order)
        return chosen_order
 
 
class TrackedHeuristicsPlayer(MetricsMixin, SimpleHeuristicsPlayer):
    def choose_move(self, battle):
        chosen_order = super().choose_move(battle)
        self._track_move_selection(battle, chosen_order)
        return chosen_order
 
 
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
            chosen_order = self.create_order(best_move)
        else:
            chosen_order = self.choose_random_move(battle)
        
        self._track_move_selection(battle, chosen_order)
        return chosen_order
 
 
class LookaheadPlayer(MetricsMixin, Player):
    DEFAULT_DEPTH = 2
 
    def __init__(self, *args, depth: int = DEFAULT_DEPTH, **kwargs):
        super().__init__(*args, **kwargs)
        self._depth = depth
 
    def choose_move(self, battle):
        if not battle.available_moves:
            chosen_order = self.choose_random_move(battle)
        else:
            state = self._snapshot(battle)
            best_move = self._best_move(state, battle)
            chosen_order = self.create_order(best_move)
        
        self._track_move_selection(battle, chosen_order)
        return chosen_order
 
    def _best_move(self, state, battle):
        best_val = float("-inf")
        best = None
        for move in battle.available_moves:
            next_state = self._apply_move(state, move, is_agent=True)
            val = self._expectimax(next_state, self._depth - 1, is_agent_turn=False)
            if val > best_val:
                best_val = val
                best = move
        return best
 
    def _expectimax(self, state, depth, is_agent_turn):
        if depth == 0 or state["our_hp"] <= 0 or state["opp_hp"] <= 0:
            return self._evaluate(state)
        if is_agent_turn:
            best = float("-inf")
            for move in state["our_moves"]:
                child = self._apply_move(state, move, is_agent=True)
                best = max(best, self._expectimax(child, depth - 1, False))
            return best if state["our_moves"] else self._evaluate(state)
        else:
            opp_moves = state["opp_moves"]
            if not opp_moves:
                return self._expectimax(state, depth - 1, True)
            total = sum(
                self._expectimax(self._apply_move(state, m, is_agent=False), depth - 1, True)
                for m in opp_moves
            )
            return total / len(opp_moves)
 
    def _snapshot(self, battle):
        our = battle.active_pokemon
        opp = battle.opponent_active_pokemon
        return {
            "our_hp":    our.current_hp_fraction,
            "opp_hp":    opp.current_hp_fraction,
            "our_type1": our.type_1,
            "our_type2": our.type_2,
            "opp_type1": opp.type_1,
            "opp_type2": opp.type_2,
            "our_moves": list(battle.available_moves),
            "opp_moves": list(battle.opponent_active_pokemon.moves.values())
                         or list(battle.available_moves),
        }
 
    def _apply_move(self, state, move, *, is_agent):
        DAMAGE_FACTOR = 0.25
        new = state.copy()
        if move.base_power == 0:
            return new
        if is_agent:
            multiplier = move.type.damage_multiplier(
                state["opp_type1"], state["opp_type2"], type_chart=GEN_DATA.type_chart
            )
            new["opp_hp"] = max(0.0, state["opp_hp"] - move.base_power * multiplier * DAMAGE_FACTOR / 100)
        else:
            multiplier = move.type.damage_multiplier(
                state["our_type1"], state["our_type2"], type_chart=GEN_DATA.type_chart
            )
            new["our_hp"] = max(0.0, state["our_hp"] - move.base_power * multiplier * DAMAGE_FACTOR / 100)
        return new
 
    def _evaluate(self, state):
        return state["our_hp"] - state["opp_hp"]
