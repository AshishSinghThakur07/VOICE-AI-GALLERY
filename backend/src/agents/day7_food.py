"""Day 7: Food & Grocery Ordering Voice Agent."""
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

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

logger = logging.getLogger("agent.day7")

# Load catalog
CATALOG_FILE = Path(__file__).parent.parent / "shared" / "data" / "day7_catalog.json"

def load_catalog():
    """Load food catalog from JSON file."""
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return {"categories": {}, "recipes": {}}

CATALOG = load_catalog()

# Session cart (in production, use proper session state)
_session_carts: Dict[str, List[Dict]] = {}


class FoodOrderingAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly food and grocery ordering assistant. Your job is to help customers order food and groceries.

            Your approach:
            - Greet customers warmly and explain what you can help with
            - Help customers add items to their cart
            - Handle "ingredients for X" requests intelligently (e.g., "ingredients for peanut butter sandwich")
            - Ask for clarifications when needed (size, brand, quantity)
            - When asked "what's in my cart", use the get_cart tool
            - Support cart operations: add, remove, update quantities
            - When the user says "place order", "checkout", "I'm done", use the place_order tool
            - Be conversational and confirm actions verbally
            
            Important:
            - Use the search_catalog tool to find items
            - Use the get_recipe_items tool for "ingredients for X" requests
            - Always confirm what you're adding to the cart
            - Show enthusiasm and be helpful""",
        )

    @function_tool
    async def search_catalog(
        self,
        context: RunContext,
        query: str,
        category: Optional[str] = None,
    ) -> str:
        """Search the food catalog for items.
        
        Args:
            query: Search query (item name, brand, etc.)
            category: Optional category filter (groceries, snacks, prepared_food)
            
        Returns:
            List of matching items with prices
        """
        query_lower = query.lower()
        results = []
        
        categories_to_search = [category] if category else CATALOG.get("categories", {}).keys()
        
        for cat in categories_to_search:
            items = CATALOG.get("categories", {}).get(cat, [])
            for item in items:
                name = item.get("name", "").lower()
                if query_lower in name or any(query_lower in tag.lower() for tag in item.get("tags", [])):
                    results.append(item)
        
        if not results:
            return f"No items found matching '{query}'. Try searching for bread, eggs, milk, pasta, or prepared food items."
        
        # Format results
        formatted = []
        for item in results[:5]:  # Limit to 5 results
            price = item.get("price", 0)
            size = item.get("size", "")
            formatted.append(f"- {item['name']} ({size}) - ₹{price} [ID: {item['id']}]")
        
        return "Found items:\n" + "\n".join(formatted)

    @function_tool
    async def get_recipe_items(self, context: RunContext, recipe_name: str) -> str:
        """Get items needed for a recipe.
        
        Args:
            recipe_name: Name of the recipe (e.g., "peanut butter sandwich", "pasta dish")
            
        Returns:
            List of items needed for the recipe
        """
        recipes = CATALOG.get("recipes", {})
        recipe_key = recipe_name.lower().replace(" ", "_")
        
        if recipe_key in recipes:
            recipe = recipes[recipe_key]
            item_ids = recipe.get("items", [])
            
            # Get item details
            items = []
            for cat_items in CATALOG.get("categories", {}).values():
                for item in cat_items:
                    if item["id"] in item_ids:
                        items.append(f"- {item['name']} ({item['size']}) - ₹{item['price']} [ID: {item['id']}]")
            
            return f"For {recipe['name']}, you'll need:\n" + "\n".join(items)
        else:
            available = ", ".join([r.replace("_", " ") for r in recipes.keys()])
            return f"Recipe '{recipe_name}' not found. Available recipes: {available}"

    @function_tool
    async def add_to_cart(
        self,
        context: RunContext,
        item_id: str,
        quantity: int = 1,
    ) -> str:
        """Add an item to the cart.
        
        Args:
            item_id: ID of the item to add
            quantity: Quantity to add (default: 1)
            
        Returns:
            Confirmation message
        """
        # Find item in catalog
        item = None
        for cat_items in CATALOG.get("categories", {}).values():
            for i in cat_items:
                if i["id"] == item_id:
                    item = i
                    break
            if item:
                break
        
        if not item:
            return f"Item with ID '{item_id}' not found in catalog."
        
        # Get or create cart for this session
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        if room_id not in _session_carts:
            _session_carts[room_id] = []
        
        cart = _session_carts[room_id]
        
        # Check if item already in cart
        for cart_item in cart:
            if cart_item["id"] == item_id:
                cart_item["quantity"] += quantity
                total_price = cart_item["quantity"] * item["price"]
                return f"Updated quantity. You now have {cart_item['quantity']}x {item['name']} in your cart (₹{total_price} total)."
        
        # Add new item
        cart_item = {
            "id": item_id,
            "name": item["name"],
            "price": item["price"],
            "quantity": quantity,
        }
        cart.append(cart_item)
        
        total_price = quantity * item["price"]
        return f"Added {quantity}x {item['name']} to your cart (₹{total_price})."

    @function_tool
    async def get_cart(self, context: RunContext) -> str:
        """Get current cart contents.
        
        Returns:
            Cart summary with items and total
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        cart = _session_carts.get(room_id, [])
        
        if not cart:
            return "Your cart is empty."
        
        items = []
        total = 0
        for item in cart:
            item_total = item["quantity"] * item["price"]
            total += item_total
            items.append(f"- {item['quantity']}x {item['name']} - ₹{item_total}")
        
        return f"Your cart contains:\n" + "\n".join(items) + f"\n\nTotal: ₹{total}"

    @function_tool
    async def remove_from_cart(
        self,
        context: RunContext,
        item_id: str,
    ) -> str:
        """Remove an item from the cart.
        
        Args:
            item_id: ID of the item to remove
            
        Returns:
            Confirmation message
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        cart = _session_carts.get(room_id, [])
        
        for i, item in enumerate(cart):
            if item["id"] == item_id:
                removed = cart.pop(i)
                return f"Removed {removed['name']} from your cart."
        
        return f"Item with ID '{item_id}' not found in cart."

    @function_tool
    async def place_order(
        self,
        context: RunContext,
        customer_name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> str:
        """Place the current order.
        
        Args:
            customer_name: Optional customer name
            address: Optional delivery address
            
        Returns:
            Order confirmation
        """
        room_id = context.agent.room.name if hasattr(context.agent, 'room') else "default"
        cart = _session_carts.get(room_id, [])
        
        if not cart:
            return "Your cart is empty. Add some items before placing an order."
        
        # Calculate total
        total = sum(item["quantity"] * item["price"] for item in cart)
        
        # Create order
        order = {
            "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customer_name": customer_name or "Guest",
            "address": address or "Not provided",
            "items": cart.copy(),
            "total": total,
            "currency": "INR",
            "timestamp": datetime.now().isoformat(),
            "status": "received",
        }
        
        # Save order
        orders = load_json("day7_orders.json", default=[])
        if not isinstance(orders, list):
            orders = []
        orders.append(order)
        
        if save_json("day7_orders.json", orders):
            # Clear cart
            _session_carts[room_id] = []
            
            logger.info(f"Order placed: {order['order_id']}")
            return f"Order placed successfully! Order ID: {order['order_id']}. Total: ₹{total}. Your order will be prepared and delivered soon. Thank you!"
        else:
            return "I had trouble placing your order. Please try again."


async def entrypoint(ctx: JobContext):
    """Entrypoint for Day 7 food ordering agent."""
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "day7",
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
        agent=FoodOrderingAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


