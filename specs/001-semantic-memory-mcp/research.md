# Research: Semantic Memory MCP Server

## Technology Choices

### Backend Framework
- **Decision**: Python with the official MCP SDK.
- **Rationale**: The constitution specifies Python, and the MCP SDK is required for protocol compliance.
- **Alternatives considered**: None, as this is dictated by the project constraints.

### Graph Database
- **Decision**: RDFLib
- **Rationale**: RDFLib is the primary library for working with RDF in Python. It provides the necessary tools for parsing, serializing, and querying RDF graphs.
- **Alternatives considered**: None, as RDFLib is the standard choice for this stack.

### Inference Engine
- **Decision**: A simple forward-chaining inference engine implemented in Python.
- **Rationale**: The requirements specify a lightweight inference engine. A simple forward-chaining engine is easy to implement and will be sufficient for the initial set of features. Heavy-duty engines like Jena are explicitly disallowed.
- **Alternatives considered**:
    - **Rete algorithm**: A more complex and performant algorithm for forward-chaining. This was rejected as overkill for the initial requirements.

### Persistence
- **Decision**: Turtle (.ttl) files.
- **Rationale**: The user chose this option for its human-readability and standardization.
- **Alternatives considered**:
    - **SQLite**: Rejected by the user, but could be reconsidered if performance with .ttl files becomes an issue at scale.
