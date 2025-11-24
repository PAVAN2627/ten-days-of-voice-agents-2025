# backend/src/agent_day4.py
"""
Day 4 - Teach-the-Tutor Agent (fixed version)

- Voices (Murf Falcon):
    learn     -> Matthew
    quiz      -> Alicia
    teach_back-> Ken

- STT: Deepgram nova-3
- LLM: Google Gemini 2.5 Flash
- Loads content from backend/shared-data/day4_tutor_content.json
- Persists mastery to backend/tutor_state/tutor_state.json
- Passes RoomInputOptions to session.start (LiveKit API compatibility)
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from dotenv import load_dotenv

# livekit agents imports
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    RunContext,
    function_tool,
)
from livekit.plugins import google, murf, deepgram, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")
logger = logging.getLogger("day4.tutor")

# -----------------------
# Paths & constants
# -----------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHARED_DATA_DIR = os.path.join(ROOT, "shared-data")
CONTENT_PATH = os.path.join(SHARED_DATA_DIR, "day4_tutor_content.json")
STATE_DIR = os.path.join(ROOT, "tutor_state")
os.makedirs(STATE_DIR, exist_ok=True)
STATE_PATH = os.path.join(STATE_DIR, "tutor_state.json")

# Voice mapping
VOICE_LEARN = "Matthew"
VOICE_QUIZ = "Anusha"
VOICE_TEACH = "Ken"

# -----------------------
# Helpers: load/save
# -----------------------
def load_content() -> List[Dict[str, Any]]:
    if not os.path.exists(CONTENT_PATH):
        logger.error("Day4 content file not found at %s", CONTENT_PATH)
        return []
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return {"last_mode": None, "last_concept": None, "mastery": {}}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load state: %s", e)
        return {"last_mode": None, "last_concept": None, "mastery": {}}

def save_state(state: Dict[str, Any]):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to save state: %s", e)

# -----------------------
# Wrapper for dynamic voice switching
# -----------------------
class DynamicMurfTTS:
    """Wrapper around Murf TTS that allows voice switching at runtime"""
    def __init__(self, initial_voice: str = VOICE_LEARN):
        self.current_voice = initial_voice
        self.tts = murf.TTS(
            voice=self.current_voice,
            style="Conversation",
            text_pacing=True
        )
    
    async def synthesize(self, text: str, *args, **kwargs):
        """Delegate to underlying TTS"""
        return await self.tts.synthesize(text, *args, **kwargs)
    
    def switch_voice(self, new_voice: str):
        """Switch to a new voice by recreating the TTS instance"""
        if new_voice != self.current_voice:
            logger.info(f"🎤 Voice switching: {self.current_voice} → {new_voice}")
            self.current_voice = new_voice
            self.tts = murf.TTS(
                voice=new_voice,
                style="Conversation",
                text_pacing=True
            )
    
    def __getattr__(self, name):
        """Delegate all other attributes to the underlying TTS"""
        return getattr(self.tts, name)

# -----------------------
# Small evaluation helpers
# -----------------------
def score_explanation(reference: str, user_text: str) -> Dict[str, Any]:
    """Simple overlap-based scoring (0-100) + short feedback."""
    def words(s):
        return re.findall(r"\w+", (s or "").lower())
    ref_words = set(words(reference))
    user_words = set(words(user_text))
    if not ref_words:
        return {"score": 0, "feedback": "No reference available to score against."}
    common = ref_words & user_words
    ratio = len(common) / max(len(ref_words), 1)
    score = int(min(100, round(ratio * 100)))
    if score >= 80:
        fb = "Excellent — you covered the key points clearly."
    elif score >= 50:
        fb = "Good — you covered several ideas but missed some details."
    else:
        fb = "Nice attempt — try to state the core idea and one short example."
    return {"score": score, "feedback": fb}

# -----------------------
# Tools exposed to LLM / agent flow
# -----------------------
@function_tool
async def list_concepts(ctx: RunContext[dict]):
    """List all available programming concepts that can be learned."""
    content = load_content()
    if not content:
        return "No concepts available."
    lines = [f"- {c['id']}: {c.get('title','')}" for c in content]
    return "Available concepts:\n" + "\n".join(lines)

@function_tool
async def set_concept(ctx: RunContext[dict], concept_id: str):
    """Select a concept by its ID to work with (e.g., 'variables', 'loops')."""
    content = load_content()
    cid = (concept_id or "").strip()
    match = next((c for c in content if c["id"] == cid), None)
    if not match:
        return f"Concept '{cid}' not found. Use list_concepts to see IDs."
    ctx.userdata["tutor"]["concept_id"] = cid
    state = load_state()
    state["last_concept"] = cid
    save_state(state)
    return f"Concept set to: {match.get('title', cid)}"

@function_tool
async def set_mode(ctx: RunContext[dict], mode: str):
    """Change the learning mode: 'learn' (explanation), 'quiz' (questions), or 'teach_back' (student teaches)."""
    m = (mode or "").strip().lower()
    if m not in ("learn", "quiz", "teach_back"):
        return "Unknown mode. Choose 'learn', 'quiz', or 'teach_back'."
    ctx.userdata["tutor"]["mode"] = m
    state = load_state()
    state["last_mode"] = m
    save_state(state)
    return f"Mode set to: {m}"

@function_tool
async def explain_concept(ctx: RunContext[dict]):
    """Explain the currently selected concept in detail."""
    cid = ctx.userdata["tutor"].get("concept_id")
    if not cid:
        return "No concept selected. Use set_concept to pick one."
    content = load_content()
    match = next((c for c in content if c["id"] == cid), None)
    if not match:
        return "Selected concept not found."
    # Mark explained count
    state = load_state()
    state.setdefault("mastery", {})
    ms = state["mastery"].get(cid, {"times_explained": 0, "times_quizzed": 0, "times_taught_back": 0, "last_score": None, "avg_score": None})
    ms["times_explained"] = ms.get("times_explained", 0) + 1
    state["mastery"][cid] = ms
    save_state(state)
    return f"{match.get('title')}: {match.get('summary')}"

@function_tool
async def get_mcq(ctx: RunContext[dict]):
    """Get the next multiple-choice quiz question for the selected concept."""
    cid = ctx.userdata["tutor"].get("concept_id")
    if not cid:
        return {"error": "No concept selected"}
    content = load_content()
    match = next((c for c in content if c["id"] == cid), None)
    if not match:
        return {"error": "Concept not found"}
    questions = match.get("quiz", []) or match.get("mcq", [])
    if not questions:
        return {"error": "No quiz questions for this concept"}
    # maintain rotation index in userdata
    idx = ctx.userdata["tutor"].get("quiz_index", 0) % len(questions)
    ctx.userdata["tutor"]["quiz_index"] = idx + 1
    q = questions[idx]
    return {"question": q["question"], "options": q["options"], "answer": q["answer"], "index": idx}

@function_tool
async def evaluate_mcq(ctx: RunContext[dict], user_answer: str):
    """Score the user's multiple-choice quiz answer and return feedback."""
    cid = ctx.userdata["tutor"].get("concept_id")
    if not cid:
        return {"error": "No concept selected"}
    content = load_content()
    match = next((c for c in content if c["id"] == cid), None)
    if not match:
        return {"error": "Concept not found"}
    # fetch last asked question index
    idx = (ctx.userdata["tutor"].get("quiz_index", 1) - 1)
    questions = match.get("quiz", []) or match.get("mcq", [])
    if not questions:
        return {"error": "No questions"}
    if idx < 0 or idx >= len(questions):
        idx = max(0, len(questions) - 1)
    q = questions[idx]
    correct_i = q["answer"]
    options = q["options"]
    ua = (user_answer or "").lower().strip()

    # 1) letter (a/b/c/d)
    sel = None
    m = re.search(r"\b([abcd])\b", ua)
    if m:
        sel = ord(m.group(1)) - 97
    else:
        # number 1-4
        m2 = re.search(r"\b([1-4])\b", ua)
        if m2:
            sel = int(m2.group(1)) - 1

    # 2) match option text
    if sel is None:
        for i, opt in enumerate(options):
            if opt.lower() in ua:
                sel = i
                break
    # 3) partial overlap heuristic
    if sel is None:
        ua_words = set(re.findall(r"\w+", ua))
        best_i = None
        best_score = 0
        for i, opt in enumerate(options):
            opt_words = set(re.findall(r"\w+", opt.lower()))
            common = ua_words & opt_words
            if len(common) > best_score:
                best_score = len(common)
                best_i = i
        if best_score >= 1:
            sel = best_i

    # 4) final fallback check for any keyword from correct option
    if sel is None:
        for w in re.findall(r"\w+", options[correct_i].lower()):
            if w in ua:
                sel = correct_i
                break

    correct = (sel == correct_i)
    feedback = ("Correct — well done!" if correct else f"Not quite. Correct answer: {options[correct_i]}.")
    # update mastery
    state = load_state()
    state.setdefault("mastery", {})
    ms = state["mastery"].get(cid, {"times_explained": 0, "times_quizzed": 0, "times_taught_back": 0, "last_score": None, "avg_score": None})
    ms["times_quizzed"] = ms.get("times_quizzed", 0) + 1
    sc = 100 if correct else 0
    ms["last_score"] = sc
    prev = ms.get("avg_score")
    ms["avg_score"] = sc if prev is None else round((prev + sc) / 2, 1)
    state["mastery"][cid] = ms
    save_state(state)

    return {"correct": bool(correct), "selected": sel, "correct_index": correct_i, "feedback": feedback}

