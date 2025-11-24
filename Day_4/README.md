# Day 4 - Active Recall Tech Tutor 🎓

An intelligent voice-powered tutoring agent that teaches programming concepts through **Active Recall** methodology using three distinct learning modes.

## 🎯 Overview

The Active Recall Tutor helps students master programming fundamentals through scientifically-proven active learning techniques:

- **Learn Mode**: Clear explanations of concepts
- **Quiz Mode**: Interactive multiple-choice questions  
- **Teach-Back Mode**: Students explain concepts for feedback

## 🎤 Voice Personalities

The agent uses different Murf Falcon voices for each mode to create distinct learning experiences:

- **Learn Mode**: Matthew (warm, explanatory tone)
- **Quiz Mode**: Anusha (engaging, questioning tone)  
- **Teach-Back Mode**: Ken (encouraging, feedback-focused tone)

## 📚 Programming Concepts Covered

1. **Variables** - Data storage and reuse
2. **Loops** - Repetitive execution (for/while loops)
3. **Functions** - Reusable code blocks and organization
4. **Conditions** - Decision-making with if/elif/else

## 🚀 Key Features

### Dynamic Voice Switching
- Automatic voice changes based on learning mode
- Real-time TTS voice swapping using custom `DynamicMurfTTS` wrapper
- Seamless transitions between different teaching personalities

### Intelligent Content Management
- JSON-based content storage (`day4_tutor_content.json`)
- Persistent learning progress tracking (`tutor_state.json`)
- Mastery scoring and analytics

### Advanced Interaction Handling
- Early message interception for quick responses
- Multiple event handlers for different user inputs
- Smart concept selection and mode switching

### Active Recall Implementation
- **Spaced Repetition**: Tracks learning attempts per concept
- **Retrieval Practice**: Quiz mode with immediate feedback
- **Elaborative Interrogation**: Teach-back mode with scoring

## 🛠 Technical Architecture

### Core Components

```python
# Dynamic TTS with voice switching
class DynamicMurfTTS:
    def switch_voice(self, new_voice: str)
    async def synthesize(self, text: str)

# Main tutor agent with mode handling
class TutorAgent(Agent):
    async def on_message(self, message)
    async def _switch_voice(self, mode: str)
```

### Function Tools

- `list_concepts()` - Display available programming topics
- `set_concept(concept_id)` - Select learning topic
- `set_mode(mode)` - Switch between learn/quiz/teach_back
- `explain_concept()` - Provide detailed explanations
- `get_mcq()` - Generate quiz questions
- `evaluate_mcq(answer)` - Score quiz responses
- `evaluate_teachback(explanation)` - Score student explanations
- `get_mastery_report()` - Show learning progress

### Event Handlers

```python
@session.on("tool_called")
def _tool_called_handler(ev):
    # Automatic voice switching on mode change

@session.on("received_text") 
async def _text_received_handler(ev):
    # Quick responses for common commands

@session.on("user_speech_committed")
async def _user_speech_handler(message):
    # Early interception of list requests
```

## 📊 Learning Analytics

The system tracks comprehensive mastery metrics:

```json
{
  "mastery": {
    "variables": {
      "times_explained": 2,
      "times_quizzed": 5,
      "times_taught_back": 3,
      "last_score": 85,
      "avg_score": 78.5
    }
  }
}
```

## 🎮 User Interaction Flow

### 1. Concept Selection
```
User: "List concepts" or "Show me topics"
Agent: Lists all available programming concepts
User: "Set concept variables" or "I want to learn about loops"
Agent: Confirms concept selection
```

### 2. Mode Selection
```
User: "Switch to learn mode" or "I want to take a quiz"
Agent: Changes voice and activates selected mode
```

### 3. Learning Modes

**Learn Mode (Matthew)**:
- Provides clear, structured explanations
- Uses conversational tone
- Focuses on understanding core concepts

**Quiz Mode (Anusha)**:
- Presents multiple-choice questions
- Evaluates answers with immediate feedback
- Tracks quiz performance

**Teach-Back Mode (Ken)**:
- Prompts student to explain concepts
- Scores explanations using word overlap analysis
- Provides constructive feedback

## 🔧 Setup & Configuration

### Prerequisites
- Python 3.9+ with uv package manager
- LiveKit server and credentials
- API keys: Murf, Google (Gemini), Deepgram

### Environment Variables
```bash
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
MURF_API_KEY=your_murf_key
GOOGLE_API_KEY=your_google_key
DEEPGRAM_API_KEY=your_deepgram_key
```

### Running the Agent
```bash
cd Day_4/backend
uv sync
uv run python src/agent.py dev
```

## 🧪 Testing

The agent includes comprehensive test coverage:

```bash
cd Day_4/backend
uv run pytest tests/
```

## 🎯 Educational Methodology

### Active Recall Principles
1. **Retrieval Practice**: Students actively recall information rather than passive review
2. **Spaced Repetition**: Concepts revisited at increasing intervals
3. **Elaborative Interrogation**: Students explain "why" and "how" concepts work
4. **Interleaving**: Mixed practice across different programming concepts

### Adaptive Learning
- Progress tracking per concept
- Difficulty adjustment based on performance
- Personalized feedback and recommendations

## 🚀 Advanced Features

### Smart Message Interception
- Early detection of list requests before LLM processing
- Immediate responses for common commands
- Reduced latency for frequent interactions

### Voice Personality Mapping
- Context-aware voice selection
- Emotional tone matching to learning mode
- Consistent personality traits per mode

### Robust Error Handling
- Graceful fallbacks for voice switching failures
- Content loading error recovery
- State persistence across sessions

## 📈 Performance Optimizations

- **Prewarm VAD**: Voice Activity Detection loaded at startup
- **Dynamic TTS**: Runtime voice switching without session restart
- **Event-driven Architecture**: Efficient message handling
- **Persistent State**: Fast session recovery

## 🔮 Future Enhancements

- [ ] Adaptive difficulty based on mastery scores
- [ ] Multi-language programming concept support
- [ ] Visual code examples integration
- [ ] Collaborative learning sessions
- [ ] Advanced analytics dashboard

## 📝 Usage Examples

### Basic Interaction
```
Agent: "Hello! I'm your Tech Tutor. Which programming concept would you like to start with?"
User: "List concepts"
Agent: "Here are the concepts: Variables, Loops, Functions, Conditions"
User: "Set concept variables"
Agent: "Concept set to: Variables. Would you like to learn, take a quiz, or teach-back?"
User: "Learn mode"
Agent: [Matthew voice] "Variables store values so you can reuse them later..."
```

### Mode Switching
```
User: "Switch to quiz mode"
Agent: [Anusha voice] "Switched to quiz mode. Here's a question: What best describes a variable?"
User: "A label used to store data"
Agent: "Correct — well done!"
```

## 🏆 Learning Outcomes

Students using this tutor will:
- Master fundamental programming concepts through active practice
- Develop metacognitive awareness of their learning progress
- Experience personalized, adaptive instruction
- Build confidence through immediate feedback and encouragement

---

**Built for the AI Voice Agents Challenge by murf.ai**

*Leveraging Murf Falcon TTS, LiveKit Agents, and Google Gemini for next-generation voice-powered education.*