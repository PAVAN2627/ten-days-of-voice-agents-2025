# Day 1: Basic Voice Agent

## Overview
A foundational voice agent built with LiveKit Agents and Murf Falcon TTS. This agent demonstrates the core setup for voice interactions with speech-to-text, language model processing, and text-to-speech capabilities.

## Features
- Real-time voice conversation
- Murf Falcon TTS integration for ultra-fast speech synthesis
- Deepgram STT for speech recognition
- Google Gemini LLM for natural language processing
- LiveKit Turn Detection for conversation flow
- Background noise cancellation

## Quick Start

### Backend Setup
```bash
cd Day_1/backend
uv sync
cp .env.example .env.local
# Configure your API keys in .env.local
uv run python src/agent.py dev
```

### Frontend Setup
```bash
cd Day_1/frontend
pnpm install
cp .env.example .env.local
# Configure LiveKit credentials
pnpm dev
```

### Run LiveKit Server
```bash
livekit-server --dev
```

## Configuration
Required environment variables:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `MURF_API_KEY`
- `GOOGLE_API_KEY`
- `DEEPGRAM_API_KEY`

## Agent Capabilities
- Basic conversational AI
- Voice input/output processing
- Real-time audio streaming
- Session management

## Tech Stack
- **Backend**: Python, LiveKit Agents, Murf TTS
- **Frontend**: React, Next.js, LiveKit React SDK
- **AI Services**: Google Gemini, Deepgram, Murf Falcon

## Next Steps
This basic agent serves as the foundation for more specialized agents in subsequent days.