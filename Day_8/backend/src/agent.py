import logging
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, openai, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from game_state import GameState, Universe
from story_controller import should_end_story, get_story_progress_hint
from combat_enforcer import CombatEnforcer
from story_logger import create_story_logger, StoryLogger

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Game storage directory
GAME_SAVES_DIR = Path("game_saves")
GAME_SAVES_DIR.mkdir(exist_ok=True)

# Global game state storage (room_id -> GameState)
game_sessions = {}

# Global story logger storage (room_id -> StoryLogger)
story_loggers = {}

def save_game_state(room_id: str, game_state: GameState):
    """Save game state to file"""
    try:
        save_file = GAME_SAVES_DIR / f"{room_id}.json"
        game_state.save_to_file(str(save_file))
        logger.info(f"Game saved: {save_file}")
    except Exception as e:
        logger.error(f"Failed to save game: {e}")

def load_game_state(room_id: str) -> GameState | None:
    """Load game state from file if it exists"""
    try:
        save_file = GAME_SAVES_DIR / f"{room_id}.json"
        if save_file.exists():
            game_state = GameState.load_from_file(str(save_file))
            logger.info(f"Game loaded: {save_file}")
            return game_state
    except Exception as e:
        logger.error(f"Failed to load game: {e}")
    return None

# Track session context for tools
_session_context = {}

