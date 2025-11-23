# Feature Specification: Semantic Memory Visualization Dashboard

**Feature Branch**: `004-visualization-dashboard`
**Created**: 2025-11-22
**Status**: Draft
**Input**: User description: "Je souhaite spécifier un Dashboard de Visualisation pour le serveur MCP Semantic Memory. Ce dashboard est une application web permettant aux utilisateurs de superviser et comprendre l'activité du graphe de connaissances en temps réel."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Monitor Recent Facts in Real-Time (Priority: P1)

A developer testing the Semantic Memory system needs to verify that facts are being correctly ingested into the knowledge graph and observe them as they are added, with clear indication of whether each fact was explicitly provided or automatically inferred.

**Why this priority**: This is the most fundamental need for anyone using the system - immediate feedback that data ingestion is working. Without this visibility, users cannot trust or debug the system.

**Independent Test**: Can be fully tested by adding facts through the MCP server's `add_memory` tool and verifying they appear in the dashboard within the real-time update interval. Delivers immediate value by providing transparency into system operations.

**Acceptance Scenarios**:

1. **Given** the dashboard is open and connected to the server, **When** a new fact "Alice works at TechCorp" is added to the knowledge graph, **Then** the fact appears in the Recent Facts view within 2 seconds with timestamp and provenance marked as "Explicit"
2. **Given** facts exist in the Recent Facts view, **When** the system performs automatic inference and generates "Bob rdf:type Agent" from "Bob rdf:type Person", **Then** the inferred fact appears marked with provenance "Inferred" and distinguishable from explicit facts
3. **Given** the Recent Facts view displays 50+ facts, **When** a user scrolls to the bottom, **Then** older facts are loaded via pagination without page reload
4. **Given** both explicit and inferred facts are displayed, **When** a user applies the "Explicit only" filter, **Then** only user-provided facts are shown
5. **Given** RDF triples contain URIs like `http://xmlns.com/foaf/0.1/Person`, **When** facts are displayed, **Then** URIs are rendered as human-readable labels (e.g., "Person" or "foaf:Person")

---

### User Story 2 - Audit Loaded Inference Rules (Priority: P1)

A system operator needs to verify which inference rules are currently active in the system, understand what each rule does, and confirm that custom rules have been successfully loaded.

**Why this priority**: Rules are the core logic of the inference system. Without visibility into which rules are active, users cannot understand system behavior or diagnose why expected inferences aren't happening.

**Independent Test**: Can be tested by loading the dashboard with default rules, adding a custom rule file to the user rules directory, restarting the server, and verifying the custom rule appears in the Loaded Rules view. Delivers value by providing complete visibility into system configuration.

**Acceptance Scenarios**:

1. **Given** the server has loaded default and custom rules, **When** the user views the Loaded Rules page, **Then** all rules are listed with name, source (Default/Custom), and description
2. **Given** a rule file contains SPARQL comments describing its purpose, **When** the rule is displayed, **Then** the description is extracted and shown to the user
3. **Given** rules have been executing and generating inferences, **When** viewing the rule list, **Then** each rule shows a count of inferences it has produced since server startup
4. **Given** a user wants to understand what a rule does, **When** they click "View SPARQL", **Then** the full SPARQL CONSTRUCT query is displayed in a read-only code viewer with syntax highlighting
5. **Given** a rule has been disabled or failed to load, **When** viewing the rule list, **Then** its status is clearly marked as "Inactive" or "Error" with an explanation

---

### User Story 3 - Observe Live Inference Activity (Priority: P2)

A developer testing a new custom rule needs to see in real-time when inferences are triggered, which rule produced them, and what new facts were generated, including whether the inference requires user verification.

**Why this priority**: Essential for debugging and understanding system behavior, but can be implemented after basic fact monitoring. Enables advanced users to understand the reasoning process.

**Independent Test**: Can be tested by adding facts that trigger a specific rule, then verifying the inference appears in the Live Inferences view with correct attribution and generated triples. Delivers value by making the "black box" reasoning transparent.

**Acceptance Scenarios**:

