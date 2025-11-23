"""CLI tool to list inference rules."""

import argparse
from src.services.inference_engine import InferenceEngine


def main():
    """List all inference rules configured in the system."""
    parser = argparse.ArgumentParser(
        description='List inference rules in the system.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed rule information including SPARQL queries'
    )
    
    args = parser.parse_args()
    
    # Initialize inference engine to get rules
    # Note: This creates a temporary instance just to inspect rules
    try:
        engine = InferenceEngine(rules=[], verification_service=None)
        rules = engine.rules
        
        if not rules:
            print("✓ No inference rules configured.")
            print("The system will not perform automatic inference.")
            return
        
        print(f"📋 Inference Rules ({len(rules)} total)\n")
        
        for i, rule in enumerate(rules, 1):
            print(f"[{i}] {rule.name}")
            
            if hasattr(rule, 'description') and rule.description:
                print(f"    Description: {rule.description}")
            
            if args.verbose:
                print(f"    Conditions:")
                for condition in rule.conditions:
                    print(f"      - {condition}")
                print(f"    Conclusion: {rule.conclusion}")
                
                if hasattr(rule, 'sparql_query') and rule.sparql_query:
                    print(f"    SPARQL Query:")
                    for line in rule.sparql_query.strip().split('\n'):
                        print(f"      {line}")
            
            print()
        
        if not args.verbose:
            print("💡 Use --verbose to see detailed rule information")
    
    except Exception as e:
        print(f"✗ Failed to load inference rules: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
