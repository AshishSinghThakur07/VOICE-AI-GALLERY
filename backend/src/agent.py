"""Main agent router for multi-day voice agent platform."""
import logging

from dotenv import load_dotenv
from livekit.agents import (
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.plugins import silero

from agents import get_agent_entrypoint

logger = logging.getLogger("agent")

load_dotenv(".env.local")


def prewarm(proc: JobProcess):
    """Prewarm function to load models before agents start."""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entrypoint that routes to the appropriate agent based on room config."""
    # Extract agent name from room configuration
    agent_name = "day1"  # Default to day1
    
    # Try to get agent name from room config
    if ctx.room_config and ctx.room_config.agents:
        agent_name = ctx.room_config.agents[0].agent_name or "day1"
    else:
        # Fallback: try to extract from room name
        room_name_parts = ctx.room.name.split("_")
        if len(room_name_parts) > 1:
            potential_agent = room_name_parts[-1].lower()
            if potential_agent.startswith("day"):
                agent_name = potential_agent
    
    logger.info(f"Routing to agent: {agent_name}")
    
    # Get the appropriate agent entrypoint
    agent_entrypoint = get_agent_entrypoint(agent_name)
    
    # Call the agent's entrypoint
    await agent_entrypoint(ctx)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
