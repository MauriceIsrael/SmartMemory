# Contracts for 007-knowledge-graph-core

This feature primarily defines internal Python interfaces and data structures (`IFactQueue`, `IFactHandler`, Pydantic `Fact` model) rather than external API contracts (like REST or GraphQL endpoints).

Therefore, there is no OpenAPI or GraphQL schema in this directory. The contracts are implicitly defined by the Python Abstract Base Classes (`abc.ABC`) and Pydantic models detailed in `data-model.md`.

Any future external-facing APIs that interact with these core components would define their contracts in their respective feature directories.