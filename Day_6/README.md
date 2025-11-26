# Day 6 — Fraud Alert Voice Agent

A LiveKit-based voice agent that calls customers about suspicious transactions, performs two-step verification, and records outcomes in a SQLite database.

## Features

- **Phone Integration**: LiveKit telephony with real phone number
- **Voice Stack**: Deepgram (STT) → Google Gemini (LLM) → Murf (TTS)
- **Database**: SQLite for fraud case management
- **Two-Step Verification**: Card verification + security questions
- **Real-time Updates**: Automatic database updates after each call

## Quick Start

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd Day_6/backend
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API keys
   ```

3. **Start the agent:**
   ```bash
   uv run python src/agent.py dev
   ```

### Frontend Setup (Optional)

1. **Install dependencies:**
   ```bash
   cd Day_6/frontend
   pnpm install
   ```

2. **Start the UI:**
   ```bash
   pnpm dev
   ```

## Phone Testing

Call the configured LiveKit phone number. The agent will:

1. Greet the customer about a suspicious transaction
2. Ask for the last 4 digits of their card
3. Ask their security question
4. Mark the transaction as `confirmed_safe` or `confirmed_fraud`
5. Save the result to the SQLite database

## Database Management

**Check database:**
```bash
cd Day_6/backend/src
python verify_db.py
```

**Database location:** `Day_6/backend/src/fraud_cases.db`

## Configuration

Key environment variables in `.env.local`:

```bash
# LiveKit Configuration
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# API Keys
GOOGLE_API_KEY=your_gemini_key
DEEPGRAM_API_KEY=your_deepgram_key
MURF_API_KEY=your_murf_key
```

## Project Structure

```
Day_6/
├── backend/
│   ├── src/
│   │   ├── agent.py          # Main voice agent
│   │   ├── database.py       # SQLite operations
│   │   ├── fraud_cases.db    # SQLite database
│   │   └── verify_db.py      # Database verification
│   └── README.md
├── frontend/
│   ├── app/
│   ├── components/
│   └── README.md
└── README.md                 # This file
```

## How It Works

1. **Incoming Call** → LiveKit phone number
2. **Agent Activation** → Voice agent starts conversation
3. **Identity Verification** → Card + security question
4. **Decision Making** → AI determines fraud/safe
5. **Database Update** → Result saved to SQLite
6. **Call Completion** → Customer informed of outcome

## Development

- **Agent logs** show STT/LLM/TTS metrics
- **Database updates** happen in real-time
- **Frontend UI** provides visual interface for testing
- **SQLite browser** can be used to inspect data

## Production Ready

This setup includes:
- ✅ Production-grade phone integration
- ✅ Secure database storage
- ✅ Real-time fraud detection
- ✅ Scalable architecture
- ✅ Comprehensive logging