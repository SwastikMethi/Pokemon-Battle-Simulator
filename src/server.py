import asyncio
import sys
import os
import logging

from typing import Dict
import asyncio
import sys
import os
# from src.logger_file import logger
import json

logging.basicConfig(
    filename='mcp_server.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Fix import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextResourceContents

from src.utils.data_loader import PokemonDataLoader
from src.resources.pokemon_data import PokemonDataResource
from src.tools import battle_simulator

# Initialize MCP server
app = Server("pokemon-battle-server")

# Set up data loader and resources
data_loader = PokemonDataLoader()
pokemon_resource = PokemonDataResource(data_loader)

@app.list_resources()
async def list_resources() -> list[Resource]:
    return pokemon_resource.list_resources()

@app.read_resource()
async def read_resource(uri: str) -> list[TextResourceContents]:
    try:
        """Read Pokemon data resource"""
        result = await pokemon_resource.get_pokemon_resource(uri)
        return result
    
    except Exception as e:
        return TextResourceContents(
            uri=uri,
            mimeType="text/plain",
            text=f"Error: {e}"
        )

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="battle_simulate",
            description="Simulate a Pokemon battle between two Pokemons. Returns detailed battle log and winner.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pokemon1": {
                        "type": "string",
                        "description": "Name of the first Pokemon (e.g., 'pikachu')"
                    },
                    "pokemon2": {
                        "type": "string", 
                        "description": "Name of the second Pokemon (e.g., 'charizard')"
                    }
                },
                "required": ["pokemon1", "pokemon2"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict):
    """Execute tool calls"""
    try:
        # logger.info(f"DEBUG: Calling tool {name} with arguments: {arguments}")

        if name == "battle_simulate":
            result =  await battle_simulator.simulate_battle(
                arguments["pokemon1"],
                arguments["pokemon2"]
            )
            # logger.info(f"DEBUG: Battle result type: {type(result)}")

            if not isinstance(result, dict):
                # logger.warning(f"Unexpected result type: {type(result)}")
                return {"error": f"Unexpected result type: {type(result)}"}
            return result
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        # logger.error(f"Error in call_tool: {e}", exc_info=True)
        return {"error": f"Tool execution failed: {str(e)}"}

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

