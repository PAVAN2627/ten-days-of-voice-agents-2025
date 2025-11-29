# Day 8 Game UI - Complete Reference

## UI Components Overview

### 1. **GameStateDisplay Component** (`game-state.tsx`)
Displays all game state information in a compact, tabbed interface.

**Features:**
- **Real-time HP Bar**: Shows health with color coding (Green > 50%, Yellow 25-50%, Red < 25%)
- **Character Stats**: Strength, Intelligence, Luck attributes
- **Inventory Management**: List of items with add/remove capabilities
- **Quest Tracking**: Active/completed quest status with descriptions
- **World Info**: Current location, NPCs present, available paths
- **Universe-specific Theming**: Different color schemes for each universe

**Tabs:**
```
┌─────────────────────────────────────┐
│ Character | Inventory | Quests | World │
├─────────────────────────────────────┤
│ Content based on selected tab       │
└─────────────────────────────────────┘
```

### 2. **GameView Component** (`game-view.tsx`)
Main game interface with 3-column layout.

**Layout:**
```
┌────────────────────────────────────────────────────────────────┐
│          Universe & Turn Information (Header)                  │
├──────────────┬──────────────────────────┬──────────────────────┤
│   Left Panel │     Center Panel         │    Right Panel       │
│              │                          │                      │
│  Character   │  Story Messages          │  Quick Actions       │
│  Stats Panel │  ├─ Agent Messages       │  ├─ Roll Dice        │
│  ├─ HP Bar   │  ├─ User Responses       │  ├─ Inventory        │
│  ├─ Stats    │  └─ System Events        │  ├─ Save Game        │
│  ├─ Inventory│                          │  └─ Show Map         │
│  ├─ Quests   │  Message Input Box       │                      │
│  └─ World    │  (Type or Voice Input)   │  Quick Stats         │
│              │                          │  Recent Events       │
└──────────────┴──────────────────────────┴──────────────────────┘
```

## Color Scheme by Universe

### Fantasy
- **Primary**: Purple/Violet
- **Gradient**: `from-purple-600 to-purple-800`
- **Accent**: Gold/Amber

### Cyberpunk
- **Primary**: Pink/Neon
- **Gradient**: `from-pink-600 to-purple-800`
- **Accent**: Cyan/Bright Blue

### Space Opera
- **Primary**: Deep Blue
- **Gradient**: `from-blue-600 to-blue-800`
- **Accent**: Light Blue/Cyan

### Post-Apocalypse
- **Primary**: Red/Orange
- **Gradient**: `from-red-700 to-orange-800`
- **Accent**: Yellow/Rust

### Horror
- **Primary**: Black/Dark Gray
- **Gradient**: `from-gray-900 to-black`
- **Accent**: Red/Blood Red

### Romance Drama
- **Primary**: Rose/Pink
- **Gradient**: `from-rose-600 to-pink-800`
- **Accent**: Light Pink/Purple

## Message Types

### 1. Agent Message (GM Narration)
```
┌─────────────────────────────────────────┐
│ GAME MASTER                  Timestamp  │
├─────────────────────────────────────────┤
│ [Purple gradient background]            │
│ The Game Master describes the scene...  │
│ "What do you do?"                       │
└─────────────────────────────────────────┘
```

### 2. User Response
```
┌─────────────────────────────────────────┐
│ YOUR RESPONSE                Timestamp  │
├─────────────────────────────────────────┤
│ [Blue gradient background]              │
│ Your action or dialogue...              │
│ Heard: "[Voice transcription]"          │
└─────────────────────────────────────────┘
```

### 3. System Message
```
┌─────────────────────────────────────────┐
│ [Dark background]                       │
│ System notification or event...         │
└─────────────────────────────────────────┘
```

## Character Panel Details

### HP Display
```
Name                    Status
┌─────────────────────────────────┐
│ [████████░░░░] 85/100 HP        │
└─────────────────────────────────┘
```

**Status Colors:**
- 🟢 **Healthy**: > 50% HP
- 🟡 **Injured**: 25-50% HP
- 🔴 **Critical**: < 25% HP

### Stats Grid
```
┌──────────┬────────────┬────────┐
│ Strength │ Intelligence│ Luck  │
│    10    │     12      │   8   │
│ Physical │  Knowledge  │Fortune│
└──────────┴────────────┴────────┘
```

### Inventory List
```
Items (5)
─────────────────────────────
• Magic Sword
• Health Potion
• Ancient Map
• Golden Coin
• Mysterious Key
```

