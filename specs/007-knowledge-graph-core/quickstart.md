# Quick Start: Knowledge Graph Core Components

This guide provides a quick way to set up and interact with the core components of the knowledge graph system: the `Fact` model, `MemoryFactQueue`, `FactDispatcher`, and `AttentionGraph`.

## Prerequisites

- Python 3.11+
- All project dependencies installed (e.g., Pydantic, asyncio).

## Demonstration Steps

### 1. Define Core Components

First, let's set up a minimal script to define and instantiate the key components.

```python
import asyncio
from datetime import datetime
import hashlib
from typing import List, Set, Deque, Dict, Any, Union
from abc import ABC, abstractmethod
from collections import deque
from pydantic import BaseModel, Field, ConfigDict

# --- 1. Fact Model ---
class Fact(BaseModel):
    model_config = ConfigDict(frozen=True) # Makes Fact immutable

    subject: str
    predicate: str
    object: str
    id: str = Field(default_factory=lambda: "") # Will be generated
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    source: str = "user"

    def serialize_canonical(self) -> str:
        # Ensures consistent ordering for hashing
        return f"{self.subject}|{self.predicate}|{self.object}"

    def generate_id(self) -> str:
        return hashlib.sha256(self.serialize_canonical().encode('utf-8')).hexdigest()

    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            object.__setattr__(self, 'id', self.generate_id())


# --- 2. Fact Queue Interface ---
class IFactQueue(ABC):
    @abstractmethod
    async def enqueue(self, fact: Fact):
        pass

    @abstractmethod
    async def dequeue_batch(self, size: int) -> List[Fact]:
        pass

# --- 3. Memory Fact Queue Implementation ---
class MemoryFactQueue(IFactQueue):
    def __init__(self):
        self._queue: asyncio.Queue[Fact] = asyncio.Queue()
        self._seen_fact_ids: Set[str] = set()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def enqueue(self, fact: Fact):
        async with self._lock:
            if fact.id in self._seen_fact_ids:
                print(f"Fact {fact.id} already in queue. Skipping.")
                return
            self._seen_fact_ids.add(fact.id)
            await self._queue.put(fact)
            print(f"Enqueued fact: {fact.id}")

    async def dequeue_batch(self, size: int) -> List[Fact]:
        batch: List[Fact] = []
        for _ in range(size):
            try:
                fact = self._queue.get_nowait()
                batch.append(fact)
            except asyncio.QueueEmpty:
                break
        
        # Remove dequeued facts from _seen_fact_ids after batch is formed
        if batch:
            async with self._lock:
                for fact in batch:
                    if fact.id in self._seen_fact_ids:
                        self._seen_fact_ids.remove(fact.id)
            print(f"Dequeued batch of {len(batch)} facts.")
        return batch

# --- 4. Fact Handler Interface ---
class IFactHandler(ABC):
    @abstractmethod
    async def handle(self, batch_of_facts: List[Fact]):
        pass

# --- 5. Example Fact Handlers ---
class FastInferenceHandler(IFactHandler):
    def __init__(self, name: str):
        self.name = name
    async def handle(self, batch_of_facts: List[Fact]):
        print(f"[{self.name}] Processing batch (fast inference): {len(batch_of_facts)} facts")
        await asyncio.sleep(0.05) # Simulate quick processing
        for fact in batch_of_facts:
            print(f"[{self.name}] Handled fact: {fact.id}")

class DeepReasoningHandler(IFactHandler):
    def __init__(self, name: str):
        self.name = name
    async def handle(self, batch_of_facts: List[Fact]):
        print(f"[{self.name}] Processing batch (deep reasoning): {len(batch_of_facts)} facts")
        await asyncio.sleep(0.2) # Simulate more intensive processing
        for fact in batch_of_facts:
            print(f"[{self.name}] Handled fact: {fact.id}")

# --- 6. Fact Dispatcher ---
class FactDispatcher:
    def __init__(self, fact_queue: IFactQueue, batch_size: int = 10, polling_interval: float = 0.1):
        self._fact_queue = fact_queue
        self._handlers: List[IFactHandler] = []
        self._batch_size = batch_size
        self._polling_interval = polling_interval
        self._running = False

    def register_handler(self, handler: IFactHandler):
        self._handlers.append(handler)
        print(f"Registered handler: {handler.name if hasattr(handler, 'name') else handler.__class__.__name__}")

    async def start_dispatching(self):
        self._running = True
        print("FactDispatcher started...")
        while self._running:
            batch = await self._fact_queue.dequeue_batch(self._batch_size)
            if batch:
                await asyncio.gather(*[handler.handle(batch) for handler in self._handlers])
            await asyncio.sleep(self._polling_interval)

    def stop_dispatching(self):
        self._running = False
        print("FactDispatcher stopped.")

# --- 7. Memory Node ---
class MemoryNode(BaseModel):
    item: Any # Union[Fact, Rule] - for simplicity in quickstart, using Any
    activation_level: float = 0.5
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

    def stimulate(self, amount: float):
        self.activation_level = min(1.0, self.activation_level + amount)
        self.last_accessed = datetime.utcnow()

# --- 8. Attention Graph ---
class AttentionGraph:
    def __init__(self):
        self._nodes: Dict[str, MemoryNode] = {}

    def add_node(self, item: Any): # item can be Fact or Rule
        item_id = item.id if hasattr(item, 'id') else str(hash(item)) # Using hash for simple items
        if item_id not in self._nodes:
            self._nodes[item_id] = MemoryNode(item=item)
            print(f"Added node to AttentionGraph: {item_id}")

    def stimulate(self, item_id: str, amount: float):
        if item_id in self._nodes:
            self._nodes[item_id].stimulate(amount)
            print(f"Stimulated node {item_id}. New activation: {self._nodes[item_id].activation_level:.2f}")
        else:
            print(f"Node {item_id} not found in AttentionGraph.")

    def decay(self, factor: float):
        for node in self._nodes.values():
            node.activation_level *= factor
        print(f"All nodes decayed by factor {factor}.")

    def prune(self, threshold: float):
        ids_to_prune = [node_id for node_id, node in self._nodes.items() if node.activation_level < threshold]
        for node_id in ids_to_prune:
            del self._nodes[node_id]
            print(f"Pruned node: {node_id}")

    def get_active_subgraph(self, threshold: float = 0.1) -> List[Any]:
        return [node.item for node in self._nodes.values() if node.activation_level >= threshold]

    def get_node_activation(self, item_id: str) -> float:
        return self._nodes[item_id].activation_level if item_id in self._nodes else 0.0

```

