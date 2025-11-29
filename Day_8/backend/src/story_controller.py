"""
Story Controller - Manages story progression and ending conditions

This module ensures adventures don't go too long and reach natural conclusions.
It tracks turn count and provides hints to guide toward story endings.
"""

def should_end_story(game_state, player_action: str) -> tuple[bool, str]:
    """
    Determine if the story should end based on turn count and player actions.
    
    Returns:
        (should_end: bool, ending_message: str)
    """
    if not game_state:
        return False, ""
    
    # Increment turn count
    game_state.turn_count += 1
    current_turn = game_state.turn_count
    
    # Check for explicit ending requests
    ending_keywords = ["end", "finish", "stop", "quit", "done", "complete", "finish the game", "end game"]
    player_action_lower = player_action.lower()
    if any(keyword in player_action_lower for keyword in ending_keywords):
        return True, "Adventure complete! You've finished your quest. Well done! Start a new game?"
    
    # HARD STOP: Auto-end after 5 turns (never exceed this)
    if current_turn >= 5:
        return True, "Your adventure ends here! You win! Well done! Start a new game?"
    
    # SOFT STOP: Suggest ending after 4 turns
    if current_turn >= 4:
        # Check for natural ending conditions
        if "village" in game_state.current_location.lower() or "home" in player_action_lower:
            return True, "You return home! Your adventure is complete. Start a new game?"
        
        # Check if player has accomplished goals (collected items/completed quests)
        completed_quests = [q for q in game_state.quests if q.completed]
        if completed_quests:
            return True, "Quest complete! You win! Start a new game?"
        
        # Otherwise suggest ending
        return True, "Your adventure is complete! You win! Start a new game?"
    
    return False, ""

def get_story_progress_hint(game_state) -> str:
    """
    Get a hint about story progress to guide toward ending.
    Returns a string that can be appended to GM responses.
    """
    if not game_state:
        return ""
    
    turns = game_state.turn_count
    
    if turns >= 4:
        return " (Story ending now!)"
    elif turns >= 3:
        return " (Almost done!)"
    elif turns >= 2:
        return " (Halfway there)"
    
    return ""

def get_story_stage(game_state) -> str:
    """
    Get the current story stage for the GM to understand pacing.
    
    Returns:
        Story stage: "introduction", "challenge", "resolution"
    """
    if not game_state:
        return "introduction"
    
    turns = game_state.turn_count
    
    if turns <= 1:
        return "introduction"
    elif turns <= 3:
        return "challenge"
    else:
        return "resolution"

def format_turn_counter(game_state) -> str:
    """
    Format a string showing current turn and progress to player.
    
    Returns:
        Formatted string like "Turn 3/7"
    """
    if not game_state:
        return ""
    
    return f"(Turn {game_state.turn_count}/4)"
