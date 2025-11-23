# Feature Specification: Ontology Loader with Intelligent Caching

**Feature Branch**: `002-ontology-cache`  
**Created**: 2025-11-22  
**Status**: Draft  
**Input**: User description: "Build a robust ontology foundation with intelligent HTTP caching for FOAF, SKOS, and Schema.org"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Server Starts with Pre-loaded Ontologies (Priority: P1)

As a developer, when I start the MCP server, it should automatically load standard ontologies (FOAF, SKOS, Schema.org) so that the knowledge graph has foundational vocabulary without requiring manual setup.

**Why this priority**: This is the core value proposition - autonomous ontology loading. Without this, the feature doesn't exist.

**Independent Test**: Can be fully tested by starting the server and querying the graph for known ontology terms (e.g., `foaf:Person`, `skos:Concept`) and delivers immediate value by providing semantic structure.

**Acceptance Scenarios**:

1. **Given** the server has never been started before, **When** the server starts, **Then** FOAF, SKOS, and Schema.org ontologies are downloaded and loaded into the knowledge graph
2. **Given** the server has cached ontologies, **When** the server starts, **Then** ontologies are loaded from cache in < 100ms
3. **Given** ontologies are loaded, **When** I query for `foaf:Person`, **Then** the system returns the complete class definition with properties

---

### User Story 2 - Intelligent Cache Updates (Priority: P2)

As a system administrator, I want the server to automatically check for ontology updates without re-downloading unchanged files, so that I always have current ontologies while minimizing network usage.

**Why this priority**: Ensures ontologies stay current while being efficient. Important but not critical for initial functionality.

**Independent Test**: Can be tested by mocking HTTP responses with ETag/Last-Modified headers and verifying cache behavior.

**Acceptance Scenarios**:

1. **Given** cached ontologies exist with ETag headers, **When** the server starts, **Then** it sends conditional HTTP requests (If-None-Match) to check for updates
2. **Given** the remote ontology hasn't changed (304 Not Modified), **When** cache validation occurs, **Then** the cached version is used without re-downloading
3. **Given** the remote ontology has changed (200 OK with new ETag), **When** cache validation occurs, **Then** the new version is downloaded and cached
4. **Given** cached ontologies exist with Last-Modified headers, **When** the server starts, **Then** it sends conditional HTTP requests (If-Modified-Since)

---

### User Story 3 - Offline Fail-Safe Mode (Priority: P1)

As a user, when the network is unavailable, I want the server to use cached ontologies so that the system remains functional offline.

**Why this priority**: Critical for reliability and user experience. System should degrade gracefully.

**Independent Test**: Can be tested by disconnecting network and starting the server - should work with cached ontologies.

**Acceptance Scenarios**:

1. **Given** cached ontologies exist and network is unavailable, **When** the server starts, **Then** it loads ontologies from cache and logs a warning about offline mode
2. **Given** no cached ontologies exist and network is unavailable, **When** the server starts, **Then** it logs an error but continues startup (without ontologies)
3. **Given** network becomes available after offline start, **When** cache refresh is triggered, **Then** ontologies are updated in the background

---

### User Story 4 - Cache Management and Diagnostics (Priority: P3)

As a developer, I want to inspect cache status and manually refresh ontologies, so that I can troubleshoot issues and force updates when needed.

**Why this priority**: Nice to have for debugging and maintenance, but not essential for core functionality.

**Independent Test**: Can be tested via CLI commands or API endpoints that expose cache metadata.

**Acceptance Scenarios**:

1. **Given** the server is running, **When** I request cache status, **Then** I see each ontology's URL, cache date, ETag, and file size
2. **Given** I want to force a refresh, **When** I trigger a manual cache clear, **Then** all ontologies are re-downloaded on next startup
3. **Given** corrupted cache files, **When** the server detects invalid RDF, **Then** it re-downloads the ontology and logs the error

---

### Edge Cases

- What happens when an ontology URL returns 404 or 500 errors?
  - System should log error, use cached version if available, continue startup
- How does the system handle partial downloads or network interruptions?
  - Use atomic file writes (write to temp, then rename) to prevent corrupted cache
- What if cache directory permissions are incorrect?
  - Log clear error message with suggested fix, attempt to create directory
- How to handle ontologies that redirect to different URLs?
  - Follow redirects (max 5), cache final URL for future requests
- What if two ontologies define conflicting terms?
  - Load in defined order (FOAF → SKOS → Schema.org), later definitions override

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load FOAF, SKOS, and a curated subset of Schema.org ontologies at startup
- **FR-002**: System MUST cache downloaded ontologies in a local directory with metadata (ETag, Last-Modified, download timestamp)
- **FR-003**: System MUST validate cached ontologies using HTTP conditional requests (If-None-Match, If-Modified-Since)
- **FR-004**: System MUST use cached ontologies when network is unavailable (fail-safe mode)
- **FR-005**: System MUST parse and load ontologies into the RDF graph using rdflib
- **FR-006**: System MUST complete ontology loading in < 2 seconds on cold start, < 100ms on warm start
- **FR-007**: System MUST log all cache operations (downloads, validations, errors) with appropriate severity levels
- **FR-008**: System MUST handle HTTP errors gracefully (timeouts, 404, 500) without blocking startup
- **FR-009**: System MUST use atomic file operations to prevent cache corruption
- **FR-010**: System MUST provide a mechanism to manually clear cache and force re-download

### Key Entities

- **OntologySource**: Represents a remote ontology (URL, preferred format, priority/load order)
- **CacheEntry**: Represents a cached ontology file (local path, ETag, Last-Modified, download timestamp, file hash)
- **CacheMetadata**: SQLite database storing cache entries and validation state
- **OntologyLoader**: Orchestrates loading process (fetch, validate, parse, load into graph)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Server starts successfully with all ontologies loaded in < 2 seconds on first run
- **SC-002**: Server starts with cached ontologies in < 100ms on subsequent runs (warm cache)
- **SC-003**: System successfully operates offline using cached ontologies (0% network dependency after initial download)
- **SC-004**: Cache validation reduces network usage by > 90% for unchanged ontologies (304 responses)
- **SC-005**: Knowledge graph contains all expected ontology terms (e.g., `foaf:Person`, `skos:Concept`, `schema:Thing`) after startup
- **SC-006**: System recovers gracefully from all tested error scenarios (network failures, HTTP errors, corrupted cache) without crashing