### Quests Tab
```
Quest Status
─────────────────────────────
◆ Active Quest
  "Find the ancient artifact"

✓ Completed Quest
  "Defeat the orc warlord"

◇ Inactive Quest
  "Explore the ruins"
```

### World Tab
```
Current Location
─────────────────────────────
Dark Forest
Ancient trees block most sunlight.
→ Paths: Village, Cave

People Here
─────────────────────────────
Wizard Eldara [Friendly]
  Role: Village Wizard
```

## Quick Actions Panel

### Button Styles
```
┌─────────────────────────────┐
│ 🎲 Roll Dice       [Green]  │
├─────────────────────────────┤
│ 📦 Check Inventory [Orange] │
├─────────────────────────────┤
│ 💾 Save Game       [Purple] │
├─────────────────────────────┤
│ 🗺️ Show Map        [Blue]   │
└─────────────────────────────┘
```

### Quick Stats
```
Quick Stats
─────────────────────────────
Health:  ██████████░░ 85/100
Status:  Healthy
Items:   5
Quests:  2
```

### Recent Events
```
Recent Events
─────────────────────────────
• Moved to Dark Forest
• Met Eldara the Wizard
• Received ancient map
```

## Input Methods

### Text Input
```
┌────────────────────────────┬──────────┐
│ Type your action...        │  Send   │
└────────────────────────────┴──────────┘
```

### Voice Input Indicator
```
🔴 ◆ ◆ ◆ Listening...
```

### Loading State
```
◆ ◆ ◆ Game Master is thinking...
```

## Responsive Design

### Full Screen (Desktop)
- Left Panel: 288px (w-72)
- Center Panel: Flex-1 (auto)
- Right Panel: 256px (w-64)
- Minimum width: 1400px recommended

### Tablet Mode (Optional)
- Stacked layout
- Collapsible panels
- Swipe-able tab navigation

### Mobile Mode (Future)
- Full-width story view
- Bottom sheet character panel
- Overlay inventory/quests

## Animations

### Fade-in Animation
```css
.animate-fade-in {
  animation: fade-in 0.3s ease-in-out;
}
```

### Message Entry
- New messages fade in smoothly
- Slight upward slide animation
- Staggered animation for multiple items

### Loading Indicators
- Bouncing dots animation
- Color pulsing effects
- Smooth transitions between states

## Theme Support

### Dark Mode (Default)
- Background: Slate-950 to Slate-900
- Text: White/Slate-100
- Borders: Slate-700

### Light Mode (Optional)
- Background: Slate-50 to Slate-100
- Text: Slate-900
- Borders: Slate-300

## Integration Points

### Game State Data Structure
```typescript
interface GameStateData {
  universe: string;
  player: Character;
  current_location: string;
  locations: { [key: string]: Location };
  npcs: { [key: string]: NPC };
  quests: Quest[];
  events: Event[];
  turn_count: number;
}
```

### Message Data Structure
```typescript
interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  transcript?: string; // Voice input
}
```

## Usage Example

```tsx
import { GameView } from '@/components/app/game-view';

export default function Game() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [gameState, setGameState] = useState<GameStateData | undefined>();

  return (
    <GameView
      messages={messages}
      gameState={gameState}
      isListening={false}
      isLoading={false}
      onSendMessage={(msg) => {
        // Handle user message
      }}
    />
  );
}
```

## Future Enhancements

- [ ] Map visualization
- [ ] Combat animation effects
- [ ] Particle effects for spells
- [ ] Music/sound effects integration
- [ ] Inventory drag-and-drop
- [ ] Character customization UI
- [ ] Settings panel
- [ ] Accessibility features (high contrast mode, screen reader support)
- [ ] Mobile responsive layout
- [ ] Touch gesture support

## CSS Classes Reference

```css
/* Backgrounds */
.bg-gradient-to-br
.from-slate-800
.to-slate-900
.from-purple-600
.to-purple-800

/* Text */
.text-white
.text-slate-100
.text-slate-400
.text-slate-500

/* Borders */
.border-slate-700
.border-purple-700
.border-blue-700

/* Animations */
.animate-fade-in
.animate-bounce
.animate-pulse

/* Responsive */
.w-72
.w-64
.flex-1
.min-w-0
```

---

**UI Created**: November 28, 2025
**Components**: GameStateDisplay, GameView
**Status**: Production Ready ✅
