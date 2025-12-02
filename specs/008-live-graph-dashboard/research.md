# Research: Real-time Frontend Updates

**Feature**: 008-live-graph-dashboard

## 1. Objective
The goal is to determine the optimal real-time communication protocol for pushing knowledge graph updates from the FastAPI backend to the SvelteKit frontend.

## 2. Key Question
- **What is the best choice between WebSockets and Server-Sent Events (SSE) for this use case?**

## 3. Analysis

### Use Case Requirements
- **Data Flow**: The flow is one-way (unidirectional) from the server to the client. The backend sends updates to the frontend dashboard; the frontend does not send data back over this channel.
- **Simplicity**: The solution should be as simple as possible to implement and maintain.
- **Reliability**: The connection should handle automatic reconnections if it drops.
- **Compatibility**: It must be well-supported by both FastAPI (Python) and modern web browsers (for SvelteKit).

### Technology Comparison

| Feature | Server-Sent Events (SSE) | WebSockets |
| :--- | :--- | :--- |
| **Data Flow** | Unidirectional (Server -> Client) | Bidirectional |
| **Protocol** | Standard HTTP | Upgraded HTTP connection (ws://) |
| **Client-Side API** | Native `EventSource` API | Requires JavaScript library |
| **Reconnection** | Built-in automatically | Must be implemented manually |
| **Complexity** | Low. Easy to implement on both client and server. | High. More complex handshake and message framing. |
| **Firewall/Proxy** | Works over standard HTTP, so generally no issues. | Can sometimes be blocked by misconfigured proxies. |

## 4. Decision

**Decision**: **Server-Sent Events (SSE)** is the chosen technology.

**Rationale**:
- **Sufficient for the Use Case**: SSE is designed specifically for one-way, server-to-client push notifications, which perfectly matches our requirement. Bidirectional communication (WebSockets) is not needed and would add unnecessary complexity.
- **Simplicity and Maintainability**: SSE is significantly simpler to implement. FastAPI has good support for SSE response types, and the frontend can use the native browser `EventSource` API without any third-party libraries.
- **Robustness**: The `EventSource` API handles connection drops and reconnections automatically, reducing the amount of client-side logic we need to write and improving the user experience.

**Alternatives considered**:
- **WebSockets**: Rejected as overkill. The bidirectional capability is not required.
- **Polling**: Rejected as inefficient. It would create unnecessary HTTP requests and would not be truly "real-time."
