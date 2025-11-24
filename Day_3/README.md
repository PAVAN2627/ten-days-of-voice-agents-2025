# Day 3: Wellness Companion Agent

## Overview
A supportive daily wellness companion that conducts personalized check-ins to track mood, energy, stress levels, and personal goals. The agent provides contextual advice based on user input and maintains a complete wellness history with previous session recall.

## Features
- Interactive daily wellness check-ins
- Comprehensive mood and energy tracking
- Stress level assessment and monitoring
- Personal goal setting (1-3 daily goals)
- **Automatic Todoist task creation** from wellness goals
- Dynamic, contextual advice generation
- Persistent wellness history with JSON storage
- Previous check-in recall and comparison
- Warm, emotionally supportive conversation style
- Female voice (Tanushree) for comforting interaction

## Wellness Metrics Tracked
- **Mood**: User's current emotional state (free text)
- **Energy**: Low/medium/high or descriptive text
- **Stress**: Stress levels and sources
- **Goals**: 1-3 small daily goals

## Agent Capabilities
- **Conversational Flow**: One-question-at-a-time approach for natural interaction
- **Memory**: Recalls and references previous wellness check-ins
- **Personalization**: Generates unique, contextual advice (not templated responses)
- **Emotional Intelligence**: Provides validation, encouragement, and support
- **Adaptive Responses**: Adjusts advice based on mood, energy, and stress combinations
- **Goal Guidance**: Helps break down goals into manageable micro-steps

## Function Tools
- `set_mood()` - Records current mood
- `set_energy()` - Captures energy level
- `set_stress()` - Documents stress status
- `set_goals()` - Sets daily goals (1-3 items)
- `complete_checkin()` - Saves entry and provides advice

## Quick Start

### Backend Setup
```bash
cd Day_3/backend
uv sync
cp .env.example .env.local
# Configure API keys in .env.local:
# LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# MURF_API_KEY, GOOGLE_API_KEY, DEEPGRAM_API_KEY
# TODOIST_API_TOKEN (for automatic task creation)
# TODOIST_PROJECT_ID (optional - numeric project ID)
uv run python src/agent.py dev
```

### Frontend Setup
```bash
cd Day_3/frontend
pnpm install
cp .env.example .env.local
# Configure LiveKit credentials
pnpm dev
```

### Run LiveKit Server
```bash
livekit-server --dev
```

## Wellness Dashboard
The frontend includes a wellness dashboard showing:
- Heart rate monitoring
- Activity tracking (steps)
- Nutrition progress
- Sleep tracking

## Data Persistence
- Wellness entries saved to `backend/wellness_logs/wellness_log.json`
- Historical data enables progress tracking
- Previous check-ins inform current conversations
- **Automatic Todoist integration**: Creates parent task for each check-in with child tasks for each goal

## Example Check-in Flow

### First-time User:
1. Agent: "Hi! It's nice to meet you — I do a short daily check-in. How are you feeling right now?"
2. User: "I'm feeling okay, just a bit tired"
3. Agent: "What's your energy level like?"
4. User: "Medium energy"
5. Agent: "Any stress you're dealing with?"
6. User: "No stress today"
7. Agent: "What are 1-3 small goals for today?"
8. User: "Finish my pending college tasks"
9. Agent: *Provides personalized advice and saves check-in*

### Returning User:
1. Agent: "Hi — welcome back. I see your last check-in: Mood: okay. Energy: medium. Stress: No stress reported. Goals: finish my pending college tasks. Now tell me how are you feeling right now?"
2. User: "Very low today"
3. Agent: *Continues with energy, stress, and goals questions*

## Wellness Entry Structure
```json
{
  "timestamp": "2025-11-24T12:14:49.137793Z",
  "mood": "okay",
  "energy": "medium",
  "stress": "No stress reported",
  "goals": ["finish my pending college tasks"],
  "summary": "Mood: okay. Energy: medium. Stress: No stress reported. Goals: finish my pending college tasks."
}
```

## Advice Generation
The agent uses a sophisticated advice generation system that creates original, contextual guidance based on:

### Input Factors:
- **Mood Analysis**: Detects low mood keywords (sad, down, tired) vs positive indicators
- **Energy Assessment**: Adapts recommendations for low, medium, or high energy states
- **Stress Evaluation**: Provides grounding techniques for stressed users
- **Goal Integration**: Helps break goals into 15-30 minute micro-steps
- **Historical Context**: References previous check-ins for continuity

### Advice Principles:
- **Gentleness**: Emphasizes self-kindness and small steps
- **Practicality**: Suggests actionable, time-bound activities
- **Emotional Support**: Validates feelings and encourages progress
- **Personalization**: Tailors advice to specific mood/energy combinations
- **Non-medical**: Focuses on wellness support, not medical advice

## Todoist Integration

### Automatic Task Creation
When you complete a wellness check-in, the agent automatically:
1. **Creates a parent task** with your check-in summary
2. **Creates child tasks** for each of your goals
3. **Organizes tasks** in your specified Todoist project (or default)

### Setup Todoist Integration
1. Get your Todoist API token from [Todoist App Console](https://todoist.com/app/settings/integrations)
2. Add to `.env.local`:
   ```
   TODOIST_API_TOKEN=your_api_token_here
   TODOIST_PROJECT_ID=your_project_id_here
   ```
3. The agent will automatically sync your wellness goals to Todoist

### Example Todoist Output
```
📋 Parent Task: "Wellness check-in (2025-11-24 12:14:49) — Mood: okay. Energy: medium. Stress: No stress reported. Goals: finish my pending college tasks."
  └── 🎯 Child Task: "Goal: finish my pending college tasks"
  └── 🎯 Child Task: "Goal: relax and listen to music"
```

## Tech Stack
- **Backend**: Python, LiveKit Agents, JSON persistence, Todoist API
- **Frontend**: React, Next.js, Wellness Dashboard UI
- **AI Services**: Google Gemini, Deepgram, Murf Falcon (Tanushree voice)
- **Integrations**: Todoist REST API v2
- **UI Components**: Phosphor Icons, Motion animations