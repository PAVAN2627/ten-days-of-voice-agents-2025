# Game UI Implementation Guide

## Overview
The Day 8 Game Master frontend has been completely redesigned with a professional gaming UI featuring:
- **Left Panel**: Character stats, HP bar, inventory, quests, world info
- **Center Panel**: Story narrative with GM messages and player responses
- **Right Panel**: Quick actions and recent events
- **Real-time Game State**: All HP, stats, and game progress displayed

## Files Created

### 1. `components/app/game-state.tsx`
**Component**: `GameStateDisplay`
**Purpose**: Displays complete game state information in tabbed interface
**Size**: ~250 lines

**Features:**
- Universe-specific color theming
- Real-time HP bar with status colors
- Tabbed interface (Character, Inventory, Quests, World)
- NPC encounter display
- Location information
- Quest tracking

**Props:**
```typescript
interface GameStateDisplayProps {
  gameState?: GameStateData;
  selectedTab?: 'character' | 'inventory' | 'quests' | 'world';
  onTabChange?: (tab: ...) => void;
}
```

### 2. `components/app/game-view.tsx`
**Component**: `GameView`
**Purpose**: Main game interface with 3-column layout
**Size**: ~350 lines

**Features:**
- Full game layout (left, center, right panels)
- Story message display with animation
- Voice/text input handling
- Loading and listening indicators
- Quick action buttons
- Recent events sidebar

**Props:**
```typescript
interface GameViewProps {
  messages: Message[];
  gameState?: any;
  isListening?: boolean;
  isLoading?: boolean;
  onSendMessage?: (message: string) => void;
}
```

### 3. `styles/globals.css`
**Added**: Game UI animations
**Animations**:
- `animate-fade-in`: Message entry animation
- `delay-100`, `delay-200`: Staggered animations
- Keyframes for smooth transitions

### 4. `GAME_UI_GUIDE.md`
**Purpose**: Complete UI reference and design specification

## Integration Steps

### Step 1: Update the App Component
Modify `components/app/app.tsx` to use GameView:

```tsx
import { GameView } from './game-view';
import { useState, useEffect } from 'react';

export function App() {
  const [messages, setMessages] = useState([]);
  const [gameState, setGameState] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Handle game state updates from WebSocket/API
  const handleGameStateUpdate = (newState) => {
    setGameState(newState);
  };

  // Handle new messages
  const handleSendMessage = (message) => {
    // Add user message
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }]);

    // Send to agent and wait for response
    // ...
  };

  return (
    <GameView
      messages={messages}
      gameState={gameState}
      isListening={isListening}
      isLoading={isLoading}
      onSendMessage={handleSendMessage}
    />
  );
}
```

### Step 2: Connect to Backend API
Create an API hook to fetch game state:

```typescript
// hooks/useGameState.ts
import { useEffect, useState } from 'react';

export function useGameState(roomId: string) {
  const [gameState, setGameState] = useState(null);

  useEffect(() => {
    const pollGameState = async () => {
      try {
        const response = await fetch(
          `/api/game/state?room=${roomId}`
        );
        const data = await response.json();
        setGameState(data);
      } catch (error) {
        console.error('Failed to fetch game state:', error);
      }
    };

    const interval = setInterval(pollGameState, 1000);
    return () => clearInterval(interval);
  }, [roomId]);

  return gameState;
}
```

### Step 3: WebSocket Integration (Optional)
For real-time updates:

```typescript
// hooks/useGameSocket.ts
import { useEffect } from 'react';

export function useGameSocket(roomId: string, onStateUpdate) {
  useEffect(() => {
    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_LIVEKIT_URL.replace('http', 'ws')}/game/${roomId}`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onStateUpdate(data);
    };

    return () => ws.close();
  }, [roomId, onStateUpdate]);
}
```

### Step 4: Update Backend API Route
Create an API endpoint to expose game state:

```python
# Day_8/backend/src/api.py
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from agent import game_sessions

app = FastAPI()

@app.get("/api/game/state")
async def get_game_state(room: str = Query(...)):
    if room not in game_sessions:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    
    game_state = game_sessions[room]
    return game_state.to_dict()

@app.get("/api/game/character")
async def get_character(room: str = Query(...)):
    if room not in game_sessions:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    
    game_state = game_sessions[room]
    return {
        "name": game_state.player.name,
        "hp": game_state.player.hp,
        "max_hp": game_state.player.max_hp,
        "status": game_state.player.status,
        "strength": game_state.player.strength,
        "intelligence": game_state.player.intelligence,
        "luck": game_state.player.luck,
        "inventory": game_state.player.inventory,
    }
```

## Data Flow

```
Frontend                  Backend
─────────────────────────────────────
User Input ──────→ Agent Processing
    ↓                     ↓
GameState Display ←── GameState Update
    ↓
