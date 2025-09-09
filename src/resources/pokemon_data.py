from mcp.types import Resource, TextResourceContents
import json
from typing import List
from src.utils.data_loader import PokemonDataLoader
from src.logger_file import logger
import urllib.parse

# logger.info("in pokemon data file")
class PokemonDataResource:
    def __init__(self, data_loader: PokemonDataLoader):
        self.data_loader = data_loader

    def list_resources(self) -> List[Resource]:
        return [
            Resource(
                uri="pokemon://search",
                name="Pokemon Search",
                description="Search for available Pokemon. Returns list of Pokemon names you can query.",
                mimeType="application/json"
            ),
            Resource(
                uri="pokemon://pokemon/pikachu",
                name="Pokemon Data(pikachu)",
                description="Get comprehensive data for any Pokemon(pikachu) including stats, types, abilities, and moves",
                mimeType="application/json"
            ),
            Resource(
                uri="pokemon://type-chart",
                name="Type Effectiveness Chart",
                description="Get the complete Pokemon type effectiveness chart",
                mimeType="application/json"
            )
        ]

    async def get_pokemon_resource(self, uri: str) -> TextResourceContents:
        try:
            uri_str = str(uri)
            decoded_uri = urllib.parse.unquote(uri_str)

            # logger.info(f"Original URI: {uri_str}")
            # logger.info(f"Decoded URI: {decoded_uri}")

            if decoded_uri == "pokemon://search":
                logger.info("pokemon search")
            # Return list of searchable Pokemon
                pokemon_list = [
                    "pikachu", "charizard", "blastoise", "venusaur", "alakazam", 
                    "machamp", "gengar", "dragonite", "mewtwo", "mew"
                ]
                text = json.dumps({
                    "available_pokemon": pokemon_list,
                    "usage": "Use pokemon://pokemon/{name} to get specific Pokemon data",
                    "examples": [
                        "pokemon://pokemon/pikachu",
                        "pokemon://pokemon/charizard"
                    ]
                }, indent=2)

            elif decoded_uri.startswith("pokemon://pokemon/"):
                logger.info("non-dynamic pokemon details")
                # logger.info("in function 1")
                pokemon_name = decoded_uri.split("/")[-1].lower()
                pokemon = await self.data_loader.fetch_pokemon_data(pokemon_name)
                
                # Convert to JSON
                pokemon_dict = {
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
                    "moves": [{"name": move.name, "type": move.type, "power": move.power} 
                             for move in pokemon.moves],
                    "height": pokemon.height,
                    "weight": pokemon.weight
                }
                
                text = json.dumps(pokemon_dict, indent=2)
                # logger.info(f"content: {content}")
                
            elif decoded_uri == "pokemon://type-chart":
                logger.info("Effectiveness chart")
                # logger.info("in function 2")
                # Get type effectiveness chart
                type_chart = await self.data_loader.load_type_effectiveness()
                text = json.dumps(type_chart, indent=2)
                
            else:
                # logger.info("in function 3")
                text = json.dumps({"error": f"Invalid URI format {decoded_uri}"})
            # return TextResourceContents(
            #     uri=uri_str,
            #     mimeType="application/json",
            #     text=text
            # )
            return text
        
        except Exception as e:
            logger.error(f"error in get_poekomon resource:{e}",exc_info=True)
            uri_str = str(uri) if hasattr(uri, '__str__') else uri
            return [TextResourceContents(
                uri=uri_str,
                mimeType="application/json",
                text=json.dumps({"error": f"Failed to fetch resource: {str(e)}"})
            )]
