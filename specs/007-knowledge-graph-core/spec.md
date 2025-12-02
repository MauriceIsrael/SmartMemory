# Feature Specification: Knowledge Graph Core Components

**Feature Branch**: `007-knowledge-graph-core`  
**Created**: 2025-11-29  
**Status**: Draft  
**Input**: User description: "Role: Senior Backend Architect Context: We are building an MCP server for Knowledge Graph reasoning. Task: Design the Data Structures and the Ingestion Queue mechanism. Requirements: 1. **Fact Structure**: Create a strictly typed structure for a `Fact`. - Must contain: subject, predicate, object (triplet). - Must contain metadata: `id` (hash of the triplet), `createdAt`, `source` (provenance). - Must implement a method to serialize to canonical string format for hashing. 2. **Ingestion Queue**: - Define an interface `IFactQueue`. - Implement an in-memory version `MemoryFactQueue` (using a thread-safe Queue/Deque). - The queue must support `enqueue(fact)` and `dequeue_batch(size)`. - Include a mechanism to prevent duplicates currently sitting in the queue (e.g., a Set of IDs alongside the Queue). 3. **Technology**: Python (using Pydantic for models and asyncio for queues). /speckit.specify Role: Senior Backend Architect Context: MCP Knowledge Server. We have an `IFactQueue`. We need a Dispatcher to process facts. Task: Design the `FactDispatcher` utilizing an Observer/Pub-Sub pattern. Requirements: 1. **Dispatcher**: - Class `FactDispatcher` that runs an infinite loop (async) monitoring the `IFactQueue`. - It processes facts in batches to optimize I/O. 2. **Subscribers (Handlers)**: - Define an abstract base class `IFactHandler` with an async method `handle(batch_of_facts)`. - The Dispatcher must allow registering multiple handlers (e.g., `register_handler(handler)`). - When a batch is dequeued, the Dispatcher sends it to ALL registered handlers in parallel (using `asyncio.gather`). 3. **Specific Handlers Stub**: - Create a skeleton for `FastInferenceHandler` (placeholder for SPARQL). - Create a skeleton for `DeepReasoningHandler` (placeholder for the background complex reasoning). 4. **Concurrency**: Ensure the dispatcher does not block incoming ingestion while processing handlers. /speckit.specify Role: AI Researcher / Architect Context: We need a localized graph structure that mimics "Working Memory" with decay. Task: Design the `WorkingMemoryGraph`. Requirements: 1. **Node Wrapper**: - Create a `MemoryNode` class that wraps a `Fact` or `Rule`. - Attributes: `activation_level` (float 0.0 to 1.0), `last_accessed` (timestamp). 2. **The Graph Manager**: - Class `AttentionGraph`. - Method `stimulate(fact_id, amount)`: Increases activation, capped at 1.0. - Method `decay(factor)`: Multiplies all activation levels by a factor (e.g., 0.9). - Method `prune(threshold)`: Removes nodes with activation < threshold to save memory. - Method `get_active_subgraph()`: Returns only nodes/edges currently above threshold."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fact Ingestion and Structuring (Priority: P1)

As a system developer, I need to add new facts into a structured, queued pipeline so that they can be processed reliably and without loss.

**Why this priority**: This is the foundational capability for the entire knowledge graph system. Without a way to ingest and structure data, no further reasoning or processing can occur.

**Independent Test**: Can be tested by enqueuing a fact and verifying it appears in the queue with the correct structure and metadata. Value is delivered by providing a reliable entry point for data.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** a new piece of information (subject, predicate, object) is provided, **Then** a `Fact` object is created with a unique ID, timestamp, and source.
2. **Given** a valid `Fact` object, **When** it is added to the ingestion queue, **Then** it is successfully stored and available for batch dequeuing.
3. **Given** a `Fact` is already in the queue, **When** the identical fact is added again, **Then** the queue prevents the duplicate from being added to ensure idempotent processing.

---

### User Story 2 - Asynchronous Fact Processing (Priority: P2)

As a system architect, I need a dispatcher that processes facts from the queue and distributes them to multiple, independent handlers in parallel, so that we can apply different reasoning or storage strategies concurrently.

**Why this priority**: This enables the core processing logic. It decouples data ingestion from its processing and allows for a flexible, extensible architecture where new capabilities (handlers) can be added without modifying the core pipeline.

**Independent Test**: Register two mock handlers. Enqueue a batch of facts. Verify that both handlers receive the exact same batch of facts for processing.

**Acceptance Scenarios**:

1. **Given** facts are present in the ingestion queue, **When** the dispatcher runs, **Then** it dequeues facts in batches.
2. **Given** multiple handlers are registered with the dispatcher, **When** a batch is dequeued, **Then** the dispatcher sends the batch to all registered handlers simultaneously.
3. **Given** handlers are processing a batch, **When** new facts are enqueued, **Then** the ingestion process is not blocked.

