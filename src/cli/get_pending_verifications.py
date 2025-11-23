import argparse
from src.services.verification_service import VerificationService

def main():
    try:
        parser = argparse.ArgumentParser(description='Get pending verifications.')
        args = parser.parse_args()

        verification_service = VerificationService()
        pending_verifications = verification_service.get_pending()

        if not pending_verifications:
            print("✓ No pending verifications.")
            print("The knowledge graph has no inferred facts awaiting user confirmation.")
        else:
            print(f"Found {len(pending_verifications)} pending verification(s):\n")
            for i, verification in enumerate(pending_verifications, 1):
                print(f"[{i}] {verification.json()}")
                print()
    except Exception as e:
        import logging
        logging.error(f"Failed to get pending verifications: {e}")
        import sys
        sys.exit(1)

if __name__ == '__main__':
    main()