@function_tool
async def evaluate_teachback(ctx: RunContext[dict], explanation: str):
    """Score the user's explanation in teach-back mode and return feedback."""
    cid = ctx.userdata["tutor"].get("concept_id")
    if not cid:
        return {"error": "No concept selected"}
    content = load_content()
    match = next((c for c in content if c["id"] == cid), None)
    if not match:
        return {"error": "Concept not found"}
    result = score_explanation(match.get("summary", ""), explanation or "")
    # update mastery
    state = load_state()
    state.setdefault("mastery", {})
    ms = state["mastery"].get(cid, {"times_explained": 0, "times_quizzed": 0, "times_taught_back": 0, "last_score": None, "avg_score": None})
    ms["times_taught_back"] = ms.get("times_taught_back", 0) + 1
    ms["last_score"] = result["score"]
    prev = ms.get("avg_score")
    ms["avg_score"] = result["score"] if prev is None else round((prev + result["score"]) / 2, 1)
    state["mastery"][cid] = ms
    save_state(state)
    return result

@function_tool
async def get_mastery_report(ctx: RunContext[dict]):
    """Get a detailed report of the user's mastery progress across all concepts."""
    state = load_state()
    mastery = state.get("mastery", {})
    if not mastery:
        return "No mastery data yet."
    lines = []
    for cid, info in mastery.items():
        lines.append(f"{cid}: last={info.get('last_score')}, avg={info.get('avg_score')}, taught_back={info.get('times_taught_back')}, quizzed={info.get('times_quizzed')}")
    return "Mastery:\n" + "\n".join(lines)