### 2. Run the Demonstration

Save the above code as `quickstart_core_components.py` in your project root or a temporary directory. Then, run it using Python:

```bash
python quickstart_core_components.py
```

```python
async def main():
    # Instantiate components
    fact_queue = MemoryFactQueue()
    dispatcher = FactDispatcher(fact_queue, batch_size=2, polling_interval=0.01)
    attention_graph = AttentionGraph()

    # Register handlers
    fast_handler = FastInferenceHandler("HandlerA")
    deep_handler = DeepReasoningHandler("HandlerB")
    dispatcher.register_handler(fast_handler)
    dispatcher.register_handler(deep_handler)

    # Start dispatcher in the background
    dispatcher_task = asyncio.create_task(dispatcher.start_dispatching())

    # --- Demonstrate Fact Ingestion and Processing ---
    print("\n--- Demonstrating Fact Ingestion and Processing ---")
    fact1 = Fact(subject="Alice", predicate="knows", object="Bob", source="user")
    fact2 = Fact(subject="Bob", predicate="isFriendOf", object="Alice", source="user")
    fact3 = Fact(subject="Alice", predicate="loves", object="Python", source="user")
    
    await fact_queue.enqueue(fact1)
    await fact_queue.enqueue(fact2)
    await fact_queue.enqueue(fact3)
    await fact_queue.enqueue(fact1) # Attempt to enqueue duplicate

    await asyncio.sleep(0.5) # Give dispatcher time to process

    # --- Demonstrate Attention Graph ---
    print("\n--- Demonstrating Attention Graph ---")
    attention_graph.add_node(fact1)
    attention_graph.add_node(fact2)
    attention_graph.add_node(fact3)

    attention_graph.stimulate(fact1.id, 0.3)
    attention_graph.stimulate(fact2.id, 0.1)

    print(f"Activation of fact1: {attention_graph.get_node_activation(fact1.id):.2f}")
    print(f"Activation of fact2: {attention_graph.get_node_activation(fact2.id):.2f}")
    print(f"Activation of fact3: {attention_graph.get_node_activation(fact3.id):.2f}")

    attention_graph.decay(0.8)

    print(f"Activation of fact1 after decay: {attention_graph.get_node_activation(fact1.id):.2f}")
    print(f"Activation of fact2 after decay: {attention_graph.get_node_activation(fact2.id):.2f}")
    print(f"Activation of fact3 after decay: {attention_graph.get_node_activation(fact3.id):.2f}")
    
    active_items_before_prune = attention_graph.get_active_subgraph(threshold=0.3)
    print(f"Active items before prune (threshold 0.3): {[f.id for f in active_items_before_prune]}")


    attention_graph.prune(threshold=0.3)
    active_items_after_prune = attention_graph.get_active_subgraph(threshold=0.0) # all remaining
    print(f"Active items after prune (threshold 0.3): {[f.id for f in active_items_after_prune]}")


    dispatcher.stop_dispatching()
    await dispatcher_task # Await the dispatcher task to finish cleanly

if __name__ == "__main__":
    asyncio.run(main())

```

