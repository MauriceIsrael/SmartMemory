# SmartMemory

**Give your LLM structured memory** | Transform conversations into verified knowledge graphs

<p align="center">
  <em>An MCP server that teaches AI assistants business rules through natural dialogue</em>
</p>

---

## 🎯 What is SmartMemory?

SmartMemory enables your favorite LLM (Claude, Gemini, etc.) to:

- 📝 **Remember facts** in a structured, verifiable format
- 🧠 **Learn business rules** through conversation
- ⚡ **Automatically deduce** new information using inference
- ✅ **Request validation** for uncertain conclusions

**Use cases**: Regulatory compliance, access control, business rules, enterprise knowledge bases

---

## 🚀 Quick Start

### Step 1: Install SmartMemory

```bash
# Clone the repository
git clone https://github.com/yourusername/SmartMemory
cd SmartMemory

# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install SmartMemory
pip install -e .
```

### Step 2: Verify Installation

Run the quick demo to verify everything works:

```bash
python examples/quick_demo.py
```

You should see SmartMemory:
- ✅ Add facts (Alice and Bob work at Google)
- ✅ Answer queries (Who works at Google?)
- ✅ Apply rules and deduce new information

---

## 🤖 Connect Your LLM

SmartMemory uses the **Model Context Protocol (MCP)** to integrate with AI assistants.

### Option A: Claude Desktop

**1. Locate the configuration file**

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**2. Add SmartMemory**

Edit the file and add:

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

> ⚠️ **Important**: Replace `/absolute/path/to/SmartMemory` with the actual path on your machine!

**3. Restart Claude Desktop**

Close and relaunch the application. SmartMemory is now available!

### Option B: Other MCP Clients (Gemini, etc.)

To use SmartMemory with other MCP-compatible LLMs, refer to your MCP client's documentation:

