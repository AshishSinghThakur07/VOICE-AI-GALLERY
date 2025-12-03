"""Day 10: Voice Improv Battle Agent."""
import logging
import json
import random
import asyncio
from typing import Dict, Any, List, Optional

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    MetricsCollectedEvent,
    RoomInputOptions,
    function_tool,
    metrics,
    tokenize,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent.day10")

# Scenarios
SCENARIOS = [
    "You are a barista who has to tell a customer that their latte is actually a portal to another dimension.",
    "You are a time-travelling tour guide explaining modern smartphones to someone from the 1800s.",
    "You are a restaurant waiter who must calmly tell a customer that their order has escaped the kitchen.",
    "You are a customer trying to return an obviously cursed object to a very skeptical shop owner.",
    "You are a cat trying to explain to your owner why you knocked over the expensive vase.",
    "You are a superhero whose only power is making toast perfectly, trying to join the Avengers.",
]

# Session state
_session_states: Dict[str, Dict[str, Any]] = {}

def get_session_state(room_id: str) -> Dict[str, Any]:
    if room_id not in _session_states:
        _session_states[room_id] = {
            "player_name": None,
            "current_round": 0,
            "max_rounds": 3,
            "rounds": [],
            "phase": "intro", # intro, awaiting_improv, reacting, done
            "current_scenario": None
        }
    return _session_states[room_id]

class ImprovHostAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are the host of a TV improv show called 'Improv Battle'.
            
            Your Persona:
            - High-energy, witty, charismatic game show host.
            - You are clear about the rules.
            - You react realistically to the player's improv:
                - Sometimes amused, sometimes unimpressed, sometimes pleasantly surprised.
                - Light teasing and honest critique are allowed and encouraged.
                - Always stay respectful and non-abusive.
            
            Game Flow:
            1. **Intro**: 
               - Welcome the player (use their name if known). 
               - Explain the rules: "I'll give you a scenario, and you have to act it out. When you're done, say 'End Scene' or just stop talking, and I'll judge you."
               - Ask if they are ready to start.
            
            2. **Rounds**: Run for exactly 3 rounds.
               - **Start Round**: Call `get_next_scenario` to get a scenario.
               - **Announce**: Read the scenario clearly and dramatically. Say "Action!" to start.
               - **Listen**: Wait for the user to perform.
               - **React**: When the user finishes (or says "End Scene"), give your feedback. Be specific about what worked or didn't.
               - **Record**: Call `record_round_result` immediately after giving feedback.
            
            3. **Outro**: 
               - After 3 rounds, summarize the player's performance based on the recorded results.
               - Mention specific moments.
               - Thank them and end the show.
            
            Important Guidelines:
            - **ALWAYS** call `get_next_scenario` before announcing a new scenario.
            - **ALWAYS** call `record_round_result` after reacting to a performance.
            - If the user is silent for too long, prompt them gently: "Don't be shy, the camera is rolling!"
            - If the user says "stop game" or "end show", gracefully thank them and stop.
            """,
        )

    @function_tool
    async def get_next_scenario(self, context: RunContext) -> str:
        """Get the next improv scenario to play. Call this at the start of each round."""
        try:
            room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
            state = get_session_state(room_id)
            
            if state["current_round"] >= state["max_rounds"]:
                return "GAME_OVER"
                
            state["current_round"] += 1
            # Ensure we don't repeat scenarios if possible
            available_scenarios = [s for s in SCENARIOS if s not in [r["scenario"] for r in state["rounds"]]]
            if not available_scenarios:
                available_scenarios = SCENARIOS
                
            scenario = random.choice(available_scenarios)
            state["current_scenario"] = scenario
            state["phase"] = "awaiting_improv"
            
            logger.info(f"Starting Round {state['current_round']} with scenario: {scenario}")
            return f"Round {state['current_round']} Scenario: {scenario}"
        except Exception as e:
            logger.error(f"Error in get_next_scenario: {e}")
            return "Error getting scenario. Let's just improvise something about a broken robot!"

    @function_tool
    async def record_round_result(self, context: RunContext, reaction_summary: str) -> str:
        """Record the result of the round after you have given feedback.
        
        Args:
            reaction_summary: A brief summary of your reaction/feedback to the player's performance.
        """
        try:
            room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
            state = get_session_state(room_id)
            
            if state["current_scenario"]:
                state["rounds"].append({
                    "scenario": state["current_scenario"],
                    "reaction": reaction_summary
                })
                state["phase"] = "reacting"
                logger.info(f"Recorded result for round {state['current_round']}")
                
            return "Round recorded. Proceed to next round or outro."
        except Exception as e:
            logger.error(f"Error in record_round_result: {e}")
            return "Error recording result, but let's keep the show moving!"

    @function_tool
    async def get_player_name(self, context: RunContext) -> str:
        """Get the player's name from the session metadata."""
        try:
            # Try to get from metadata first
            if hasattr(context.agent, 'room') and context.agent.room.metadata:
                try:
                    metadata = json.loads(context.agent.room.metadata)
                    name = metadata.get("player_name")
                    if name:
                        return name
                except json.JSONDecodeError:
                    pass
            
            room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
            state = get_session_state(room_id)
            if state["player_name"]:
                return state["player_name"]
                
            return "Contestant"
        except Exception as e:
            logger.error(f"Error in get_player_name: {e}")
            return "Contestant"

async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 10 Improv Host."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day10",
    }

    logger.info(f"Starting Day 10 Agent in room {ctx.room.name}")

    # Set up voice AI pipeline
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Promo", 
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
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
        agent=ImprovHostAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()
    logger.info("Day 10 Agent connected")
