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
# Voice switching helper
# -----------------------
def switch_session_voice(session: AgentSession, new_voice: str):
    """Switch the session's TTS voice by replacing the TTS instance"""
    try:
        logger.info(f"🎤 Switching session voice to: {new_voice}")
        logger.info(f"Session type: {type(session)}")
        logger.info(f"Session attributes: {[attr for attr in dir(session) if 'tts' in attr.lower()]}")
        
        new_tts = murf.TTS(
            voice=new_voice,
            style="Conversation",
            text_pacing=True
        )
        
        # Try multiple ways to replace TTS
        updated = False
        if hasattr(session, '_tts'):
            old_tts = getattr(session, '_tts', None)
            session._tts = new_tts
            logger.info(f"Updated session._tts from {old_tts} to {new_tts}")
            updated = True
            
        if hasattr(session, 'tts'):
            old_tts = getattr(session, 'tts', None)
            session.tts = new_tts
            logger.info(f"Updated session.tts from {old_tts} to {new_tts}")
            updated = True
        
        # Force update internal TTS references
        try:
            if hasattr(session, '_agent_output') and hasattr(session._agent_output, '_tts'):
                session._agent_output._tts = new_tts
                logger.info("Updated session._agent_output._tts")
                updated = True
        except Exception as e:
            logger.warning(f"Could not update _agent_output._tts: {e}")
            
        if updated:
            logger.info(f"✓ Session voice switched to {new_voice}")
        else:
            logger.warning("No TTS attributes found to update")
            
        return updated
    except Exception as e:
        logger.error(f"Voice switch failed: {e}", exc_info=True)
        return False

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
# Specialized Agents for Each Mode
# -----------------------
class MainTutorAgent(Agent):
    """Main coordinator agent that handles concept selection and mode handoffs"""
    def __init__(self, content: List[dict]):
        instructions = """You are the Main Active Recall Tech Tutor Coordinator.

Your role: Help students select programming concepts and learning modes, then transfer them to specialized tutors.

When user wants to see concepts:
1. Call list_concepts() to show available topics
2. Ask: "Which concept would you like to work with?"

When user selects a concept:
1. Call set_concept(concept_id) 
2. Ask: "Which learning mode would you prefer?"
   - Learn mode: I'll explain the concept clearly
   - Quiz mode: I'll test you with questions  
   - Teach-back mode: You explain it to me

When user chooses a mode:
1. Call the appropriate transfer function
2. The specialized tutor will take over

RULES:
- ALWAYS use list_concepts tool, never list yourself
- Keep responses SHORT and friendly
- Transfer immediately when mode is chosen
- Focus on coordination, not teaching"""

        super().__init__(
            instructions=instructions,
            tools=[
                list_concepts,
                set_concept, 
                self.transfer_to_learn_mode,
                self.transfer_to_quiz_mode,
                self.transfer_to_teachback_mode,
                get_mastery_report
            ]
        )
        self.content = content
        self._session = None
    
    async def on_enter(self) -> None:
        """Greeting when agent starts"""
        greeting = (
            "Hello! I'm your Tech Tutor Coordinator. I'll help you master programming concepts through active learning. "
            "We have three specialized tutors: Learn (explanations), Quiz (questions), and Teach-Back (you explain). "
            "Which programming concept would you like to start with? Say 'list concepts' to see all topics."
        )
        await self.session.send_text(greeting)
    
    @function_tool
    async def transfer_to_learn_mode(self, ctx: RunContext[dict]):
        """Transfer to Learn Mode tutor for concept explanations"""
        concept_id = ctx.userdata["tutor"].get("concept_id")
        if not concept_id:
            return "Please select a concept first using set_concept."
        
        ctx.userdata["tutor"]["mode"] = "learn"
        return LearnModeAgent(self.content), "Transferring to Learn Mode tutor with Matthew's voice"
    
    @function_tool 
    async def transfer_to_quiz_mode(self, ctx: RunContext[dict]):
        """Transfer to Quiz Mode tutor for interactive questions"""
        concept_id = ctx.userdata["tutor"].get("concept_id")
        if not concept_id:
            return "Please select a concept first using set_concept."
            
        ctx.userdata["tutor"]["mode"] = "quiz"
        return QuizModeAgent(self.content), "Transferring to Quiz Mode tutor with Anusha's voice"
    
    @function_tool
    async def transfer_to_teachback_mode(self, ctx: RunContext[dict]):
        """Transfer to Teach-Back Mode tutor for student explanations"""
        concept_id = ctx.userdata["tutor"].get("concept_id")
        if not concept_id:
            return "Please select a concept first using set_concept."
            
        ctx.userdata["tutor"]["mode"] = "teach_back" 
        return TeachBackModeAgent(self.content), "Transferring to Teach-Back Mode tutor with Ken's voice"