- **Antigravity (Gemini)**: MCP server auto-configures
- **Other clients**: See [docs/getting-started.md](docs/getting-started.md#mcp-configuration)

---

## 💬 Interactive Demo: From Facts to Rules

Here is a real example of a dialogue with SmartMemory. Notice how the system starts with zero knowledge, learns facts, proposes rules based on patterns, and then uses those rules to answer questions it couldn't answer before.

```
> I know Bob
LLM: ✦ I've processed your statement "I know Bob" and confirmed there are no pending verifications.

> He goes at work by car
LLM: ✦ I've noted that Bob goes to work by car.

> Can Bob vote?
LLM: ✦ Based on the information you provided, I can't definitively answer whether Bob can vote. 
     However, you mentioned he goes to work by car, which implies he is an adult.
     
     May I add an inference rule that if a person goes to work by car, they are considered an adult?

> yes
LLM: ✨ Rule Suggestion: 'goes_to_work_by_car_implies_adult'
     Description: A person who goes to work by car is an adult.
     Confidence: 0.8
     
     Please review the preview and approve it.

> I approve
LLM: ✅ Rule 'goes_to_work_by_car_implies_adult' approved and activated.
     
     Now, to determine if Bob can vote, I need to add another rule: that an adult can vote.
     May I add an inference rule that if a person is an adult, they can vote?

> yes
LLM: ✨ Rule Suggestion: 'adult_can_vote'
     Description: An adult can vote.
     Confidence: 0.8
     
     Please review the preview and approve it.

> I approve
LLM: ✅ Rule 'adult_can_vote' approved and activated.
     ✦ Yes, based on the rules we've established, Bob can vote.

> great!
LLM: ✦ I'm glad I could help! Is there anything else you'd like to know?

> Je connais Alice
LLM: ✦ J'ai noté que vous connaissez Alice.

> Elle va au boulot en train
LLM: ✦ J'ai enregistré qu'Alice va au travail en train.

> est-ce qu'Alice peut voter?
LLM: ✦ I can't definitively say if Alice can vote yet. We know she goes to work by train. 
     Similar to our previous discussion about Bob, going to work by train strongly suggests that she is an adult.
     
     May I add an inference rule that if a person goes to work by train, they are considered an adult?

> non ce n'est pas complètement sur, que peut-on déduire du fait qu'elle travaille ?
LLM: ✦ Okay, I've noted that Alice works.
     Given that she works, we can infer she is an adult. May I add an inference rule that if a person works, they are considered an adult?

> en France l'age legal pour travailler est 16 ans...
LLM: ✦ You've brought up an excellent point. The legal working age in France is 16, but the voting age is 18, so we can't directly infer voting eligibility from the fact that someone works.
     
     To resolve this, do you happen to know Alice's age?

> non on ne peut rien en déduire
LLM: ✦ Given the information we have, and the legal ages for working and voting in France, I cannot definitively determine if Alice can vote.
```

### What just happened?

1.  **Fact Accumulation**: The system learned specific facts about Bob and Alice (`:knows`, `:goesToWorkBy`).
2.  **Rule Induction**: When asked a question it couldn't answer ("Can Bob vote?"), it looked for logical paths. It noticed a pattern ("goes by car") and proposed a high-level rule ("car -> adult").
3.  **Chain Reasoning**: It realized that to answer the voting question, it needed a second link ("adult -> vote"), which it also proposed.
4.  **Inference Execution**: Once approved, these rules were immediately applied to answer the original question.
5.  **Ambiguity Handling**: For Alice, the system tried to apply a similar logic ("train -> adult"), but the user corrected it. The system adapted, avoiding the incorrect inference.

This loop of **Observation -> Induction -> Verification -> Execution** is the core of SmartMemory.

---

## 📊 Visualize Your Knowledge

SmartMemory includes a **web dashboard** to visually explore your knowledge graph.

### Quick Launch

```bash
# From the SmartMemory directory
./scripts/start_dashboard.sh
```

The dashboard automatically opens at `http://localhost:5173`

**Features**:
- 📊 Real-time knowledge graph statistics
- 🔍 Search and browse facts
- ⚙️ Manage inference rules
- 🔄 Auto-refresh during LLM conversations

<details>
<summary>📝 Manual setup (optional)</summary>

If you prefer to launch components separately:

**Backend** (Terminal 1):
```bash
cd src/supervision_backend
export PYTHONPATH=$PYTHONPATH:$(pwd)/../..
../../venv/bin/uvicorn main:app --reload --port 8000
```

**Frontend** (Terminal 2):
```bash
cd src/supervision_frontend
npm install
npm run dev -- --open
```

</details>

---

## 🎓 Extract Interesting Rules

### Default Rules

SmartMemory ships with 5 baseline rules:

1. **Relation symmetry**: If Alice knows Bob, then Bob knows Alice
2. **Colleagues**: Two people working at the same company are colleagues
3. **Uncle/aunt**: A parent's sibling is an uncle/aunt
4. **Adult**: A person 18 years or older is an adult
5. **Voting eligibility**: An adult can vote

### How to Create Your Own Rules?

#### Method 1: Through Conversation (Recommended)

Simply state your rule in natural language:

```
You: "An employee working for more than 5 years gets extra vacation days"

LLM: I understand. Here's the SPARQL rule I propose:
     
     Name: seniority_extra_vacation
     IF: ?employee :yearsOfService ?years AND ?years > 5
     THEN: ?employee :hasRight :ExtraVacation
     
     Is this correct?

You: "Yes, add it"
LLM: ✓ Rule activated and applied to the graph
```

**What happens here?** The LLM performs **rule extraction** from natural language - a key neuro-symbolic capability that bridges unstructured dialogue with formal logic. This is conceptually similar to **knowledge distillation** but operates at the symbolic level, creating interpretable, auditable rules rather than neural weights.

#### Method 2: From Documents
 
 You can load documents containing your rules using the `load_document` CLI tool.
 
 **Prerequisites**:
 You must provide an LLM configuration for the system to extract rules from the text.
 
 **Option A: Using OpenAI (or Anthropic)**
 ```bash
 export OPENAI_API_KEY="sk-..."
 # or
 export ANTHROPIC_API_KEY="sk-ant-..."
 ```
 
 **Option B: Using Ollama (Local)**
 ```bash
 export SMART_MEMORY_LLM_MODEL="ollama/llama3"
 export OLLAMA_HOST="http://localhost:11434"
 ```
 
 **Command**:
 Run the loader using the module execution path (ensure `src` is in PYTHONPATH):
 
 ```bash
 # Load a PDF with company regulations
 PYTHONPATH=src python3 -m smart_memory.cli.load_document --file "company_handbook.pdf" --title "Company Handbook"
 ```
 
 SmartMemory will:
 1. 📄 Parse the document
 2. 🧠 Extract potential rules using the configured LLM
 3. 📋 Present rules for bulk validation
 4. ✅ Activate approved rules
 
 **Concrete example**: Loading official chess rules
 ```bash
 PYTHONPATH=src python3 -m smart_memory.cli.load_document --file "chess_rules_FIDE.pdf" --title "Regles FIDE"
 ```
 
 The LLM will automatically extract rules like:
 - "A king in check must move"
 - "Castling is only possible if the king has never moved"
 - etc.
 
 You can then approve all correct rules in bulk.
 
 **Under the hood**: This leverages the LLM's **semantic understanding** to identify normative patterns in unstructured text, then formalizes them as SPARQL CONSTRUCT or ASK queries. The human validation step implements **human-in-the-loop** verification, critical for high-stakes domains.

#### Method 3: Custom SPARQL Files

For advanced users, create `.sparql` files in `user_rules/`:

```sparql
# user_rules/my_rule.sparql
PREFIX : <http://example.org/>

CONSTRUCT {
  ?employee :hasRight :ExtraVacation .
}
WHERE {
  ?employee :yearsOfService ?years .
  FILTER(?years > 5)
}
```

See [docs/CUSTOM_RULES.md](docs/CUSTOM_RULES.md) for the complete guide.

**For experts**: SmartMemory uses **SPARQL 1.1 CONSTRUCT** queries as the rule representation language. This choice provides:
- First-order logic expressiveness with negation-as-failure (via FILTER NOT EXISTS)
- Integration with standard RDF/OWL reasoners
- Decidability guarantees (rules are monotonic by design)
- Transparent rule execution via SPARQL query plans

### View Active Rules

**Via dashboard**: "Inference Rules" tab

**Via CLI**:
```bash
# List all rules
python scripts/list_rules.py

# View a specific rule
python scripts/list_rules.py --rule-id "driving_requires_license"
```

---

## 🔍 Practical Use Cases

### 1. GDPR Compliance

```
You: "Personal data cannot be retained for more than 3 years"
LLM: [Creates validation rule]

You: "User X has an account created in 2019"
LLM: ⚠️ ALERT: User X's data exceeds retention limit (GDPR rule)
```

**Technical note**: This demonstrates **compliance reasoning** - the rule acts as a constraint checker. In Description Logic terms, this is an ABox consistency check against TBox constraints.

### 2. Access Control

```
You: "Only managers can approve expenses above €1000"
LLM: [Activates rule]

You: "Alice wants to approve a €1500 expense"
LLM: ✓ Alice is a manager, she can approve
     (automatically deduced via rule)
```

**Technical note**: This implements **role-based access control (RBAC)** through forward-chaining inference. The system performs **materialized reasoning**, pre-computing permissions rather than checking at query time.

### 3. Technical Knowledge Base

```
You: [Loads technical manual]
LLM: I extracted 47 troubleshooting rules. Would you like to review them?

Later...
You: "The system shows error E502"
LLM: According to the rules, this indicates a network issue.
     Recommended actions: 1) Check cable, 2) Restart router
```

**Technical note**: This showcases **diagnostic reasoning** via backward chaining. The inference engine traces from observed symptoms (error code) to root causes, explaining its conclusions through the rule chain.

---

## 🧠 Neuro-Symbolic Architecture

SmartMemory implements a **hybrid neuro-symbolic AI architecture** that combines:

- **Neural component (LLM)**: 
  - Natural language understanding
  - Pattern recognition from unstructured data
  - Rule proposal from examples
  - Semantic similarity matching

- **Symbolic component (RDF/SPARQL)**:
  - Formal knowledge representation
  - Guaranteed logical consistency
  - Transparent inference traces
  - Auditable provenance

```
┌─────────────────────────────────────────────────────────┐
│                    User Interaction                     │
│              (Natural Language Dialogue)                │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ MCP Protocol
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SmartMemory MCP Server                     │
│                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐   │
│  │  Triple Extractor   │    │  Inference Engine   │   │
│  │  (Neural)           │───▶│  (Symbolic)         │   │
│  │                     │    │                     │   │
│  │  • NL→RDF          │    │  • Forward chaining │   │
│  │  • Confidence      │    │  • SPARQL rules     │   │
│  │  • Entity linking  │    │  • OWL reasoning    │   │
│  └─────────────────────┘    └─────────────────────┘   │
│                     │              │                   │
│                     ▼              ▼                   │
│         ┌────────────────────────────────┐            │
│         │   RDF Knowledge Graph          │            │
│         │   • Named graphs (provenance)  │            │
│         │   • Reified statements         │            │
│         │   • Timestamped quads          │            │
│         └────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

**Key architectural decisions**:

1. **Separation of concerns**: Neural extraction is isolated from symbolic reasoning, enabling independent optimization of each component
2. **Provenance-first design**: Every triple is stored in a named graph with metadata (source, timestamp, confidence)
3. **Monotonic reasoning**: Rules only add triples, never retract (enabling incremental materialization)
4. **Human-in-the-loop**: Low-confidence inferences trigger verification prompts before materialization

---

## ⚙️ Advanced Configuration

### Enable OWL Reasoning (Optional)

By default, SmartMemory uses lightweight SPARQL rules for fast startup (<2s).

To enable full OWL reasoning (FOAF, Schema.org ontologies):

1. Edit `src/smart_memory/config.py`
2. Change `OWL_REASONING = False` to `OWL_REASONING = True`
3. Restart SmartMemory

> ⚠️ Startup will be slower (~5-10s) but you gain access to sophisticated inferences.

**Technical details**: With OWL reasoning enabled:
- **RDFS entailment**: Automatic subclass/subproperty inference
- **OWL 2 RL profile**: Limited but decidable subset of OWL
- **Ontology alignment**: Cross-ontology reasoning (e.g., `foaf:knows` ⟷ `schema:knows`)
- **Property chains**: Transitive/inverse property inference

Trade-off: T-Box reasoning cost is O(n²) in worst case vs O(n) for pure SPARQL rules.

### Customize Confidence Thresholds

Edit `src/smart_memory/config.py`:

```python
# Minimum confidence for automatic acceptance
AUTO_ACCEPT_THRESHOLD = 0.9  # Default: 0.95

# Minimum confidence for human verification prompt
VERIFICATION_THRESHOLD = 0.6  # Default: 0.7

# Below this: silent rejection
# Between 0.6-0.9: request verification
# Above 0.9: automatic acceptance
```

---

## 📚 Complete Documentation

- **[Getting Started Guide](docs/getting-started.md)**: Detailed installation and examples
- **[MCP Tools Reference](docs/getting-started.md#tools-overview)**: All available tools
- **[Custom Rules Guide](docs/CUSTOM_RULES.md)**: Write your own SPARQL inference rules
- **[Architecture Deep Dive](docs/architecture-overview.md)**: Internal design and decisions

---

## 🔬 For Researchers

SmartMemory implements concepts from:

- **Neuro-symbolic AI**: Hybrid reasoning combining neural and symbolic approaches
- **Knowledge graph completion**: Rule-based vs embedding-based inference
- **Explainable AI (XAI)**: Every inference has a transparent SPARQL trace
- **Human-in-the-loop ML**: Active learning with confidence-based human queries
- **Semantic Web**: RDF, SPARQL, OWL standards for knowledge representation

**Key differentiators**:
- **Rule transparency**: Unlike neural KGC methods (TransE, DistMult), all inferences are explainable via SPARQL query plans
- **Formal guarantees**: Logical consistency is maintained (unlike pure LLM memory)
- **Collaborative learning**: Human and LLM co-create the ontology through dialogue

**Relevant papers**:
- Garcez et al. (2019) - *Neural-Symbolic Learning and Reasoning*
- Hitzler & Sarker (2022) - *Neuro-Symbolic Artificial Intelligence: The State of the Art*
- Bouraoui et al. (2020) - *Extracting Rules from Deep Neural Networks*

---

## 🛠️ Technical Stack

- **Backend**: Python 3.11+, RDFLib (RDF processing), OWL-RL (reasoning)
- **Query Language**: SPARQL 1.1 (queries + CONSTRUCT rules)
- **Integration**: Model Context Protocol (MCP) SDK
- **Dashboard**: SvelteKit, TypeScript, TailwindCSS
- **Persistence**: Turtle (.ttl) serialization + named graphs

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- How to submit PRs

Areas of interest:
- Additional MCP client integrations
- Performance optimization for large graphs
- New inference rule templates
- UI/UX improvements for dashboard

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Built with ❤️ using:
- [RDFLib](https://rdflib.readthedocs.io/) - RDF/SPARQL processing
- [Model Context Protocol](https://modelcontextprotocol.io/) - LLM integration
- W3C Semantic Web standards (SPARQL, OWL, RDF)

---

**Questions?** Open an issue or discussion on GitHub

**Version**: 0.1.0 | **By**: SmartMemory Contributors