1. **Given** a spatial transitivity rule is active, **When** facts "Alice lives in Paris" and "Paris is in France" are added, **Then** the Live Inferences view shows a new inference entry with timestamp, rule name, and generated triple "Alice resides in France"
2. **Given** inferences are being generated, **When** viewing the inference log, **Then** each entry indicates whether it came from Level 1 (ontology inference) or Level 2 (SPARQL rule)
3. **Given** a rule generates an uncertain inference, **When** it appears in the log, **Then** it is marked with confidence level "Uncertain" and shows verification status (pending/validated/rejected)
4. **Given** the Live Inferences view is open, **When** new inferences are generated, **Then** they appear automatically without manual refresh within 3 seconds
5. **Given** hundreds of inferences have been generated, **When** viewing the log, **Then** only recent entries (last 100) are shown by default with option to load more or search

---

### User Story 4 - System Health Overview at a Glance (Priority: P2)

A system operator needs a quick overview of the knowledge graph's health and activity to ensure everything is functioning correctly without having to inspect detailed logs.

**Why this priority**: Provides operational awareness and early warning of issues. Important for production systems but not critical for initial development and testing.

**Independent Test**: Can be tested by adding various facts and rules, then verifying the dashboard overview displays accurate aggregate metrics and alerts. Delivers value by enabling proactive monitoring.

**Acceptance Scenarios**:

1. **Given** the knowledge graph contains facts, **When** the user views the Dashboard Overview, **Then** key metrics are displayed: total triples, explicit vs inferred count, active rules count, inferences in last 24h
2. **Given** ontologies are loaded from cache, **When** viewing the overview, **Then** the ontology status section shows count of loaded ontologies and their source (cached/network)
3. **Given** a rule has produced a syntax error or infinite recursion was detected, **When** viewing the overview, **Then** an alert is prominently displayed in the alerts section
4. **Given** the system is operating normally, **When** viewing the overview, **Then** no alerts are shown and all status indicators are green
5. **Given** metrics update in real-time, **When** new facts are added, **Then** the overview metrics refresh within 5 seconds to reflect changes

---

### User Story 5 - Export Data for External Analysis (Priority: P3)

An auditor needs to export the current view of facts, rules, or inferences to CSV or JSON format for external analysis, reporting, or archival purposes.

**Why this priority**: Important for compliance and advanced analysis workflows, but not essential for core dashboard functionality. Can be added after visualization features are stable.

**Independent Test**: Can be tested by displaying facts in a view, clicking "Export to CSV", and verifying a valid CSV file is downloaded with all visible data. Delivers value by enabling integration with external tools.

**Acceptance Scenarios**:

1. **Given** the Recent Facts view displays filtered results, **When** a user clicks "Export to CSV", **Then** a CSV file containing all visible facts (subject, predicate, object, timestamp, provenance) is downloaded
2. **Given** the Loaded Rules view is displayed, **When** a user selects "Export to JSON", **Then** a JSON file containing rule definitions with metadata is downloaded
3. **Given** the Live Inferences view shows recent inferences, **When** exporting, **Then** the export includes inference timestamps, rule names, generated triples, and confidence levels
4. **Given** a large dataset is being exported, **When** the export is triggered, **Then** a progress indicator is shown and the file downloads once complete without timing out

---

### Edge Cases

