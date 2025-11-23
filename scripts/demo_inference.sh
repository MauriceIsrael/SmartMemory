#!/usr/bin/env bash
# Demo script to test the inference and verification workflow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🧪 SmartMemory Inference Demo"
echo "=============================="
echo ""

# Step 1: Show current state
echo "📊 Step 1: Current Knowledge Graph State"
echo "----------------------------------------"
PYTHONPATH=. venv/bin/python src/cli/list_facts.py
echo ""

# Step 2: Show configured rules
echo "📋 Step 2: Configured Inference Rules"
echo "-------------------------------------"
PYTHONPATH=. venv/bin/python src/cli/list_rules.py
echo ""

# Step 3: Add a fact
echo "➕ Step 3: Adding a new fact"
echo "----------------------------"
echo "Adding: :Alice :knows :Bob"
PYTHONPATH=. venv/bin/python src/cli/add_fact.py ":Alice" ":knows" ":Bob"
echo ""

# Step 4: Check for pending verifications
echo "🔍 Step 4: Checking for Pending Verifications"
echo "---------------------------------------------"
PYTHONPATH=. venv/bin/python src/cli/get_pending_verifications.py
echo ""

# Step 5: Show updated graph
echo "📊 Step 5: Updated Knowledge Graph"
echo "----------------------------------"
PYTHONPATH=. venv/bin/python src/cli/list_facts.py --count 10
echo ""

echo "✅ Demo complete!"
echo ""
echo "💡 Tips:"
echo "  - Check server logs to see inference engine output"
echo "  - Add inference rules in src/server.py to see automatic deduction"
echo "  - Use 'tail -f server.log' to monitor real-time inference"
