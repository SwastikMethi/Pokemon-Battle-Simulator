from mcp.types import TextResourceContents
import json
from typing import List
from src.utils.data_loader import PokemonDataLoader
from src.logger_file import logger

async def get_pokemon_data(pokemon_name: str) -> dict:
    try:
        data_loader = PokemonDataLoader()
        pokemon = await data_loader.fetch_pokemon_data(pokemon_name)
        logger.info(f"{pokemon_name} data recieved.")

        return {
                "id": pokemon.id,
                "name": pokemon.name,
                "types": pokemon.types,
                "stats": {
                    "hp": pokemon.stats.hp,
                    "attack": pokemon.stats.attack,
                    "defense": pokemon.stats.defense,
                    "special_attack": pokemon.stats.special_attack,
                    "special_defense": pokemon.stats.special_defense,
                    "speed": pokemon.stats.speed,
                    "total": (pokemon.stats.hp + pokemon.stats.attack + 
                            pokemon.stats.defense + pokemon.stats.special_attack + 
                            pokemon.stats.special_defense + pokemon.stats.speed)
                },
                "abilities": pokemon.abilities,
                "moves": [{"name": move.name, "type": move.type, "power": move.power} for move in pokemon.moves],
                "physical_attributes":{"height": pokemon.height, "weight": pokemon.weight}
            }
    except Exception as e:
        logger.error(f"Error fetching Pokemon data for {pokemon_name}: {e}")
        return {"error": f"Could not fetch data for {pokemon_name}: {str(e)}"}

