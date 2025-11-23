# Day 3: Wellness Companion Agent

## Overview
A supportive daily wellness companion that conducts check-ins to track mood, energy, stress levels, and personal goals. The agent provides personalized, contextual advice and maintains a wellness history.

## Features
- Daily wellness check-ins
- Mood and energy tracking
- Stress level monitoring
- Goal setting and tracking
- Personalized advice generation
- Wellness history persistence
- Contextual emotional support

## Wellness Metrics Tracked
- **Mood**: User's current emotional state (free text)
- **Energy**: Low/medium/high or descriptive text
- **Stress**: Stress levels and sources
- **Goals**: 1-3 small daily goals

## Agent Capabilities
- Warm, supportive conversation style
- One-question-at-a-time approach
- Context-aware advice generation
- Previous check-in recall and comparison
- Emotional validation and encouragement

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
# Configure API keys
uv run python src/agent.py dev
```

### Frontend Setup
```bash
cd Day_3/frontend
pnpm install
cp .env.example .env.local
pnpm dev
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

## Example Check-in Flow
1. Agent: "Hi! How are you feeling right now?"
2. User: "I'm feeling a bit stressed today"
3. Agent: "What's your energy level like?"
4. User: "Pretty low, I'm tired"
5. Agent: "What's causing the stress?"
6. User: "Work deadlines"
7. Agent: "Any small goals for today?"
8. User: "Just finish one project task"
9. Agent: *Provides personalized advice and saves check-in*

## Wellness Entry Structure
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "mood": "stressed",
  "energy": "low",
  "stress": "work deadlines",
  "goals": ["finish one project task"],
  "summary": "Mood: stressed. Energy: low. Stress: work deadlines. Goals: finish one project task."
}
```

## Advice Generation
The agent generates original, contextual advice based on:
- Current mood and energy levels
- Stress factors
- Personal goals
- Historical patterns
- Emotional support principles

## Tech Stack
- **Backend**: Python, LiveKit Agents, JSON persistence
- **Frontend**: React, Next.js, Wellness Dashboard UI
- **AI Services**: Google Gemini, Deepgram, Murf Falcon (Tanushree voice)
- **UI Components**: Phosphor Icons, Motion animations