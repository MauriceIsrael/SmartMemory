# Neuro-Symbolic AI in SmartMemory

**SmartMemory** implements a practical **Neuro-Symbolic** architecture, bridging the gap between the flexible, probabilistic world of Large Language Models (LLMs) and the rigid, deterministic world of formal logic (Knowledge Graphs).

## The Problem

- **LLMs (Neural)** are creative and flexible but prone to hallucinations and lack "truth". They cannot guarantee that $A \implies B$.
- **Knowledge Graphs (Symbolic)** are precise and verifiable but rigid and hard to populate. They require strict schemas and formal query languages (SPARQL).

## The Solution: Hybrid Architecture

SmartMemory uses the LLM as a **semantic interface** to the formal system, creating a loop where both systems play to their strengths.

```mermaid
graph TD
    User[User Input] --> LLM[LLM (Neural)]
    LLM -->|1. Extract Facts| KG[Knowledge Graph (Symbolic)]
    LLM -->|2. Propose Rules| RuleEngine[Rule Engine]
    RuleEngine -->|3. Validate| Human[Human Approval]
    Human -->|4. Activate| KG
    KG -->|5. Infer New Facts| KG
    KG -->|6. Provenance| LLM
    LLM -->|7. Explain| User
```

### 1. Neural Extraction, Symbolic Storage
The LLM converts natural language ("Alice works at Google") into formal RDF triples (`:Alice schema:worksFor :Google`).
- **Benefit**: User speaks natural language, system stores structured data.

### 2. Conversational Rule Learning
Instead of hardcoding logic, the LLM **observes patterns** and proposes formal rules.
- **User**: "Driving requires a license."
- **LLM**: "I can formalize that. If `?x uses :Car`, then `?x requires :DrivingLicense`."
- **System**: Generates SPARQL `CONSTRUCT` query.

### 3. Human-in-the-Loop Verification
The symbolic system acts as a **guardrail**.
- **Soft Inference**: LLM "thinks" X might be true.
- **Hard Inference**: System **proves** X is true using approved rules.
- **Verification**: If confidence < 1.0, the system asks the user to confirm, turning a probability into a hard fact.

### 4. Provenance & Explainability
Every fact in SmartMemory has a **provenance chain**:
- **Source**: Did a user say it? Did a rule infer it?
- **Rule**: Which rule generated this fact?
- **Confidence**: How certain are we?

This makes the AI's knowledge **auditable**. You can ask "Why do you believe X?" and get a precise answer pointing to the specific rule and source facts.

## Why This Matters

This approach enables **reliable AI agents** for enterprise use cases:
- **Compliance**: "Why was access granted?" (Traceable to specific policy rule)
- **Consistency**: Rules apply universally, unlike LLM prompts which can be inconsistent.
- **Evolution**: The system gets smarter as it learns more rules from the user.
