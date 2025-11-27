# Testing SmartMemory MCP Tools in Gemini

Quick verification that all 7 MCP tools work correctly.

## Test Checklist

### ✅ Test 1: add_memory (Natural Language)

**Dans Gemini, demandez**:
```
Please remember that Alice works at Google as a software engineer.
```

**Résultat attendu**:
- ✓ Gemini utilise l'outil `add_memory`
- ✓ Confirmation que 2-3 triples ont été ajoutés
- ✓ Pas de blocage (retour rapide, < 5 secondes)
- ✓ Message indiquant le nombre total de triples

**Vérifier dans les logs** (`/tmp/smartmemory.log`):
```
add_memory called with input: ...
Added X explicit triple(s)
OWL-RL reasoning disabled, skipping  ← IMPORTANT!
SPARQL rule engine executed
```

---

### ✅ Test 2: add_memory (Triple Notation)

**Dans Gemini, demandez**:
```
Remember this triple: :Bob foaf:knows :Alice
```

**Résultat attendu**:
- ✓ Triple ajouté explicitement
- ✓ Pas de blocage

---

### ✅ Test 3: query_memory (Simple Query)

**Dans Gemini, demandez**:
```
Who works at Google?
```

**Résultat attendu**:
- ✓ Gemini utilise `query_memory` avec une requête SPARQL
- ✓ Résultats affichés (Alice devrait apparaître)
- ✓ Pas d'erreur "Unknown namespace prefix"

---

### ✅ Test 4: search_entity

**Dans Gemini, demandez**:
```
Find all people named Alice in my knowledge graph.
```

**Résultat attendu**:
- ✓ Gemini utilise `search_entity`
- ✓ Alice est trouvée
- ✓ Retour rapide

---

### ✅ Test 5: get_graph_stats

**Dans Gemini, demandez**:
```
How much do you know about me? Show me statistics.
```

**Résultat attendu**:
- ✓ Gemini utilise `get_graph_stats`
- ✓ Affichage du nombre de triples
- ✓ Breakdown par source (user, owl-rl, sparql-rule)
- ✓ Nombre de règles actives

---

### ✅ Test 6: list_rules

**Dans Gemini, demandez**:
```
What inference rules are active?
```

**Résultat attendu**:
- ✓ Gemini utilise `list_rules`
- ✓ Liste de ~5 règles par défaut
- ✓ Chaque règle avec description et confiance

---

### ✅ Test 7: verify_inference (si applicable)

**D'abord, créez une situation qui nécessite vérification**:
```
Alice works at Thales. Bob works at Thales.
```

Si une inférence "Alice colleague Bob" est créée avec faible confiance:

**Dans Gemini, demandez**:
```
Show me any inferences that need my verification.
```

Puis acceptez ou rejetez.

**Résultat attendu**:
- ✓ Liste des inférences en attente
- ✓ `verify_inference` fonctionne pour accepter/rejeter

---

### ✅ Test 8: MCP Prompts

**Dans Gemini, tapez `/` pour voir les prompts**:

Vous devriez voir:
- `/remember-fact`
- `/query-knowledge`
- `/add-custom-rule`
- `/show-stats`
- `/verify-inferences`

**Testez un prompt**:
```
/remember-fact Charlie is a data scientist
```

---

## 🐛 Problèmes Potentiels

### Si add_memory bloque
- Vérifier que `SEMMEM_ENABLE_OWL_REASONING=false` dans config
- Regarder `/tmp/smartmemory.log` pour voir où ça bloque

### Si query_memory échoue avec "Unknown namespace"
- La requête SPARQL manque des PREFIX
- Gemini doit inclure les PREFIX nécessaires

### Si aucun outil n'apparaît
- Redémarrer Gemini complètement
- Vérifier que le serveur tourne: `ps aux | grep semantic_memory`
- Vérifier la config MCP dans `~/.gemini/settings.json`

---

## 📊 Résultats Attendus

Temps de réponse pour chaque outil (avec OWL-RL désactivé):
- `add_memory`: < 2 secondes
- `query_memory`: < 1 seconde
- `search_entity`: < 1 seconde  
- `get_graph_stats`: < 1 seconde
- `list_rules`: < 1 seconde
- `verify_inference`: < 1 seconde

Si un outil prend > 10 secondes, il y a probablement un problème de raisonnement OWL-RL.

---

## ✅ Checklist Finale

Après avoir tout testé:

- [ ] ✅ add_memory fonctionne sans blocage
- [ ] ✅ query_memory retourne des résultats
- [ ] ✅ search_entity trouve les entités
- [ ] ✅ get_graph_stats affiche les statistiques
- [ ] ✅ list_rules liste les règles
- [ ] ✅ verify_inference (si testé) fonctionne
- [ ] ✅ MCP Prompts apparaissent avec `/`
- [ ] ✅ Pas de timeout ou blocage > 10s

Si tous les tests passent, SmartMemory est **opérationnel** ! 🎉
