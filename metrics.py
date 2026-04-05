import numpy as np
from scipy import stats
from collections import defaultdict


def analyze_statistical_significance(player1_wins, player2_wins, n_battles):
    """Check if win rate differences are statistically significant"""
    p_value = stats.binomtest(player1_wins, n_battles, 0.5).pvalue
    return p_value < 0.05  # True if significant


def analyze_streaks(battle_results):
    """Analyze winning and losing streaks from battle results"""
    if not battle_results:
        return {
            'longest_win_streak': 0,
            'longest_loss_streak': 0,
            'current_streak': 0,
            'current_streak_type': None,
            'total_streaks': 0,
            'avg_streak_length': 0.0
        }
    
    longest_win = longest_loss = current_streak = 0
    current_type = None
    streaks = []
    
    for won in battle_results:
        if current_type == won:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 1
            current_type = won
        
        if won and current_streak > longest_win:
            longest_win = current_streak
        elif not won and current_streak > longest_loss:
            longest_loss = current_streak
    
    if current_streak > 0:
        streaks.append(current_streak)
    
    return {
        'longest_win_streak': longest_win,
        'longest_loss_streak': longest_loss,
        'current_streak': current_streak,
        'current_streak_type': 'win' if current_type else 'loss' if current_type is not None else None,
        'total_streaks': len(streaks),
        'avg_streak_length': float(np.mean(streaks)) if streaks else 0.0
    }


def analyze_move_preferences(move_data):
    """Analyze move type preferences and effectiveness patterns"""
    if not move_data:
        return {
            'offensive_moves_pct': 0.0,
            'defensive_moves_pct': 0.0,
            'status_moves_pct': 0.0,
            'super_effective_moves_pct': 0.0,
            'not_very_effective_moves_pct': 0.0,
            'normal_effective_moves_pct': 0.0,
            'switch_frequency_pct': 0.0,
            'avg_turn_when_switching': 0.0
        }
    
    total_moves = len(move_data)
    offensive = sum(1 for m in move_data if m.get('category') == 'offensive')
    defensive = sum(1 for m in move_data if m.get('category') == 'defensive')
    status = sum(1 for m in move_data if m.get('category') == 'status')
    switches = sum(1 for m in move_data if m.get('is_switch', False))
    
    effective_counts = defaultdict(int)
    switch_turns = []
    
    for move in move_data:
        if move.get('is_switch', False):
            switch_turns.append(move.get('turn', 0))
        else:
            effectiveness = move.get('effectiveness', 1.0)
            if effectiveness > 1.0:
                effective_counts['super'] += 1
            elif effectiveness < 1.0:
                effective_counts['not_very'] += 1
            else:
                effective_counts['normal'] += 1
    
    total_attacks = total_moves - switches
    
    return {
        'offensive_moves_pct': (offensive / total_attacks * 100) if total_attacks > 0 else 0.0,
        'defensive_moves_pct': (defensive / total_attacks * 100) if total_attacks > 0 else 0.0,
        'status_moves_pct': (status / total_attacks * 100) if total_attacks > 0 else 0.0,
        'super_effective_moves_pct': (effective_counts['super'] / total_attacks * 100) if total_attacks > 0 else 0.0,
        'not_very_effective_moves_pct': (effective_counts['not_very'] / total_attacks * 100) if total_attacks > 0 else 0.0,
        'normal_effective_moves_pct': (effective_counts['normal'] / total_attacks * 100) if total_attacks > 0 else 0.0,
        'switch_frequency_pct': (switches / total_moves * 100) if total_moves > 0 else 0.0,
        'avg_turn_when_switching': float(np.mean(switch_turns)) if switch_turns else 0.0
    }


class MetricsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._turns = []
        self._win_hp = []
        self._fainted_per_battle = []
        
        # Performance consistency tracking
        self._battle_results = []  # Sequence of True/False for wins/losses
        
        # Move selection tracking
        self._move_data = []  # Detailed move information
        self._current_battle_moves = []
        
    def _battle_finished_callback(self, battle):
        self._turns.append(battle.turn)
        fainted = sum(1 for p in battle.team.values() if p.fainted)
        self._fainted_per_battle.append(fainted)
        
        # Track battle result for streak analysis
        self._battle_results.append(battle.won)
        
        # Store move data from current battle
        if self._current_battle_moves:
            self._move_data.extend(self._current_battle_moves)
            self._current_battle_moves = []
        
        if battle.won:
            hp_frac = sum(p.current_hp_fraction for p in battle.team.values()) / len(battle.team)
            self._win_hp.append(hp_frac)

    def _track_move_selection(self, battle, chosen_order):
        """Track details about move selection for analysis"""
        if not hasattr(self, '_move_data'):
            return
            
        move_info = {
            'turn': battle.turn,
            'is_switch': hasattr(chosen_order, 'pokemon') and chosen_order.pokemon is not None,
            'category': 'status',  # Default
            'effectiveness': 1.0   # Default neutral
        }
        
        # If it's a move (not switch)
        if hasattr(chosen_order, 'move') and chosen_order.move is not None:
            move = chosen_order.move
            opponent_pokemon = battle.opponent_active_pokemon
            
            # Categorize move type
            if move.base_power > 0:
                move_info['category'] = 'offensive'
            elif move.heal > 0 or any(boost > 0 for boost in move.boosts.values()) if hasattr(move, 'boosts') and move.boosts else False:
                move_info['category'] = 'defensive'
            else:
                move_info['category'] = 'status'
            
            # Calculate type effectiveness if opponent exists
            if opponent_pokemon and hasattr(move, 'type'):
                try:
                    from poke_env.data import GenData
                    gen_data = GenData.from_gen(9)
                    effectiveness = move.type.damage_multiplier(
                        opponent_pokemon.type_1,
                        opponent_pokemon.type_2,
                        type_chart=gen_data.type_chart,
                    )
                    move_info['effectiveness'] = effectiveness
                except:
                    pass  # Keep default if calculation fails
        
        self._current_battle_moves.append(move_info)

    @property
    def avg_turns(self):
        return float(np.mean(self._turns)) if self._turns else 0.0

    @property
    def avg_win_hp(self):
        return float(np.mean(self._win_hp)) if self._win_hp else 0.0

    @property
    def avg_fainted(self):
        return float(np.mean(self._fainted_per_battle)) if self._fainted_per_battle else 0.0
    
    @property
    def streak_analysis(self):
        """Get performance consistency analysis"""
        return analyze_streaks(self._battle_results)
    
    @property
    def move_analysis(self):
        """Get move selection analysis"""
        return analyze_move_preferences(self._move_data)
    
    def get_performance_summary(self):
        """Get comprehensive performance analysis"""
        streaks = self.streak_analysis
        moves = self.move_analysis
        
        return {
            'basic_stats': {
                'total_battles': len(self._battle_results),
                'wins': sum(self._battle_results),
                'win_rate': sum(self._battle_results) / len(self._battle_results) if self._battle_results else 0,
                'avg_turns': self.avg_turns,
                'avg_win_hp': self.avg_win_hp,
                'avg_fainted': self.avg_fainted
            },
            'consistency': streaks,
            'move_patterns': moves
        }