"""
Test script to identify which events are actually fired by LiveKit agents
"""
import logging
from livekit.agents import AgentSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print all available events on AgentSession
print("AgentSession available methods and attributes:")
for attr in dir(AgentSession):
    if not attr.startswith("_"):
        print(f"  - {attr}")

# Check for event decorators
print("\nLooking for event registration methods:")
for attr in dir(AgentSession):
    if "on" in attr.lower() or "event" in attr.lower() or "listen" in attr.lower():
        print(f"  - {attr}")

# Print the actual session instance to see what we can work with
print("\nChecking AgentSession.on method signature:")
if hasattr(AgentSession, "on"):
    import inspect
    try:
        sig = inspect.signature(AgentSession.on)
        print(f"  Signature: {sig}")
        # Try to get docstring
        doc = AgentSession.on.__doc__
        if doc:
            print(f"  Docstring: {doc[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
