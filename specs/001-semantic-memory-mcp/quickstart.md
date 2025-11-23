# Quickstart: Semantic Memory MCP Server

This guide provides a quick overview of how to use the Semantic Memory MCP Server.

## Adding a Fact
To add a new fact to the knowledge graph, use the `add_fact` tool:

```json
{
  "tool": "add_fact",
  "subject": ":User",
  "predicate": ":likes",
  "object": ":ScienceFiction"
}
```

The server will add this triple to the `explicit_graph`.

## Querying the Graph
You can query the knowledge graph using SPARQL with the `query_graph` tool:

```json
{
  "tool": "query_graph",
  "query": "SELECT ?s WHERE { ?s ?p ?o }"
}
```

This will return a list of all subjects in the graph.

## Elicitation Loop
When the server makes an uncertain inference, it will return a `request_verification` tool call. The client should then ask the user for confirmation.

**Example `request_verification` tool call:**
```json
{
  "tool": "request_verification",
  "id": "verification_123",
  "triple": {
    "subject": ":User",
    "predicate": ":mightLike",
    "object": ":Asimov"
  },
  "certainty_score": 0.7
}
```

The client should then ask the user: "Since you like Science Fiction, do you also appreciate Asimov?".

To get a list of all pending verifications, use the `get_pending_verifications` tool:

```json
{
  "tool": "get_pending_verifications"
}
```

This will return a list of all `VerificationRequest` objects.
