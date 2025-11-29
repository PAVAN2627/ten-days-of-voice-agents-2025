import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class Universe(Enum):
    FANTASY = "fantasy"
    CYBERPUNK = "cyberpunk"
    SPACE_OPERA = "space_opera"
    POST_APOCALYPSE = "post_apocalypse"
    HORROR = "horror"

@dataclass
class Character:
    name: str
    hp: int = 100
    max_hp: int = 100
    strength: int = 10
    intelligence: int = 10
    luck: int = 10
    inventory: List[str] = None
    status: str = "Healthy"
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

@dataclass
class NPC:
    name: str
    role: str
    attitude: str = "neutral"
    alive: bool = True
    location: str = ""

@dataclass
class Location:
    name: str
    description: str
    paths: List[str] = None
    
    def __post_init__(self):
        if self.paths is None:
            self.paths = []

@dataclass
class Quest:
    name: str
    description: str
    completed: bool = False
    active: bool = True

@dataclass
class Event:
    description: str
    timestamp: str
    location: str = ""

class GameState:
    def __init__(self, universe: Universe = Universe.FANTASY):
        self.universe = universe
        self.player = Character(name="Adventurer")
        self.npcs: Dict[str, NPC] = {}
        self.locations: Dict[str, Location] = {}
        self.current_location = ""
        self.quests: List[Quest] = []
        self.events: List[Event] = []
        self.turn_count = 0
        
        self._initialize_universe()
    
    def _initialize_universe(self):
        """Initialize the game world based on selected universe"""
        if self.universe == Universe.FANTASY:
            self._init_fantasy()
        elif self.universe == Universe.CYBERPUNK:
            self._init_cyberpunk()
        elif self.universe == Universe.SPACE_OPERA:
            self._init_space_opera()
        elif self.universe == Universe.POST_APOCALYPSE:
            self._init_post_apocalypse()
        elif self.universe == Universe.HORROR:
            self._init_horror()
    
    def _init_fantasy(self):
        self.locations = {
            "village": Location("Village Square", "A peaceful village with cobblestone streets", ["forest", "tavern"]),
            "forest": Location("Dark Forest", "Ancient trees block out most sunlight", ["village", "cave"]),
            "cave": Location("Mysterious Cave", "A deep cave with strange glowing crystals", ["forest"]),
            "tavern": Location("The Prancing Pony", "A warm tavern filled with travelers", ["village"])
        }
        self.current_location = "village"
        self.npcs = {
            "innkeeper": NPC("Brom the Innkeeper", "tavern keeper", "friendly", True, "tavern"),
            "wizard": NPC("Eldara the Wise", "village wizard", "mysterious", True, "village")
        }
        self.player.inventory = ["rusty sword", "leather pouch"]
    
    def _init_cyberpunk(self):
        self.locations = {
            "street": Location("Neon Street", "Rain-soaked streets with holographic ads", ["bar", "alley"]),
            "bar": Location("Chrome Bar", "A dive bar with synthetic music", ["street"]),
            "alley": Location("Dark Alley", "Shadows hide dangerous secrets", ["street", "hideout"]),
            "hideout": Location("Hacker Hideout", "Screens everywhere, cables hanging", ["alley"])
        }
        self.current_location = "street"
        self.npcs = {
            "bartender": NPC("Zara", "bartender", "suspicious", True, "bar"),
            "hacker": NPC("Ghost", "information broker", "neutral", True, "hideout")
        }
        self.player.inventory = ["neural implant", "credit chip"]
    
    def _init_space_opera(self):
        self.locations = {
            "bridge": Location("Ship Bridge", "Command center with star charts", ["quarters", "engine"]),
            "quarters": Location("Crew Quarters", "Small living spaces", ["bridge", "cargo"]),
            "engine": Location("Engine Room", "Humming with energy", ["bridge"]),
            "cargo": Location("Cargo Bay", "Storage for supplies", ["quarters"])
        }
        self.current_location = "bridge"
        self.npcs = {
            "pilot": NPC("Rex", "ship pilot", "loyal", True, "bridge"),
            "engineer": NPC("Kira", "chief engineer", "grumpy", True, "engine")
        }
        self.player.inventory = ["plasma pistol", "comm device"]
    
    def _init_post_apocalypse(self):
        self.locations = {
            "wasteland": Location("Barren Wasteland", "Cracked earth under a red sky", ["bunker", "ruins"]),
            "bunker": Location("Underground Bunker", "Safe but claustrophobic", ["wasteland"]),
            "ruins": Location("City Ruins", "Collapsed buildings and debris", ["wasteland", "shelter"]),
            "shelter": Location("Survivor Shelter", "A makeshift camp", ["ruins"])
        }
        self.current_location = "wasteland"
        self.npcs = {
            "survivor": NPC("Maya", "shelter leader", "cautious", True, "shelter"),
            "raider": NPC("Scar", "wasteland raider", "hostile", True, "wasteland")
        }
        self.player.inventory = ["water bottle", "scrap metal", "medkit"]
    
    def _init_horror(self):
        self.locations = {
            "mansion": Location("Old Mansion", "A scary old house with creaking floors", ["basement", "garden"]),
            "basement": Location("Dark Basement", "Cold and dark with strange sounds", ["mansion"]),
            "garden": Location("Dead Garden", "Old garden with dead plants", ["mansion", "cemetery"]),
            "cemetery": Location("Spooky Cemetery", "Old graves with broken stones", ["garden"])
        }
        self.current_location = "mansion"
        self.npcs = {
            "ghost": NPC("Sarah", "lost spirit", "sad", True, "mansion"),
            "caretaker": NPC("Old Tom", "cemetery keeper", "mysterious", True, "cemetery")
        }
        # Start with flashlight, old key, and medkit
        self.player.inventory = ["flashlight", "old key", "medkit"]
    
    def roll_dice(self, sides: int = 20, modifier: int = 0) -> Dict[str, Any]:
        """Roll dice with modifier"""
        roll = random.randint(1, sides)
        total = roll + modifier
        
        if total >= 15:
            result = "success"
        elif total >= 10:
            result = "partial"
        else:
            result = "failure"
        
        return {
            "roll": roll,
            "modifier": modifier,
            "total": total,
            "result": result
        }
    
    def add_event(self, description: str):
        """Add an event to history"""
        event = Event(
            description=description,
            timestamp=datetime.now().isoformat(),
            location=self.current_location
        )
        self.events.append(event)
    
    def move_to_location(self, location_name: str) -> bool:
        """Move player to new location if valid"""
        if location_name in self.locations:
            current_loc = self.locations.get(self.current_location)
            if current_loc and location_name in current_loc.paths:
                self.current_location = location_name
                self.add_event(f"Moved to {location_name}")
                return True
        return False
    
    def add_item(self, item: str):
        """Add item to player inventory"""
        self.player.inventory.append(item)
        self.add_event(f"Acquired {item}")
    
    def remove_item(self, item: str) -> bool:
        """Remove item from inventory"""
        if item in self.player.inventory:
            self.player.inventory.remove(item)
            self.add_event(f"Used/lost {item}")
            return True
        return False
    
    def damage_player(self, damage: int):
        """Apply damage to player"""
        self.player.hp = max(0, self.player.hp - damage)
        if self.player.hp <= 0:
            self.player.status = "Critical"
        elif self.player.hp <= 30:
            self.player.status = "Injured"
        else:
            self.player.status = "Healthy"
    
    def heal_player(self, amount: int):
        """Heal player"""
        self.player.hp = min(self.player.max_hp, self.player.hp + amount)
        if self.player.hp > 30:
            self.player.status = "Healthy"
        elif self.player.hp > 0:
            self.player.status = "Injured"
    
    def get_current_location_info(self) -> Dict[str, Any]:
        """Get current location details"""
        loc = self.locations.get(self.current_location)
        if not loc:
            return {}
        
        npcs_here = [npc for npc in self.npcs.values() 
                    if npc.location == self.current_location and npc.alive]
        
        return {
            "name": loc.name,
            "description": loc.description,
            "paths": loc.paths,
            "npcs": [{"name": npc.name, "role": npc.role} for npc in npcs_here]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for saving"""
        return {
            "universe": self.universe.value,
            "player": asdict(self.player),
            "npcs": {k: asdict(v) for k, v in self.npcs.items()},
            "locations": {k: asdict(v) for k, v in self.locations.items()},
            "current_location": self.current_location,
            "quests": [asdict(q) for q in self.quests],
            "events": [asdict(e) for e in self.events],
            "turn_count": self.turn_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Load game state from dictionary"""
        universe = Universe(data["universe"])
        game_state = cls(universe)
        
        # Load player
        player_data = data["player"]
        game_state.player = Character(**player_data)
        
        # Load NPCs
        game_state.npcs = {k: NPC(**v) for k, v in data["npcs"].items()}
        
        # Load locations
        game_state.locations = {k: Location(**v) for k, v in data["locations"].items()}
        
        # Load other data
        game_state.current_location = data["current_location"]
        game_state.quests = [Quest(**q) for q in data["quests"]]
        game_state.events = [Event(**e) for e in data["events"]]
        game_state.turn_count = data["turn_count"]
        
        return game_state
    
    def save_to_file(self, filename: str):
        """Save game state to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'GameState':
        """Load game state from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)