import sys
import os
import asyncio

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.server import main

if __name__ == "__main__":
    print("Starting Pokemon MCP Server...")
    asyncio.run(main())
