# 🎲 Day 8: Voice-Powered RPG Game Master

An immersive voice-controlled RPG adventure game with multiple universes, real-time combat, dynamic storytelling, and automatic story transcript saving.

## ✨ Features

### 🌍 Multiple Universes
- **Fantasy** - Dragons, magic, medieval adventures
- **Horror** - Ghosts, haunted mansions, supernatural terror
- **Space Opera** - Aliens, spaceships, galactic exploration
- **Cyberpunk** - Neon cities, hackers, dystopian future
- **Post-Apocalypse** - Zombies, wastelands, survival

### 🎮 Core Gameplay
- **Voice-Controlled** - Speak your actions naturally
- **Real-Time Combat** - Dynamic HP tracking with automatic damage calculation
- **Inventory System** - Find items, use healing potions, manage equipment
- **Location Exploration** - Navigate through universe-specific locations
- **Character Stats** - Strength, Intelligence, and Luck attributes
- **Quest System** - Create, track, and complete quests
- **NPC Interactions** - Talk to characters and build relationships
- **Dice Rolling** - D20 mechanics with attribute modifiers

### 🎨 Immersive Experience
- **Universe-Specific Backgrounds** - Atmospheric visuals for each world
- **Background Music** - Thematic music with volume controls
- **Real-Time UI Updates** - Live HP bars, inventory display, location tracking
- **Gender-Aware Narration** - Correct pronouns based on player choice
- **Story Transcript Saving** - Every adventure saved as readable text file

### 🎯 Game Balance
- **Short Adventures** - 3-4 turns for quick, engaging gameplay
- **Balanced Combat** - Fair damage and healing distribution
- **Auto-Save System** - Game state persistence across sessions
- **Victory/Defeat Conditions** - Clear win/loss scenarios

## 🛠️ Tech Stack

### Backend
- **Python** - Core game logic
- **LiveKit** - Voice communication
- **Deepgram Nova-3** - Speech-to-Text
- **Azure OpenAI GPT-4o** - LLM for storytelling
- **Murf AI Matthew** - Text-to-Speech (Narration style)

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type-safe development
- **Framer Motion** - Smooth animations
- **Tailwind CSS** - Styling

### Storage
- **JSON** - Game state and story transcripts

## 📁 Project Structure

```
Day_8/
├── backend/
│   ├── src/
│   │   ├── agent.py              # Main game master agent
│   │   ├── game_state.py         # Game state management
│   │   ├── combat_enforcer.py    # Combat system
│   │   ├── story_controller.py   # Story progression
│   │   └── story_logger.py       # Story transcript saving
│   ├── game_saves/               # Game state saves
│   ├── story_saves/              # Story transcripts (.txt)
│   └── .env.local                # Environment variables
├── frontend/
│   ├── components/
│   │   └── app/
│   │       ├── rpg-welcome-view.tsx    # Universe selection
│   │       ├── rpg-session-view.tsx    # Game UI
│   │       └── view-controller.tsx     # View management
│   ├── public/
│   │   ├── backgrounds/          # Universe backgrounds
│   │   └── music/                # Background music
│   └── styles/
│       └── globals.css           # Global styles
└── README.md                     # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- LiveKit Cloud account
- Azure OpenAI API key
- Murf AI API key
- Deepgram API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd Day_8/backend
```

2. Create `.env.local` file:
```env
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview

MURF_API_KEY=your-murf-key

DEEPGRAM_API_KEY=your-deepgram-key
```

3. Install dependencies:
```bash
uv sync
```

4. Run the agent:
```bash
uv run python src/agent.py dev
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd Day_8/frontend
```

2. Create `.env.local` file:
```env
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

3. Install dependencies:
```bash
pnpm install
```

4. Run the development server:
```bash
pnpm dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## 🎮 How to Play

1. **Choose Your Universe** - Select from 5 unique worlds
2. **Enter Your Name** - Personalize your character
3. **Select Gender** - For proper pronoun usage
4. **Start Adventure** - Begin your voice-controlled journey
5. **Speak Your Actions** - Use natural language to play
6. **Manage Resources** - Track HP, inventory, and stats
7. **Complete the Quest** - Survive 3-4 turns to win
8. **Save Your Story** - Transcripts auto-save to text files

## 🎯 Game Commands

### Voice Commands
- "I attack the monster"
- "Use medkit"
- "Go to the ruins"
- "Talk to the wizard"
- "Check my inventory"
- "Save story"
- "Finish adventure"

### UI Controls
- **Music Toggle** - Turn background music on/off
- **Restart Button** - Start a new adventure
- **Microphone** - Enable/disable voice input

## 📖 Story Transcripts

All adventures are automatically saved to `backend/story_saves/` as readable text files:

Format: `[playername]_[universe]_[timestamp].txt`

Example: `pavan_horror_20251129_153045.txt`

Stories include:
- Full narrative transcript
- Final statistics (HP, stats, inventory)
- Adventure length
- Victory/defeat outcome

## 🎨 Customization

### Adding New Universes

1. Update `game_state.py`:
```python
class Universe(Enum):
    YOUR_UNIVERSE = "your_universe"
```

2. Add initialization in `GameState._initialize_universe()`

3. Add background image to `frontend/public/backgrounds/`

4. Add music to `frontend/public/music/`

### Adjusting Difficulty

Edit `combat_enforcer.py`:
- Damage ranges
- Healing item frequency
- Enemy types

### Changing Story Length

Edit `story_controller.py`:
- Turn limits
- Story progression stages

## 🐛 Troubleshooting

### Backend Issues
- **Agent not starting**: Check `.env.local` credentials
- **Voice not working**: Verify Deepgram/Murf API keys
- **Combat not applying**: Check `combat_enforcer.py` logs

### Frontend Issues
- **UI not updating**: Check browser console for parsing errors
- **Music not playing**: Ensure files exist in `public/music/`
- **Background not loading**: Check `public/backgrounds/` images

### Common Fixes
- Clear browser cache
- Restart both backend and frontend
- Check all API keys are valid
- Ensure LiveKit room is accessible

## 📝 Development Notes

### Key Files
- `agent.py` - Main game logic and function tools
- `game_state.py` - Universe definitions and state management
- `rpg-session-view.tsx` - UI and real-time parsing
- `story_logger.py` - Story transcript generation

### Testing
```bash
# Test story saving
cd backend
python test_story_save.py

# Test combat system
python test_combat.py
```

## 🎯 Future Enhancements

- [ ] Multiplayer support
- [ ] More universes (Western, Steampunk, etc.)
- [ ] Character leveling system
- [ ] Equipment and crafting
- [ ] Boss battles
- [ ] Achievement system
- [ ] Story branching paths
- [ ] Voice emotion detection
- [ ] Custom universe creator

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Murf AI** - Voice Agent Challenge
- **LiveKit** - Real-time voice infrastructure
- **Deepgram** - Speech-to-Text
- **Azure OpenAI** - GPT-4o LLM
- **Next.js** - React framework

## 📧 Contact

Built by Pavan Mali for the Murf AI Voice Agent Challenge

---

**Day 8 of 10 Days of AI Voice Agents** 🚀

#MurfAIVoiceAgentsChallenge #VoiceAgents #RPG #InteractiveStorytelling
