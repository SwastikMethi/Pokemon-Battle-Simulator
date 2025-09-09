import requests
import httpx
import pandas as pd
import json
import os
from typing import Dict, List
from src.models import Pokemon, PokemonStats, Move
from src.logger_file import logger

class PokemonDataLoader:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2/"
        self.cache_dir = "data/cache/"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.client = httpx.AsyncClient(timeout=30.0)

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.json")

    async def _get(self, endpoint: str, cache_key: str) -> dict:
        cachefile = self._cache_path(cache_key)
        if os.path.exists(cachefile):
            try:
                with open(cachefile, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading {cachefile}: {e}")

        url = self.base_url + endpoint
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            if response.status_code == 200:
                data = response.json()
                with open(cachefile, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            return data
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return {}

    async def fetch_pokemon_data(self, pokemon_identifier: str) -> Pokemon:
        # Implement API calls with caching
        pokemon_identifier = pokemon_identifier.lower().strip()
        data = await self._get(f"pokemon/{pokemon_identifier}", f"pokemon_{pokemon_identifier}")
        if not data:
            raise ValueError(f"Pokemon '{pokemon_identifier}' not found")

        stats_data = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        stats = PokemonStats(
            hp=stats_data.get("hp", 0),
            attack=stats_data.get("attack", 0),
            defense=stats_data.get("defense", 0),
            special_attack=stats_data.get("special-attack", 0),
            special_defense=stats_data.get("special-defense", 0),
            speed=stats_data.get("speed", 0)
        )
        moves = []
        for move_data in data["moves"][:4]:
            move_name = move_data["move"]["name"]
            move_details = await self._get(f"move/{move_name}", f"move_{move_name}")
            
            if move_details:
                moves.append(Move(
                    name=move_details["name"],
                    power=move_details.get("power") or 50,
                    type=move_details["type"]["name"],
                    accuracy=move_details.get("accuracy") or 80,
                    pp=move_details.get("pp") or 10
                ))
        pokemon = Pokemon(
            id=data["id"],
            name=data["name"],
            types=[t["type"]["name"] for t in data["types"]],
            stats=stats,
            abilities=[a["ability"]["name"] for a in data["abilities"]],
            moves=moves,
            height=data.get("height", 0),
            weight=data.get("weight", 0)
        )
        
        return pokemon

    async def load_type_effectiveness(self)-> Dict[str, Dict[str, float]]:
        # Load type chart data
        type_effectiveness = {}
        types_data = await self._get("type", "all_types")
        for t in types_data["results"]:
            type_name = t["name"]
            type_data = await self._get(f"type/{type_name}", f"type_{type_name}")

            damage_relations = type_data["damage_relations"]
            type_effectiveness[type_name] = {
                "no_damage_to": [x["name"] for x in damage_relations["no_damage_to"]],
                "half_damage_to": [x["name"] for x in damage_relations["half_damage_to"]],
                "double_damage_to": [x["name"] for x in damage_relations["double_damage_to"]],
                "no_damage_from": [x["name"] for x in damage_relations["no_damage_from"]],
                "half_damage_from": [x["name"] for x in damage_relations["half_damage_from"]],
                "double_damage_from": [x["name"] for x in damage_relations["double_damage_from"]],
            }

        return type_effectiveness
    
    async def close(self):
    # """Clean up HTTP client"""
        if hasattr(self, 'client'):
            await self.client.aclose()