# SmartMemory Logging Guide

## Where are the logs when running with Gemini?

SmartMemory écrit ses logs sur **stderr**. Quand le serveur est lancé par Gemini via MCP, les logs peuvent être dans plusieurs endroits.

## 🔍 Trouver les logs

### Option 1: Activer le logging dans un fichier

Ajoutez cette variable d'environnement dans votre configuration MCP Gemini :

```json
{
  "mcpServers": {
    "semantic-memory": {
      "command": "/home/momo/Antigravity/SmartMemory/venv/bin/python",
      "args": ["-m", "semantic_memory.server"],
      "env": {
        "SEMMEM_LOG_LEVEL": "DEBUG",
        "SEMMEM_LOG_FILE": "/tmp/smartmemory.log"
      }
    }
  }
}
```

Puis consultez les logs :
```bash
tail -f /tmp/smartmemory.log
```

### Option 2: Logs Antigravity

Gemini enregistre probablement stderr dans ses propres logs. Cherchez dans :
```bash
# Chercher les logs récents d'Antigravity
ls -lt ~/.gemini/antigravity/brain/*/

# Ou dans les tmp
ls -lt ~/.gemini/tmp/
```

### Option 3: Redirection manuelle

Créez un wrapper script qui redirige stderr vers un fichier :

**Fichier: `~/smartmemory_wrapper.sh`**
```bash
#!/bin/bash
cd /home/momo/Antigravity/SmartMemory
source venv/bin/activate
python -m semantic_memory.server 2>> /tmp/smartmemory_stderr.log
```

Puis dans la config Gemini :
```json
{
  "command": "/home/momo/smartmemory_wrapper.sh",
  "args": []
}
```

## 📊 Niveaux de logging disponibles

```bash
export SEMMEM_LOG_LEVEL=DEBUG   # Très verbeux (tous les détails)
export SEMMEM_LOG_LEVEL=INFO    # Normal (recommandé)
export SEMMEM_LOG_LEVEL=WARNING # Seulement les avertissements
export SEMMEM_LOG_LEVEL=ERROR   # Seulement les erreurs
```

## 🧪 Tester le logging

Testez manuellement pour voir les logs :

```bash
cd /home/momo/Antigravity/SmartMemory
source venv/bin/activate

# Avec fichier de log
export SEMMEM_LOG_FILE=/tmp/test.log
python -m semantic_memory.server

# Dans un autre terminal
tail -f /tmp/test.log
```

Vous devriez voir :
```
2025-11-25 21:20:00 - semantic_memory.server - INFO - Initializing Semantic Memory Server v0.1.0
2025-11-25 21:20:00 - semantic_memory.logging_config - INFO - File logging enabled: /tmp/test.log
2025-11-25 21:20:01 - semantic_memory.server - INFO - Starting up Semantic Memory server...
...
```

## 🐛 Debugging en temps réel

Pour voir exactement ce que fait le serveur quand Gemini l'appelle :

1. **Activez DEBUG logging** :
   ```json
   "env": {
     "SEMMEM_LOG_LEVEL": "DEBUG",
     "SEMMEM_LOG_FILE": "/tmp/smartmemory_debug.log"
   }
   ```

2. **Ouvrez le fichier de log** dans un autre terminal :
   ```bash
   tail -f /tmp/smartmemory_debug.log
   ```

3. **Utilisez SmartMemory** dans Gemini et regardez les logs en direct

Vous verrez :
- Quand des tools sont appelés
- Les arguments passés
- Les résultats retournés
- Les erreurs éventuelles
- Les inférences déclenchées

## 📝 Exemple de sortie de log

```
2025-11-25 21:20:15 - semantic_memory.server - INFO - MCP tools registered.
2025-11-25 21:20:15 - semantic_memory.server - INFO - MCP prompts registered.
2025-11-25 21:20:16 - semantic_memory.tools.add_memory - INFO - add_memory called with input: Alice works at Google
2025-11-25 21:20:16 - semantic_memory.nlp.triple_extractor - DEBUG - Extracting triples from: Alice works at Google
2025-11-25 21:20:16 - semantic_memory.nlp.triple_extractor - DEBUG - Pattern 'works_at' matched, extracted 3 triples
2025-11-25 21:20:16 - semantic_memory.inference.reasoner - INFO - Applying OWL-RL reasoning...
2025-11-25 21:20:16 - semantic_memory.inference.rule_engine - INFO - Executing SPARQL rules...
2025-11-25 21:20:17 - semantic_memory.tools.add_memory - INFO - Added 3 explicit triples, inferred 2 triples
```

## ❓ Si vous ne voyez toujours pas de logs

1. Vérifiez que le serveur démarre :
   ```bash
   ps aux | grep semantic_memory
   ```

2. Vérifiez les permissions :
   ```bash
   touch /tmp/smartmemory.log
   chmod 666 /tmp/smartmemory.log
   ```

3. Cherchez dans tous les fichiers récents :
   ```bash
   find /tmp -name "*smart*" -o -name "*semantic*" 2>/dev/null
   find ~/.gemini -name "*.log" -mtime -1 2>/dev/null
   ```
