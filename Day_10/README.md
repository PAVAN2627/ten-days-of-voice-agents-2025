# Day 10: Improv Battle - Voice Game Show 🎭🎤

A voice-first improv game show where players perform improvisation scenarios and receive real-time feedback from an AI host. Experience the future of interactive entertainment with natural voice conversations, dynamic scenarios, and intelligent feedback.

## 🎮 What is Improv Battle?

Improv Battle is an interactive voice game show that challenges players to improvise in character based on fun scenarios. The AI host guides you through 3 rounds, provides encouraging feedback, and celebrates your creativity. It's like having a personal improv coach available 24/7!

## ✨ Key Features

### 🎭 **Interactive Voice Gameplay**
- Natural conversation with AI host using Murf AI's Anusha voice (Indian English)
- Real-time speech recognition with Deepgram Nova-3
- Intelligent turn detection for smooth conversations
- Background music that adapts to game state

### 🎯 **3-Round Game Format**
- **Round 1-3**: Unique improv scenarios with Indian cultural context
- Real-time feedback after each performance
- Progress tracking (0/3 → 1/3 → 2/3 → 3/3)
- Personalized closing summary

### 🎨 **Modern UI/UX**
- Beautiful gradient backgrounds with animated effects
- Real-time transcript display with timestamps
- Live game status and round progress indicators
- Smooth animations with Framer Motion
- Responsive design for all screen sizes

### 📊 **Game State Management**
- Track player name and current round
- Monitor game phase (intro, awaiting_improv, reacting, done)
- Real-time score updates
- Complete game history

### 💾 **Game Saves**
- Save complete game transcripts
- Timestamped recordings
- Player statistics and round details
- Easy retrieval and replay

### 🎵 **Audio Experience**
- Welcome screen music
- Background game music (low volume)
- Music toggle controls
- Microphone on/off controls

## � Advvanced Features Implemented

### 🏗️ **Robust Architecture**
✔ **Function Tools** – 5 specialized tools for game management  
✔ **State Management** – Centralized game state with phase tracking  
✔ **Error Handling** – Graceful handling of edge cases  
✔ **Content Filtering** – Azure-safe prompts and scenarios  

### 🎤 **Voice Intelligence**
✔ **Natural Conversations** – Context-aware responses  
✔ **Turn Detection** – Multilingual model for smooth interactions  
✔ **Voice Activity Detection** – Silero VAD for accurate speech detection  
✔ **Noise Cancellation** – BVC for clear audio  

### 🎨 **UI Components**
✔ **Message Logger** – Real-time transcript capture  
✔ **Chat Overlay** – Live conversation display  
✔ **Debug Panel** – Development tools  
✔ **Progress Indicators** – Visual round tracking  

### 📝 **Improv Scenarios**
1. Auto-rickshaw driver explaining scenic routes
2. Street food vendor describing famous golgappa recipe
3. Customer service agent helping with large orders
4. Wedding planner sharing memorable entrance stories
5. Chai vendor explaining why chai is special

## �️ vTech Stack

**Voice & AI:**
- **LiveKit** - Real-time voice communication platform
- **Deepgram Nova-3** - Advanced speech-to-text
- **Azure OpenAI GPT-4** - Intelligent conversation engine
- **Murf AI Anusha** - Natural Indian English text-to-speech
- **Silero VAD** - Voice activity detection
- **Multilingual Turn Detector** - Conversation flow management

**Frontend:**
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **LiveKit Components React** - Pre-built voice UI components

**Backend:**
- **Python 3.11+** - Core backend language
- **LiveKit Agents SDK** - Voice agent framework
- **Pydantic** - Data validation
- **python-dotenv** - Environment management

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- LiveKit server (local or cloud)
- API keys for Deepgram, Azure OpenAI, and Murf AI

### Backend Setup

```bash
cd Day_10/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your API keys
```

### Frontend Setup

```bash
cd Day_10/frontend

# Install dependencies
npm install

# The frontend uses the backend's LiveKit connection
```

## ⚙️ Configuration

Create `backend/.env.local` with:

```env
# LiveKit Configuration
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# API Keys
DEEPGRAM_API_KEY=your_deepgram_key
MURF_API_KEY=your_murf_key

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

## 🚀 Running the Application

### Start LiveKit Server (if running locally)

```bash
livekit-server --dev
```

### Start Backend Agent

```bash
cd Day_10/backend
python src/agent.py dev
```

### Start Frontend

```bash
cd Day_10/frontend
npm run dev
```

### Access the Application

Open your browser to `http://localhost:3000`