class LearnModeAgent(Agent):
    """Specialized agent for Learn Mode with Matthew's voice"""
    def __init__(self, content: List[dict]):
        instructions = """You are Matthew, the Learn Mode Tutor. Your voice is warm and explanatory.

Your role: Provide clear, detailed explanations of programming concepts.

When you enter:
1. Greet warmly and explain the selected concept
2. Use explain_concept() to get the content
3. Provide additional examples and clarifications
4. Ask if they want to switch modes or select a new concept

Style: 
- Warm, patient, and thorough
- Use analogies and examples
- Encourage questions
- Offer to switch to quiz or teach-back mode"""

        super().__init__(
            instructions=instructions,
            tools=[
                explain_concept,
                self.return_to_main,
                self.switch_to_quiz,
                self.switch_to_teachback
            ]
        )
        self.content = content
        self._session = None
    
    async def on_enter(self) -> None:
        """Switch voice and start explaining"""
        if self._session:
            switch_session_voice(self._session, VOICE_LEARN)
        
        await self.session.send_text("Hi! I'm Matthew, your Learn Mode tutor. Let me explain this concept clearly for you.")
        # Automatically explain the concept
        await self.session.call_tool("explain_concept")
        await self.session.send_text("Would you like me to explain more, or shall we try a quiz or teach-back session?")
    
    @function_tool
    async def return_to_main(self, ctx: RunContext[dict]):
        """Return to main coordinator to select new concept"""
        return MainTutorAgent(self.content), "Returning to main tutor for concept selection"
    
    @function_tool
    async def switch_to_quiz(self, ctx: RunContext[dict]):
        """Switch to quiz mode for the same concept"""
        return QuizModeAgent(self.content), "Switching to Quiz Mode"
    
    @function_tool
    async def switch_to_teachback(self, ctx: RunContext[dict]):
        """Switch to teach-back mode for the same concept"""
        return TeachBackModeAgent(self.content), "Switching to Teach-Back Mode"

class QuizModeAgent(Agent):
    """Specialized agent for Quiz Mode with Anusha's voice"""
    def __init__(self, content: List[dict]):
        instructions = """You are Anusha, the Quiz Mode Tutor. Your voice is engaging and questioning.

Your role: Test students with multiple-choice questions and provide feedback.

When you enter:
1. Greet energetically and start a quiz
2. Use get_mcq() to get questions
3. Wait for answers and use evaluate_mcq() to score
4. Provide encouraging feedback
5. Offer more questions or mode switches

Style:
- Energetic and encouraging
- Celebrate correct answers
- Provide helpful hints for wrong answers
- Keep the energy high"""

        super().__init__(
            instructions=instructions,
            tools=[
                get_mcq,
                evaluate_mcq,
                self.return_to_main,
                self.switch_to_learn,
                self.switch_to_teachback
            ]
        )
        self.content = content
        self._session = None
    
    async def on_enter(self) -> None:
        """Switch voice and start quiz"""
        if self._session:
            switch_session_voice(self._session, VOICE_QUIZ)
        
        await self.session.send_text("Hey there! I'm Anusha, your Quiz Mode tutor. Ready for some questions? Let's test your knowledge!")
        # Automatically start with a question
        result = await self.session.call_tool("get_mcq")
        if isinstance(result, dict) and not result.get("error"):
            await self.session.send_text(f"Here's your question: {result['question']}")
            for i, option in enumerate(result['options']):
                await self.session.send_text(f"{chr(65+i)}) {option}")
            await self.session.send_text("What's your answer?")
    
    @function_tool
    async def return_to_main(self, ctx: RunContext[dict]):
        """Return to main coordinator"""
        return MainTutorAgent(self.content), "Returning to main tutor"
    
    @function_tool
    async def switch_to_learn(self, ctx: RunContext[dict]):
        """Switch to learn mode"""
        return LearnModeAgent(self.content), "Switching to Learn Mode"
    
    @function_tool
    async def switch_to_teachback(self, ctx: RunContext[dict]):
        """Switch to teach-back mode"""
        return TeachBackModeAgent(self.content), "Switching to Teach-Back Mode"

class TeachBackModeAgent(Agent):
    """Specialized agent for Teach-Back Mode with Ken's voice"""
    def __init__(self, content: List[dict]):
        instructions = """You are Ken, the Teach-Back Mode Tutor. Your voice is encouraging and feedback-focused.

Your role: Listen to student explanations and provide constructive feedback.

When you enter:
1. Greet supportively and ask for explanation
2. Listen carefully to their explanation
3. Use evaluate_teachback() to score and provide feedback
4. Offer encouragement and suggestions
5. Ask if they want to try again or switch modes

Style:
- Supportive and patient
- Focus on constructive feedback
- Encourage effort and improvement
- Help build confidence"""

        super().__init__(
            instructions=instructions,
            tools=[
                evaluate_teachback,
                self.return_to_main,
                self.switch_to_learn,
                self.switch_to_quiz
            ]
        )
        self.content = content
        self._session = None
    
    async def on_enter(self) -> None:
        """Switch voice and prompt for explanation"""
        if self._session:
            switch_session_voice(self._session, VOICE_TEACH)
        
        await self.session.send_text("Hello! I'm Ken, your Teach-Back tutor. I'd love to hear you explain the concept in your own words. This helps reinforce your learning. Please go ahead and explain what you understand about this topic.")
    
    @function_tool
    async def return_to_main(self, ctx: RunContext[dict]):
        """Return to main coordinator"""
        return MainTutorAgent(self.content), "Returning to main tutor"
    
    @function_tool
    async def switch_to_learn(self, ctx: RunContext[dict]):
        """Switch to learn mode"""
        return LearnModeAgent(self.content), "Switching to Learn Mode"
    
    @function_tool
    async def switch_to_quiz(self, ctx: RunContext[dict]):
        """Switch to Quiz Mode"""
        return QuizModeAgent(self.content), "Switching to Quiz Mode"
    


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

    # Create session with initial TTS
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY")),
        tts=murf.TTS(voice=VOICE_LEARN, style="Conversation", text_pacing=True),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata,
    )

    # Create main coordinator agent
    agent = MainTutorAgent(content)
    agent._session = session  # Pass session to agent for voice switching

    # Start session (MUST complete before event handlers are registered)
    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    # Pass session reference to all agents for voice switching
    agent._session = session

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