class GameMaster(Agent):
    def __init__(self, room_id: str = "default", universe_preference: str = None, player_name: str = None, player_gender: str = None) -> None:
        self.room_id = room_id
        self.player_name = player_name
        self.player_gender = player_gender
        self.first_message = True  # Track if this is the first interaction
        self.combat_enforcer = CombatEnforcer()  # Add combat enforcer
        self.last_player_action = ""  # Track last action for combat
        
        # Try to load existing game for this room
        loaded_game = load_game_state(room_id)
        if loaded_game:
            game_sessions[room_id] = loaded_game
            self.universe_preference = loaded_game.universe.value
            self.first_message = False  # Not first if loading existing game
        else:
            # Don't set universe_preference here - let user choose first
            self.universe_preference = None
        super().__init__(
            instructions=self._get_gm_instructions(),
        )
        
    def _get_gm_instructions(self) -> str:
        # If no universe preference set yet, this is the first interaction
        if not self.universe_preference:
            return """You are a Game Master for an interactive RPG adventure game.

FIRST MESSAGE: Give a brief, exciting intro (1 sentence) and ask them to confirm their name and universe.

Example: "Welcome, brave adventurer! I am your Game Master, ready to guide you through epic tales. Please tell me your name and which world you've chosen!"

When the player responds with their name and universe choice:
1. Confirm their choice with enthusiasm (1 sentence)
2. Call auto_start_game(player_name, player_gender, universe)
3. If they don't mention gender, assume "neutral"
4. Start the adventure immediately

Examples:
Player: "I'm Pavan, I chose horror"
You: "Excellent choice, Pavan! The horror realm awaits..." [Call auto_start_game("Pavan", "male", "horror")]

Player: "Sarah, fantasy world"
You: "Perfect, Sarah! Your fantasy adventure begins now..." [Call auto_start_game("Sarah", "female", "fantasy")]

Keep it brief and exciting - don't ask too many questions, just confirm and start!"""
        
        # If universe preference is set, proceed with game
        # Get player info from game state if available
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        player_gender = getattr(self, 'player_gender', 'neutral') if hasattr(self, 'player_gender') else 'neutral'
        
        # Determine pronouns
        if player_gender == 'male':
            pronouns = "he/him/his"
        elif player_gender == 'female':
            pronouns = "she/her/hers"
        else:
            pronouns = "they/them/their"
        
        base_instructions = """You are a Game Master running fun voice RPG adventures.
        
UNIVERSE: {universe_hint}

PLAYER GENDER: {gender}
PRONOUNS TO USE: {pronouns}

IMPORTANT: Always use the correct pronouns when referring to the player!
- Male player: "he goes", "his sword", "him"
- Female player: "she goes", "her sword", "her"

🚨🚨🚨 CRITICAL FUNCTION CALL RULES - MUST FOLLOW EXACTLY:

RULE 1: WHEN PLAYER FINDS ANY ITEM → ALWAYS CALL add_inventory_item("item_name") FIRST
Examples:
- "You find a silver locket" → CALL add_inventory_item("silver locket") → Returns "📦 You acquired: silver locket"
- "You spot a medkit" → CALL add_inventory_item("medkit") → Returns "📦 You acquired: medkit"
- "A key appears" → CALL add_inventory_item("key") → Returns "📦 You acquired: key"

RULE 2: WHEN PLAYER USES ANY ITEM → ALWAYS CALL use_inventory_item("item_name") FIRST
Examples:
- Player says "use medkit" → CALL use_inventory_item("medkit") → Returns "✅ You used: medkit. You heal! Health: 60/100"
- Player says "drink potion" → CALL use_inventory_item("health potion") → Returns "✅ You used: health potion. You heal! Health: 80/100"
- Player says "use key" → CALL use_inventory_item("key") → Returns "✅ You used: key"

RULE 3: WHEN PLAYER TAKES DAMAGE → ALWAYS CALL damage_player(amount, "source")
Example: "Trap hits you" → CALL damage_player(20, "trap") → Returns "The trap hits you! Health: 40/100"

RULE 4: ALWAYS INCLUDE "Health: X/Y" in your response after damage or healing!

🚨 THE FUNCTIONS MUST BE CALLED BEFORE YOU DESCRIBE WHAT HAPPENS!
The function returns the message you should include in your response.

REAL EXAMPLES FROM GAME:

Scenario: Player searches and finds medkit
❌ WRONG: "You find a medkit! This could save your life!"
✅ CORRECT: [Call add_inventory_item("medkit")] "You find a medkit! 📦 You acquired: medkit. Health: 30/100"

Scenario: Player uses medkit
❌ WRONG: "You use the medkit and feel better! (Health: 60/100)"
✅ CORRECT: [Call use_inventory_item("medkit")] "You use the medkit! Health: 60/100"

Scenario: Player gets hit by trap
❌ WRONG: "A trap snaps shut! You're badly injured (Health: 14/100)"
✅ CORRECT: [Call damage_player(25, "trap")] "A trap snaps shut! Health: 14/100"

🚨 THE UI ONLY UPDATES WHEN YOU CALL THESE FUNCTIONS!
If you don't call the function, the inventory/HP won't change!

🎮 MANDATORY COMBAT SYSTEM - NO BORING EXPLORATION:
EVERY RESPONSE MUST HAVE DANGER AND DAMAGE!

STRICT RULES:
1. NEVER let player explore safely - always add danger
2. ALWAYS call damage_player() when describing any threat
3. Damage range: 15-30 HP per attack
4. Give healing items after 2-3 attacks: add_inventory_item("health potion")
5. If HP < 30, say "You're badly hurt!"
6. If HP = 0, end game: "You fall unconscious. Game over!"

HORROR UNIVERSE COMBAT (MUST USE):
- Ghosts attack: damage_player(20, "ghost attack")
- Shadow creatures: damage_player(25, "shadow creature")
- Dark spirits: damage_player(20, "dark spirit")
- Possessed objects: damage_player(15, "possessed object")
- Monster claws: damage_player(20, "monster claw")
- Traps spring: damage_player(15, "trap")
- Falls: damage_player(15, "fall damage")

NOTE: Horror universe has GHOSTS, SPIRITS, SHADOWS - NOT zombies!
Zombies are in POST-APOCALYPSE universe only!

FANTASY UNIVERSE COMBAT:
- Wolf attacks: damage_player(20, "wolf bite")
- Orc hits: damage_player(25, "orc club")
- Dragon fire: damage_player(30, "dragon fire")
- Arrow trap: damage_player(15, "arrow trap")

SPACE UNIVERSE COMBAT:
- Alien attack: damage_player(25, "alien claw")
- Laser shot: damage_player(20, "laser blast")
- Explosion: damage_player(30, "explosion")
- Radiation: damage_player(15, "radiation")

CYBERPUNK UNIVERSE COMBAT:
- Gang attack: damage_player(20, "gang member")
- Hacker virus: damage_player(15, "virus")
- Explosion: damage_player(25, "explosion")
- Fall: damage_player(15, "fall")

POST-APOCALYPSE COMBAT:
- Zombie attack: damage_player(25, "zombie")
- Raider shot: damage_player(20, "raider gun")
- Radiation: damage_player(15, "radiation")
- Trap: damage_player(15, "trap")
        """.format(
            universe_hint=self._get_universe_hint(),
            gender=player_gender,
            pronouns=pronouns
        )
        return base_instructions + """
        
IMPORTANT RULES:
        
CRITICAL STORY LENGTH RULES:
- Keep adventures VERY SHORT: 3-4 player actions maximum
- Use SIMPLE ENGLISH words that are easy to understand
- Keep responses VERY SHORT (1-2 sentences only)
- ALWAYS end with "What do you do?"
- Use common words, avoid difficult vocabulary
- After 2-3 player actions, START WRAPPING UP THE STORY
- At turn 4+, FORCE the story to conclude: "You win! The adventure is complete!"
- LIMIT conversation history to last 8 messages to avoid token overflow
- ALWAYS call save_story_transcript() when story finishes

ACTION-PACKED STORYTELLING (VERY SHORT):
- Turn 1: Quick intro + combat (damage 15-20)
- Turn 2: Challenge + give healing item (damage 15-20)
- Turn 3: Final battle (damage 15-20)
- Turn 4: VICTORY! Call save_story_transcript() and finish!

KEEP IT VERY SHORT:
- Maximum 3-4 turns total
- Don't drag out the story
- Get to the point quickly
- Finish with victory or defeat by turn 3-4
- ALWAYS call save_story_transcript() at the end

MANUAL END:
- If player says "end", "finish", "stop" → End immediately
- Call save_story_transcript()
- Say: "Your adventure ends! Story saved. Well done!"

🚨 CRITICAL LOCATION RULES (MUST FOLLOW):
When player moves or changes location, you MUST use this EXACT format:
"You enter the [Location Name]"

CORRECT EXAMPLES:
✅ "You enter the Dark Forest. What do you do?"
✅ "You enter the Village Square. What do you do?"
✅ "You enter the Old Mansion. What do you do?"

WRONG EXAMPLES (DON'T USE):
❌ "You go to the forest"
❌ "You arrive at the village"
❌ "You walk into the mansion"

WHY: The UI parses "You enter the" to update the location display!

STORY PROGRESSION (STRICT):
- Turn 1: Introduction + first challenge (damage 15-20)
- Turn 2: Combat + give healing item (damage 15-20)
- Turn 3: Final battle (damage 15-20)
- Turn 4: VICTORY! Call save_story_transcript() and finish!
- Turn 5+: MANDATORY ending with save_story_transcript()

MANUAL END COMMAND (IMPORTANT):
- If player says "finish story", "stop game", "complete adventure", "save story" → END IMMEDIATELY
- STEP 1: CALL save_story_transcript() - THIS IS MANDATORY!
- STEP 2: Wait for the function to return the filepath
- STEP 3: Say: "Your adventure is complete! Your story has been saved to [filepath]. Well done, [player name]!"
- Don't continue the story after they ask to finish
- AVOID using words like "end" or "quit" - use "finish" or "complete" instead

🚨 CRITICAL: At turn 4 or when HP reaches 0, you MUST call save_story_transcript() before saying anything else!

VICTORY CONDITIONS:
- If player survives to turn 4 with HP > 0, they WIN!
- YOU MUST CALL save_story_transcript() IMMEDIATELY - THIS IS MANDATORY!
- Wait for the function to return the filepath
- Then say: "You win! You defeated [enemy]! Health: X/100. Your story has been saved to [filepath]!"

DEFEAT CONDITIONS:
- If player HP reaches 0, they LOSE
- YOU MUST CALL save_story_transcript() IMMEDIATELY - THIS IS MANDATORY!
- Wait for the function to return the filepath
- Then say: "You fall unconscious... Your story has been saved to [filepath]. Try again?"

MANUAL SAVE:
- If player says "save story", "save my adventure", "save transcript" → CALL save_story_transcript()
- Return the filepath to the player

RESPONSE LENGTH:
- Maximum 2 sentences per response
- Don't give multiple choice options (1, 2, 3) - just describe and ask "What do you do?"
- Keep it simple and fast-paced

QUEST & NPC SYSTEM:
- When player meets an NPC, create an interesting quest or rumor
- Use talk_to_npc(npc_name) to generate dialogue
- Use create_quest(quest_name, description) when appropriate
- Use complete_quest(quest_name) when player finishes something important
- Use check_story_progress() to track adventure length
- Track what NPCs the player has met and their attitudes
- Make NPC interactions feel real and consequential

Response Style:
- Use simple, common English words
- Avoid complex or difficult vocabulary
- Keep responses VERY SHORT (1-2 sentences max)
- NO multiple choice lists (don't say "1. Do this 2. Do that")
- Just describe the scene briefly and ask "What do you do?"
- End stories quickly after 5-6 turns

GOOD Examples (Simple & Short):
- "You see a dark cave. What do you do?"
- "A wolf jumps out! What do you do?"
- "You find a magic sword. What do you do?"
- Turn 5: "You win! The village is safe. The end!"
- Turn 6: "You saved everyone! Game over!"

BAD Examples (NEVER DO THIS):
- "Do you: 1. Go left 2. Go right 3. Go forward" ❌ NO LISTS!
- "Would you like to: Follow the path, Investigate, or Mark it" ❌ NO OPTIONS!
- Long descriptions with multiple paragraphs ❌ TOO LONG!
- "You cautiously approach the magnificent edifice" ❌ TOO COMPLEX!

CRITICAL: Just describe what happens in 1-2 sentences, then ask "What do you do?"

STRICT RULES:
- Maximum 2 sentences per response
- No numbered choice lists
- End adventure at turn 6-7 maximum
- Use words like: big, small, dark, bright, old, new, good, bad, fast, slow

🚨 CRITICAL COMBAT & DAMAGE RULES (MUST FOLLOW):

RULE 1: ALWAYS call damage_player() when describing ANY attack or injury
- Wolf bites → damage_player(20, "wolf bite")
- Player falls → damage_player(15, "fall")
- Trap springs → damage_player(15, "trap")
- Ghost attacks → damage_player(25, "ghost")

RULE 2: ALWAYS call add_inventory_item() when player finds/picks up items
- Finds sword → add_inventory_item("magic sword")
- Picks up potion → add_inventory_item("health potion")
- Gets key → add_inventory_item("old key")

RULE 3: ALWAYS call use_inventory_item() when player uses healing items
- Player says "use first aid kit" → use_inventory_item("first aid kit")
- Player says "drink potion" → use_inventory_item("health potion")
- Player says "use medkit" → use_inventory_item("medkit")
- This automatically heals the player AND removes the item!

OR call heal_player() directly:
- Drinks potion → heal_player(30, "health potion")
- Rests → heal_player(20, "resting")
- Uses medkit → heal_player(30, "medkit")

RULE 4: Use modify_stat() to change Strength, Intelligence, or Luck
- Player finds strength item → modify_stat("strength", 2, "found strength potion")
- Player trains → modify_stat("intelligence", 1, "trained with wizard")
- Player gets cursed → modify_stat("luck", -1, "cursed by ghost")
- Player finds lucky charm → modify_stat("luck", 2, "found lucky charm")

WHEN TO MODIFY STATS:
- Turn 2-3: Give +1 or +2 to one stat (reward for exploration)
- Turn 4-5: Optionally give another +1 to a different stat
- Keep changes small (+1 or +2, rarely -1)
- Match stat to universe (Strength for combat, Intelligence for puzzles, Luck for finding items)

RULE 4: Use EXACT message formats so UI can parse them:
✅ "The wolf attacks! Health: 80/100. What do you do?"
✅ "📦 You acquired: magic sword"
✅ "You heal! Health: 100/100. What do you do?"

🚨 CRITICAL FORMAT RULES - MUST FOLLOW EXACTLY:
- ALWAYS include "Health: X/Y" in EVERY response where combat happens
- Use this EXACT format: "Health: 80/100" (with colon and slash)
- Put it at the END of your message before "What do you do?"
- Example: "A goblin attacks! Health: 69/100. What do you do?"
- DON'T use other formats like "health is now" or "health drops to"
- The UI ONLY reads "Health: X/Y" format reliably

CORRECT FORMAT:
✅ "Wolf bites you! Health: 82/100. What do you do?"
✅ "Goblin attacks! Health: 69/100. What do you do?"

WRONG FORMATS (DON'T USE):
❌ "Your health is now 82 out of 100"
❌ "Your health drops to 69 out of 100"
❌ "You take 20 damage"

WHY: The UI parses "Health: X/Y" format to update HP display!

🚨 NEVER just describe combat without calling the function!
Example:
❌ BAD: "The wolf bites you and you're bleeding"
✅ GOOD: [Call damage_player(20, "wolf bite")] "The wolf bites you! You take 20 damage!"
"""
    
    def _get_universe_hint(self) -> str:
        player_gender = getattr(self, 'player_gender', 'neutral') if hasattr(self, 'player_gender') else 'neutral'
        
        # Use correct pronouns based on player gender
        pronoun_guide = ""
        if player_gender == 'male':
            pronoun_guide = "Use 'he/him/his' when referring to the player"
        elif player_gender == 'female':
            pronoun_guide = "Use 'she/her/hers' when referring to the player"
        else:
            pronoun_guide = "Use 'they/them/their' when referring to the player"
            
        return f"D&D-style adventure storytelling mode - {pronoun_guide}"
    
    @function_tool
    async def auto_start_game(self, context: RunContext, player_name: str, player_gender: str, universe: str) -> str:
        """Automatically start the game with pre-selected options from the UI.
        
        Args:
            player_name: The player's character name
            player_gender: The player's gender (male or female)
            universe: The selected universe
        
        Returns:
            Game start message
        """
        self.player_name = player_name
        self.player_gender = player_gender
        self.first_message = False
        
        logger.info(f"Auto-starting game: {player_name} ({player_gender}) in {universe}")
        
        # Start the game directly
        return await self.start_new_game(context, universe, player_name, player_gender)

    @function_tool
    async def choose_universe(self, context: RunContext, choice: str) -> str:
        """Let the player choose which universe/story type they want.
        
        Args:
            choice: The universe choice (fantasy, space, cyberpunk, horror, love, or post-apocalypse)
        
        Returns:
            Confirmation and start of the game
        """
        # Store the universe preference
        self.universe_preference = choice
        
        # Get player info
        player_name = getattr(self, 'player_name', 'Adventurer')
        player_gender = getattr(self, 'player_gender', 'neutral')
        
        # Map common responses to universes
        universe_map = {
            "fantasy": "fantasy",
            "magic": "fantasy",
            "medieval": "fantasy",
            "dragon": "fantasy",
            "1": "fantasy",
            "space": "space_opera",
            "sci-fi": "space_opera",
            "scifi": "space_opera",
            "alien": "space_opera",
            "spaceship": "space_opera",
            "2": "space_opera",
            "cyber": "cyberpunk",
            "cyberpunk": "cyberpunk",
            "tech": "cyberpunk",
            "neon": "cyberpunk",
            "3": "cyberpunk",
            "apocalypse": "post_apocalypse",
            "post": "post_apocalypse",
            "wasteland": "post_apocalypse",
            "6": "post_apocalypse",
            "horror": "horror",
            "scary": "horror",
            "ghost": "horror",
            "spooky": "horror",
            "4": "horror"
        }
        
        choice_lower = choice.lower()
        universe_key = universe_map.get(choice_lower, "fantasy")
        
        # Now start the game with the chosen universe
        return await self.start_new_game(context, universe_key, player_name, player_gender)

    @function_tool
    async def start_new_game(self, context: RunContext, universe: str = "fantasy", player_name: str = "Adventurer", player_gender: str = "neutral"):
        """Start a new RPG adventure in the specified universe.
        
        Args:
            universe: The game universe (fantasy, cyberpunk, space_opera, post_apocalypse, horror)
            player_name: The player's character name
            player_gender: The player's gender (male, female, neutral) - important for correct pronouns
        """
        session_id = self.room_id
        _session_context[session_id] = context
        
        # Store gender for later use
        if not hasattr(self, 'player_gender'):
            self.player_gender = player_gender
        
        # Map common universe requests
        universe_map = {
            "mars": "space_opera",
            "moon": "space_opera",
            "space": "space_opera", 
            "sci-fi": "space_opera",
            "scifi": "space_opera",
            "alien": "space_opera",
            "cyber": "cyberpunk",
            "tech": "cyberpunk",
            "neon": "cyberpunk",
            "apocalypse": "post_apocalypse",
            "wasteland": "post_apocalypse",
            "zombie": "post_apocalypse",
            "magic": "fantasy",
            "medieval": "fantasy",
            "dragon": "fantasy",
            "scary": "horror",
            "ghost": "horror",
            "haunted": "horror",
            "spooky": "horror",
            "monster": "horror"
        }
        
        universe_key = universe.lower()
        if universe_key in universe_map:
            universe_key = universe_map[universe_key]
            
        try:
            universe_enum = Universe(universe_key)
        except ValueError:
            universe_enum = Universe.FANTASY
            
        game_state = GameState(universe_enum)
        game_state.player.name = player_name
        game_state.turn_count = 0  # Initialize turn counter
        game_sessions[session_id] = game_state
        save_game_state(session_id, game_state)  # Auto-save new game
        
        # Create story logger
        story_logger = create_story_logger(game_state, player_name)
        story_loggers[session_id] = story_logger
        
        logger.info(f"Started new {universe} game for {player_name}")
        
        location_info = game_state.get_current_location_info()
        # Create welcome message with IMMEDIATE COMBAT and proper location format
        # Store context for first attack
        _session_context[session_id] = context
        
        # Apply immediate damage on game start
        import random
        start_damage = random.randint(15, 25)
        game_state.damage_player(start_damage)
        game_state.add_event(f"Game started - took {start_damage} damage")
        
        # Add starting items to inventory with proper notification
        starting_items = game_state.player.inventory.copy()
        save_game_state(session_id, game_state)
        
        # Build starting inventory message - list all items clearly
        inventory_msg = ""
        if starting_items:
            items_list = ", ".join(starting_items)
            inventory_msg = f" You have: {items_list}."
        
        # Return welcome message with location, HP, and starting items
        if universe_enum == Universe.SPACE_OPERA:
            return f"Welcome {player_name}! You enter the {location_info['name']}. An alien attacks you! Health: {game_state.player.hp}/{game_state.player.max_hp}.{inventory_msg} What do you do?"
        elif universe_enum == Universe.CYBERPUNK:
            return f"Welcome {player_name}! You enter the {location_info['name']}. A gang member attacks you! Health: {game_state.player.hp}/{game_state.player.max_hp}.{inventory_msg} What do you do?"
        elif universe_enum == Universe.POST_APOCALYPSE:
            return f"Welcome {player_name}! You enter the {location_info['name']}. A zombie attacks you! Health: {game_state.player.hp}/{game_state.player.max_hp}.{inventory_msg} What do you do?"
        elif universe_enum == Universe.HORROR:
            return f"Welcome {player_name}! You enter the {location_info['name']}. A ghost attacks you! Health: {game_state.player.hp}/{game_state.player.max_hp}.{inventory_msg} What do you do?"
        else:
            return f"Welcome {player_name}! You enter the {location_info['name']}. A wolf attacks you! Health: {game_state.player.hp}/{game_state.player.max_hp}.{inventory_msg} What do you do?"

    @function_tool
    async def roll_dice(self, context: RunContext, action: str, attribute: str = "luck"):
        """Roll dice for a player action with attribute modifier.
        
        Args:
            action: What the player is attempting
            attribute: Which attribute to use (strength, intelligence, luck)
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        # Get attribute modifier
        modifier = 0
        if attribute == "strength":
            modifier = (game_state.player.strength - 10) // 2
        elif attribute == "intelligence":
            modifier = (game_state.player.intelligence - 10) // 2
        elif attribute == "luck":
            modifier = (game_state.player.luck - 10) // 2
            
        roll_result = game_state.roll_dice(20, modifier)
        game_state.add_event(f"Rolled for {action}: {roll_result['total']} ({roll_result['result']})")
        game_state.turn_count += 1
        save_game_state(session_id, game_state)  # Auto-save
        
        logger.info(f"Dice roll for {action}: {roll_result}")
        
        return f"Rolling for {action}... You rolled {roll_result['roll']} + {roll_result['modifier']} = {roll_result['total']} ({roll_result['result']})!"

    @function_tool
    async def check_inventory(self, context: RunContext):
        """Check the player's current inventory and status."""
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        inventory_list = ", ".join(game_state.player.inventory) if game_state.player.inventory else "nothing"
        
        return f"Health: {game_state.player.hp}/{game_state.player.max_hp} ({game_state.player.status}). Inventory: {inventory_list}. Stats - Strength: {game_state.player.strength}, Intelligence: {game_state.player.intelligence}, Luck: {game_state.player.luck}."

    @function_tool
    async def save_story(self, context: RunContext):
        """Save your current story progress to file."""
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game to save!"
        
        save_game_state(session_id, game_state)
        return f"Your {game_state.universe.value} adventure has been saved! You can continue this story later."

    @function_tool
    async def move_location(self, context: RunContext, location: str):
        """Move to a new location if path exists. ALWAYS triggers an attack!
        
        Args:
            location: The location name to move to
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        if game_state.move_to_location(location):
            location_info = game_state.get_current_location_info()
            universe = game_state.universe
            location_name = location_info['name']
            
            # AUTOMATIC COMBAT - Apply damage when moving to new location
            import random
            damage_amount = random.randint(15, 25)
            
            # Get attack type based on universe
            if universe == Universe.POST_APOCALYPSE:
                attack_sources = ["zombie attack", "raider ambush", "radiation", "trap"]
                attack_descriptions = {
                    "zombie attack": "A zombie jumps out and attacks you",
                    "raider ambush": "Raiders ambush you",
                    "radiation": "You walk through radiation",
                    "trap": "You trigger a trap"
                }
            elif universe == Universe.HORROR:
                attack_sources = ["ghost attack", "monster claw", "trap", "fall"]
                attack_descriptions = {
                    "ghost attack": "A ghost appears and attacks you",
                    "monster claw": "A monster claws at you",
                    "trap": "A trap springs",
                    "fall": "You slip and fall"
                }
            elif universe == Universe.SPACE_OPERA:
                attack_sources = ["alien attack", "laser blast", "explosion", "radiation"]
                attack_descriptions = {
                    "alien attack": "An alien attacks you",
                    "laser blast": "A laser turret fires at you",
                    "explosion": "An explosion hits you",
                    "radiation": "Radiation damages you"
                }
            elif universe == Universe.CYBERPUNK:
                attack_sources = ["gang attack", "hacker virus", "explosion", "fall"]
                attack_descriptions = {
                    "gang attack": "Gang members attack you",
                    "hacker virus": "A virus attacks your implants",
                    "explosion": "An explosion hits you",
                    "fall": "You fall from a ledge"
                }
            else:  # Fantasy
                attack_sources = ["wolf attack", "orc ambush", "arrow trap", "fall"]
                attack_descriptions = {
                    "wolf attack": "A wolf attacks you",
                    "orc ambush": "Orcs ambush you",
                    "arrow trap": "An arrow trap fires",
                    "fall": "You fall into a pit"
                }
            
            attack_source = random.choice(attack_sources)
            attack_desc = attack_descriptions[attack_source]
            
            # Apply damage automatically
            game_state.damage_player(damage_amount)
            game_state.add_event(f"Took {damage_amount} damage from {attack_source}")
            game_state.turn_count += 1
            save_game_state(session_id, game_state)
            
            # Return message with proper location format and simple HP display
            # CRITICAL: Use "You enter the" format so frontend can parse location
            return f"You enter the {location_name}. {attack_desc}! Health: {game_state.player.hp}/{game_state.player.max_hp}. What do you do?"
        else:
            current_loc = game_state.locations.get(game_state.current_location)
            if current_loc:
                available = ", ".join(current_loc.paths)
                return f"You cannot go there. You can go to: {available}. What do you do?"
            else:
                return f"You cannot go to {location} from here. What do you do?"

    @function_tool
    async def add_inventory_item(self, context: RunContext, item: str):
        """Add an item to player inventory. ALWAYS use this when player finds or picks up items!
        
        Args:
            item: The item to add
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        game_state.add_item(item)
        save_game_state(session_id, game_state)
        # CRITICAL: Use exact format that frontend parses
        return f"📦 You acquired: {item}"

    @function_tool
    async def use_inventory_item(self, context: RunContext, item: str):
        """Use/remove an item from inventory. If it's a healing item, automatically heal the player!
        
        Args:
            item: The item to use
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        if game_state.remove_item(item):
            save_game_state(session_id, game_state)
            
            # Check if it's a healing item - automatically heal
            healing_items = {
                "first aid kit": 30,
                "health potion": 30,
                "medkit": 30,
                "healing herb": 20,
                "stim pack": 25,
                "medical nanobots": 35,
                "bandage": 15,
            }
            
            item_lower = item.lower()
            for healing_item, heal_amount in healing_items.items():
                if healing_item in item_lower:
                    game_state.heal_player(heal_amount)
                    save_game_state(session_id, game_state)
                    return f"✅ You used: {item}. You heal! Health: {game_state.player.hp}/{game_state.player.max_hp}"
            
            return f"✅ You used: {item}"
        else:
            return f"❌ You don't have {item} in your inventory."

    @function_tool
    async def damage_player(self, context: RunContext, damage: int, source: str = "unknown"):
        """Apply damage to the player. ALWAYS use this when describing any attack or injury!
        
        Args:
            damage: Amount of damage
            source: What caused the damage
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        old_hp = game_state.player.hp
        game_state.damage_player(damage)
        game_state.add_event(f"Took {damage} damage from {source}")
        save_game_state(session_id, game_state)
        
        # CRITICAL: Use simple format - just show final HP
        return f"The {source} hits you! Health: {game_state.player.hp}/{game_state.player.max_hp}"

    @function_tool
    async def heal_player(self, context: RunContext, amount: int, source: str = "healing"):
        """Heal the player. ALWAYS call this when player uses healing items!
        
        Args:
            amount: Amount to heal (default 30 for first aid kit)
            source: What provided the healing
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        game_state.heal_player(amount)
        game_state.add_event(f"Healed {amount} HP from {source}")
        save_game_state(session_id, game_state)
        
        # Use simple format that frontend parses
        return f"You heal! Health: {game_state.player.hp}/{game_state.player.max_hp}"

    @function_tool
    async def save_game(self, context: RunContext):
        """Save the current game state."""
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game to save!"
            
        # Create saves directory if it doesn't exist
        os.makedirs("saves", exist_ok=True)
        
        filename = f"saves/game_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        game_state.save_to_file(filename)
        
        logger.info(f"Game saved to {filename}")
        return f"Game saved successfully! File: {filename}"

    @function_tool
    async def load_game(self, context: RunContext, filename: str):
        """Load a saved game state.
        
        Args:
            filename: The save file to load
        """
        session_id = self.room_id
        
        try:
            game_state = GameState.load_from_file(filename)
            game_sessions[session_id] = game_state
            
            location_info = game_state.get_current_location_info()
            recent_events = game_state.events[-3:] if game_state.events else []
            events_text = " Recent events: " + ", ".join([e.description for e in recent_events]) if recent_events else ""
            
            logger.info(f"Game loaded from {filename}")
            return f"Game loaded! You are {game_state.player.name} at {location_info['name']}.{events_text}"
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return f"Failed to load game from {filename}. Error: {str(e)}"

    @function_tool
    async def get_game_status(self, context: RunContext):
        """Get current game status and world state."""
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
            
        location_info = game_state.get_current_location_info()
        recent_events = game_state.events[-5:] if game_state.events else []
        
        status = {
            "player": game_state.player.name,
            "universe": game_state.universe.value,
            "location": location_info['name'],
            "health": f"{game_state.player.hp}/{game_state.player.max_hp}",
            "status": game_state.player.status,
            "inventory_count": len(game_state.player.inventory),
            "turn_count": game_state.turn_count,
            "recent_events": [e.description for e in recent_events]
        }
        
        return f"Game Status: {json.dumps(status, indent=2)}"

    @function_tool
    async def talk_to_npc(self, context: RunContext, npc_name: str):
        """Talk to an NPC and learn about quests or rumors.
        
        Args:
            npc_name: The NPC's name to talk to
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
        
        # Find the NPC
        npc = None
        for npc_data in game_state.npcs.values():
            if npc_name.lower() in npc_data.name.lower():
                npc = npc_data
                break
        
        if not npc:
            return f"You don't see {npc_name} here. Look around first!"
        
        if not npc.alive:
            return f"{npc.name} is no longer with us..."
        
        # Check if NPC is in current location
        if npc.location != game_state.current_location:
            return f"{npc.name} is not here. You are at {game_state.get_current_location_info()['name']}."
        
        # Generate dialogue based on attitude
        attitude = npc.attitude.lower()
        location_info = game_state.get_current_location_info()
        
        dialogues = {
            "friendly": f"{npc.name} smiles warmly. 'Welcome! I have heard stories about great quests. Would you like to help?'",
            "neutral": f"{npc.name} nods at you. '{npc.name} here. What do you want to know?'",
            "hostile": f"{npc.name} gives you a cold look. 'What do you want? Leave me alone.'"
        }
        
        dialogue = dialogues.get(attitude, f"{npc.name} looks at you silently.")
        game_state.add_event(f"Talked to {npc.name}")
        game_state.turn_count += 1
        save_game_state(session_id, game_state)  # Auto-save
        
        return dialogue

    @function_tool
    async def create_quest(self, context: RunContext, quest_name: str, description: str):
        """Create a new quest for the player.
        
        Args:
            quest_name: The name of the quest
            description: What the quest is about
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
        
        from game_state import Quest
        quest = Quest(
            name=quest_name,
            description=description,
            active=True,
            completed=False
        )
        game_state.quests.append(quest)
        game_state.add_event(f"Quest started: {quest_name}")
        game_state.turn_count += 1
        save_game_state(session_id, game_state)  # Auto-save
        
        logger.info(f"Quest created: {quest_name}")
        return f"New quest: {quest_name}! {description}"

    @function_tool
    async def complete_quest(self, context: RunContext, quest_name: str):
        """Mark a quest as completed.
        
        Args:
            quest_name: The name of the quest to complete
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
        
        for quest in game_state.quests:
            if quest_name.lower() in quest.name.lower():
                quest.completed = True
                quest.active = False
                game_state.add_event(f"Quest completed: {quest.name}")
                game_state.turn_count += 1
                save_game_state(session_id, game_state)  # Auto-save
                return f"Quest complete! {quest.name} is done!"
        
        return f"Quest '{quest_name}' not found."

    @function_tool
    async def list_quests(self, context: RunContext):
        """List all active and completed quests.
        
        Returns:
            Summary of current quests
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
        
        active_quests = [q for q in game_state.quests if q.active]
        completed_quests = [q for q in game_state.quests if q.completed]
        
        result = ""
        if active_quests:
            result += "Active Quests:\n"
            for q in active_quests:
                result += f"- {q.name}: {q.description}\n"
        
        if completed_quests:
            result += "\nCompleted Quests:\n"
            for q in completed_quests:
                result += f"- {q.name}\n"
        
        if not active_quests and not completed_quests:
            result = "No quests yet. Talk to NPCs to find out about adventures!"
        
        return result

    @function_tool
    async def check_story_progress(self, context: RunContext):
        """Check how far along the adventure is and if it should be ending soon.
        
        Returns:
            Story progress and hint
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
        
        should_end, end_message = should_end_story(game_state, "check_progress")
        
        if should_end:
            # Save story transcript when game ends
            await self.save_story_transcript(context)
            return end_message
        
        hint = get_story_progress_hint(game_state)
        progress = f"Turn {game_state.turn_count}/12. {hint}"
        
        return progress
    
    @function_tool
    async def modify_stat(self, context: RunContext, stat_name: str, amount: int, reason: str = ""):
        """Modify a player stat (strength, intelligence, or luck).
        
        Args:
            stat_name: Which stat to modify ("strength", "intelligence", or "luck")
            amount: How much to change (positive or negative)
            reason: Why the stat changed (e.g., "found strength potion")
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game. Start a new adventure first!"
        
        stat_name = stat_name.lower()
        
        if stat_name == "strength":
            game_state.player.strength += amount
            game_state.player.strength = max(1, min(20, game_state.player.strength))  # Keep between 1-20
            stat_emoji = "💪"
        elif stat_name == "intelligence":
            game_state.player.intelligence += amount
            game_state.player.intelligence = max(1, min(20, game_state.player.intelligence))
            stat_emoji = "🧠"
        elif stat_name == "luck":
            game_state.player.luck += amount
            game_state.player.luck = max(1, min(20, game_state.player.luck))
            stat_emoji = "🍀"
        else:
            return f"Unknown stat: {stat_name}"
        
        game_state.add_event(f"{stat_name.title()} {'+' if amount > 0 else ''}{amount}: {reason}")
        save_game_state(session_id, game_state)
        
        change_text = "increased" if amount > 0 else "decreased"
        current_value = getattr(game_state.player, stat_name)
        
        return f"{stat_emoji} {stat_name.title()} {change_text} by {abs(amount)}! Now: {current_value}"
    
    @function_tool
    async def save_story_transcript(self, context: RunContext):
        """Save the adventure story to a text file.
        
        Returns:
            Confirmation message with file path
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game to save!"
        
        try:
            # Create story logger if it doesn't exist
            if session_id not in story_loggers:
                story_logger = create_story_logger(game_state, game_state.player.name)
                story_loggers[session_id] = story_logger
            else:
                story_logger = story_loggers[session_id]
            
            # Get conversation history from context
            # Add all game events to story
            for event in game_state.events:
                story_logger.add_message("Game Master", event.description)
            
            filepath = story_logger.save_story()
            logger.info(f"Story saved to {filepath}")
            return f"✅ Your adventure has been saved! Check: {filepath}"
        except Exception as e:
            logger.error(f"Failed to save story: {e}")
            return f"Failed to save story: {str(e)}"
    
    @function_tool
    async def process_player_action(self, context: RunContext, action: str):
        """Process any player action and automatically apply combat if needed.
        This function is called automatically to enforce combat rules.
        
        Args:
            action: What the player is doing
        """
        session_id = self.room_id
        game_state = game_sessions.get(session_id)
        
        if not game_state:
            return "No active game."
        
        # Apply automatic combat
        combat_occurred, enemy_name, damage = CombatEnforcer.apply_automatic_combat(game_state, action)
        
        if combat_occurred:
            save_game_state(session_id, game_state)
            
            # CRITICAL: Simple format - just show final HP
            combat_msg = f"The {enemy_name} hits you! Health: {game_state.player.hp}/{game_state.player.max_hp}"
            
            # Check if player should get healing item
            if CombatEnforcer.should_give_healing_item(game_state):
                healing_item = CombatEnforcer.get_healing_item(game_state)
                game_state.add_item(healing_item)
                save_game_state(session_id, game_state)
                return f"{combat_msg}. 📦 You acquired: {healing_item}"
            
            return combat_msg
        
        return "Action processed."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    # Create saves directory
    os.makedirs("saves", exist_ok=True)
    os.makedirs("game_saves", exist_ok=True)


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Get Azure credentials
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION")

    logger.info(f"Azure Endpoint: {azure_endpoint}")
    logger.info(f"Azure Deployment: {azure_deployment}")
    logger.info(f"Azure API Key present: {bool(azure_key)}")

    # Set up a voice AI pipeline for the Game Master
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # Using Azure OpenAI LLM (Google Gemini quota exhausted)
        llm=openai.LLM.with_azure(
                azure_endpoint=azure_endpoint,
                azure_deployment=azure_deployment,
                api_version=azure_version,
                api_key=azure_key,
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # Using Murf TTS with narration style for dramatic storytelling
        # Note: Murf voice IDs may differ from documentation
        # Using default US English voice with Narration style for best storytelling
        tts=murf.TTS(
                voice="en-US-matthew",  # US English - dramatic narration voice
                style="Narration",  # Dramatic storytelling style
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Detect universe preference from room metadata if available
    universe_pref = ctx.room.metadata if hasattr(ctx, 'room') and hasattr(ctx.room, 'metadata') else None
    
    # Select voice based on universe (will be updated when universe is chosen)
    # For now, use default voice - voice will match the storytelling style
    
    # Start the session with the Game Master
    await session.start(
        agent=GameMaster(room_id=ctx.room.name, universe_preference=universe_pref),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
