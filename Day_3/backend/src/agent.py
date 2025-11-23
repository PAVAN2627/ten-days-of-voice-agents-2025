import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Annotated

from dotenv import load_dotenv
from pydantic import Field

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
    metrics,
    MetricsCollectedEvent,
)

from livekit.plugins import google, murf, deepgram, silero, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

print("\n========== DAY 3 WELLNESS AGENT (FINAL) LOADED ==========\n")

# -----------------------
# Data models
# -----------------------
@dataclass
class WellnessEntry:
    timestamp: str
    mood: str
    energy: str
    stress: str
    goals: List[str]
    summary: str

@dataclass
class WellnessState:
    mood: Optional[str] = None
    energy: Optional[str] = None
    stress: Optional[str] = None
    goals: List[str] = field(default_factory=list)

@dataclass
class Userdata:
    wellness: WellnessState
    history: List[dict]

# -----------------------
# File helpers
# -----------------------
def get_logs_folder() -> str:
    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "wellness_logs"))
    os.makedirs(folder, exist_ok=True)
    return folder

def get_log_file() -> str:
    return os.path.join(get_logs_folder(), "wellness_log.json")

def load_history() -> List[dict]:
    path = get_log_file()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"⚠️ Failed to load history: {e}")
        return []

def save_entry(entry: WellnessEntry) -> None:
    path = get_log_file()
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
                except Exception:
                    history = []
        else:
            history = []

        history.append(entry.__dict__)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"\n✅ Wellness entry saved: {path}")
        print(json.dumps(entry.__dict__, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ ERROR saving entry: {e}")
        raise

# -----------------------
# Advice generator
# -----------------------
def generate_original_advice(mood: str, energy: str, stress: str, goals: List[str]) -> str:
    """
    Create an original, contextual, emotionally-supportive advice paragraph.
    The wording is constructed programmatically each time (not strict templates).
    """
    # normalize keywords
    m = (mood or "").strip().lower()
    e = (energy or "").strip().lower()
    s = (stress or "").strip().lower()
    g = [str(x).strip() for x in (goals or [])]

    parts: List[str] = []

    # Start reflection line (unique)
    parts.append("Thanks for sharing—I've taken that in.")

    # If mood low / words indicating low
    low_mood_keywords = ("sad", "low", "down", "bad", "unhappy", "tired", "depressed")
    stressed_keywords = ("stres", "anx", "worried", "tense", "pressure", "panic")
    positive_keywords = ("good", "happy", "great", "fine", "well", "okay", "content")

    # energy handling
    if e in ("low", "low energy", "tired", "drained"):
        parts.append("Right now your energy seems limited — that calls for gentleness.")
        parts.append("If possible, aim for one small, doable step that won't use much energy.")
    elif e in ("high", "high energy", "energized", "very high"):
        parts.append("You have momentum — it could be a good moment to make a meaningful push on one thing.")
        parts.append("Choose a clear, short chunk of work so energy helps you finish it cleanly.")
    else:
        # medium / unspecified
        parts.append("You have steady energy; small plans and short breaks can keep that steady pace.")

    # mood handling
    if any(k in m for k in low_mood_keywords):
        parts.append("Be kind to yourself today — small acts of care really do add up.")
        parts.append("If a task feels heavy, break it into the tiniest next step and celebrate that step.")
    elif any(k in m for k in positive_keywords):
        parts.append("That positive tone is useful — consider using it to do one thing that matters to you.")
        parts.append("A short pause to notice progress will help keep the good feeling steady.")
    else:
        parts.append("You're in a place where small, practical moves will make the day feel steadier.")

    # stress handling
    if any(k in s for k in stressed_keywords):
        parts.append("When stress shows up, try a short grounding action: 30 seconds of steady breathing or a two-minute walk.")
    elif "no stress" in s or s.strip() == "":
        parts.append("Since stress seems low, it's a great chance to use small windows productively and kindly.")
    else:
        parts.append("If something is bothering you, naming the smallest next action can reduce how big the problem feels.")

    # goals handling
    if g:
        # Build a goal-tailored encouragement (unique)
        first_goal = g[0]
        parts.append(f"For your goal — “{first_goal}” — try splitting it into a micro-step you can finish within 15–30 minutes.")
        if len(g) > 1:
            parts.append("For the rest, pick one to focus on so you don't spread yourself thin.")
    else:
        parts.append("If you're not sure about goals today, one tiny intention (even 'rest a little') is a useful plan.")

    # final gentle nudge
    parts.append("Remember: a small kind action toward yourself is still progress. I'll remember this for next time.")

    # Join into a single, natural paragraph but keep short sentences
    advice = " ".join(parts)
    return advice

# -----------------------
# Tools (function_tool handlers)
# -----------------------
@function_tool
async def set_mood(ctx: RunContext[Userdata], mood: Annotated[str, Field(description="User mood (in own words)")] ):
    val = mood.strip() or "Not specified"
    ctx.userdata.wellness.mood = val
    print(f"📝 set_mood -> {val}")
    return f"Thanks — I've recorded your mood as: {val}."

@function_tool
async def set_energy(ctx: RunContext[Userdata], energy: Annotated[str, Field(description="Energy level: low/medium/high or free text")] ):
    val = energy.strip() or "Not specified"
    ctx.userdata.wellness.energy = val
    print(f"⚡ set_energy -> {val}")
    return f"Okay — energy set to: {val}."

@function_tool
async def set_stress(ctx: RunContext[Userdata], stress: Annotated[str, Field(description="Stress description or 'no'")] ):
    raw = (stress or "").strip()
    if raw.lower() in ("no", "none", "nothing", "no stress", "i am fine", "im fine", ""):
        val = "No stress reported"
    else:
        val = raw
    ctx.userdata.wellness.stress = val
    print(f"😌 set_stress -> {val}")
    return f"Noted — stress: {val}."

@function_tool
async def set_goals(ctx: RunContext[Userdata], goals: Annotated[List[str], Field(description="List of 1–3 small goals")] ):
    cleaned = [g.strip() for g in (goals or []) if isinstance(g, str) and g.strip()]
    ctx.userdata.wellness.goals = cleaned
    print(f"🎯 set_goals -> {cleaned}")
    if cleaned:
        return f"Got it — your goals: {', '.join(cleaned)}."
    return "No goals recorded."

@function_tool
async def complete_checkin(ctx: RunContext[Userdata]):
    w = ctx.userdata.wellness
    w.mood = w.mood or "Not specified"
    w.energy = w.energy or "Not specified"
    w.stress = w.stress or "No stress reported"
    w.goals = w.goals or []

    goals_text = ", ".join(w.goals) if w.goals else "none"
    summary = f"Mood: {w.mood}. Energy: {w.energy}. Stress: {w.stress}. Goals: {goals_text}."

    entry = WellnessEntry(
        timestamp=datetime.utcnow().isoformat() + "Z",
        mood=w.mood,
        energy=w.energy,
        stress=w.stress,
        goals=w.goals,
        summary=summary
    )

    try:
        save_entry(entry)
    except Exception as e:
        print(f"❌ complete_checkin: failed to save entry: {e}")
        return "I recorded the check-in in memory, but I couldn't save it to disk."

    # generate original advice (unique)
    advice = generate_original_advice(w.mood, w.energy, w.stress, w.goals)

    # Return friendly recap + advice
    return f"Check-in saved. {summary} Advice: {advice}"

# -----------------------
# Agent
# -----------------------
class WellnessAgent(Agent):
    def __init__(self, history: List[dict]):
        # Build a full recap of last entry if exists
        if history:
            last = history[-1]
            last_full = (
                f"Previously you logged:\n"
                f"- You Mood was: {last.get('mood', 'n/a')}\n"
                f"-    your Energy was: {last.get('energy', 'n/a')}\n"
                f"-    your Stress was: {last.get('stress', 'n/a')}\n"
                f"- and you said your Goals were: {', '.join(last.get('goals', [])) or 'none'}\n"
                "Now tell me how are you feeling right now?"
            )
        else:
            last_full = "I don't have any past check-ins for you yet."

        super().__init__(
            instructions=f"""
You are a warm, supportive daily wellness companion.
Tone: kind, short sentences, emotionally supportive.
Do NOT offer medical advice or diagnosis.

Flow:
1) Greet the user briefly.
2) If previous check-in exists, mention the full recap (as provided below) before asking today's questions.
3) Ask about mood (one question at a time).
4) Ask about energy.
5) Ask about stress.
6) Ask for 1–3 small goals.
7) After all collected, generate original, context-aware emotional guidance (not canned templates), then call complete_checkin.
8) End with a recap and confirm.

Previous recap to mention if present:
{last_full}

Ask only one question at a time. Keep the conversation grounded and gentle.
""",
            tools=[set_mood, set_energy, set_stress, set_goals, complete_checkin],
        )

# -----------------------
# Prewarm: load VAD
# -----------------------
def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception as e:
        # non-fatal: proceed without local VAD if it fails
        print(f"⚠️ prewarm: VAD load failed: {e}")
        proc.userdata["vad"] = None

# -----------------------
# Entrypoint
# -----------------------
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    print("\n=== WELLNESS AGENT STARTING ===")
    print("Logs folder:", get_logs_folder())

    history = load_history()
    userdata = Userdata(wellness=WellnessState(), history=history)

    # Build greeting: if history present, provide full recap before asking today's mood
    if history:
        last = history[-1]
        greeting = (
            "Hi — welcome back. I see your last check-in:\n"
            f"- Mood: {last.get('mood', 'n/a')}\n"
            f"- Energy: {last.get('energy', 'n/a')}\n"
            f"- Stress: {last.get('stress', 'n/a')}\n"
            f"- Goals: {', '.join(last.get('goals', [])) or 'none'}.\n"
            "now tell me How are you feeling right now?"
        )
    else:
        greeting = "Hi! It's nice to meet you — I do a short daily check-in. How are you feeling right now?"

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="tanushree",   # female voice from Murf voice list
            style="Conversation",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata
    )

    # start session (no unsupported kwargs)
    try:
        await session.start(
            agent=WellnessAgent(history),
            room=ctx.room,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC()
            )
        )
    except TypeError as e:
        # defensive: if start signature differs in your environment, print and re-raise
        print(f"❌ session.start() error: {e}")
        raise

    # Send greeting text to the user (this will be converted to TTS)
    try:
        await session.send_text(greeting)
    except Exception as e:
        # fallback: just log
        print(f"⚠️ send_text failed: {e}")

    # collect metrics (optional)
    usage_collector = metrics.UsageCollector()
    @session.on("metrics_collected")
    def _on_metrics(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

    # connect the job to allow the session lifecycle
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