Message Display
    ↓
Story Continues
```

## Message Structure

```typescript
interface Message {
  id: string;                    // Unique identifier
  type: 'user' | 'agent' | 'system';
  content: string;               // Main message text
  timestamp: Date;               // When message was sent
  transcript?: string;           // Voice transcription
}
```

## Game State Structure

```typescript
interface GameStateData {
  universe: string;              // fantasy, cyberpunk, space_opera, etc.
  player: {
    name: string;
    hp: number;
    max_hp: number;
    strength: number;
    intelligence: number;
    luck: number;
    inventory: string[];
    status: string;              // Healthy, Injured, Critical
  };
  current_location: string;      // Location ID/name
  locations: {
    [key: string]: {
      name: string;
      description: string;
      paths: string[];
    }
  };
  npcs: {
    [key: string]: {
      name: string;
      role: string;
      attitude: string;          // friendly, neutral, hostile
      alive: boolean;
      location: string;
    }
  };
  quests: Array<{
    name: string;
    description: string;
    completed: boolean;
    active: boolean;
  }>;
  events: Array<{
    description: string;
    timestamp: string;
    location?: string;
  }>;
  turn_count: number;
}
```

## Styling

### Colors by Universe
```css
/* Fantasy */
.fantasy { @apply from-purple-600 to-purple-800; }

/* Cyberpunk */
.cyberpunk { @apply from-pink-600 to-purple-800; }

/* Space Opera */
.space { @apply from-blue-600 to-blue-800; }

/* Post-Apocalypse */
.post-apoc { @apply from-red-700 to-orange-800; }

/* Horror */
.horror { @apply from-gray-900 to-black; }

/* Romance */
.romance { @apply from-rose-600 to-pink-800; }
```

## Testing

### Test Message Display
```tsx
const testMessages: Message[] = [
  {
    id: '1',
    type: 'agent',
    content: 'Welcome to your fantasy adventure!',
    timestamp: new Date(),
  },
  {
    id: '2',
    type: 'user',
    content: 'I go to the tavern',
    timestamp: new Date(),
    transcript: 'I go to the tavern',
  },
];

<GameView
  messages={testMessages}
  gameState={mockGameState}
/>
```

### Test Game State
```typescript
const mockGameState: GameStateData = {
  universe: 'fantasy',
  turn_count: 3,
  player: {
    name: 'Aragorn',
    hp: 85,
    max_hp: 100,
    strength: 15,
    intelligence: 12,
    luck: 10,
    inventory: ['rusty sword', 'leather pouch'],
    status: 'Healthy',
  },
  current_location: 'village',
  locations: {
    village: {
      name: 'Village Square',
      description: 'A peaceful village with cobblestone streets',
      paths: ['forest', 'tavern'],
    },
  },
  npcs: {
    innkeeper: {
      name: 'Brom',
      role: 'tavern keeper',
      attitude: 'friendly',
      alive: true,
      location: 'tavern',
    },
  },
  quests: [],
  events: [],
};
```

## Performance Optimization

### Message Virtualization (Optional)
For games with many messages:

```tsx
import { VirtualList } from 'react-virtual';

<VirtualList
  height={600}
  itemCount={messages.length}
  itemSize={100}
>
  {({ index, style }) => (
    <div style={style}>
      {/* Render message */}
    </div>
  )}
</VirtualList>
```

### Game State Memoization
```tsx
const memoizedGameState = useMemo(
  () => gameState,
  [gameState]
);
```

## Accessibility

### Semantic HTML
- Use `<article>` for messages
- Use `<button>` for interactive elements
- Proper heading hierarchy

### ARIA Labels
```tsx
<button
  aria-label="Send message"
  aria-pressed={isLoading}
>
  Send
</button>
```

### Screen Reader Support
- Announce new messages
- Describe game state changes
- Provide alternative text for icons

## Browser Support
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ⚠️ Needs responsive updates

## Troubleshooting

### Game State Not Updating
1. Check API endpoint is running
2. Verify room ID matches backend
3. Check WebSocket connection
4. Inspect browser console for errors

### Messages Not Displaying
1. Verify message structure
2. Check timestamp is valid Date
3. Ensure content is not empty
4. Look for JavaScript errors

### UI Not Responsive
1. Clear browser cache
2. Check CSS imports
3. Verify Tailwind CSS configuration
4. Test in different browsers

## Future Enhancements

- [ ] Map visualization component
- [ ] Combat animation effects
- [ ] Spell/ability UI
- [ ] Equipment/gear management
- [ ] Character customization panel
- [ ] Settings menu
- [ ] Save/load UI
- [ ] Replay system
- [ ] Multiplayer chat
- [ ] Voice visualization

---

**Last Updated**: November 28, 2025
**Status**: Ready for Integration ✅
