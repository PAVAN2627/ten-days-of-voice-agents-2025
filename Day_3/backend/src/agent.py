# src/agent.py
import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Annotated

import requests

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
load_dotenv(".env.local")  # load TODOIST_API_TOKEN / TODOIST_PROJECT_ID if present

print("\n========== DAY 3 WELLNESS AGENT (TODOIST MCP) LOADED ==========\n")

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

        print(f"\n✅ Wellness entry saved locally: {path}")
        print(json.dumps(entry.__dict__, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ ERROR saving entry: {e}")
        raise

# -----------------------
# Todoist integration (Option A: push every check-in)
# -----------------------
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")
TODOIST_PROJECT_ID = os.getenv("TODOIST_PROJECT_ID")  # should be numeric string

def todoist_headers():
    return {
        "Authorization": f"Bearer {TODOIST_API_TOKEN}",
        "Content-Type": "application/json",
    }

def create_todoist_task(content: str, project_id: Optional[str] = None, parent_id: Optional[str] = None) -> dict:
    """
    Create a Todoist task. Returns parsed JSON on success.
    """
    url = "https://api.todoist.com/rest/v2/tasks"
    payload = {"content": content}
    if project_id:
        # API expects numeric project_id
        try:
            payload["project_id"] = int(project_id)
        except Exception:
            # if conversion fails, omit project_id and let task be created in default project (not recommended)
            pass
    if parent_id:
        payload["parent_id"] = parent_id

    resp = requests.post(url, headers=todoist_headers(), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

def push_checkin_to_todoist(entry: WellnessEntry) -> dict:
    """
    Push the check-in to Todoist:
    - Create a parent task with the check-in summary
    - Create child tasks for each goal (if any)
    Returns a dict with status info.
    """
    if not TODOIST_API_TOKEN:
        return {"status": "skipped", "reason": "TODOIST_API_TOKEN not set"}

    result = {"created": [], "errors": []}
    try:
        # Parent task content
        timestamp_short = entry.timestamp.replace("T", " ").replace("Z", "")
        parent_content = f"Wellness check-in ({timestamp_short}) — {entry.summary}"
        parent = create_todoist_task(parent_content, project_id=TODOIST_PROJECT_ID)
        parent_id = parent.get("id")
        result["created"].append({"parent": parent})

        # Create a child task for each goal
        for g in entry.goals:
            try:
                child_content = f"Goal: {g}"
                child = create_todoist_task(child_content, project_id=TODOIST_PROJECT_ID, parent_id=parent_id)
                result["created"].append({"child": child})
            except Exception as e:
                result["errors"].append({"goal": g, "error": str(e)})

        return {"status": "ok", "detail": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# -----------------------
# Advice generator (original)
# -----------------------
def generate_original_advice(mood: str, energy: str, stress: str, goals: List[str]) -> str:
    m = (mood or "").strip().lower()
    e = (energy or "").strip().lower()
    s = (stress or "").strip().lower()
    g = [str(x).strip() for x in (goals or [])]

    parts: List[str] = []
    parts.append("Thanks for sharing — I hear you.")

    low_mood_keywords = ("sad", "low", "down", "bad", "unhappy", "tired", "depressed")
    stressed_keywords = ("stres", "anx", "worried", "tense", "pressure", "panic")
    positive_keywords = ("good", "happy", "great", "fine", "well", "okay", "content")

    if e in ("low", "low energy", "tired", "drained"):
        parts.append("Energy feels small today; be gentle with what you ask of yourself.")
        parts.append("Pick one tiny action that feels doable and stop there if it becomes too much.")
    elif e in ("high", "high energy", "energized", "very high"):
        parts.append("You’ve got momentum — channel it into one clear, short task to use it well.")
        parts.append("Try to keep the task bite-sized so the win comes quickly.")
    else:
        parts.append("A steady pace will help. Little wins and short breaks suit you today.")

    if any(k in m for k in low_mood_keywords):
        parts.append("When your mood is low, gentle steps and small comforts matter more than big effort.")
        parts.append("Consider a short, kind activity — a warm drink, a 5-minute stretch, or a pause.")
    elif any(k in m for k in positive_keywords):
        parts.append("Your positive mood can be used to do something meaningful, even if small.")
        parts.append("Notice and name one small success to keep the momentum kind and real.")
    else:
        parts.append("A practical next step — even a tiny one — will help the day feel steadier.")

    if any(k in s for k in stressed_keywords):
        parts.append("If stress feels present, try a two-minute grounding exercise or a short walk to soften it.")
    elif "no stress" in s or s.strip() == "":
        parts.append("Stress seems low — use that space gently for something you value or for rest.")
    else:
        parts.append("If something is nagging you, writing one smallest next action can reduce its weight.")

    if g:
        first_goal = g[0]
        parts.append(f"For your goal “{first_goal}”, try a micro-step you can finish in 15–30 minutes.")
        if len(g) > 1:
            parts.append("Focus on one goal at a time rather than all at once.")
    else:
        parts.append("If you don't have a goal today, consider a small intention like 'rest for 10 minutes'.")

    parts.append("Small, kind steps add up — they count.")

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

    # Push to Todoist (Option A: automatic)
    todoist_result = push_checkin_to_todoist(entry)

    # Generate original advice
    advice = generate_original_advice(w.mood, w.energy, w.stress, w.goals)

    # Friendly recap + advice + todoist status
    todoist_status = todoist_result.get("status", "skipped")
    return f"Check-in saved. {summary} Advice: {advice} (todoist: {todoist_status})"

# -----------------------
# Agent
# -----------------------
class WellnessAgent(Agent):
    def __init__(self, history: List[dict]):
        if history:
            last = history[-1]
            last_full = (
                f"Your last check-in:\n"
                f"- Mood: {last.get('mood', 'n/a')}\n"
                f"- Energy: {last.get('energy', 'n/a')}\n"
                f"- Stress: {last.get('stress', 'n/a')}\n"
                f"- Goals: {', '.join(last.get('goals', [])) or 'none'}\n"
            )
        else:
            last_full = "This is your first logged check-in."

        super().__init__(
            instructions=f"""
You are a warm, supportive daily wellness companion.
Tone: kind, short sentences, emotionally supportive.
Do NOT offer medical advice or diagnosis.

Flow:
1) Greet the user briefly.
2) If previous check-in exists, say the full recap (shown below) before asking today's questions.
3) Ask about mood (one question at a time).
4) Ask about energy.
5) Ask about stress.
6) Ask for 1–3 small goals.
7) After collecting all, generate original, context-aware emotional guidance (no canned templates), call complete_checkin, and then recap.

Previous recap to mention if present:
{last_full}

Ask only one question at a time. Keep the conversation grounded and gentle.
""",
            tools=[set_mood, set_energy, set_stress, set_goals, complete_checkin],
        )

# -----------------------
# Prewarm
# -----------------------
def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception as e:
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

    if history:
        last = history[-1]
        greeting = (
            "Hi, welcome back. Here's your last check-in:\n"
            f"- Mood: {last.get('mood', 'n/a')}\n"
            f"- Energy: {last.get('energy', 'n/a')}\n"
            f"- Stress: {last.get('stress', 'n/a')}\n"
            f"- Goals: {', '.join(last.get('goals', [])) or 'none'}.\n"
            "How are you feeling today?"
        )
    else:
        greeting = "Hi! It's nice to meet you. I do a short daily check-in. How are you feeling today?"

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="tanushree",
            style="Conversation",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata
    )

    # Start session
    await session.start(
        agent=WellnessAgent(history),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    # Send greeting
    try:
        await session.send_text(greeting)
    except Exception as e:
        print(f"⚠️ send_text failed: {e}")

    # metrics
    usage_collector = metrics.UsageCollector()
    @session.on("metrics_collected")
    def _on_metrics(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

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
