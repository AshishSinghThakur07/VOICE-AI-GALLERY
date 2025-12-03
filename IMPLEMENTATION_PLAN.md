# 🎯 Implementation Plan: Multi-Day Voice Agent Platform

## Overview

Build a unified platform where users can select and interact with different voice agents for Days 1-10 of the Murf AI Voice Agents Challenge.

---

## 📋 Architecture Overview

### Backend Structure
```
backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── day1_basic.py          # Basic assistant (✅ Done)
│   │   ├── day2_barista.py        # Coffee shop barista
│   │   ├── day3_wellness.py       # Health & wellness companion
│   │   ├── day4_tutor.py          # Active recall coach
│   │   ├── day5_sdr.py            # Sales Development Rep
│   │   ├── day6_fraud.py          # Fraud alert agent
│   │   ├── day7_food.py           # Food & grocery ordering
│   │   ├── day8_gamemaster.py     # D&D-style game master
│   │   └── day9_ecommerce.py     # E-commerce agent
│   ├── shared/
│   │   ├── data/                  # JSON files, databases
│   │   │   ├── day2_orders.json
│   │   │   ├── day3_wellness_log.json
│   │   │   ├── day4_tutor_content.json
│   │   │   ├── day5_leads.json
│   │   │   ├── day6_fraud_cases.json
│   │   │   ├── day7_catalog.json
│   │   │   ├── day7_orders.json
│   │   │   ├── day8_world_state.json
│   │   │   └── day9_catalog.json
│   │   └── tools/                 # Shared tool functions
│   │       ├── file_ops.py
│   │       ├── database.py
│   │       └── helpers.py
│   └── agent.py                   # Main router/dispatcher
└── ...
```

### Frontend Structure
```
frontend/
├── app/
│   ├── (app)/
│   │   ├── page.tsx               # Main page with agent selector
│   │   └── layout.tsx
│   └── api/
│       └── connection-details/
│           └── route.ts            # ✅ Already supports agentName
├── components/
│   ├── app/
│   │   ├── agent-selector.tsx     # NEW: Agent selection UI
│   │   └── ...
│   └── ...
└── ...
```

---

## 🏗️ Implementation Phases

### Phase 1: Backend Agent Router (Day 1-2)
**Goal:** Set up routing system to handle multiple agents

#### Tasks:
1. **Create agent registry** (`backend/src/agents/__init__.py`)
   - Map agent names to entrypoint functions
   - Centralized agent configuration

2. **Refactor main agent.py**
   - Add agent dispatcher/router
   - Load agent based on `agent_name` from room config
   - Maintain backward compatibility with Day 1

3. **Create Day 2 Barista Agent** (`backend/src/agents/day2_barista.py`)
   - Coffee shop persona
   - Order state management
   - JSON file persistence
   - Function tools for order operations

#### Deliverables:
- ✅ Agent routing system working
- ✅ Day 1 agent accessible via router
- ✅ Day 2 barista agent functional

---

### Phase 2: Frontend Agent Selector (Day 1-2)
**Goal:** Build UI for selecting agents

#### Tasks:
1. **Create Agent Selector Component** (`frontend/components/app/agent-selector.tsx`)
   - Card-based UI showing all available agents
   - Agent descriptions and icons
   - Selection state management

2. **Update Main Page** (`frontend/app/(app)/page.tsx`)
   - Show agent selector before connection
   - Pass selected agent to connection API
   - Update app-config with selected agent

3. **Update Welcome View** (`frontend/components/app/welcome-view.tsx`)
   - Integrate agent selector
   - Show selected agent info

#### Deliverables:
- ✅ Agent selector UI component
- ✅ Users can select Day 1 or Day 2 agent
- ✅ Selected agent connects correctly

---

### Phase 3: Days 3-5 Implementation
**Goal:** Implement wellness, tutor, and SDR agents

#### Tasks:
1. **Day 3: Wellness Companion** (`backend/src/agents/day3_wellness.py`)
   - Daily check-in flow
   - Mood/energy tracking
   - JSON persistence
   - Reference to past check-ins