- What happens when the connection to the MCP server is lost or times out?
- How does the dashboard handle extremely rapid fact addition (100+ facts/second)?
- What happens when RDF URIs cannot be resolved to human-readable labels?
- How does the system display very long SPARQL queries that don't fit in the viewing area?
- What happens when inference logs grow to thousands of entries - is there automatic cleanup?
- How does the dashboard behave on mobile or tablet devices with limited screen space?
- What happens when a rule name contains special characters or is very long?
- How does the system handle facts with Unicode characters, emojis, or non-Latin scripts?
- What happens when multiple browser tabs are open viewing the same dashboard?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboard MUST display recently added RDF triples in chronological order with timestamp, subject, predicate, object, and provenance information
- **FR-002**: Dashboard MUST distinguish between explicit facts (user-provided) and inferred facts (system-generated) through clear visual indicators
- **FR-003**: Dashboard MUST convert RDF URIs to human-readable labels using ontology definitions or showing abbreviated forms (e.g., "foaf:Person" instead of full URI)
- **FR-004**: Dashboard MUST provide filtering capabilities to view explicit facts only, inferred facts only, or both
- **FR-005**: Dashboard MUST implement pagination or infinite scrolling for fact lists exceeding 50 items
- **FR-006**: Dashboard MUST display all loaded inference rules with name, source type (Default/Custom), and description
- **FR-007**: Dashboard MUST show inference statistics for each rule including count of facts generated since server startup
- **FR-008**: Dashboard MUST provide a read-only view of SPARQL code for each rule with syntax highlighting
- **FR-009**: Dashboard MUST indicate rule status (Active/Inactive/Error) with explanations for non-active rules
- **FR-010**: Dashboard MUST display a real-time log of inference activities showing timestamp, rule attribution, generated triples, and confidence level
- **FR-011**: Dashboard MUST differentiate between Level 1 (ontology) and Level 2 (SPARQL rule) inferences in the activity log
- **FR-012**: Dashboard MUST show verification status (pending/validated/rejected) for uncertain inferences
- **FR-013**: Dashboard MUST update all views automatically without manual refresh when new data is available (polling interval ≤ 3 seconds or real-time via WebSocket)
- **FR-014**: Dashboard MUST display a global overview section showing aggregate metrics: total triples, explicit vs inferred ratio, active rules count, 24-hour inference count
- **FR-015**: Dashboard MUST show ontology loading status indicating count of loaded ontologies and their source (cached/network)
- **FR-016**: Dashboard MUST display system alerts for errors (rule syntax errors, infinite recursion detections, connection failures)
- **FR-017**: Dashboard MUST support exporting visible data to CSV format with appropriate column headers and data formatting
- **FR-018**: Dashboard MUST support exporting visible data to JSON format with complete metadata preserved
- **FR-019**: Dashboard MUST provide visual feedback during export operations with progress indication for large datasets
- **FR-020**: Dashboard MUST handle connection failures gracefully by displaying a reconnection status and attempting automatic reconnection
- **FR-021**: Dashboard MUST be responsive and remain functional on desktop browsers (Chrome, Firefox, Safari, Edge) at standard resolutions (1920x1080 and above)

### Key Entities *(include if feature involves data)*

- **Fact Display Record**: A UI representation of an RDF triple with timestamp, provenance indicator, and human-readable labels for subject/predicate/object
- **Rule Information**: Metadata about an inference rule including name, source type, SPARQL code, description, execution statistics, and status
- **Inference Log Entry**: A timestamped record of an inference event with rule attribution, generated triples, inference level, and confidence status
- **System Metrics**: Aggregate statistics about the knowledge graph including triple counts, rule counts, inference rates, and ontology status
- **Alert Item**: A notification about system issues such as rule errors, connection problems, or detected anomalies with severity level and description

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can see newly added facts appear in the dashboard within 3 seconds of addition to the knowledge graph
- **SC-002**: The dashboard remains responsive and interactive when displaying up to 1,000 facts without pagination lag or UI freezing
- **SC-003**: Users can identify whether a fact was explicitly provided or automatically inferred within 1 second of viewing the facts list
- **SC-004**: System operators can view all loaded rules and their execution statistics in a single page view without scrolling horizontally
- **SC-005**: Developers testing rules can observe inference activity in real-time and trace which rule generated which facts within 5 seconds of the inference occurring
- **SC-006**: Users can access the dashboard and view all primary features (facts, rules, inferences, overview) without requiring knowledge of RDF, SPARQL, or semantic web technologies
- **SC-007**: Users can export any view to CSV or JSON format and receive the file within 10 seconds for datasets up to 10,000 records
- **SC-008**: The dashboard maintains connection stability and automatically recovers from temporary network interruptions within 30 seconds without data loss or requiring page reload
- **SC-009**: All dashboard views remain usable and readable on desktop screens at 1920x1080 resolution with no overlapping UI elements or truncated text
- **SC-010**: Users can complete common workflows (viewing recent facts, checking rule status, exporting data) in under 1 minute from dashboard load