# -----------------------
# Tutor Agent
# -----------------------
class TutorAgent(Agent):
    def __init__(self, content: List[dict], dynamic_tts=None):
        instructions = """You are an Active Recall Tech Tutor.

Your role: Help students learn programming concepts through three modes: learn (explanation), quiz (questions), and teach-back (student explains).

When user wants to see concepts or says "list"/"show"/"concepts":
1. Call list_concepts() to get available concepts
2. Present them and ask: "Which concept would you like to work with?"

When user selects a concept:
1. Call set_concept(concept_id)
2. Ask: "Would you like to learn, take a quiz, or teach-back this concept?"

When user chooses a mode (learn/quiz/teach_back):
1. Call set_mode(mode)
2. Execute that mode

THREE MODES:
- learn: Explain concept. Call explain_concept()
- quiz: Ask multiple-choice question. Call get_mcq() → wait for answer → call evaluate_mcq()
- teach_back: Ask student to explain. Call evaluate_teachback()

RULES:
- NEVER list concepts yourself - always use list_concepts tool
- Keep responses SHORT and conversational
- When user picks concept → call set_concept() immediately
- When user picks mode → call set_mode() immediately
- After quiz question → wait for answer
- DO NOT repeat concept names twice

PRIORITY:
1. list/show/concepts keyword → call list_concepts()
2. User picks concept → call set_concept()
3. User picks mode → call set_mode()
4. Always use tools, never make up responses."""

        super().__init__(
            instructions=instructions,
            tools=[
                list_concepts,
                set_concept,
                set_mode,
                explain_concept,
                get_mcq,
                evaluate_mcq,
                evaluate_teachback,
                get_mastery_report
            ]
        )
        self._session = None
        self._dynamic_tts = dynamic_tts  # Store reference to dynamic TTS wrapper
    
    async def on_message(self, message) -> None:
        """Intercept messages to handle voice switching and list requests"""
        try:
            logger.info(f"🎯 on_message CALLED with message: {message}")
            
            # Extract message text
            msg_text = ""
            if hasattr(message, "text"):
                msg_text = message.text
                logger.info(f"   Got text from message.text: '{msg_text}'")
            elif isinstance(message, str):
                msg_text = message
                logger.info(f"   Message is string: '{msg_text}'")
            else:
                logger.info(f"   Message type: {type(message)}, dir: {dir(message)}")
            
            msg_lower = msg_text.lower().strip() if msg_text else ""
            logger.info(f"   Lowercase: '{msg_lower}'")
            
            # EARLY INTERCEPTION: Handle list/concept requests BEFORE LLM
            if self._session:
                concept_id = self._session.userdata.get("tutor", {}).get("concept_id")
                
                # Intercept list requests
                list_keywords = ["list", "show", "see", "all", "available", "concepts", "have you"]
                if any(kw in msg_lower for kw in list_keywords) and not concept_id:
                    logger.info(f"⚡ EARLY INTERCEPT: List request in '{msg_lower}'")
                    result = await self._session.call_tool("list_concepts")
                    await self._session.send_text(f"Here are the concepts:\n{result}")
                    return
                
                # Intercept affirmations
                if msg_lower in ["yes", "yeah", "ok", "okay", "sure", "please"] and not concept_id:
                    logger.info(f"⚡ EARLY INTERCEPT: Affirmation '{msg_lower}'")
                    result = await self._session.call_tool("list_concepts")
                    await self._session.send_text(f"Here are the concepts:\n{result}")
                    return
            
            logger.info(f"   No early intercept, calling parent LLM")
            # Call parent LLM for normal processing
            await super().on_message(message)
            
            # After parent processing, check if mode changed and switch voice
            if self._session and self._dynamic_tts:
                new_mode = self._session.userdata.get("tutor", {}).get("mode")
                if new_mode:
                    logger.info(f"🎤 on_message detected mode: {new_mode}")
                    await self._switch_voice(new_mode)
        except Exception as e:
            logger.error(f"Error in on_message: {e}", exc_info=True)
    
    async def _switch_voice(self, mode: str) -> None:
        """Switch voice for the given mode using the dynamic TTS wrapper"""
        try:
            if not self._dynamic_tts:
                return
            
            voice_map = {
                "learn": VOICE_LEARN,
                "quiz": VOICE_QUIZ,
                "teach_back": VOICE_TEACH,
            }
            
            voice = voice_map.get(mode, VOICE_LEARN)
            logger.info(f"🎤 Switching to {voice} for mode {mode}")
            
            # Use the wrapper's switch_voice method
            self._dynamic_tts.switch_voice(voice)
            logger.info(f"✓ Voice switched to {voice}")
        except Exception as e:
            logger.error(f"Voice switch error: {e}", exc_info=True)

