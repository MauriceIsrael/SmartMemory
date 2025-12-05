#!/usr/bin/env python3
"""
CLI tool to list custom inference rules added by the LLM.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from smart_memory.inference.rule_engine import load_rules
from smart_memory.config import config


def main():
    """List all custom inference rules."""
    print("📋 Custom Inference Rules\n")
    print("=" * 80)
    
    # Load all rules
    rules = load_rules([config.default_rules_dir, config.user_rules_dir])
    
    # Filter custom rules
    custom_rules = [r for r in rules if r.source == "custom"]
    
    if not custom_rules:
        print("\n✓ No custom rules found.")
        print(f"\nCustom rules are stored in: {config.user_rules_dir}")
        return
    
    print(f"\nFound {len(custom_rules)} custom rule(s):\n")
    
    for i, rule in enumerate(custom_rules, 1):
        print(f"\n{i}. {rule.id}")
        print(f"   File: {rule.file_path}")
        print(f"   Status: {'✓ Active' if rule.is_active else '✗ Inactive'}")
        
        if rule.description:
            print(f"   Description: {rule.description}")
        
        if not rule.is_active and rule.validation_error:
            print(f"   ⚠ Error: {rule.validation_error}")
        
        print(f"   Executed: {rule.execution_count} times")
        print(f"   Inferred: {rule.triples_generated} triples")
    
    print("\n" + "=" * 80)
    print(f"\nTotal: {len(custom_rules)} custom rules")
    print(f"Active: {sum(1 for r in custom_rules if r.is_active)}")
    print(f"Inactive: {sum(1 for r in custom_rules if not r.is_active)}")


if __name__ == "__main__":
    main()
