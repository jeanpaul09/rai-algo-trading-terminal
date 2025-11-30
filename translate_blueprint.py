#!/usr/bin/env python3
"""
Command-line tool to translate Strategy Blueprint JSON to Python strategy code.

Usage:
    python translate_blueprint.py <blueprint.json> <output.py>

Example:
    python translate_blueprint.py blueprints/example_ma_cross_blueprint.json strategies/ma_cross.py
"""

import sys
from pathlib import Path
from rai_algo.blueprint_translator import translate_blueprint


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python translate_blueprint.py <blueprint.json> <output.py>")
        print("\nExample:")
        print("  python translate_blueprint.py blueprints/example_ma_cross_blueprint.json strategies/ma_cross.py")
        sys.exit(1)
    
    blueprint_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not Path(blueprint_path).exists():
        print(f"Error: Blueprint file not found: {blueprint_path}")
        sys.exit(1)
    
    try:
        translate_blueprint(blueprint_path, output_path)
        print(f"\n✅ Successfully translated blueprint to: {output_path}")
        print("\nNext steps:")
        print(f"  1. Review the generated code in {output_path}")
        print("  2. Implement any TODO sections")
        print("  3. Test with backtest_example.py")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


