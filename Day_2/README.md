# Day 2: Coffee Shop Barista Agent

## Overview
An AI barista agent for "Brew & Bean Cafe" that takes coffee orders through voice interaction. The agent collects order details, validates completeness, and saves orders to JSON files.

## Features
- Interactive coffee ordering system
- Order state management with validation
- Function tools for structured data collection
- JSON order persistence
- Real-time order tracking and logging

## Agent Capabilities
The barista agent can handle:
- **Drink Types**: latte, cappuccino, americano, espresso, mocha, coffee
- **Sizes**: small, medium, large
- **Milk Options**: whole, skim, almond, oat
- **Extras**: sugar, whipped cream, caramel, extra shot
- **Customer Names**: for order personalization

## Function Tools
- `set_drink_type()` - Records coffee selection
- `set_size()` - Sets drink size
- `set_milk()` - Specifies milk preference
- `set_extras()` - Adds optional extras
- `set_name()` - Captures customer name
- `complete_order()` - Finalizes and saves order

## Quick Start

### Backend Setup
```bash
cd Day_2/backend
uv sync
cp .env.example .env.local
# Configure API keys
uv run python src/agent.py dev
```

### Frontend Setup
```bash
cd Day_2/frontend
pnpm install
cp .env.example .env.local
pnpm dev
```

## Order Management
- Orders are saved to `backend/orders/` directory
- Each order gets a timestamped JSON file
- Order validation ensures all required fields are collected
- Real-time logging shows order progress

## Example Order Flow
1. Customer: "I'd like a coffee"
2. Agent: "What type of coffee would you like?"
3. Customer: "A large latte with oat milk"
4. Agent: "Any extras like sugar or whipped cream?"
5. Customer: "Extra shot please, and my name is John"
6. Agent: "Perfect! Your large latte with oat milk and extra shot is ready, John!"

## Order Data Structure
```json
{
  "drinkType": "latte",
  "size": "large", 
  "milk": "oat",
  "extras": ["extra shot"],
  "name": "John"
}
```

## Tech Stack
- **Backend**: Python, LiveKit Agents, Function Tools
- **Frontend**: React, Next.js, LiveKit React SDK
- **Storage**: JSON file system
- **AI Services**: Google Gemini, Deepgram, Murf Falcon