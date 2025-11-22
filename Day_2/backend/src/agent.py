import logging
import json
import os
import asyncio
from datetime import datetime
from typing import Annotated, Literal
from dataclasses import dataclass, field

print("\n========== agent.py LOADED SUCCESSFULLY ==========\n")

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
    tokenize,
    metrics,
    MetricsCollectedEvent,
    RunContext,
    function_tool,
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# ORDER STATE
# ======================================================
@dataclass
class OrderState:
    """Coffee shop order state"""
    drinkType: str | None = None
    size: str | None = None
    milk: str | None = None
    extras: list[str] = field(default_factory=list)
    name: str | None = None
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.drinkType is not None,
            self.size is not None,
            self.milk is not None,
            self.extras is not None,
            self.name is not None
        ])
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "drinkType": self.drinkType,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name
        }

@dataclass
class Userdata:
    """User session data"""
    order: OrderState

# ======================================================
# BARISTA AGENT WITH FUNCTION TOOLS
# ======================================================

# Define function tools that will update the order state
@function_tool
async def set_drink_type(
    ctx: RunContext[Userdata],
    drink: Annotated[
        Literal["latte", "cappuccino", "americano", "espresso", "mocha", "coffee"],
        Field(description="The type of coffee drink the customer wants"),
    ],
) -> str:
    """Set the drink type. Call when customer specifies which coffee they want."""
    ctx.userdata.order.drinkType = drink
    print(f"☕ DRINK SET TO: {drink}")
    print(f"📊 Current order: {ctx.userdata.order.to_dict()}")
    return f"Got it! One {drink}."

@function_tool
async def set_size(
    ctx: RunContext[Userdata],
    size: Annotated[
        Literal["small", "medium", "large"],
        Field(description="The size of the drink"),
    ],
) -> str:
    """Set the size. Call when customer specifies small, medium, or large."""
    ctx.userdata.order.size = size
    print(f"📏 SIZE SET TO: {size}")
    print(f"📊 Current order: {ctx.userdata.order.to_dict()}")
    return f"{size.title()} size noted."

@function_tool
async def set_milk(
    ctx: RunContext[Userdata],
    milk: Annotated[
        Literal["whole", "skim", "almond", "oat"],
        Field(description="The type of milk for the drink"),
    ],
) -> str:
    """Set milk preference. Call when customer specifies milk type."""
    ctx.userdata.order.milk = milk
    print(f"🥛 MILK SET TO: {milk}")
    print(f"📊 Current order: {ctx.userdata.order.to_dict()}")
    return f"{milk.title()} milk, perfect."

@function_tool
async def set_extras(
    ctx: RunContext[Userdata],
    extras: Annotated[
        list[Literal["sugar", "whipped cream", "caramel", "extra shot"]] | None,
        Field(description="List of extras, or empty/None for no extras"),
    ] = None,
) -> str:
    """Set extras. Call when customer specifies add-ons or says no extras."""
    ctx.userdata.order.extras = extras if extras else []
    print(f"🎯 EXTRAS SET TO: {ctx.userdata.order.extras}")
    print(f"📊 Current order: {ctx.userdata.order.to_dict()}")
    
    if ctx.userdata.order.extras:
        return f"Added {', '.join(ctx.userdata.order.extras)}."
    return "No extras, got it."

@function_tool
async def set_name(
    ctx: RunContext[Userdata],
    name: Annotated[str, Field(description="Customer's name for the order")],
) -> str:
    """Set customer name. Call when customer provides their name."""
    ctx.userdata.order.name = name.strip().title()
    print(f"👤 NAME SET TO: {ctx.userdata.order.name}")
    print(f"📊 Current order: {ctx.userdata.order.to_dict()}")
    return f"Great, {ctx.userdata.order.name}!"

@function_tool
async def complete_order(ctx: RunContext[Userdata]) -> str:
    """Finalize and save order to JSON. ONLY call when ALL fields are filled."""
    order = ctx.userdata.order
    
    if not order.is_complete():
        missing = []
        if not order.drinkType: missing.append("drink type")
        if not order.size: missing.append("size")
        if not order.milk: missing.append("milk")
        if order.extras is None: missing.append("extras")
        if not order.name: missing.append("name")
        
        print(f"❌ Cannot complete - missing: {', '.join(missing)}")
        return f"Cannot complete order yet. Still need: {', '.join(missing)}"
    
    print(f"🎉 ORDER COMPLETE: {order.to_dict()}")
    
    try:
        save_order_to_json(order)
        extras_text = f" with {', '.join(order.extras)}" if order.extras else ""
        return f"Perfect! Your {order.size} {order.drinkType} with {order.milk} milk{extras_text} is all set, {order.name}. We'll have that ready shortly!"
    except Exception as e:
        print(f"❌ FAILED TO SAVE ORDER: {e}")
        return "Order recorded but there was an issue saving it. We'll make your drink!"

class BaristaAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a friendly barista at Murf AI Cafe.
            Take coffee orders by collecting: drink type, size, milk, extras, and name.
            
            Available: latte, cappuccino, americano, espresso, mocha, coffee
            Sizes: small, medium, large
            Milk: whole, skim, almond, oat
            Extras: sugar, whipped cream, caramel, extra shot, or none
            
            Use the tools to record each part. Ask for missing info one at a time.
            Once complete, use complete_order to save. Be friendly and concise.
            """,
            tools=[
                set_drink_type,
                set_size,
                set_milk,
                set_extras,
                set_name,
                complete_order,
            ],
        )

def create_empty_order():
    return OrderState()

# ======================================================
# ORDER SAVE FOLDER
# ======================================================
def get_orders_folder():
    base_dir = os.path.dirname(__file__)   # src/
    backend_dir = os.path.abspath(os.path.join(base_dir, ".."))
    folder = os.path.join(backend_dir, "orders")
    os.makedirs(folder, exist_ok=True)
    return folder

def save_order_to_json(order: OrderState) -> str:
    print(f"\n🔄 ATTEMPTING TO SAVE ORDER: {order.to_dict()}")
    folder = get_orders_folder()
    filename = datetime.now().strftime("order_%Y%m%dT%H%M%S.json")
    path = os.path.join(folder, filename)

    try:
        with open(path, "w") as f:
            json.dump(order.to_dict(), f, indent=4)
        
        print("\n✅ === ORDER SAVED SUCCESSFULLY ===")
        print(f"📁 Path: {path}")
        print(f"📋 Order Details: {json.dumps(order.to_dict(), indent=2)}")
        print("=====================================\n")
        
        return path
    except Exception as e:
        print(f"\n❌ ERROR SAVING ORDER: {e}")
        print(f"📁 Attempted path: {path}")
        print(f"📋 Order data: {order.to_dict()}")
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
# PREWARM
# ======================================================
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

# ======================================
#   MAIN ENTRYPOINT
# ======================================
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "="*50)
    print("🏪 BREW & BEAN CAFE AGENT STARTING")
    print("📁 Orders folder:", get_orders_folder())
    print("🎤 Ready to take customer orders!")
    print("="*50 + "\n")

    # Create user session data with empty order
    userdata = Userdata(order=create_empty_order())
    
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"\n🆕 NEW CUSTOMER SESSION: {session_id}")
    print(f"📝 Initial order state: {userdata.order.to_dict()}\n")

    # Create session with userdata
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,  # Pass userdata to session
    )

    usage_collector = metrics.UsageCollector()
    @session.on("metrics_collected")
    def _on_metrics(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

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
