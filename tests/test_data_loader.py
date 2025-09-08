from src.utils.data_loader import PokemonDataLoader

def test_pokemon_loading():
    loader = PokemonDataLoader()
    
    # Test with a popular Pokemon
    pikachu = loader.fetch_pokemon_data("pikachu")
    print(f"Loaded: {pikachu.name}")
    print(f"Types: {pikachu.types}")
    print(f"HP: {pikachu.stats.hp}")
    
    # Test type effectiveness
    type_chart = loader.load_type_effectiveness()
    print(f"Fire type damage relations: {type_chart.get('fire', {})}")

if __name__ == "__main__":
    test_pokemon_loading()