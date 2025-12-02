# Research: Core Knowledge Graph Components Best Practices

**Feature**: 007-knowledge-graph-core

## 1. Objective
To confirm best practices and specific implementations for the core Python components: Fact structure, Ingestion Queue, Fact Dispatcher (Pub-Sub), and Working Memory Graph.

## 2. Key Areas of Research

### a. Pydantic Model Design for Immutable Data (Fact Structure)
- **Question**: How to best design the `Fact` structure using Pydantic, ensuring immutability and canonical serialization for hashing?
- **Findings**:
    - Pydantic v2 models can be configured for immutability using `ConfigDict(frozen=True)`. This ensures that once a `Fact` instance is created, its attributes cannot be changed.
    - Canonical serialization for hashing often involves converting the object to a sorted JSON string (or a consistent string representation of its core components) and then hashing that string (e.g., using SHA256). For RDF-like triples, sorting subject, predicate, and object ensures consistent hashing.
- **Decision**: Implement `Fact` as a Pydantic v2 model with `ConfigDict(frozen=True)`. A `serialize_canonical` method will convert the triplet (s, p, o) into a sorted string representation for ID generation via hashing.

### b. Async-Safe Queues and Duplicate Prevention (Ingestion Queue)
- **Question**: What are the best patterns for an asynchronous, thread-safe queue with duplicate prevention in Python's `asyncio` context?
- **Findings**:
    - `asyncio.Queue` is the standard choice for async-safe queues in Python. It provides `put` and `get` methods that are naturally awaitable and handle concurrent access correctly within an `asyncio` event loop.
    - For duplicate prevention, maintaining a `set` of `Fact` IDs (or their canonical hash) alongside the `asyncio.Queue` is the most straightforward approach. Before `put`ing a `Fact` into the queue, check if its ID is in the `set`. Add the ID to the `set` when enqueuing, remove it when dequeuing. A `threading.Lock` (or `asyncio.Lock` if the set manipulation needs to be awaited) would protect the `set` if queue operations are called from different threads, though typically in `asyncio` this is managed by the event loop. Given the `IFactQueue` interface is async, `asyncio.Lock` is appropriate for protecting the set's state.
- **Decision**: Use `asyncio.Queue` for the primary queue storage. Implement duplicate prevention using an `asyncio.Lock` to protect a `set` of fact IDs, ensuring a fact's ID is added to the set upon enqueue and removed upon successful dequeue.

### c. Asynchronous Pub-Sub/Observer in Python (Fact Dispatcher)
- **Question**: What are the best design patterns for an asynchronous Pub-Sub/Observer mechanism for the `FactDispatcher` in `asyncio`?
- **Findings**:
    - The core idea is to maintain a list of `IFactHandler` subscribers. When the dispatcher dequeues a batch of facts, it iterates through these handlers and calls their `handle` method.
    - To execute handlers in parallel, `asyncio.gather(*[handler.handle(batch) for handler in self._handlers])` is the idiomatic way. This runs all handler tasks concurrently and awaits their completion.
    - The dispatcher itself should run in an infinite `asyncio` loop, periodically attempting to dequeue facts.
- **Decision**: The `FactDispatcher` will maintain a list of `IFactHandler` instances. It will use `asyncio.gather` to run the `handle` methods of all registered handlers concurrently for each dequeued batch. The dispatcher's main loop will be an `asyncio` coroutine.

### d. Efficient Data Structures for Graph-like (Nodes with Activation)
- **Question**: What Python data structures are efficient for managing `MemoryNode`s with activation levels and supporting operations like stimulate, decay, prune, and subgraph retrieval?
- **Findings**:
    - A simple Python `dict` (hash map) where keys are `Fact` or `Rule` IDs and values are `MemoryNode` instances is highly efficient for `stimulate` (O(1) average lookup).
    - `decay` and `prune` operations involve iterating over all nodes, so their complexity will be O(N) where N is the number of nodes.
    - `get_active_subgraph` would also involve iterating over nodes and filtering, resulting in O(N) complexity.
- **Decision**: Use a Python `dict` to store `MemoryNode` instances, keyed by their unique `Fact` or `Rule` ID. This provides efficient access for stimulating and managing activation states.

## 3. Conclusion
The research confirms the architectural choices outlined in the feature specification and provides specific Python implementation patterns for the core components.
