# Guide: Voir les Logs du Serveur MCP

Ce guide explique comment voir les logs de votre serveur SmartMemory MCP.

## Comprendre le Fonctionnement

Quand vous lancez `gemini`, il démarre **une nouvelle instance** de votre serveur MCP selon la configuration dans `~/.gemini/settings.json`. Cette instance est indépendante et gérée par Gemini CLI.

## Option 1: Logs dans un Fichier (Recommandé)

### Configuration

Modifiez votre `~/.gemini/settings.json` pour ajouter la variable d'environnement `LOG_FILE` :

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/home/momo/Antigravity/SmartMemory/venv/bin/python",
      "args": ["/home/momo/Antigravity/SmartMemory/src/server.py"],
      "env": {
        "PYTHONPATH": "/home/momo/Antigravity/SmartMemory",
        "LOG_FILE": "/home/momo/Antigravity/SmartMemory/mcp_server.log"
      }
    }
  }
}
```

### Visualisation

Après avoir redémarré Gemini (`/mcp refresh`), utilisez :

```bash
# Voir les logs en temps réel
./scripts/monitor_logs.sh

# Ou directement avec tail
tail -f mcp_server.log

# Voir les 100 dernières lignes
tail -n 100 mcp_server.log

# Rechercher dans les logs
grep "inference" mcp_server.log
grep "🔍" mcp_server.log  # Règles déclenchées
```

## Option 2: Logs via journalctl (si systemd)

Si votre système utilise systemd :

```bash
# Voir les logs du processus Python
journalctl -f | grep "semantic-memory"

# Ou chercher par PID
ps aux | grep "src/server.py"
journalctl -f _PID=<PID>
```

## Option 3: Logs stderr de Gemini

Gemini CLI capture stderr. Vous pouvez rediriger :

```bash
# Lancer Gemini avec redirection
gemini 2>&1 | tee gemini_session.log
```

## Exemples de Logs

### Démarrage du Serveur

```
2025-11-22 17:35:23,026 - __main__ - INFO - 🚀 Starting Semantic Memory MCP Server...
2025-11-22 17:35:23,026 - __main__ - INFO - 📚 Loading standard ontologies...
2025-11-22 17:35:54,664 - __main__ - INFO - ✓ Loaded 2/3 ontologies
2025-11-22 17:35:54,664 - __main__ - INFO - 🧠 Creating inference rules...
2025-11-22 17:35:54,664 - __main__ - INFO - ✓ Created 3 inference rule(s)
2025-11-22 17:35:54,666 - __main__ - INFO - ✅ Services initialized successfully
2025-11-22 17:35:54,666 - __main__ - INFO -    - Knowledge graph: 2 fact(s)
2025-11-22 17:35:54,666 - __main__ - INFO -    - Ontologies: 17505 triple(s)
2025-11-22 17:35:54,666 - __main__ - INFO -    - Inference rules: 3
```

### Ajout de Fait avec Inférence

```
2025-11-22 17:40:15,123 - __main__ - INFO - Adding fact: :User :likes :Programming
2025-11-22 17:40:15,124 - src.services.inference_engine - DEBUG - Starting inference process with 3 rule(s)
2025-11-22 17:40:15,125 - src.services.inference_engine - INFO - 🔍 Rule 'programming_enthusiast' triggered by 1 fact(s)
2025-11-22 17:40:15,125 - src.services.inference_engine - DEBUG -    Fact: :User :likes :Programming
2025-11-22 17:40:15,126 - src.services.inference_engine - INFO -    ⚠️  Inferred (low confidence 0.70): :User :isA :Developer
2025-11-22 17:40:15,126 - src.services.inference_engine - INFO -    → Requesting user verification
2025-11-22 17:40:15,127 - src.services.inference_engine - INFO -    Rule 'programming_enthusiast' produced 0 automatic inference(s)
2025-11-22 17:40:15,127 - src.services.inference_engine - INFO - 📊 Inference summary: 0 fact(s) added automatically, 1 pending verification(s)
```

## Niveaux de Log

| Symbole | Signification |
|---------|---------------|
| 🚀 | Démarrage du serveur |
| 📚 | Chargement des ontologies |
| 🧠 | Création des règles |
| ✅ | Initialisation réussie |
| 🔍 | Règle d'inférence déclenchée |
| ✓ | Inférence haute confiance (auto-ajoutée) |
| ⚠️ | Inférence basse confiance (vérification) |
| → | Action prise |
| 📊 | Résumé des inférences |
| ❌ | Erreur |

## Debugging

### Activer les logs DEBUG

Modifiez `src/server.py` ligne 32 :

```python
logging.basicConfig(
    level=logging.DEBUG,  # Au lieu de INFO
    handlers=log_handlers,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Vérifier que le serveur tourne

```bash
# Trouver le processus
ps aux | grep "src/server.py"

# Voir les connexions réseau
lsof -i | grep python
```

### Tester manuellement

```bash
# Lancer le serveur manuellement pour voir tous les logs
cd /home/momo/Antigravity/SmartMemory
PYTHONPATH=. LOG_FILE=test.log venv/bin/python src/server.py

# Dans un autre terminal
tail -f test.log
```

## Astuces

1. **Filtrer les logs par type** :
   ```bash
   grep "🔍" mcp_server.log  # Règles déclenchées
   grep "⚠️" mcp_server.log   # Vérifications demandées
   grep "ERROR" mcp_server.log  # Erreurs
   ```

2. **Surveiller en continu** :
   ```bash
   watch -n 2 'tail -n 20 mcp_server.log'
   ```

3. **Logs colorés** :
   ```bash
   tail -f mcp_server.log | ccze -A  # Si ccze est installé
   ```

4. **Rotation des logs** (pour éviter les gros fichiers) :
   ```bash
   # Créer un logrotate config
   cat > /etc/logrotate.d/smartmemory << EOF
   /home/momo/Antigravity/SmartMemory/mcp_server.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   EOF
   ```