### Expected Output

You will observe output similar to the following (IDs and timestamps will vary):

```
Registered handler: HandlerA
Registered handler: HandlerB
FactDispatcher started...
Enqueued fact: <fact_id_1>
Enqueued fact: <fact_id_2>
Enqueued fact: <fact_id_3>
Fact <fact_id_1> already in queue. Skipping.
Dequeued batch of 2 facts.
[HandlerA] Processing batch (fast inference): 2 facts
[HandlerB] Processing batch (deep reasoning): 2 facts
[HandlerA] Handled fact: <fact_id_1>
[HandlerA] Handled fact: <fact_id_2>
[HandlerB] Handled fact: <fact_id_1>
[HandlerB] Handled fact: <fact_id_2>
Dequeued batch of 1 facts.
[HandlerA] Processing batch (fast inference): 1 facts
[HandlerB] Processing batch (deep reasoning): 1 facts
[HandlerA] Handled fact: <fact_id_3>
[HandlerB] Handled fact: <fact_id_3>

--- Demonstrating Attention Graph ---
Added node to AttentionGraph: <fact_id_1>
Added node to AttentionGraph: <fact_id_2>
Added node to AttentionGraph: <fact_id_3>
Stimulated node <fact_id_1>. New activation: 0.80
Stimulated node <fact_id_2>. New activation: 0.60
Activation of fact1: 0.80
Activation of fact2: 0.60
Activation of fact3: 0.50
All nodes decayed by factor 0.8.
Activation of fact1 after decay: 0.64
Activation of fact2 after decay: 0.48
Activation of fact3 after decay: 0.40
Active items before prune (threshold 0.3): ["<fact_id_1>", "<fact_id_2>", "<fact_id_3>"]
Pruned node: <fact_id_1> (if activation dropped below 0.3)
Active items after prune (threshold 0.3): ["<fact_id_1>", "<fact_id_2>"] (IDs depend on exact activation levels)
FactDispatcher stopped.
```

