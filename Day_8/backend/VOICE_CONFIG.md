# Voice Configuration for RPG Game Master

## Current Voice
**Matthew (en-US)** ✅ - Dramatic narration voice with "Narration" style

### Why Matthew with Narration Style?
- Specifically designed for storytelling and narration
- Works excellently across all game universes
- Dramatic and engaging delivery
- Clear pronunciation
- Best available option in Murf for RPG storytelling

### Note on Indian English Voices
The Indian English voices listed (Nikhil, Ronnie, Samar, etc.) may not be available in the current Murf API version or may use different voice IDs. The documentation shows these voices but they may require different configuration or API access.

## Available Indian English Voices

### Male Voices

**Nikhil (en-IN)** - CURRENT
- Style: Conversation
- Best for: Horror, Post-Apocalypse, Space Opera
- Tone: Deep, dramatic, authoritative
- Perfect for: Action-packed adventures and dark themes

**Ronnie (en-IN)**
- Style: Conversation
- Best for: All universes (most versatile)
- Tone: Clear, versatile, engaging
- Perfect for: General storytelling

**Samar (en-IN)**
- Style: Conversation
- Best for: Fantasy, Cyberpunk
- Tone: Warm, friendly, engaging
- Perfect for: Lighter adventures and fantasy worlds

### Female Voices

**Anisha (en-IN)**
- Style: Conversation
- Best for: Fantasy, Romance
- Tone: Warm, expressive
- Perfect for: Emotional storytelling

**Anusha (en-IN)**
- Style: Conversation
- Best for: Cyberpunk, Space Opera
- Tone: Modern, energetic
- Perfect for: Futuristic settings

**Tanushree (en-IN)**
- Style: Conversation
- Best for: Horror, Mystery
- Tone: Mysterious, captivating
- Perfect for: Suspenseful narratives

## Recommended Voice Mapping by Universe

### Fantasy
- Primary: **Samar** (warm, engaging)
- Alternative: Anisha (expressive)

### Horror
- Primary: **Nikhil** (dramatic, dark) ✅ CURRENT
- Alternative: Tanushree (mysterious)

### Space Opera
- Primary: **Nikhil** (authoritative) ✅ CURRENT
- Alternative: Anusha (futuristic)

### Cyberpunk
- Primary: **Anusha** (modern, energetic)
- Alternative: Samar (engaging)

### Post-Apocalypse
- Primary: **Nikhil** (gritty, dramatic) ✅ CURRENT
- Alternative: Ronnie (versatile)

## How to Change Voice

Edit `Day_8/backend/src/agent.py` line ~1115:

```python
tts=murf.TTS(
    voice="en-US-matthew",  # Current working voice
    style="Narration",      # Use "Narration" for storytelling
    tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
    text_pacing=True
),
```

## Available Verified Voices
These voices are confirmed to work with Murf API:
- **en-US-matthew** (male) - Narration style ✅ CURRENT
- **en-US-natalie** (female) - Narration style
- **en-US-terrell** (male) - Conversation style
- **en-US-clint** (male) - Narration style

To get the full list of available voices, use:
```bash
curl https://api.murf.ai/v1/speech/voices
```

## Technical Limitation
**Voice cannot change based on universe selection** because:
- LiveKit session is created before universe is chosen
- Voice is set at session initialization
- Cannot be changed mid-session

**Solution**: Use **Ronnie (en-IN)** - the most versatile voice that works well for ALL universes

## Notes
- Voice is set at session start and cannot be changed mid-game
- All voices support "Conversation" style for natural storytelling
- Indian English voices provide better localization for Indian users
- Current voice (Ronnie) is the best all-around choice for multi-universe gameplay
- If you want universe-specific voices, you'd need to restart the backend with a different voice setting
