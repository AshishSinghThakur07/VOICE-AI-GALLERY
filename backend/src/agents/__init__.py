"""Agent registry for multi-day voice agent platform."""
from typing import Callable
from livekit.agents import JobContext

# Import agents (lazy loading to avoid circular imports)
AGENT_REGISTRY: dict[str, Callable[[JobContext], None]] = {}


def register_agent(agent_name: str, entrypoint_fn: Callable[[JobContext], None]):
    """Register an agent entrypoint."""
    AGENT_REGISTRY[agent_name] = entrypoint_fn


def get_agent_entrypoint(agent_name: str) -> Callable[[JobContext], None]:
    """Get the entrypoint function for a given agent name."""
    # Lazy import to avoid circular dependencies
    if not AGENT_REGISTRY:
        from . import day1_basic, day2_barista, day3_wellness, day4_tutor, day5_sdr, day6_fraud, day7_food, day8_gamemaster, day9_ecommerce
        
        register_agent("day1", day1_basic.entrypoint)
        register_agent("day2", day2_barista.entrypoint)
        register_agent("day3", day3_wellness.entrypoint)
        register_agent("day4", day4_tutor.entrypoint)
        register_agent("day5", day5_sdr.entrypoint)
        register_agent("day6", day6_fraud.entrypoint)
        register_agent("day7", day7_food.entrypoint)
        register_agent("day8", day8_gamemaster.entrypoint)
        register_agent("day9", day9_ecommerce.entrypoint)
        
        from . import day10_improv
        register_agent("day10", day10_improv.entrypoint)
    
    # Normalize agent name (remove "day" prefix if present, handle variations)
    normalized_name = agent_name.lower().replace("day", "").strip()
    if normalized_name and normalized_name.isdigit():
        agent_name = f"day{normalized_name}"
    
    return AGENT_REGISTRY.get(agent_name, AGENT_REGISTRY.get("day1"))


def list_available_agents() -> list[str]:
    """List all available agent names."""
    if not AGENT_REGISTRY:
        get_agent_entrypoint("day1")  # Trigger registration
    return list(AGENT_REGISTRY.keys())
