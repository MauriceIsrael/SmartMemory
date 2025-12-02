# Architecture SmartMemory

## Vue d'ensemble des services

SmartMemory est composé de **3 modules principaux** qui fonctionnent de manière complémentaire :

```mermaid
graph TB
    LLM[LLM Client<br/>Claude/Gemini]
    MCP[MCP Server<br/>server.py<br/>Python]
    HTTP[HTTP Backend<br/>FastAPI<br/>Python]
    WEB[Web Frontend<br/>SvelteKit<br/>TypeScript]
    KG[(Knowledge Graph<br/>knowledge_graph.ttl)]
    
    LLM <-->|MCP Protocol<br/>stdio| MCP
    WEB <-->|HTTP REST<br/>:8000| HTTP
    MCP -->|rdflib| KG
    HTTP -->|rdflib| KG
    
    style MCP fill:#3776ab,color:#fff
    style HTTP fill:#009688,color:#fff
    style WEB fill:#ff3e00,color:#fff
    style KG fill:#f4a261,color:#000
```

---

## 1. MCP Server (Serveur MCP)

**Fichier principal** : [`src/server.py`](file:///home/momo/Antigravity/SmartMemory/src/server.py)

### Rôle
- Interface directe entre le **LLM** (Claude, Gemini, etc.) et le graphe de connaissances
- Expose des **outils MCP** (7 au total) que le LLM peut appeler
- Gère l'**inférence à deux niveaux** (OWL-RL + règles SPARQL)
- Fonctionne via le **Model Context Protocol (MCP)**

### Communication
- **Protocole** : MCP via `stdio` (standard input/output)
- **Client** : LLM configuré dans `claude_desktop_config.json` ou équivalent
- **Transport** : Pas de HTTP, communication directe par pipes/stdin/stdout

### Outils exposés au LLM
1. `add_fact()` - Ajouter un fait au graphe
2. `query_memory()` - Exécuter des requêtes SPARQL
3. `search_entity()` - Recherche full-text d'entités
4. `verify_inference()` - Confirmer/rejeter des inférences
5. `load_custom_rule()` - Charger une règle d'inférence personnalisée
6. `list_rules()` - Lister les règles actives
7. `get_graph_stats()` - Statistiques du graphe

### Démarrage
```bash
# Démarré automatiquement par le client MCP (Claude Desktop)
# Ou manuellement pour tests :
python -m semantic_memory.server
```

---

## 2. HTTP Backend (Serveur HTTP)

**Fichier principal** : [`src/supervision_backend/main.py`](file:///home/momo/Antigravity/SmartMemory/src/supervision_backend/main.py)

### Rôle
- API REST pour le **dashboard de supervision**
- Permet de visualiser et administrer le système
- Offre une interface **indépendante du LLM**

### Communication
- **Protocole** : HTTP/REST
- **Port** : 8000 (par défaut)
- **Client** : Frontend SvelteKit
- **CORS** : Configuré pour accepter `http://localhost:5173`

### Endpoints API
- `GET /` - Health check
- `GET /health` - Statut détaillé
- `GET /api/stats` - Statistiques du graphe
- `GET /api/facts` - Liste des faits
- `GET /api/rules` - Règles d'inférence
- `GET /api/inference` - Contrôle de l'inférence

### Démarrage
```bash
cd src/supervision_backend
uvicorn main:app --reload --port 8000
```

---

## 3. Web Frontend (Client Web)

**Répertoire** : [`src/supervision_frontend/`](file:///home/momo/Antigravity/SmartMemory/src/supervision_frontend)

### Rôle
- **Interface utilisateur** pour superviser le système
- Dashboard avec visualisations, graphiques, administration
- Permet de contrôler l'inférence sans passer par le LLM

### Communication
- **Protocole** : HTTP (fetch API)
- **Serveur cible** : Backend FastAPI sur `http://localhost:8000`
- **Port de dev** : 5173 (Vite dev server)

### Technologies
- **Framework** : SvelteKit
- **Langage** : TypeScript
- **Build** : Vite
- **UI** : Svelte 5 avec runes

### Démarrage
```bash
cd src/supervision_frontend
npm run dev -- --open
```

---

## Interconnexions

### 1. LLM ↔ MCP Server
```
Claude Desktop Config (JSON)
    ↓
Démarre src/server.py via Python
    ↓
Communication bidirectionnelle via MCP
    - LLM envoie des appels d'outils
    - MCP Server répond avec résultats
```

### 2. Frontend ↔ Backend
```
SvelteKit (5173)
    ↓ HTTP GET/POST
Backend FastAPI (8000)
    ↓ Réponses JSON
SvelteKit affiche les données
```

### 3. Accès au Knowledge Graph

**Les deux serveurs accèdent au même graphe** :
- **MCP Server** : Lecture/écriture via `PersistenceService`
- **HTTP Backend** : Lecture/écriture via les mêmes services

**Fichier partagé** : `knowledge_graph.ttl` (format Turtle RDF)

> ⚠️ **Important** : Pas de synchronisation en temps réel actuellement. Si le MCP Server modifie le graphe, le Backend doit recharger les données.

---

## Flux de données typiques

### Scénario 1 : Ajout d'un fait via LLM
```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant L as LLM (Claude)
    participant M as MCP Server
    participant K as Knowledge Graph
    
    U->>L: "Alice travaille chez Google"
    L->>M: add_fact(":Alice", ":worksAt", ":Google")
    M->>K: Ajoute le triple + inférences
    K-->>M: Confirmé
    M-->>L: "Fait ajouté + 2 inférences"
    L-->>U: "J'ai enregistré que..."
```

### Scénario 2 : Consultation via Dashboard
```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend (Svelte)
    participant B as Backend (FastAPI)
    participant K as Knowledge Graph
    
    U->>F: Ouvre /dashboard
    F->>B: GET /api/stats
    B->>K: Query SPARQL pour stats
    K-->>B: Résultats
    B-->>F: JSON {triples: 1523, ...}
    F-->>U: Affiche dashboard
```

---

## Pourquoi cette architecture ?

### Séparation des préoccupations
1. **MCP Server** : Optimisé pour l'interaction LLM
   - Communication synchrone via stdio
   - Outils adaptés au langage naturel
   
2. **HTTP Backend** : Optimisé pour les applications web
   - API REST standard
   - Endpoints structurés
   
3. **Web Frontend** : Interface utilisateur riche
   - Pas besoin d'un LLM pour administrer
   - Visualisations graphiques

### Avantages
- ✅ **Flexibilité** : Utiliser le système via LLM OU via dashboard
- ✅ **Découplage** : Frontend et MCP Server indépendants
- ✅ **Standards** : MCP pour LLM, REST pour web
- ✅ **Scalabilité** : Backend peut être déployé séparément

### Limitations actuelles
- ⚠️ Pas de synchronisation temps réel entre MCP et HTTP
- ⚠️ Deux serveurs à démarrer séparément
- ⚠️ Duplication possible de logique métier

---

## Résumé

| Module | Technologie | Port | Client | Protocole |
|--------|-------------|------|--------|-----------|
| **MCP Server** | Python + FastMCP | stdio | LLM (Claude) | MCP |
| **HTTP Backend** | FastAPI | 8000 | Frontend | REST |
| **Web Frontend** | SvelteKit | 5173 | Navigateur | HTTP |

**Point commun** : Tous accèdent au même `knowledge_graph.ttl` via `rdflib`.

![Architecture Overview](/home/momo/.gemini/antigravity/brain/df36cacc-f7c9-424e-b346-a03da4df41a1/smartmemory_architecture.webp)
