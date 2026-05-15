#!/bin/bash
# Validation des modifications SmartMemory
cd /home/momo/Antigravity/SmartMemory
source venv/bin/activate

echo "=== Vérification syntaxe Python ==="
python3 -m py_compile src/smart_memory/tools/add_memory.py && echo "✅ add_memory.py"
python3 -m py_compile src/smart_memory/tools/forget_memory.py && echo "✅ forget_memory.py"
python3 -m py_compile src/smart_memory/knowledge/graph.py && echo "✅ graph.py"
python3 -m py_compile src/smart_memory/knowledge/conflicts.py && echo "✅ conflicts.py"
python3 -m py_compile src/smart_memory/server.py && echo "✅ server.py"

echo ""
echo "=== Tests unitaires ==="
python -m pytest tests/unit/ -x -q --tb=short

echo ""
echo "=== Tests intégration (sans réseau) ==="
python -m pytest tests/integration/ -x -q --tb=short -k "not ontology"
