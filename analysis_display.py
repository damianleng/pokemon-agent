"""Advanced analysis display functions for Pokemon AI strategies"""

def print_consistency_analysis(player_name, streaks):
    """Print performance consistency analysis"""
    print(f"\n🎯 {player_name} - Performance Consistency:")
    print(f"   Longest win streak:  {streaks['longest_win_streak']:2d} battles")
    print(f"   Longest loss streak: {streaks['longest_loss_streak']:2d} battles")
    
    if streaks['current_streak_type']:
        streak_type = streaks['current_streak_type'] 
        streak_label = "wins" if streak_type == "win" else "losses"
        print(f"   Current streak:      {streaks['current_streak']:2d} {streak_label}")
    
    print(f"   Average streak:      {streaks['avg_streak_length']:4.1f} battles")

def print_move_analysis(player_name, moves):
    """Print move selection analysis"""
    print(f"\n🎲 {player_name} - Move Selection Patterns:")
    print(f"   Move Categories:")
    print(f"     Offensive moves:   {moves['offensive_moves_pct']:5.1f}%")
    print(f"     Defensive moves:   {moves['defensive_moves_pct']:5.1f}%")
    print(f"     Status moves:      {moves['status_moves_pct']:5.1f}%")
    
    print(f"   Type Effectiveness:")
    print(f"     Super effective:   {moves['super_effective_moves_pct']:5.1f}%")
    print(f"     Normal damage:     {moves['normal_effective_moves_pct']:5.1f}%")
    print(f"     Not very effective:{moves['not_very_effective_moves_pct']:5.1f}%")
    
    print(f"   Switching Behavior:")
    print(f"     Switch frequency:  {moves['switch_frequency_pct']:5.1f}%")
    if moves['avg_turn_when_switching'] > 0:
        print(f"     Avg switch timing: Turn {moves['avg_turn_when_switching']:4.1f}")

def print_comprehensive_analysis(players_data):
    """Print comprehensive analysis for all players"""
    print("\n" + "="*80)
    print("COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("="*80)
    
    for player_name, data in players_data.items():
        summary = data.get_performance_summary()
        basic = summary['basic_stats']
        
        print(f"\n📊 {player_name.upper()} ANALYSIS")
        print("-" * 50)
        print(f"Total battles: {basic['total_battles']}")
        print(f"Win rate: {basic['win_rate']*100:.1f}% ({basic['wins']}/{basic['total_battles']})")
        
        # Performance consistency
        print_consistency_analysis(player_name, summary['consistency'])
        
        # Move selection patterns  
        print_move_analysis(player_name, summary['move_patterns'])

def get_strategy_insights(players_data):
    """Extract and return strategic insights from the analysis"""
    insights = []
    
    for player_name, data in players_data.items():
        summary = data.get_performance_summary()
        moves = summary['move_patterns']
        streaks = summary['consistency']
        
        # Analyze move preferences
        if moves['offensive_moves_pct'] > 70:
            insights.append(f"{player_name}: Highly aggressive strategy (>{moves['offensive_moves_pct']:.0f}% offensive moves)")
        elif moves['defensive_moves_pct'] > 30:
            insights.append(f"{player_name}: Defensive-minded approach ({moves['defensive_moves_pct']:.1f}% defensive moves)")
        
        # Analyze type effectiveness usage
        if moves['super_effective_moves_pct'] > 40:
            insights.append(f"{player_name}: Excellent type matchup utilization ({moves['super_effective_moves_pct']:.0f}% super effective)")
        elif moves['not_very_effective_moves_pct'] > 25:
            insights.append(f"{player_name}: Poor type matchup decisions ({moves['not_very_effective_moves_pct']:.0f}% not very effective)")
        
        # Analyze consistency
        if streaks['longest_win_streak'] >= 10:
            insights.append(f"{player_name}: Shows strong momentum capability (max {streaks['longest_win_streak']} win streak)")
        if streaks['longest_loss_streak'] >= 8:
            insights.append(f"{player_name}: Concerning loss streaks (max {streaks['longest_loss_streak']} losses)")
        
        # Switching behavior
        if moves['switch_frequency_pct'] > 15:
            insights.append(f"{player_name}: Active switching strategy ({moves['switch_frequency_pct']:.1f}% switches)")
        elif moves['switch_frequency_pct'] < 5:
            insights.append(f"{player_name}: Rarely switches Pokemon ({moves['switch_frequency_pct']:.1f}%)")
    
    return insights

def print_strategic_insights(players_data):
    """Print strategic insights and recommendations"""
    insights = get_strategy_insights(players_data)
    
    if insights:
        print(f"\n💡 STRATEGIC INSIGHTS & PATTERNS")
        print("="*50)
        for insight in insights:
            print(f"• {insight}")
    
    print("\n📈 RECOMMENDATIONS:")
    print("• Focus on type effectiveness - high super-effective move % correlates with better win rates")
    print("• Consistent players (lower streak variance) tend to perform better over long sessions")
    print("• Strategic switching (5-15%) often indicates more sophisticated play")