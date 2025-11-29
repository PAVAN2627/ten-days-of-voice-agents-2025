"""
Test script to verify story saving functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from game_state import GameState, Universe
from story_logger import create_story_logger

def test_story_save():
    """Test that story saving works correctly"""
    print("Testing story save functionality...")
    
    # Create a test game state
    game_state = GameState(Universe.FANTASY)
    game_state.player.name = "TestHero"
    game_state.player.hp = 75
    game_state.turn_count = 3
    
    # Add some events
    game_state.add_event("Started adventure in Village Square")
    game_state.add_event("Took 25 damage from wolf attack")
    game_state.add_event("Acquired magic sword")
    game_state.add_event("Healed 30 HP from health potion")
    game_state.add_event("Defeated the wolf")
    
    # Create story logger
    story_logger = create_story_logger(game_state, "TestHero")
    
    # Add some messages
    story_logger.add_message("Game Master", "Welcome TestHero! You enter the Village Square. A wolf attacks you!")
    story_logger.add_message("Player", "I attack the wolf with my sword")
    story_logger.add_message("Game Master", "You swing your sword! The wolf is defeated!")
    
    # Save the story
    try:
        filepath = story_logger.save_story()
        print(f"✅ Story saved successfully to: {filepath}")
        
        # Verify file exists
        if Path(filepath).exists():
            print(f"✅ File exists and can be read")
            
            # Read and display first few lines
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n📖 Story preview (first 15 lines):")
                print("=" * 70)
                for line in lines[:15]:
                    print(line.rstrip())
                print("=" * 70)
                print(f"\nTotal lines: {len(lines)}")
            
            return True
        else:
            print(f"❌ File was not created at: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving story: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_story_save()
    sys.exit(0 if success else 1)
