from poke_env.player import RandomPlayer, Player, SimpleHeuristicsPlayer
from poke_env.battle.move import MoveCategory
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
    DAMAGE_SCALE = 0.003  # calibrated so a STAB 80bp neutral move on balanced stats ≈ 0.36 HP
    KO_BONUS = 2.0        # weight applied when an active Pokemon is knocked out in the lookahead

    def __init__(self, *args, depth: int = DEFAULT_DEPTH, **kwargs):
        super().__init__(*args, **kwargs)
        self._depth = depth

    def choose_move(self, battle):
        if not battle.available_moves and not battle.available_switches:
            chosen_order = self.choose_random_move(battle)
        else:
            state = self._snapshot(battle)
            best_action = self._best_action(state, battle)
            chosen_order = self.create_order(best_action)

        self._track_move_selection(battle, chosen_order)
        return chosen_order

    def _best_action(self, state, battle):
        best_val = float("-inf")
        best = None
        for move in battle.available_moves:
            next_state = self._apply_move(state, move, is_agent=True)
            val = self._search(next_state, self._depth - 1, is_agent_turn=False)
            if val > best_val:
                best_val = val
                best = move
        for switch in battle.available_switches:
            next_state = self._switch_state(state, switch)
            # After a switch, the opponent gets a free hit on the newly-in Pokemon.
            val = self._search(next_state, self._depth - 1, is_agent_turn=False)
            if val > best_val:
                best_val = val
                best = switch
        return best

    def _search(self, state, depth, is_agent_turn):
        if depth == 0 or state["our_hp"] <= 0 or state["opp_hp"] <= 0:
            return self._evaluate(state)
        if is_agent_turn:
            moves = state["our_moves"]
            if not moves:
                return self._evaluate(state)
            return max(
                self._search(self._apply_move(state, m, is_agent=True), depth - 1, False)
                for m in moves
            )
        else:
            moves = state["opp_moves"]
            if not moves:
                # No revealed opponent moves — simulate a generic STAB threat so the
                # lookahead plans against *something* instead of a ghost opponent.
                child = self._apply_synthetic_threat(state)
                return self._search(child, depth - 1, True)
            # Adversarial opponent: assume they pick the worst move for us.
            return min(
                self._search(self._apply_move(state, m, is_agent=False), depth - 1, True)
                for m in moves
            )

    def _snapshot(self, battle):
        our = battle.active_pokemon
        opp = battle.opponent_active_pokemon
        our_s = our.base_stats
        opp_s = opp.base_stats

        our_bench_hp = sum(
            p.current_hp_fraction for p in battle.team.values() if p is not our
        )
        opp_revealed_bench_hp = sum(
            p.current_hp_fraction for p in battle.opponent_team.values() if p is not opp
        )
        # Unrevealed opponents are assumed full-HP so eval isn't biased by info asymmetry.
        opp_unrevealed = max(0, 6 - len(battle.opponent_team))
        opp_bench_hp = opp_revealed_bench_hp + opp_unrevealed

        return {
            "our_hp":       our.current_hp_fraction,
            "opp_hp":       opp.current_hp_fraction,
            "our_types":    (our.type_1, our.type_2),
            "opp_types":    (opp.type_1, opp.type_2),
            "our_atk":      our_s["atk"],
            "our_spa":      our_s["spa"],
            "our_def":      our_s["def"],
            "our_spd":      our_s["spd"],
            "opp_atk":      opp_s["atk"],
            "opp_spa":      opp_s["spa"],
            "opp_def":      opp_s["def"],
            "opp_spd":      opp_s["spd"],
            "our_moves":    list(battle.available_moves),
            "opp_moves":    list(opp.moves.values()),
            "our_bench_hp": our_bench_hp,
            "opp_bench_hp": opp_bench_hp,
        }

    def _switch_state(self, state, switch):
        # Active↔bench swap: preserve total team HP so switching isn't a free HP gain in eval.
        s = switch.base_stats
        new = state.copy()
        new["our_bench_hp"] = state["our_bench_hp"] + state["our_hp"] - switch.current_hp_fraction
        new["our_hp"] = switch.current_hp_fraction
        new["our_types"] = (switch.type_1, switch.type_2)
        new["our_atk"] = s["atk"]
        new["our_spa"] = s["spa"]
        new["our_def"] = s["def"]
        new["our_spd"] = s["spd"]
        new["our_moves"] = list(switch.moves.values())
        return new

    def _apply_move(self, state, move, *, is_agent):
        if move.base_power == 0:
            return state.copy()

        damage = self._damage(state, move, is_agent=is_agent)
        new = state.copy()
        if is_agent:
            new["opp_hp"] = max(0.0, state["opp_hp"] - damage)
        else:
            new["our_hp"] = max(0.0, state["our_hp"] - damage)
        return new

    def _damage(self, state, move, *, is_agent):
        atk_prefix, def_prefix = ("our", "opp") if is_agent else ("opp", "our")
        attacker_types = state[f"{atk_prefix}_types"]
        defender_types = state[f"{def_prefix}_types"]

        if move.category == MoveCategory.PHYSICAL:
            atk = state[f"{atk_prefix}_atk"]
            defn = state[f"{def_prefix}_def"]
        else:
            atk = state[f"{atk_prefix}_spa"]
            defn = state[f"{def_prefix}_spd"]

        type_mult = move.type.damage_multiplier(
            defender_types[0], defender_types[1], type_chart=GEN_DATA.type_chart,
        )
        stab = 1.5 if move.type in attacker_types else 1.0
        accuracy = self._accuracy(move)

        return (
            move.base_power
            * (atk / defn)
            * type_mult
            * stab
            * accuracy
            * self.DAMAGE_SCALE
        )

    @staticmethod
    def _accuracy(move):
        acc = move.accuracy
        if acc is True or acc is None:
            return 1.0
        return acc / 100.0 if acc > 1 else float(acc)

    def _apply_synthetic_threat(self, state):
        # Stand-in for "opponent picks a solid STAB attack" when no moves are revealed yet.
        SYNTHETIC_BP = 80
        opp_types = state["opp_types"]
        our_types = state["our_types"]

        if state["opp_atk"] >= state["opp_spa"]:
            atk, defn = state["opp_atk"], state["our_def"]
        else:
            atk, defn = state["opp_spa"], state["our_spd"]

        type_mults = [
            t.damage_multiplier(our_types[0], our_types[1], type_chart=GEN_DATA.type_chart)
            for t in opp_types if t is not None
        ]
        type_mult = max(type_mults) if type_mults else 1.0

        damage = (
            SYNTHETIC_BP
            * (atk / defn)
            * type_mult
            * 1.5  # STAB (threat uses attacker's own type)
            * self.DAMAGE_SCALE
        )
        new = state.copy()
        new["our_hp"] = max(0.0, state["our_hp"] - damage)
        return new

    def _evaluate(self, state):
        our_team = state["our_hp"] + state["our_bench_hp"]
        opp_team = state["opp_hp"] + state["opp_bench_hp"]
        team_diff = our_team - opp_team
        ko = 0.0
        if state["opp_hp"] <= 0:
            ko += self.KO_BONUS
        if state["our_hp"] <= 0:
            ko -= self.KO_BONUS
        return team_diff + ko
