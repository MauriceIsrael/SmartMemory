# SmartMemory

**Give your LLM structured memory** | Transform conversations into verified knowledge graphs

<p align="center">
  <em>An MCP server that teaches AI assistants business rules through natural dialogue</em>
</p>

---

> [!CAUTION]
> **Proof of Concept Only**: This project is an experimental implementation of a Neuro-Symbolic architecture. It is designed to demonstrate how LLMs can interact with knowledge graphs for rule learning. **It is NOT intended for production or professional use.** Use it for research, experimentation, and learning purposes only.

---

## 🎯 What is SmartMemory?

SmartMemory enables your favorite LLM (Claude, Gemini, etc.) to remember facts, learn business rules, and deduce new information.

You can use it in **two main ways**:

### 1. 💬 Conversational Mode (The "Brain")
*   **For**: Individuals using LLM clients (Claude Desktop, etc.).
*   **Goal**: Have your assistant remember facts and learn logic naturally as you chat.
*   **How**: Configure it as an MCP server.
*   **[👉 Go to Setup](#-mode-1-conversational-setup-mcp)**

### 2. 🏗️ Supervision Mode (The "Factory")
*   **For**: Teams, developers, or heavy users.
*   **Goal**: Extract thousands of rules from documents (PDFs) and visualize the knowledge graph.
*   **How**: Deploy the full Dashboard via Docker.
*   **[👉 Go to Setup](#-mode-2-supervision-setup-docker)**

---

## 💬 Mode 1: Conversational Setup (MCP)

This mode gives your LLM "long-term memory" and logical deduction capabilities. You have two options:

### Option A: Hosted Server (Coming Soon) ☁️
*   **Best for**: Users who want zero setup.
*   **How**: You simply configure your MCP client to point to our hosted URL.
*   *Status*: 🚧 Under development. We will provide a public URL soon.

### Option B: Local Server (Private) 🔒
*   **Best for**: Developers & Privacy-conscious users.
*   **How**: You run the server on your own machine. Data never leaves your computer.

#### Installation Steps (Local)

1.  **Clone & Install**
    ```bash
    git clone https://github.com/yourusername/SmartMemory
    cd SmartMemory
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
    ```

2.  **Connect to Claude Desktop**
    Edit your configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
    ```json
    {
      "mcpServers": {
        "smartmemory": {
          "command": "/absolute/path/to/SmartMemory/venv/bin/python",
          "args": ["-m", "smart_memory.server"]
        }
      }
    }
    ```
    *(Replace `/absolute/path/...` with your actual path)*

3.  **Chat!**
    Restart Claude and try:
    > "I know Bob. He goes to work by car. Can he vote?"

    See [Interactive Demo](#-interactive-demo-from-facts-to-rules) below for what to expect.

---

## 🏗️ Mode 2: Supervision Setup (Docker)

This mode runs the **Web Dashboard** and **API server**. Ideally suited for:
*   Visualizing the Knowledge Graph.
*   Extracting rules from documents (PDFs).
*   Hosting a shared memory server for a team.

### Quick Start (Docker)

You don't need Python installed. Just Docker.

1.  **Run the container**
    ```bash
    docker run -p 8080:8080 -v $(pwd)/brain:/app/data smart-memory
    ```
    *(Note: The `-v` volume is optional but recommended to persist your data)*

2.  **Open the Dashboard**
    Go to `http://localhost:8080`

### Advanced Deployment

We support deploying to **Google Cloud Run**, GitHub, etc.
👉 **[Read the Deployment Guide (DEPLOY.md)](DEPLOY.md)** for full instructions on hosting it online.

### Extracting Rules from Documents

Once your dashboard is running (or via CLI):

1.  **Upload a PDF** (e.g., "Company_Policy.pdf").
2.  **Configure LLM**: The server needs an LLM API key (OpenAI, Anthropic, or local Ollama) to read the doc.
3.  **Review**: The system will propose rules. You can approve them in bulk in the dashboard.

---

## 💬 Interactive Demo: From Facts to Rules

Here is what happens when you use **Conversational Mode**:

```
> I know Bob
LLM: ✦ I've processed your statement "I know Bob".

> He goes at work by car
LLM: ✦ I've noted that Bob goes to work by car.

> Can Bob vote?
LLM: ✦ I can't answer yet. But since he drives, he is likely an adult.
     May I add a rule: "Drivers are adults"?

> yes
LLM: ✨ Rule 'drivers_are_adults' added.
     Now, may I add a rule: "Adults can vote"?

> yes
LLM: ✨ Rule 'adults_can_vote' added.
     ✦ Therefore, yes, Bob can vote.
```

---

## 🛠️ Technical Stack

- **Backend**: Python 3.11+, RDFLib, FastAPI
- **Frontend**: SvelteKit, TypeScript, TailwindCSS
- **Reasoning**: Neuro-Symbolic (LLM + SPARQL/OWL)
- **Protocol**: Model Context Protocol (MCP)

---

## 📜 License

MIT License - see [LICENSE](LICENSE)