2. **Day 4: Tutor Agent** (`backend/src/agents/day4_tutor.py`)
   - Three modes: learn, quiz, teach_back
   - Content file integration
   - Mode switching
   - Different voices per mode (Matthew, Alicia, Ken)

3. **Day 5: SDR Agent** (`backend/src/agents/day5_sdr.py`)
   - Company FAQ integration
   - Lead capture
   - End-of-call summary
   - JSON lead storage

#### Deliverables:
- ✅ All three agents functional
- ✅ Data persistence working
- ✅ Frontend updated with new options

---

### Phase 4: Days 6-7 Implementation
**Goal:** Implement fraud and food ordering agents

#### Tasks:
1. **Day 6: Fraud Alert Agent** (`backend/src/agents/day6_fraud.py`)
   - Fraud case database
   - Verification flow
   - Status updates
   - Database persistence

2. **Day 7: Food Ordering Agent** (`backend/src/agents/day7_food.py`)
   - Catalog JSON
   - Cart management
   - "Ingredients for X" intelligence
   - Order placement

#### Deliverables:
- ✅ Fraud agent with database
- ✅ Food ordering with cart
- ✅ All agents accessible from UI

---

### Phase 5: Days 8-9 Implementation
**Goal:** Implement game master and e-commerce agents

#### Tasks:
1. **Day 8: Game Master** (`backend/src/agents/day8_gamemaster.py`)
   - D&D-style storytelling
   - World state management
   - Interactive narrative
   - Save/load functionality

2. **Day 9: E-commerce Agent** (`backend/src/agents/day9_ecommerce.py`)
   - ACP-inspired structure
   - Product catalog
   - Order management
   - Voice + UI integration

#### Deliverables:
- ✅ Game master with world state
- ✅ E-commerce with ACP structure
- ✅ Complete 10-day platform

---

## 🔧 Technical Implementation Details

### Backend Agent Router Pattern

```python
# backend/src/agent.py
from livekit.agents import cli, WorkerOptions
from .agents import get_agent_entrypoint

def create_entrypoint(agent_name: str):
    """Factory function to create entrypoint for specific agent"""
    entrypoint_fn = get_agent_entrypoint(agent_name)
    return entrypoint_fn

async def main_entrypoint(ctx: JobContext):
    """Main router that dispatches to specific agent"""
    agent_name = ctx.room.name.split('_')[-1]  # Extract from room name
    # Or from room config
    agent_name = ctx.room_config.agents[0].agent_name if ctx.room_config else "day1"
    
    entrypoint_fn = get_agent_entrypoint(agent_name)
    await entrypoint_fn(ctx)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=main_entrypoint))
```

### Agent Registry

```python
# backend/src/agents/__init__.py
from typing import Callable
from livekit.agents import JobContext

AGENT_REGISTRY: dict[str, Callable[[JobContext], None]] = {
    "day1": day1_basic.entrypoint,
    "day2": day2_barista.entrypoint,
    "day3": day3_wellness.entrypoint,
    "day4": day4_tutor.entrypoint,
    "day5": day5_sdr.entrypoint,
    "day6": day6_fraud.entrypoint,
    "day7": day7_food.entrypoint,
    "day8": day8_gamemaster.entrypoint,
    "day9": day9_ecommerce.entrypoint,
}

def get_agent_entrypoint(agent_name: str):
    return AGENT_REGISTRY.get(agent_name, AGENT_REGISTRY["day1"])
```

### Frontend Agent Selector

```typescript
// frontend/components/app/agent-selector.tsx
interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  day: number;
}

const AGENTS: Agent[] = [
  {
    id: "day1",
    name: "Basic Assistant",
    description: "A helpful voice AI assistant",
    icon: "🤖",
    day: 1
  },
  {
    id: "day2",
    name: "Coffee Shop Barista",
    description: "Order your favorite coffee",
    icon: "☕",
    day: 2
  },
  // ... more agents
];
```

---

## 📁 Data Management