---

### User Story 3 - Working Memory and Attention Mechanism (Priority: P3)

As an AI researcher, I need to model a "working memory" where facts and rules have a decaying activation level, so that the system can focus its reasoning on the most relevant and recent information.

**Why this priority**: This provides an advanced capability for managing the focus of the reasoning engine, enabling more sophisticated AI behaviors by mimicking cognitive attention. It builds upon the foundational ingestion and processing pipelines.

**Independent Test**: Stimulate a node in the graph and verify its activation increases. Trigger the decay process and verify all nodes' activation levels decrease. Prune and verify only nodes below the threshold are removed.

**Acceptance Scenarios**:

1. **Given** a fact in the working memory, **When** it is stimulated, **Then** its activation level increases and is capped at 1.0.
2. **Given** a working memory with multiple activated nodes, **When** the decay process is triggered, **Then** the activation level of all nodes is reduced by a set factor.
3. **Given** a working memory with nodes at various activation levels, **When** the prune process is run with a threshold, **Then** only nodes with activation below the threshold are removed from memory.

### Edge Cases

- **Queue Overflow**: What happens if facts are enqueued faster than they can be processed? The in-memory queue could lead to an out-of-memory error. A strategy for backpressure or dropping facts may be needed in a production system.
- **Handler Failure**: How does the system handle a case where one of the parallel handlers fails while processing a batch? Does it affect other handlers? Should there be a retry mechanism?
- **Empty Graph**: How do decay and prune operations behave on an empty or near-empty working memory graph?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST represent knowledge using a `Fact` structure containing a subject, predicate, and object.
- **FR-002**: Each `Fact` MUST include metadata for a unique ID, creation timestamp, and data source.
- **FR-003**: The system MUST provide an ingestion queue to hold facts before processing.
- **FR-004**: The queue MUST support operations to add a single fact and to retrieve a batch of facts.
- **FR-005**: The system MUST prevent duplicate facts from co-existing in the queue to be processed.
- **FR-006**: The system MUST provide a dispatcher component to asynchronously process facts from the ingestion queue.
- **FR-007**: The dispatcher MUST process facts in batches to optimize throughput.
- **FR-008**: The system MUST allow for multiple, independent fact-processing modules (handlers) to be registered to receive data.
- **FR-009**: The dispatcher MUST distribute fact batches to all registered handlers in parallel.
- **FR-010**: The system MUST support a "working memory" graph model for currently relevant facts and rules.
- **FR-011**: Each item in the working memory MUST have a dynamic `activation_level` between 0.0 and 1.0.
- **FR-012**: The system MUST provide a mechanism to "stimulate" an item, increasing its activation level.
- **FR-013**: The system MUST provide a mechanism to "decay" the activation levels of all items in the working memory over time.
- **FR-014**: The system MUST be able to "prune" (remove) items from the working memory that fall below a specified activation threshold.

### Key Entities

- **Fact**: The atomic unit of knowledge, comprising a subject-predicate-object triplet and associated metadata (ID, source, timestamp).
- **Fact Ingestion Queue**: A temporary, ordered holding area for incoming facts awaiting processing.
- **Dispatcher**: A component that orchestrates fact processing by retrieving batches from the queue and distributing them to subscriber handlers.
- **Handler**: A subscriber component that performs a specific action on a batch of facts (e.g., inference, storage, logging).
- **Working Memory Graph**: A dynamic graph structure representing the current focus of the reasoning engine, where nodes have activation levels.
- **Memory Node**: A wrapper for a Fact or Rule within the Working Memory, containing its activation state and other metadata like last access time.

### Graph Structure (RDF Model)

The knowledge graph uses an RDF (Resource Description Framework) model with automatic provenance tracking via reification. Understanding the structure is critical for querying and traversal.

![RDF Graph Structure with Provenance](../../docs/images/graph_structure.png)
*Figure: RDF triple with provenance metadata using reification*

#### Nodes (Sommets)

The graph contains three types of nodes:

1. **Entity Nodes** (URIRef or BNode):
   - User entities: `:Alice`, `:Bob`, `:User` (using `user_namespace`)
   - Organization entities: `:TechCorp`, `:Google`
   - Course/Event entities: `:PythonCourse`
   - Concept nodes: Classes from ontologies (e.g., `foaf:Person`, `schema:Organization`)

2. **Literal Nodes** (RDFLiteral):
   - String values: Names, descriptions
   - Numeric values: Ages, counts
   - Dates: `xsd:dateTime` timestamps
   - Booleans: `xsd:boolean` flags

