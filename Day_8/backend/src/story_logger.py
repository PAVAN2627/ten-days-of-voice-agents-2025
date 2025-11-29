"""
Story Logger - Saves adventure transcripts to text files

This module creates readable story transcripts that players can keep.
"""

import os
from datetime import datetime
from pathlib import Path
from game_state import GameState

STORY_SAVES_DIR = Path("story_saves")
STORY_SAVES_DIR.mkdir(exist_ok=True)

class StoryLogger:
    """Logs story events to a readable text file"""
    
    def __init__(self, game_state: GameState, player_name: str):
        self.game_state = game_state
        self.player_name = player_name
        self.universe = game_state.universe.value
        self.story_lines = []
        self.start_time = datetime.now()
        
        # Create story title
        self.title = f"{player_name}'s {self.universe.replace('_', ' ').title()} Adventure"
        
    def add_message(self, speaker: str, message: str):
        """Add a message to the story transcript"""
        self.story_lines.append(f"{speaker}: {message}")
    
    def save_story(self) -> str:
        """Save the story to a text file"""
        # Create filename with timestamp
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        safe_name = self.player_name.replace(" ", "_").lower()
        filename = f"{safe_name}_{self.universe}_{timestamp}.txt"
        filepath = STORY_SAVES_DIR / filename
        
        # Build story content
        content = self._build_story_content()
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def _build_story_content(self) -> str:
        """Build the formatted story content as a narrative"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(self.title.center(70))
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"A {self.universe.replace('_', ' ').title()} Adventure")
        lines.append(f"Starring: {self.player_name}")
        lines.append(f"Date: {self.start_time.strftime('%B %d, %Y')}")
        lines.append("")
        lines.append("=" * 70)
        lines.append("")
        
        # Convert chat to narrative story
        story_paragraphs = self._convert_to_narrative()
        for paragraph in story_paragraphs:
            # Wrap paragraphs at 70 characters
            wrapped = self._wrap_text(paragraph, 70)
            lines.extend(wrapped)
            lines.append("")
        
        # Footer with stats
        lines.append("")
        lines.append("=" * 70)
        lines.append("THE END")
        lines.append("=" * 70)
        lines.append("")
        
        # Outcome
        if self.game_state.player.hp <= 0:
            lines.append("💀 The adventure ended in defeat...")
            lines.append(f"   {self.player_name} fell in battle, but their story will be remembered.")
        elif self.game_state.turn_count >= 6:
            lines.append("🏆 VICTORY!")
            lines.append(f"   {self.player_name} emerged triumphant from their perilous journey!")
        
        lines.append("")
        lines.append("-" * 70)
        lines.append("FINAL STATISTICS")
        lines.append("-" * 70)
        lines.append(f"Health: {self.game_state.player.hp}/{self.game_state.player.max_hp} ({self.game_state.player.status})")
        lines.append(f"Strength: {self.game_state.player.strength} | Intelligence: {self.game_state.player.intelligence} | Luck: {self.game_state.player.luck}")
        
        if self.game_state.player.inventory:
            lines.append(f"Final Inventory: {', '.join(self.game_state.player.inventory)}")
        
        lines.append(f"Final Location: {self.game_state.get_current_location_info()['name']}")
        lines.append(f"Adventure Length: {self.game_state.turn_count} turns")
        lines.append("")
        
        return "\n".join(lines)
    
    def _convert_to_narrative(self) -> list:
        """Convert chat messages to narrative story paragraphs"""
        paragraphs = []
        
        for line in self.story_lines:
            # Remove speaker labels and convert to narrative
            if line.startswith("Game Master: ") or line.startswith("GM: "):
                # This is narration
                text = line.replace("Game Master: ", "").replace("GM: ", "")
                # Clean up game mechanics text
                text = text.replace("What do you do?", "")
                text = text.replace("Health:", "Their health was")
                text = text.replace("/100", " out of 100")
                paragraphs.append(text.strip())
                
            elif line.startswith(f"{self.player_name}: ") or line.startswith("You: ") or line.startswith("Player: "):
                # This is player action - convert to narrative
                text = line.replace(f"{self.player_name}: ", "").replace("You: ", "").replace("Player: ", "")
                # Convert first person to third person
                text = text.replace("I ", f"{self.player_name} ")
                text = text.replace("my ", f"{self.player_name}'s ")
                text = text.replace("me ", f"{self.player_name} ")
                paragraphs.append(text.strip())
        
        return [p for p in paragraphs if p]  # Remove empty paragraphs
    
    def _wrap_text(self, text: str, width: int) -> list:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines if lines else [text]


def create_story_logger(game_state: GameState, player_name: str) -> StoryLogger:
    """Create a new story logger"""
    return StoryLogger(game_state, player_name)