## 🎮 How to Play

1. **Enter Your Name** - Type your stage name on the welcome screen
2. **Start the Game** - Click "Start Improv Battle"
3. **Listen to Scenario** - The host will present your first scenario
4. **Improvise** - Speak your improvisation in character
5. **Receive Feedback** - Get encouraging feedback from the host
6. **Continue** - Complete all 3 rounds
7. **Get Summary** - Receive personalized closing thoughts
8. **Save Game** - Click save to keep your transcript

## 🎯 Game Flow

```
Welcome Screen (0/3)
    ↓
Player Enters Name
    ↓
Game Starts - Round 1 Scenario
    ↓
Player Improvises
    ↓
Host Feedback - "Round 1 complete!" (1/3)
    ↓
Round 2 Scenario
    ↓
Player Improvises
    ↓
Host Feedback - "Round 2 complete!" (2/3)
    ↓
Round 3 Scenario
    ↓
Player Improvises
    ↓
Host Feedback - "Round 3 complete!" (3/3)
    ↓
Closing Summary
    ↓
Game Complete - Save Option
```

## 📁 Project Structure

```
Day_10/
├── backend/
│   ├── src/
│   │   └── agent.py          # Main agent with game logic
│   ├── game_saves/            # Saved game transcripts
│   ├── .env.local             # Environment configuration
│   └── pyproject.toml         # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main page
│   │   └── api/               # API routes
│   ├── components/
│   │   ├── improv-battle.tsx  # Main game component
│   │   ├── message-logger.tsx # Transcript capture
│   │   ├── chat-overlay.tsx   # Live chat display
│   │   └── debug-panel.tsx    # Debug tools
│   ├── public/
│   │   └── music/             # Background music files
│   └── package.json           # Node dependencies
└── README.md                  # This file
```

## 🎨 UI Features

- **Welcome Screen**: Animated gradient background with game instructions
- **Game Screen**: 3-panel layout with video, controls, and game info
- **Progress Bar**: Visual round completion indicator
- **Status Badge**: Current game phase display
- **Transcript Panel**: Scrollable game rules and tips
- **Control Buttons**: Mic, music, restart, and save controls

## 🔧 Customization

### Add New Scenarios

Edit `backend/src/agent.py`:

```python
self.improv_scenarios = [
    "Your new scenario here...",
    # Add more scenarios
]
```

### Change Voice

Edit `backend/src/agent.py`:

```python
tts=murf.TTS(
    voice="en-IN-anusha",  # Change to any Murf voice
    style="Conversation",
)
```

### Adjust Round Count

Edit `backend/src/agent.py`:

```python
self.max_rounds: int = 3  # Change to desired number
```

## 🐛 Troubleshooting

### Azure Content Filter Issues
If you see "jailbreak detected" errors:
- Ensure instructions don't use strong command words (MUST, CRITICAL)
- Keep scenarios neutral and positive
- Avoid confrontational language

### Voice Not Working
- Check microphone permissions in browser
- Verify LiveKit server is running
- Check API keys in .env.local

### Score Not Updating
- Ensure agent says "Round X complete!" after each round
- Check browser console for transcript messages
- Verify frontend is detecting completion markers

## 📊 Metrics & Analytics

The agent tracks:
- STT metrics (audio duration, model performance)
- LLM metrics (token usage, response time)
- TTS metrics (synthesis time, audio quality)
- End-of-utterance detection timing

## 🎓 Learning Outcomes

This project demonstrates:
- Building voice-first applications
- Real-time state synchronization
- Natural conversation design
- Error handling in voice apps
- UI/UX for voice interfaces
- Game state management
- Audio integration
- Content filtering compliance

## 🚀 Future Enhancements

- [ ] Multiplayer mode
- [ ] Leaderboards
- [ ] More scenario categories
- [ ] Video recording
- [ ] Social sharing
- [ ] Custom scenarios
- [ ] Difficulty levels
- [ ] Achievement system

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built as part of the **Murf AI Voice Agent Challenge**

- **Murf AI** - Natural text-to-speech
- **LiveKit** - Real-time voice platform
- **Deepgram** - Speech recognition
- **Azure OpenAI** - Language model

---

**Day 10/10 Complete!** 🎉

Built with ❤️ for the Murf AI Voice Agent Challenge
