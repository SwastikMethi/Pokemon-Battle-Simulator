
from src.utils.data_loader import PokemonDataLoader
from src.utils.battle_mechanics import BattleSimulator
from typing import Dict, Any
from src.logger_file import logger

# Global instances
data_loader = PokemonDataLoader()
battle_sim = None

async def simulate_battle(pokemon1_name: str, pokemon2_name: str) -> Dict[str, Any]:
    """Simulate a battle between two Pokemon"""
    global battle_sim
    
    try:
        if battle_sim is None:
            type_effectiveness = await data_loader.load_type_effectiveness()
            battle_sim = BattleSimulator(type_effectiveness)
        
        pokemon1 = await data_loader.fetch_pokemon_data(pokemon1_name)
        pokemon2 = await data_loader.fetch_pokemon_data(pokemon2_name)
        
        result = await battle_sim.simulate_battle(pokemon1, pokemon2)
        
        return {
            "battle_result": {
                "winner": result.winner,
                "loser": result.loser,
                "total_turns": result.total_turns,
                "pokemon1_final_hp": result.pokemon1_final_hp,
                "pokemon2_final_hp": result.pokemon2_final_hp
            },
            "battle_log": result.battle_log,
            "participants": {
                "pokemon1": {
                    "name": pokemon1.name,
                    "types": pokemon1.types,
                    "total_stats": sum([
                        pokemon1.stats.hp, pokemon1.stats.attack, pokemon1.stats.defense,
                        pokemon1.stats.special_attack, pokemon1.stats.special_defense, pokemon1.stats.speed
                    ])
                },
                "pokemon2": {
                    "name": pokemon2.name,
                    "types": pokemon2.types,
                    "total_stats": sum([
                        pokemon2.stats.hp, pokemon2.stats.attack, pokemon2.stats.defense,
                        pokemon2.stats.special_attack, pokemon2.stats.special_defense, pokemon2.stats.speed
                    ])
                }
            }
        }
        
    except Exception as e:
        return {
            "error": f"Battle simulation failed: {str(e)}",
            "pokemon1": pokemon1_name,
            "pokemon2": pokemon2_name
        }