# -----------------------
# Prewarm function
# -----------------------
def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception as e:
        logger.warning("VAD prewarm failed: %s", e)
        proc.userdata["vad"] = None

# -----------------------
# Entrypoint
# -----------------------
async def entrypoint(ctx: JobContext):
    """Main entry point for the tutor agent"""
    ctx.log_context_fields = {"room": ctx.room.name}
    logger.info("Starting Day4 tutor - room %s", ctx.room.name)

    # Load content from persistent storage
    content = load_content()
    if not content:
        logger.error("No content loaded. Please add day4_tutor_content.json")

    # Initialize user data
    userdata = {
        "tutor": {
            "mode": None,
            "concept_id": None,
            "quiz_index": 0,
        },
        "history": []
    }

    # Create dynamic TTS wrapper that allows voice switching
    dynamic_tts = DynamicMurfTTS(initial_voice=VOICE_LEARN)

    # Create session
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY")),
        tts=dynamic_tts,
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata,
    )

    # Create agent
    agent = TutorAgent(content, dynamic_tts=dynamic_tts)
    agent._session = session  # Pass session to agent for voice switching

    # Start session (MUST complete before event handlers are registered)
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    # Register event handlers AFTER session.start() completes
    
    @session.on("tool_called")
    def _tool_called_handler(ev):
        """Switch voice when mode changes"""
        try:
            # Extract tool name and mode argument
            tool_name = None
            mode = None
            
            # Try different attribute patterns for tool name
            if hasattr(ev, "tool") and hasattr(ev.tool, "name"):
                tool_name = ev.tool.name
            elif hasattr(ev, "name"):
                tool_name = ev.name
            elif isinstance(ev, dict):
                tool_name = ev.get("tool_name") or ev.get("name")
            
            # Extract mode argument
            if hasattr(ev, "arguments"):
                mode = ev.arguments.get("mode") if isinstance(ev.arguments, dict) else None
            elif hasattr(ev, "args"):
                mode = ev.args.get("mode") if isinstance(ev.args, dict) else None
            elif isinstance(ev, dict) and "arguments" in ev:
                mode = ev["arguments"].get("mode") if isinstance(ev["arguments"], dict) else None
            
            if tool_name and "set_mode" in str(tool_name).lower() and mode:
                logger.info(f"🎤 Tool called: set_mode({mode})")

                # Map modes to voices
                voice_map = {
                    "learn": VOICE_LEARN,
                    "quiz": VOICE_QUIZ,
                    "teach_back": VOICE_TEACH,
                }

                voice = voice_map.get(mode, VOICE_LEARN)

                # Switch voice using the wrapper
                dynamic_tts.switch_voice(voice)
                logger.info(f"✓ Voice switched to {voice}")
        except Exception as e:
            logger.error(f"Error in tool_called handler: {e}", exc_info=True)

    @session.on("received_text")
    async def _text_received_handler(ev):
        """Quick responses without LLM for common commands"""
        try:
            # Extract text from event
            text = None
            if hasattr(ev, "text"):
                text = ev.text
            elif isinstance(ev, str):
                text = ev
            elif isinstance(ev, dict):
                text = ev.get("text")
            
            if not text:
                return
            
            text_lower = text.lower().strip()
            logger.info(f"📝 User said: '{text_lower}'")

            if not text_lower:
                return

            # Get current state
            concept_id = session.userdata["tutor"].get("concept_id")
            mode = session.userdata["tutor"].get("mode")

            # Quick affirmation → list concepts
            if text_lower in ["yes", "yeah", "ok", "okay", "sure", "please"] and not concept_id:
                logger.info("⚡ Quick path: Affirmation → list_concepts")
                result = await session.call_tool("list_concepts")
                await session.send_text(f"Here are the concepts:\n{result}")
                return

            # List request → list concepts (more aggressive matching)
            list_keywords = ["list", "show", "see", "all", "available", "concepts", "have you"]
            if any(word in text_lower for word in list_keywords) and not concept_id:
                logger.info(f"⚡ Quick path: List request detected in '{text_lower}'")
                result = await session.call_tool("list_concepts")
                await session.send_text(f"Here are the concepts:\n{result}")
                return

        except Exception as e:
            logger.error(f"Error in text handler: {e}", exc_info=True)

    @session.on("user_speech_committed")
    async def _user_speech_handler(message: str):
        """Intercept user speech IMMEDIATELY after STT, before LLM"""
        try:
            logger.info(f"🎙️ User speech committed: '{message}'")
            msg_lower = message.lower().strip()
            
            concept_id = session.userdata.get("tutor", {}).get("concept_id")
            
            # List request - intercept BEFORE LLM
            list_keywords = ["list", "show", "see", "all", "available", "concepts", "share", "need"]
            if any(kw in msg_lower for kw in list_keywords) and not concept_id:
                logger.info(f"⚡ SPEECH INTERCEPT: List request detected")
                result = await session.call_tool("list_concepts")
                await session.send_text(f"Here are the concepts:\n{result}")
                # CRITICAL: We need to prevent LLM from being called
                # This might not work depending on LiveKit version
                return
            
        except Exception as e:
            logger.error(f"Error in user_speech handler: {e}", exc_info=True)

    # Send greeting AFTER session.start() and handlers registered
    greeting = (
        "Hello! I'm your Tech Tutor. I have important programming concepts to help you master. "
        "We can learn through three modes: "
        "Learn mode — I explain the concept clearly, "
        "Quiz mode — I ask you multiple-choice questions, and "
        "Teach-Back mode — You explain the concept back to me for feedback. "
        "Which programming concept would you like to start with? "
        "You can say a concept name or say 'list' to hear all available concepts."
    )
    await session.send_text(greeting)

    # Connect to room
    await ctx.connect()

# -----------------------
# Run worker
# -----------------------
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm
        )
    )
