import logging
import os
import sys
import json
from pathlib import Path
from typing import Optional
from enum import Enum

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, deepgram, noise_cancellation, openai
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
logger.info("Improv Battle Host Starting...")

load_dotenv(".env.local")


class GamePhase(Enum):
    INTRO = "intro"
    AWAITING_IMPROV = "awaiting_improv"
    REACTING = "reacting"
    DONE = "done"


class ImprovisationState:
    def __init__(self):
        self.player_name: Optional[str] = None
        self.current_round: int = 0
        self.max_rounds: int = 3
        self.rounds: list = []  # Each: {"scenario": str, "player_response": str, "host_reaction": str}
        self.phase: GamePhase = GamePhase.INTRO
        self.improv_scenarios = [
            "You are an auto-rickshaw driver explaining to a tourist about the scenic route through the city.",
            "You are a street food vendor describing your famous golgappa recipe to a curious customer.",
            "You are a customer service agent helping someone with a large rice order on an app.",
            "You are a wedding planner sharing the story of a memorable wedding entrance.",
            "You are a chai vendor explaining why chai is special to a coffee shop visitor.",
        ]
        self.current_scenario: Optional[str] = None

    def get_next_scenario(self) -> str:
        """Get the next improv scenario"""
        if self.current_round < len(self.improv_scenarios):
            self.current_scenario = self.improv_scenarios[self.current_round]
            return self.current_scenario
        return self.improv_scenarios[self.current_round % len(self.improv_scenarios)]

    def reset(self):
        """Reset game state"""
        self.player_name = None
        self.current_round = 0
        self.rounds = []
        self.phase = GamePhase.INTRO
        self.current_scenario = None


improv_state = ImprovisationState()


class ImprovisationHost(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly host of an improv game show. Your role is to be entertaining and supportive.

Your responsibilities:
1. Welcome players warmly
2. Present improv scenarios clearly
3. React to performances with encouraging feedback
4. After each improvisation, say "Round X complete!" where X is the round number
5. Provide helpful suggestions
6. Comment on creative choices
7. Guide players through 3 rounds
8. Give a positive closing summary

Game Format:
- Present scenarios one at a time
- Let players improvise in character
- React with supportive feedback
- After each performance, say "Round 1 complete!" or "Round 2 complete!" or "Round 3 complete!"
- Move to the next round
- Celebrate creativity

Your Personality:
- Friendly and encouraging
- Enthusiastic about creativity
- Supportive and helpful
- Professional and respectful

Response Style:
- Conversational and warm
- Clear and concise
- Natural speaking style
- Positive and engaging
- Keep responses brief
- After giving feedback, include the phrase "Round X complete!" where X is 1, 2, or 3"""
        )

    @function_tool
    async def start_game(self, context: RunContext, player_name: str) -> str:
        """Initialize the improv game with player name."""
        improv_state.player_name = player_name
        improv_state.phase = GamePhase.INTRO
        
        result = f"Welcome {player_name}! I'm your host and I'm excited you're here. "
        result += "Here's how this works: I'll give you improv scenarios. You improvise in character, and I'll give you feedback. "
        result += "We're doing three rounds. Ready? Let's start round one!"
        
        return result

    @function_tool
    async def present_scenario(self, context: RunContext) -> str:
        """Present the current improv scenario to the player."""
        if improv_state.current_round >= improv_state.max_rounds:
            improv_state.phase = GamePhase.DONE
            return await self.end_game(context)
        
        scenario = improv_state.get_next_scenario()
        improv_state.phase = GamePhase.AWAITING_IMPROV
        
        # Don't announce round number here - just present the scenario
        result = f"Here's your scenario: {scenario} "
        result += "Jump right in and start improvising whenever you're ready!"
        
        return result

    @function_tool
    async def react_to_improv(self, context: RunContext, player_response: str) -> str:
        """Host reacts to the player's improvisation."""
        # Mark the round as complete BEFORE incrementing
        completed_round = improv_state.current_round + 1
        
        improv_state.rounds.append({
            "round": completed_round,
            "scenario": improv_state.current_scenario,
            "player_response": player_response
        })
        
        # Create varied reactions based on response quality assessment
        reactions = [
            f"Fantastic work, {improv_state.player_name}! Your {improv_state.current_scenario.split()[3]} was charming and believable—great use of character logic and confident delivery!",
            f"That was pretty solid, {improv_state.player_name}! I especially liked how you committed to the character. Good improv instincts showing through!",
            f"Interesting take on that! You went in a direction I didn't expect. Creative choice—let's see what you do next!",
            f"Oh, that was gold! The specific details you added made it hilarious. That's the kind of committed improv that works!",
            f"Nice effort! You could lean more into the absurdity next time. Improv is about exploring the moment fully!",
            f"That was genuinely funny! The way you handled the awkwardness felt really authentic. I can tell you're enjoying this!",
        ]
        
        import random
        reaction = random.choice(reactions)
        
        improv_state.rounds[-1]["host_reaction"] = reaction
        improv_state.current_round += 1
        
        # Build response with clear round completion marker
        result = f"{reaction}\n\nRound {completed_round} complete!"
        
        if improv_state.current_round >= improv_state.max_rounds:
            improv_state.phase = GamePhase.DONE
            return result + " That's our last round! Let me give you some closing thoughts..."
        else:
            improv_state.phase = GamePhase.AWAITING_IMPROV
            next_round = improv_state.current_round + 1
            return result + f"\n\nNow, for round {next_round}:"

    @function_tool
    async def end_game(self, context: RunContext) -> str:
        """Provide closing summary and end the game."""
        improv_state.phase = GamePhase.DONE
        
        closing = f"Well {improv_state.player_name}, that's a wrap! "
        closing += "You showed up with commitment and creativity. You found specific details and built interesting worlds. "
        closing += "Your best moments were when you leaned into the character fully. "
        closing += "You're character-focused and detail-oriented. "
        closing += "Keep doing that, and you'll only get better. Thanks for playing - you were fantastic!"
        
        return closing

    @function_tool
    async def get_game_status(self, context: RunContext) -> str:
        """Get current game status."""
        if improv_state.player_name is None:
            return "Game not started yet. Say something like 'My name is Alex' to begin!"
        
        result = f"Player: {improv_state.player_name}\n"
        result += f"Round: {improv_state.current_round + 1}/{improv_state.max_rounds}\n"
        result += f"Phase: {improv_state.phase.value}\n"
        
        if improv_state.current_scenario:
            result += f"Current Scenario: {improv_state.current_scenario}\n"
        
        if improv_state.rounds:
            result += f"Completed Rounds: {len(improv_state.rounds)}\n"
        
        return result


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline with Azure OpenAI as the LLM
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM.with_azure(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            ),
        tts=murf.TTS(
                voice="en-IN-anusha", 
                style="Conversation",
            ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=ImprovisationHost(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
