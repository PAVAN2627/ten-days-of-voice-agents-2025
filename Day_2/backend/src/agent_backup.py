import logging
import json
import os
import asyncio
from datetime import datetime

print("\n========== agent.py LOADED SUCCESSFULLY ==========\n")

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    tokenize,
    metrics,
    MetricsCollectedEvent
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# BARISTA AGENT
# ======================================================
class BaristaAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a friendly barista at Copilot Cafe taking orders.
            DO NOT ask questions - the system will handle the conversation flow.
            Just acknowledge what the customer says naturally and briefly.
            Keep all responses under 10 words.
            """
        )

# ======================================================
# ORDER STATE
# ======================================================
def create_empty_order():
    return {
        "drinkType": None,
        "size": None,
        "milk": None,
        "extras": None,
        "name": None
    }

ORDER_FIELDS = ["drinkType", "size", "milk", "extras", "name"]

def get_missing_field(order):
    for f in ORDER_FIELDS:
        if order[f] is None:
            return f
    return None

# ======================================================
# ORDER SAVE FOLDER
# ======================================================
def get_orders_folder():
    base_dir = os.path.dirname(__file__)   # src/
    backend_dir = os.path.abspath(os.path.join(base_dir, ".."))
    folder = os.path.join(backend_dir, "orders")
    os.makedirs(folder, exist_ok=True)
    return folder

def save_order_to_json(order):
    print(f"\n🔄 ATTEMPTING TO SAVE ORDER: {order}")
    folder = get_orders_folder()
    filename = datetime.now().strftime("order_%Y%m%dT%H%M%S.json")
    path = os.path.join(folder, filename)

    try:
        with open(path, "w") as f:
            json.dump(order, f, indent=4)
        
        print("\n✅ === ORDER SAVED SUCCESSFULLY ===")
        print(f"📁 Path: {path}")
        print(f"📋 Order Details: {json.dumps(order, indent=2)}")
        print("=====================================\n")
        
        return path
    except Exception as e:
        print(f"\n❌ ERROR SAVING ORDER: {e}")
        print(f"📁 Attempted path: {path}")
        print(f"📋 Order data: {order}")
        print("===============================\n")
        raise e

# Test function to verify order saving works
def test_order_saving():
    """Test function to verify order saving functionality"""
    test_order = {
        "drinkType": "latte",
        "size": "medium", 
        "milk": "oat",
        "extras": ["extra shot"],
        "name": "TestCustomer"
    }
    
    try:
        path = save_order_to_json(test_order)
        print(f"✅ Test order saved successfully to: {path}")
        return True
    except Exception as e:
        print(f"❌ Test order failed: {e}")
        return False

# ======================================================
# HELPERS
# ======================================================
def pick(text, options):
    t = text.lower()
    for opt in options:
        if opt.lower() in t:
            return opt
    return None

def parse_extras(text):
    t = text.lower()
    if "none" in t or "no extra" in t or "nothing" in t:
        return []
    return [text.strip()]

# ======================================================
# PREWARM
# ======================================================
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

# ======================================================
# HANDLE USER MESSAGE
# ======================================================
async def handle_user_message(ev, session: AgentSession, order):
    raw = ev.text.strip()
    text = raw.lower()
    
    print(f"\n🎤 USER SAID: '{raw}'")
    print(f"📊 CURRENT ORDER STATE: {order}")
    
    missing = get_missing_field(order)
    print(f"🔍 MISSING FIELD: {missing}")

    if missing == "drinkType":
        d = pick(text, ["latte", "cappuccino", "americano", "coffee", "espresso", "mocha"])
        print(f"☕ DETECTED DRINK: {d}")
        if d:
            order["drinkType"] = d
            print(f"✅ DRINK SET TO: {d}")
            await session.say("What size would you like? Small, medium, or large?")
        else:
            print("❌ NO VALID DRINK DETECTED")
            await session.say("Which drink would you like? We have latte, cappuccino, americano, coffee, espresso, or mocha.")
        return

    if missing == "size":
        s = pick(text, ["small", "medium", "large"])
        print(f"📏 DETECTED SIZE: {s}")
        if s:
            order["size"] = s
            print(f"✅ SIZE SET TO: {s}")
            await session.say("Which milk would you like? Whole, skim, almond, or oat?")
        else:
            print("❌ NO VALID SIZE DETECTED")
            await session.say("Please choose small, medium, or large.")
        return

    if missing == "milk":
        m = pick(text, ["whole", "skim", "almond", "oat"])
        print(f"🥛 DETECTED MILK: {m}")
        if m:
            order["milk"] = m
            print(f"✅ MILK SET TO: {m}")
            await session.say("Any extras? Like sugar, whipped cream, caramel, or none?")
        else:
            print("❌ NO VALID MILK DETECTED")
            await session.say("Which milk would you like? Whole, skim, almond, or oat?")
        return

    if missing == "extras":
        extras = parse_extras(text)
        order["extras"] = extras
        print(f"🎯 DETECTED EXTRAS: {extras}")
        print(f"✅ EXTRAS SET TO: {extras}")
        await session.say("Great! What name should I put for the order?")
        return

    if missing == "name":
        name = raw.split()[0].title() if raw.split() else "Customer"
        order["name"] = name
        print(f"👤 DETECTED NAME: {name}")
        print(f"✅ NAME SET TO: {name}")
        print(f"🎉 ORDER COMPLETE: {order}")

        # SAVE ORDER
        try:
            path = save_order_to_json(order)
            await session.say(f"Thank you {order['name']}! Your {order['size']} {order['drinkType']} with {order['milk']} milk has been saved. Have a great day!")
        except Exception as e:
            print(f"❌ FAILED TO SAVE ORDER: {e}")
            await session.say(f"Thank you {order['name']}! I've taken your order but there was an issue saving it. Please let the manager know.")
        return

# ======================================
#   MAIN ENTRYPOINT
# ======================================
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "="*50)
    print("🏪 COPILOT CAFE AGENT STARTING")
    print("📁 Orders folder:", get_orders_folder())
    print("🎤 Ready to take customer orders!")
    print("="*50 + "\n")

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
    )

    usage_collector = metrics.UsageCollector()
    @session.on("metrics_collected")
    def _on_metrics(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

    # Create fresh order state for this customer session
    order_state = create_empty_order()
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\n🆕 NEW CUSTOMER SESSION: {session_id}")
    print(f"📝 Initial order state: {order_state}\n")
    
    # Flag to track if we're using custom logic
    using_custom_logic = True

    @session.on("user_speech_committed")
    def on_user_speech(ev):
        user_text = ev.alternatives[0].text
        print(f"\n📨 [Session {session_id}] User speech: {user_text}")
        
        # Create a simple object with text attribute for compatibility
        class TranscriptEvent:
            def __init__(self, text):
                self.text = text
        
        transcript = TranscriptEvent(user_text)
        asyncio.create_task(handle_user_message(transcript, session, order_state))

    # Add initial greeting when session starts
    async def send_greeting():
        await asyncio.sleep(1)  # Small delay to ensure connection
        if all(v is None for v in order_state.values()):  # Only greet if no order started
            print("👋 Sending welcome greeting...")
            await session.say("Welcome to Copilot Cafe! What drink can I get started for you today?")
    
    # Start greeting task
    asyncio.create_task(send_greeting())

    await session.start(
        agent=BaristaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()

# ======================================================
# RUN WORKER
# ======================================================
if __name__ == "__main__":
    print("\n>>> RUNNING WORKER...\n")
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