3. **Provenance Nodes** (Blank Nodes):
   - Reification nodes: `_:stmt1`, `_:stmt2` (automatically generated)
   - Each provenance node is of type `rdf:Statement`
   - Links to the original triple via `rdf:subject`, `rdf:predicate`, `rdf:object`

#### Edges (Arêtes)

Edges represent relationships and are categorized as follows:

##### Domain Predicates (Knowledge Layer)

These represent actual knowledge relationships:

- **Social**: `foaf:knows` (symmetric), `foaf:friendOf`
- **Professional**: `schema:worksFor`, `schema:colleague`, `schema:memberOf`
- **Educational**: `schema:instructor`, `schema:attendee`, `schema:teaches`
- **Organizational**: `schema:parentOrganization`, `schema:department`
- **Typing**: `rdf:type` (class membership)
- **Custom**: `sem:potentialMentor`, `sem:collaboratesWith`

##### Provenance Predicates (Metadata Layer)

These track the origin and quality of information:

- **`sem:source`** → Literal: `"user"` | `"owlrl"` | `"sparql-rule"` | `"user-verified"`
- **`sem:sourceRule`** → URIRef: ID of the SPARQL rule that inferred this fact
- **`sem:timestamp`** → xsd:dateTime: When the fact was added
- **`sem:confidence`** → xsd:decimal: Confidence score (0.0–1.0)
- **`sem:uncertain`** → xsd:boolean: Whether verification is needed
- **`sem:uncertainPredicate`** → URIRef: Marks which predicate is uncertain

##### Reification Predicates (Structural Layer)

Used to link provenance metadata to triples:

- **`rdf:type`** → `rdf:Statement`: Declares a node as a reified statement
- **`rdf:subject`** → URIRef: Points to the subject of the reified triple
- **`rdf:predicate`** → URIRef: Points to the predicate of the reified triple
- **`rdf:object`** → URIRef/Literal: Points to the object of the reified triple

#### Graph Traversal Patterns

To query the knowledge graph effectively, use these patterns:

**1. Basic Fact Retrieval**
```sparql
SELECT ?s ?p ?o WHERE {
  ?s ?p ?o .
  FILTER(?p NOT IN (rdf:type, rdf:subject, rdf:predicate, rdf:object, sem:source, sem:timestamp))
}
```

**2. Facts with Provenance**
```sparql
SELECT ?s ?p ?o ?source ?confidence WHERE {
  ?s ?p ?o .
  ?stmt a rdf:Statement ;
        rdf:subject ?s ;
        rdf:predicate ?p ;
        rdf:object ?o ;
        sem:source ?source ;
        sem:confidence ?confidence .
}
```

**3. User-Contributed Facts Only**
```sparql
SELECT ?s ?p ?o WHERE {
  ?s ?p ?o .
  ?stmt a rdf:Statement ;
        rdf:subject ?s ;
        sem:source "user" .
}
```

**4. Inferred Facts (OWL-RL or SPARQL Rules)**
```sparql
SELECT ?s ?p ?o ?sourceRule WHERE {
  ?s ?p ?o .
  ?stmt a rdf:Statement ;
        rdf:subject ?s ;
        sem:source ?srcType ;
        sem:sourceRule ?sourceRule .
  FILTER(?srcType IN ("owlrl", "sparql-rule"))
}
```

**5. Uncertain Facts Needing Verification**
```sparql
SELECT ?s ?p ?o ?confidence WHERE {
  ?s ?p ?o .
  ?stmt a rdf:Statement ;
        rdf:subject ?s ;
        rdf:predicate ?p ;
        sem:uncertain true ;
        sem:confidence ?confidence .
}
```

#### Multi-Graph Architecture

The system maintains three separate RDF graphs:

1. **Main Graph** (`graph`): Confirmed facts (explicit + verified inferences)
2. **Pending Verifications Graph** (`pending_verifications_graph`): Uncertain inferences awaiting user confirmation
3. **Rejected Verifications Graph** (`rejected_verifications_graph`): Inferences explicitly rejected by user

When traversing the knowledge graph, consider which graph(s) to query based on your use case.


## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid facts enqueued are eventually dequeued and delivered to all registered handlers under normal operating conditions.
- **SC-002**: The in-memory ingestion queue can handle a sustained burst of 10,000 fact submissions per second.
- **SC-003**: The dispatcher can process and distribute a batch of 100 facts to 3 handlers in under 50 milliseconds.
- **SC-004**: The working memory's decay function correctly reduces activation levels across 10,000 nodes within 100 milliseconds.
- **SC-005**: Pruning a working memory graph of 100,000 nodes correctly removes all and only the nodes below the specified activation threshold.