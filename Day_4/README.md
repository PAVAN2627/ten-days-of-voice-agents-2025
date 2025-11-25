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

## 📚 Programming Concepts Covered (EXPANDED)

**Beginner Level:**
1. **Variables** - Data storage and reuse
2. **Conditions** - Decision-making with if/elif/else

**Intermediate Level:**
3. **Loops** - Repetitive execution (for/while loops)
4. **Functions** - Reusable code blocks and organization
5. **Lists** - Collections and data structures
6. **Dictionaries** - Key-value pair storage

**Advanced Level:**
7. **Classes** - Object-oriented programming
8. **Error Handling** - Exception management

## 🚀 Advanced Features (IMPLEMENTED)

### 1. Richer Concept Mastery Model ✅
- **Enhanced Tracking**: `times_explained`, `times_quizzed`, `times_taught_back`
- **Performance Metrics**: `last_score`, `avg_score` with running averages
- **Dual Storage**: JSON files + optional SQLite database
- **Persistent Analytics**: Complete learning history preservation

### 2. Advanced Teach-Back Evaluator ✅
- **Multi-Component Scoring**:
  - Coverage: How much reference content is covered (40%)
  - Precision: Accuracy without irrelevant information (30%)
  - Key Terms: Correct programming terminology usage (30%)
- **Intelligent Feedback**: Detailed suggestions with missing key terms
- **Adaptive Scoring**: Performance-based feedback levels

### 3. Weakness Analysis & Learning Paths ✅
- **`get_weakness_analysis()`**: Identifies weakest concepts with recommendations
- **`get_learning_path()`**: Personalized study plans based on mastery
- **`get_mastery_report()`**: Visual progress tracking with status indicators
- **Smart Recommendations**: Next steps based on performance data

### 4. Database Integration ✅
- **SQLite Backend**: Advanced analytics and session logging
- **Multi-User Support**: Ready for user_id expansion
- **Automatic Fallback**: JSON storage if database unavailable
- **Session Tracking**: Detailed learning session history

### 5. Dynamic Voice Switching ✅
- **Mode-Based Voices**: Matthew (Learn), Anusha (Quiz), Ken (Teach-back)
- **Real-Time Switching**: Instant voice changes with `set_mode()`
- **Session Integration**: Direct TTS replacement without restart
- **Personality Adaptation**: Voice matches learning mode context

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
- `get_weakness_analysis()` - Identify struggling concepts
- `get_learning_path()` - Personalized study recommendations

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

## 📊 Advanced Learning Analytics

### Comprehensive Mastery Tracking
```json
{
  "mastery": {
    "variables": {
      "times_explained": 2,
      "times_quizzed": 5, 
      "times_taught_back": 3,
      "last_score": 85,
      "avg_score": 78.5
    },
    "classes": {
      "times_explained": 0,
      "times_quizzed": 1,
      "times_taught_back": 2, 
      "last_score": 31,
      "avg_score": 31.8
    }
  }
}
```

### Advanced Analytics Features
- **Weakness Analysis**: Identifies struggling concepts
- **Learning Paths**: Personalized study recommendations
- **Progress Visualization**: 🟢🟡🔴 status indicators
- **Performance Trends**: Running averages and improvement tracking
- **Database Logging**: Optional SQLite for detailed session history

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

### Running the Advanced Agent
```bash
cd Day_4/backend
uv sync
uv run python src/agent.py dev
```

### Data Storage Locations
- **JSON Storage**: `backend/tutor_state/tutor_state.json`
- **SQLite Database**: `backend/tutor_database.db` (optional)
- **Content**: `backend/shared-data/day4_tutor_content.json`

### Advanced Features Demo
```bash
python Day_4/advanced_features_demo.py
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

## ✅ Advanced Features Completed

- [x] **Richer Mastery Model**: Complete tracking with database support
- [x] **Advanced Teach-Back Evaluator**: Multi-component scoring system
- [x] **Weakness Analysis**: Smart recommendations and learning paths
- [x] **Expanded Content**: 8 concepts with level-based progression
- [x] **Database Integration**: SQLite with session logging
- [x] **Dynamic Voice Switching**: Real-time personality changes
- [x] **Visual Analytics**: Progress indicators and status reports
- [x] **Adaptive Coaching**: Performance-based recommendations

## 🔮 Future Enhancements

- [ ] Multi-user support with individual profiles
- [ ] Visual code examples and interactive coding
- [ ] Advanced spaced repetition algorithms
- [ ] Collaborative learning sessions
- [ ] Web-based analytics dashboard

## 📝 Advanced Usage Examples

### Analytics-Driven Interaction
```
Agent: "Hello! I'm your Tech Tutor. Which programming concept would you like to start with?"
User: "What should I focus on?"
Agent: [Calls get_weakness_analysis()]
       "🎯 WEAKNESS ANALYSIS:
        📉 Focus on these concepts:
        1. classes: 31% avg (3 attempts)
        💡 RECOMMENDATION: Focus on 'classes' - try teach-back mode!"
```

### Advanced Mode Switching with Voice Changes
```
User: "Switch to quiz mode"
Agent: [Voice changes to Anusha] "Hey there! I'm Anusha, ready for questions?"
User: "Switch to teach back mode" 
Agent: [Voice changes to Ken] "Hello! I'm Ken. Please explain the concept in your own words."
```

### Advanced Analytics Commands
```
User: "Show my progress"
Agent: "📊 MASTERY REPORT:
       variables: 🟢 Strong (avg: 86%, attempts: 8)
       classes: 🔴 Needs Work (avg: 31%, attempts: 3)"

User: "Give me a learning path"
Agent: "🛤️ PERSONALIZED LEARNING PATH:
       1. Variables: ✅ Mastered
       2. Conditions: 🔄 Review Needed
       3. Loops: ⭐ Not Started"
```

### Advanced Teach-Back Scoring
```
User: [Explains concept]
Agent: "Outstanding! You demonstrated deep understanding with precise terminology.
       Coverage: 85%, Precision: 92%
       Try mentioning: loop, iteration, condition"
```

## 🏆 Advanced Learning Outcomes

Students using this advanced tutor will:
- **Master 8 Programming Concepts**: From variables to classes with level progression
- **Develop Metacognitive Awareness**: Through detailed progress analytics
- **Experience Adaptive Learning**: Personalized paths based on weakness analysis
- **Receive Multi-Modal Feedback**: Voice personalities + detailed scoring
- **Track Long-Term Progress**: Persistent mastery data with trends
- **Build Confidence**: Through targeted recommendations and achievements
- **Learn Efficiently**: Focus on weakest areas with smart suggestions

---

## 🎯 Advanced Challenge Completion

**All Advanced Features Successfully Implemented:**
1. ✅ **Richer Concept Mastery Model** - Complete tracking with database
2. ✅ **Advanced Teach-Back Evaluator** - Multi-component scoring
3. ✅ **Weakness Analysis & Learning Paths** - Smart recommendations
4. ✅ **Expanded Content & Flows** - 8 concepts with level progression
5. ✅ **Database Integration** - SQLite with session logging
6. ✅ **Dynamic Voice Switching** - Real-time personality changes

**Built for the AI Voice Agents Challenge by murf.ai**

*Leveraging Murf Falcon TTS, LiveKit Agents, Google Gemini, and SQLite for advanced voice-powered education with comprehensive analytics.*