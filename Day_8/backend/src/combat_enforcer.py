"""
Combat Enforcer - Forces combat to happen automatically

This module ensures that damage is applied even if the AI forgets to call functions.
It monitors player actions and automatically triggers combat.
"""

import random
from game_state import GameState, Universe

class CombatEnforcer:
    """Enforces combat rules and automatically applies damage"""
    
    # Combat keywords that should trigger damage
    COMBAT_KEYWORDS = [
        "fight", "attack", "hit", "strike", "swing", "punch", "kick",
        "defend", "block", "dodge", "run", "escape", "flee",
        "wolf", "monster", "zombie", "ghost", "alien", "orc", "dragon",
        "enemy", "creature", "beast", "raider", "gang"
    ]
    
    # Exploration keywords that should trigger traps/ambushes
    EXPLORATION_KEYWORDS = [
        "explore", "search", "look", "investigate", "enter", "go",
        "walk", "move", "open", "check", "examine"
    ]
    
    @staticmethod
    def should_trigger_combat(player_action: str, game_state: GameState) -> bool:
        """Check if player action should trigger automatic combat"""
        action_lower = player_action.lower()
        
        # Always trigger combat on certain keywords
        for keyword in CombatEnforcer.COMBAT_KEYWORDS:
            if keyword in action_lower:
                return True
        
        # Random chance on exploration (50%)
        for keyword in CombatEnforcer.EXPLORATION_KEYWORDS:
            if keyword in action_lower:
                return random.random() < 0.5
        
        # Random chance every turn (30%)
        return random.random() < 0.3
    
    @staticmethod
    def get_combat_encounter(game_state: GameState) -> tuple[str, int]:
        """
        Get a combat encounter based on universe
        Returns: (enemy_name, damage_amount)
        REDUCED DAMAGE for better game balance
        """
        universe = game_state.universe
        
        if universe == Universe.FANTASY:
            encounters = [
                ("wolf attack", random.randint(10, 18)),
                ("orc ambush", random.randint(15, 22)),
                ("goblin attack", random.randint(8, 15)),
                ("arrow trap", random.randint(10, 15)),
                ("falling rocks", random.randint(8, 12)),
            ]
        elif universe == Universe.HORROR:
            encounters = [
                ("ghost attack", random.randint(12, 20)),
                ("shadow creature", random.randint(15, 22)),
                ("monster claw", random.randint(12, 18)),
                ("trap", random.randint(10, 15)),
                ("possessed object", random.randint(10, 18)),
                ("dark spirit", random.randint(12, 20)),
            ]
        elif universe == Universe.SPACE_OPERA:
            encounters = [
                ("alien attack", random.randint(15, 22)),
                ("laser blast", random.randint(12, 20)),
                ("explosion", random.randint(18, 25)),
                ("radiation", random.randint(10, 18)),
                ("meteor strike", random.randint(12, 20)),
            ]
        elif universe == Universe.CYBERPUNK:
            encounters = [
                ("gang attack", random.randint(12, 20)),
                ("hacker virus", random.randint(10, 18)),
                ("explosion", random.randint(15, 22)),
                ("electric shock", random.randint(10, 15)),
                ("drone attack", random.randint(12, 18)),
            ]
        elif universe == Universe.POST_APOCALYPSE:
            encounters = [
                ("zombie attack", random.randint(15, 22)),
                ("raider ambush", random.randint(12, 20)),
                ("radiation", random.randint(10, 18)),
                ("trap", random.randint(10, 15)),
                ("mutant attack", random.randint(15, 20)),
            ]
        else:
            encounters = [("enemy attack", random.randint(10, 18))]
        
        return random.choice(encounters)
    
    @staticmethod
    def apply_automatic_combat(game_state: GameState, player_action: str) -> tuple[bool, str, int]:
        """
        Apply automatic combat damage if needed
        Returns: (combat_occurred, enemy_name, damage_amount)
        """
        if not CombatEnforcer.should_trigger_combat(player_action, game_state):
            return False, "", 0
        
        enemy_name, damage = CombatEnforcer.get_combat_encounter(game_state)
        
        # Apply damage
        game_state.damage_player(damage)
        game_state.add_event(f"Took {damage} damage from {enemy_name}")
        
        return True, enemy_name, damage
    
    @staticmethod
    def get_combat_message(enemy_name: str, damage: int, current_hp: int, max_hp: int) -> str:
        """Generate a combat message"""
        messages = [
            f"💥 {enemy_name.title()}! You take {damage} damage! HP: {current_hp}/{max_hp}",
            f"⚔️ {enemy_name.title()} hits you for {damage} damage! HP: {current_hp}/{max_hp}",
            f"🩸 {enemy_name.title()}! -{damage} HP! Current HP: {current_hp}/{max_hp}",
        ]
        return random.choice(messages)
    
    @staticmethod
    def should_give_healing_item(game_state: GameState) -> bool:
        """Check if player should receive a healing item"""
        # Give healing item if HP is below 70% and player doesn't have one (more generous)
        if game_state.player.hp < game_state.player.max_hp * 0.7:
            healing_items = ["health potion", "healing herb", "medkit", "bandage", "first aid kit", "stim pack"]
            has_healing = any(item.lower() in [inv_item.lower() for inv_item in game_state.player.inventory] for item in healing_items)
            return not has_healing
        return False
    
    @staticmethod
    def get_healing_item(game_state: GameState) -> str:
        """Get appropriate healing item for universe"""
        universe = game_state.universe
        
        if universe == Universe.FANTASY:
            return "health potion"
        elif universe == Universe.HORROR:
            return "first aid kit"
        elif universe == Universe.SPACE_OPERA:
            return "medical nanobots"
        elif universe == Universe.CYBERPUNK:
            return "stim pack"
        elif universe == Universe.POST_APOCALYPSE:
            return "medkit"
        else:
            return "health potion"