### Shared Data Directory
```
backend/src/shared/data/
├── day2_orders.json          # Coffee orders
├── day3_wellness_log.json    # Wellness check-ins
├── day4_tutor_content.json   # Learning content
├── day5_leads.json           # SDR leads
├── day6_fraud_cases.json     # Fraud cases (or SQLite)
├── day7_catalog.json         # Food catalog
├── day7_orders.json          # Food orders
├── day8_world_state.json     # Game state
└── day9_catalog.json         # E-commerce catalog
```

### Database Options
- **SQLite** for Day 6 (fraud cases)
- **JSON files** for all other days
- **In-memory** for session state

---

## 🎨 Frontend UI Design

### Agent Selector Layout
```
┌─────────────────────────────────────┐
│   🎙️ Choose Your Voice Agent        │
├─────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐      │
│  │ Day 1│  │ Day 2│  │ Day 3│      │
│  │ 🤖   │  │ ☕   │  │ 💚   │      │
│  └──────┘  └──────┘  └──────┘      │
│  ┌──────┐  ┌──────┐  ┌──────┐      │
│  │ Day 4│  │ Day 5│  │ Day 6│      │
│  │ 📚   │  │ 📞   │  │ 🚨   │      │
│  └──────┘  └──────┘  └──────┘      │
│  ┌──────┐  ┌──────┐  ┌──────┐      │
│  │ Day 7│  │ Day 8│  │ Day 9│      │
│  │ 🛒   │  │ 🎲   │  │ 🛍️   │      │
│  └──────┘  └──────┘  └──────┘      │
└─────────────────────────────────────┘
```

### Features:
- **Card-based selection** with hover effects
- **Agent descriptions** on hover/click
- **Day badges** showing challenge day
- **Selected state** highlighting
- **Start button** appears after selection

---

## 🔄 Connection Flow

```
User selects agent → 
Frontend updates appConfig.agentName → 
POST /api/connection-details with agentName → 
Backend creates room with agent_name → 
Agent router dispatches to correct entrypoint → 
Agent connects to room → 
User can interact
```

---

## 📝 Implementation Checklist

### Backend
- [ ] Create agent registry system
- [ ] Refactor agent.py to use router
- [ ] Implement Day 2 barista agent
- [ ] Implement Day 3 wellness agent
- [ ] Implement Day 4 tutor agent
- [ ] Implement Day 5 SDR agent
- [ ] Implement Day 6 fraud agent
- [ ] Implement Day 7 food agent
- [ ] Implement Day 8 game master
- [ ] Implement Day 9 e-commerce agent
- [ ] Create shared data directory structure
- [ ] Create shared tool functions

### Frontend
- [ ] Create agent selector component
- [ ] Update main page with selector
- [ ] Update welcome view
- [ ] Add agent metadata/config
- [ ] Style agent cards
- [ ] Add selection state management
- [ ] Test agent switching

### Testing
- [ ] Test each agent independently
- [ ] Test agent switching
- [ ] Test data persistence
- [ ] Test error handling
- [ ] Test with different browsers

---

## 🚀 Quick Start Implementation Order

1. **Week 1: Foundation**
   - Day 1: Agent router + Day 2 barista
   - Day 2: Frontend selector + Day 3 wellness
   - Day 3: Day 4 tutor + Day 5 SDR

2. **Week 2: Completion**
   - Day 4: Day 6 fraud + Day 7 food
   - Day 5: Day 8 game master + Day 9 e-commerce
   - Day 6: Polish, testing, documentation

---

## 📚 Key Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Agent Handoffs](https://docs.livekit.io/agents/build/agents-handoffs/)
- [Function Tools](https://docs.livekit.io/agents/build/tools/)
- [Murf Falcon TTS](https://murf.ai/api/docs)

---

## 🎯 Success Criteria

✅ All 9 agents (Day 1-9) implemented and functional  
✅ Frontend UI allows easy agent selection  
✅ Each agent maintains its own data/persistence  
✅ Agents can be switched without restarting services  
✅ All primary goals from challenge tasks completed  
✅ Clean, maintainable code structure  

---

Ready to start implementation! 🚀


