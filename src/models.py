from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class PokemonStats:
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

@dataclass
class Move:
    name: str
    power: int
    type: str
    accuracy: int
    pp: int

@dataclass
class Pokemon:
    id: int
    name: str
    types: List[str]
    stats: PokemonStats
    abilities: List[str]
    moves: List[Move]
    height: int = 0
    weight: int = 0

@dataclass
class BattleResult:
    winner: str
    loser: str
    battle_log: List[str]
    total_turns: int
    pokemon1_final_hp: int
    pokemon2_final_hp: int
