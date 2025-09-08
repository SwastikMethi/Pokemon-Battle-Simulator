import sys
import os

# Add the parent directory (project root) to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


import asyncio
from src.utils.data_loader import PokemonDataLoader
from src.tools.battle_simulator import simulate_battle


async def test_basic_functionality():
    """Test basic server functionality"""
    print("Testing Pokemon data loading...")
    
    loader = PokemonDataLoader()
    try:
        # Test data loading
        pikachu = await loader.fetch_pokemon_data("pikachu")
        print(f"✓ Loaded {pikachu.name}: HP={pikachu.stats.hp}, Types={pikachu.types}")
        
        charizard = await loader.fetch_pokemon_data("charizard")
        print(f"✓ Loaded {charizard.name}: HP={charizard.stats.hp}, Types={charizard.types}")
        
        # Test battle simulation
        print("\nTesting battle simulation...")
        result = await simulate_battle("pikachu", "charizard")
        
        if "error" in result:
            print(f"✗ Battle failed: {result['']}")
        else:
            print(f"✓ Battle completed: {result['battle_result']['winner']} wins!")
            print(f"  Battle lasted {result['battle_result']['total_turns']} turns")
            print(f"  Final HPs - {pikachu.name}: {result['battle_result']['pokemon1_final_hp']}, {charizard.name}: {result['battle_result']['pokemon2_final_hp']}")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
    finally:
        await loader.close()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
