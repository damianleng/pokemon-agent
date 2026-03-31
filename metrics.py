import numpy as np


class MetricsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._turns = []
        self._win_hp = []
        self._fainted_per_battle = []

    def _battle_finished_callback(self, battle):
        self._turns.append(battle.turn)
        fainted = sum(1 for p in battle.team.values() if p.fainted)
        self._fainted_per_battle.append(fainted)
        if battle.won:
            hp_frac = sum(p.current_hp_fraction for p in battle.team.values()) / len(battle.team)
            self._win_hp.append(hp_frac)

    @property
    def avg_turns(self):
        return float(np.mean(self._turns)) if self._turns else 0.0

    @property
    def avg_win_hp(self):
        return float(np.mean(self._win_hp)) if self._win_hp else 0.0

    @property
    def avg_fainted(self):
        return float(np.mean(self._fainted_per_battle)) if self._fainted_per_battle else 0.0