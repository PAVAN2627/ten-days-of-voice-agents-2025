# Day 4 Agent Flow Diagram

## Complete User Journey with Fallback Mechanisms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ USER SPEAKS "Yes"                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 1: LLM PROCESSING (Gemini 2.5 Flash)                         │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │ • LLM receives: "yes"                                              │  │
│  │ • Instructions say: "User says yes → call list_concepts()"         │  │
│  │ • LLM tries to respond...                                          │  │
│  │                                                                    │  │
│  │ CASE A: ✓ LLM succeeds                                            │  │
│  │ → Generate tool call: list_concepts()                             │  │
│  │ → Send result to user                                             │  │
│  │ → USER HAPPY ✓                                                   │  │
│  │                                                                    │  │
│  │ CASE B: ✗ LLM returns empty (no candidates)                       │  │
│  │ → No response generated                                           │  │
│  │ → Falls through to Layer 2                                        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                     │                        │
│                                                     ▼                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 2: TEXT LISTENER FALLBACK                                    │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │ • Receives: received_text event with "yes"                         │  │
│  │ • Track: last_user_message["text"] = "yes"                         │  │
│  │ • Check: Is "yes" in simple affirmations list?                    │  │
│  │         YES → and no concept selected yet?                        │  │
│  │ • Action: Trigger fallback list_concepts()                        │  │
│  │ • Result: "Here are the available concepts: variables..."         │  │
│  │ → USER HAPPY ✓                                                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                     │                        │
│                                                     ▼                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 3: STATE LISTENER (Emergency Fallback)                       │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │ • Monitors: agent_state_changed events                            │  │
│  │ • Checks: Did user speak < 3 seconds ago?                         │  │
│  │ • Action: If stuck, force tool call                               │  │
│  │ • (Only activates if Layers 1 & 2 both fail)                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Complete Learning Flow

```
┌───────────────────────────────────────────────────────────────────────┐
│ WELCOME                                                               │
│ Agent: "Hi, I'm your Active Recall Coach. Say 'list concepts'..."    │
└───────────────┬───────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ USER: "Yes"  (or "list" or "ok" or "show")                           │
│                                                                       │
│ RESPONSE: [List_concepts tool called]                               │
│ Agent: "Here are the available concepts:                             │
│        • variables                                                   │
│        • loops                                                       │
│        • functions                                                   │
│        • conditions"                                                 │
└───────────────┬───────────────────────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────────────────────────────┐
│ USER: "variables"  (or any concept name)                             │
│                                                                       │
│ RESPONSE: [Set_concept tool called]                                  │
│ Agent: "Now, would you like to learn, take a quiz, or teach back?"  │
└───────────────┬───────────────────────────────────────────────────────┘
                │
        ┌───────┴────────┬─────────────────┐
        │                │                 │
        ▼                ▼                 ▼
     LEARN             QUIZ            TEACH-BACK
     [Matthew]        [Alicia]           [Ken]
     
     │                │                 │
     ▼                ▼                 ▼
┌────────────┐  ┌────────────┐     ┌──────────────┐
│Explain     │  │Question:   │     │Prompt:       │
│Variables   │  │What is a   │     │"Explain      │
│are...      │  │variable?   │     │variables"    │
│            │  │A) Label    │     │              │
│[Matthew    │  │B) Function │     │User speaks...│
│speaks]     │  │C) Loop     │     │              │
│            │  │D) Condition│     │[Ken listens] │
└───────────┬┘  └────────────┘     └──────┬───────┘
            │            │                 │
            ▼            ▼                 ▼
        Ready       [User answers]   [Evaluate_teach]
        for next        │                 │
        concept      [Evaluate_mcq]       ▼
                         │            Score: 75/100
                         ▼            Feedback: Good
                    Feedback +
                    "Another Q?"    "Teach again?"
                         │              │
                         └──────┬───────┘
                                │
                                ▼
                        Continue or
                        Switch modes?

```

## Voice Switching Timeline

```
USER PICKS MODE                        VOICE SWITCHES
─────────────────────────────────────────────────────

User says "learn"
  ↓
[set_mode("learn") called]
  ↓
switch_voice_for_mode(session, "learn")
  ↓
Create: murf.TTS(voice="Matthew", style="Conversation", text_pacing=True)
  ↓
✓ Matthew voice now active
  ↓
Agent: "Let me explain... variables are..."  [Matthew speaks]
─────────────────────────────────────────────────────

User says "switch to quiz"
  ↓
[set_mode("quiz") called]
  ↓
switch_voice_for_mode(session, "quiz")
  ↓
Create: murf.TTS(voice="Alicia", style="Conversation", text_pacing=True)
  ↓
✓ Alicia voice now active
  ↓
Agent: "Let's take a quiz... What is a variable?" [Alicia speaks]
─────────────────────────────────────────────────────

User says "teach back"
  ↓
[set_mode("teach_back") called]
  ↓
switch_voice_for_mode(session, "teach_back")
  ↓
Create: murf.TTS(voice="Ken", style="Conversation", text_pacing=True)
  ↓
✓ Ken voice now active
  ↓
Agent: "Please explain variables..." [Ken listens]
```

## Error Recovery Paths

```
┌─ Empty LLM Response Detected ──┐
│                                │
├─► Check last_user_message       │
│   └─► If "yes/ok/simple text"   │
│       └─► Trigger list_concepts │
│           ✓ User gets response  │
│                                │
├─► Check agent_state_changed      │
│   └─► If stuck > 3 seconds       │
│       └─► Force tool call        │
│           ✓ Agent recovers       │
│                                │
└─ Normal LLM Response ────────────┘
   └─► Tool called successfully
       ✓ User gets response
```

## Key Improvements Over Original

| Feature | Before | After |
|---------|--------|-------|
| Empty LLM response | ❌ User stuck | ✓ Fallback triggers |
| Simple input "yes" | ❌ Might hang | ✓ List shown immediately |
| Tool clarity | ⚠️ Optional | ✓ Explicit tool-first rules |
| Voice switching | ⚠️ Sometimes fails | ✓ Multiple setter methods |
| Duplicate lists | ❌ Could repeat | ✓ 5-second deduplication |
| Quiz continuation | ⚠️ Manual prompts | ✓ Automatic "Another Q?" |

## Deployment Verification

**Before deploying, test these scenarios:**

1. ✓ Say "Yes" → See concept list (not stuck)
2. ✓ Say "List concepts" → Immediate response
3. ✓ Say "variables" → Mode prompt appears
4. ✓ Say "learn" → Hear Matthew, get explanation
5. ✓ Say "quiz" → Hear Alicia, get question
6. ✓ Say "teach back" → Hear Ken, asked to explain
7. ✓ Answer quiz correctly → See feedback + "Another Q?"
8. ✓ No duplicate concept lists appearing
9. ✓ Voices are distinctly different between modes
10. ✓ Mode switching works smoothly

**Performance Targets:**
- Response time: < 2 seconds for all interactions
- Voice switch time: < 500ms
- No console errors in agent.py
- All fallback paths logged for debugging
