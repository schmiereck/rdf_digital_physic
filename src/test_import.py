import sys
try:
    print("Attempting to import from automata_lib.ca...")
    from automata_lib import ca
    print("Import successful.")
    sys.exit(0)
except ImportError as e:
    print(f"ImportError: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}", file=sys.stderr)
    sys.exit(1)
