"""Day 8: D&D-Style Game Master Agent."""
import logging
import json
from pathlib import Path
from typing import Dict, Any

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

import sys
from pathlib import Path as PathLib

# Add src directory to path for imports
src_path = PathLib(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from shared.tools.file_ops import save_json, load_json

logger = logging.getLogger("agent.day8")

# World state file
WORLD_STATE_FILE = Path(__file__).parent.parent / "shared" / "data" / "day8_world_state.json"

# Session-based world states (in production, use proper session management)
_session_states: Dict[str, Dict[str, Any]] = {}


def get_world_state(room_id: str) -> Dict[str, Any]:
    """Get or initialize world state for a session."""
    if room_id not in _session_states:
        # Load default world state
        default_state = load_json("day8_world_state.json", default={
            "universe": "fantasy",
            "tone": "dramatic",
            "player_character": {
                "name": "",
                "class": "",
                "hp": 100,
                "max_hp": 100,
                "status": "Healthy",
                "inventory": [],
                "traits": []
            },
            "npcs": [],
            "locations": {
                "current": {
                    "name": "The Enchanted Forest",
                    "description": "A mysterious forest filled with ancient trees and magical creatures.",
                    "paths": ["north", "east", "south"]
                }
            },
            "events": [],
            "quests": {
                "active": [],
                "completed": []
            },
            "session_started": False
        })
        _session_states[room_id] = default_state.copy()
    return _session_states[room_id]


def save_world_state(room_id: str, state: Dict[str, Any]):
    """Save world state (in-memory for now, can persist to file)."""
    _session_states[room_id] = state
    # Optionally save to file
    # save_json(f"day8_world_state_{room_id}.json", state)


class GameMasterAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a Game Master (GM) running a fantasy adventure in a world of dragons and magic.

            Your role:
            - Describe scenes vividly and dramatically
            - React to player actions and decisions
            - Create interesting challenges and encounters
            - End each message with a prompt for player action ("What do you do?")
            - Maintain continuity with the story
            - Use the world state tools to track characters, locations, events, and quests
            
            Story guidelines:
            - Start with an engaging opening scene
            - Create a sense of adventure and mystery
            - Allow player choices to matter
            - Build toward a mini-arc (finding something, escaping danger, completing a quest)
            - Keep sessions to 8-15 exchanges for a complete mini-arc
            
            Use tools to:
            - Update player character info when they introduce themselves
            - Track important NPCs they meet
            - Update locations as they move
            - Record key events
            - Manage quests and objectives
            
            Be creative, engaging, and responsive to player actions!""",
        )

    @function_tool
    async def update_player_character(
        self,
        context: RunContext,
        name: str = None,
        character_class: str = None,
        hp: int = None,
        status: str = None,
        add_item: str = None,
        remove_item: str = None,
    ) -> str:
        """Update player character information.
        
        Args:
            name: Player character name
            character_class: Character class (warrior, mage, rogue, etc.)
            hp: Current HP
            status: Status (Healthy, Injured, Critical)
            add_item: Item to add to inventory
            remove_item: Item to remove from inventory
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        pc = state["player_character"]
        
        if name:
            pc["name"] = name
        if character_class:
            pc["class"] = character_class
        if hp is not None:
            pc["hp"] = max(0, min(hp, pc["max_hp"]))
            if pc["hp"] < 30:
                pc["status"] = "Critical"
            elif pc["hp"] < 70:
                pc["status"] = "Injured"
            else:
                pc["status"] = "Healthy"
        if status:
            pc["status"] = status
        if add_item:
            if add_item not in pc["inventory"]:
                pc["inventory"].append(add_item)
        if remove_item and remove_item in pc["inventory"]:
            pc["inventory"].remove(remove_item)
        
        save_world_state(room_id, state)
        return f"Character updated: {pc['name']} ({pc['class']}) - HP: {pc['hp']}/{pc['max_hp']} ({pc['status']})"

    @function_tool
    async def add_npc(
        self,
        context: RunContext,
        name: str,
        role: str,
        attitude: str = "neutral",
    ) -> str:
        """Add an NPC to the world state.
        
        Args:
            name: NPC name
            role: NPC role/description
            attitude: Attitude toward player (friendly, neutral, hostile)
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        
        npc = {
            "name": name,
            "role": role,
            "attitude": attitude,
        }
        state["npcs"].append(npc)
        save_world_state(room_id, state)
        return f"Added NPC: {name} ({role}) - {attitude}"

    @function_tool
    async def update_location(
        self,
        context: RunContext,
        name: str,
        description: str,
        paths: list[str] = None,
    ) -> str:
        """Update current location.
        
        Args:
            name: Location name
            description: Location description
            paths: Available paths/directions
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        
        state["locations"]["current"] = {
            "name": name,
            "description": description,
            "paths": paths or [],
        }
        save_world_state(room_id, state)
        return f"Location updated: {name}"

    @function_tool
    async def add_event(
        self,
        context: RunContext,
        event_description: str,
    ) -> str:
        """Record a key event that happened.
        
        Args:
            event_description: Description of the event
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        
        state["events"].append(event_description)
        save_world_state(room_id, state)
        return f"Event recorded: {event_description}"

    @function_tool
    async def add_quest(
        self,
        context: RunContext,
        quest_name: str,
        description: str,
    ) -> str:
        """Add a quest to the active quests.
        
        Args:
            quest_name: Quest name
            description: Quest description
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        
        quest = {
            "name": quest_name,
            "description": description,
        }
        state["quests"]["active"].append(quest)
        save_world_state(room_id, state)
        return f"Quest added: {quest_name}"

    @function_tool
    async def complete_quest(
        self,
        context: RunContext,
        quest_name: str,
    ) -> str:
        """Mark a quest as completed.
        
        Args:
            quest_name: Quest name to complete
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        
        for quest in state["quests"]["active"]:
            if quest["name"] == quest_name:
                state["quests"]["active"].remove(quest)
                state["quests"]["completed"].append(quest)
                save_world_state(room_id, state)
                return f"Quest completed: {quest_name}"
        
        return f"Quest '{quest_name}' not found in active quests."

    @function_tool
    async def get_world_state_summary(self, context: RunContext) -> str:
        """Get a summary of the current world state.
        
        Returns:
            World state summary
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        state = get_world_state(room_id)
        
        pc = state["player_character"]
        location = state["locations"]["current"]
        
        summary = f"Player: {pc['name']} ({pc['class']}) - HP: {pc['hp']}/{pc['max_hp']} ({pc['status']})\n"
        summary += f"Location: {location['name']}\n"
        summary += f"Inventory: {', '.join(pc['inventory']) if pc['inventory'] else 'Empty'}\n"
        summary += f"Active Quests: {len(state['quests']['active'])}\n"
        summary += f"NPCs Met: {len(state['npcs'])}\n"
        summary += f"Events: {len(state['events'])}"
        
        return summary


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 8 game master."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day8",
    }

    # Set up voice AI pipeline
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
        agent=GameMasterAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


