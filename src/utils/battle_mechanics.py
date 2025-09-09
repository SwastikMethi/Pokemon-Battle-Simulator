
import random
from typing import Dict, List, Tuple
from src.models import Pokemon, Move, BattleResult
from src.logger_file import logger

class TypeEffectiveness:
    def __init__(self):
        # Complete 18-type matchup chart for accurate Pokemon battles
        self.effectiveness_chart = {
            "normal":   {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
            "fire":     {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0, "rock": 0.5, "dragon": 0.5, "steel": 2.0},
            "water":    {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "rock": 2.0, "dragon": 0.5},
            "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0, "flying": 2.0, "dragon": 0.5},
            "grass":    {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5, "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0, "dragon": 0.5, "steel": 0.5},
            "ice":      {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "steel": 0.5},
            "fighting": {"normal": 2.0, "ice": 2.0, "rock": 2.0, "dark": 2.0, "steel": 2.0,
                         "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "fairy": 0.5, "ghost": 0.0},
            "poison":   {"grass": 2.0, "fairy": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0.0},
            "ground":   {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0, "rock": 2.0, "bug": 0.5, "flying": 0.0, "steel": 2.0},
            "flying":   {"grass": 2.0, "electric": 0.5, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "steel": 0.5},
            "psychic":  {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0, "steel": 0.5},
            "bug":      {"grass": 2.0, "psychic": 2.0, "dark": 2.0, "fire": 0.5, "fighting": 0.5, "flying": 0.5, "ghost": 0.5, "poison": 0.5, "steel": 0.5, "fairy": 0.5},
            "rock":     {"fire": 2.0, "ice": 2.0, "flying": 2.0, "bug": 2.0, "fighting": 0.5, "ground": 0.5, "steel": 0.5},
            "ghost":    {"psychic": 2.0, "ghost": 2.0, "dark": 0.5, "normal": 0.0},
            "dragon":   {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
            "dark":     {"psychic": 2.0, "ghost": 2.0, "fighting": 0.5, "dark": 0.5, "fairy": 0.5},
            "steel":    {"rock": 2.0, "ice": 2.0, "fairy": 2.0, "fire": 0.5, "water": 0.5, "electric": 0.5, "steel": 0.5},
            "fairy":    {"fighting": 2.0, "dragon": 2.0, "dark": 2.0, "fire": 0.5, "poison": 0.5, "steel": 0.5}
        }

    def get_effectiveness(self, attacking_type: str, defending_types: List[str]) -> float:
        multiplier = 1.0
        attacking_type = attacking_type.lower()
        
        for defending_type in defending_types:
            defending_type = defending_type.lower()
            type_multiplier = self.effectiveness_chart.get(attacking_type, {}).get(defending_type, 1.0)
            multiplier *= type_multiplier
            
        return multiplier

class DamageCalculator:
    @staticmethod
    def calculate_damage(attacker: Pokemon, defender: Pokemon, move: Move, effectiveness: float) -> int:
        """Calculate damage using official Pokemon damage formula"""
        level = 50  # Standard competitive battle level
        
        physical_types = ["normal", "fighting", "flying", "ground", "rock", "bug", "ghost", "poison", "steel"]
        
        if move.type.lower() in physical_types:
            attack_stat = attacker.stats.attack
            defense_stat = defender.stats.defense
        else:
            attack_stat = attacker.stats.special_attack
            defense_stat = defender.stats.special_defense

        base_damage = (((2 * level / 5 + 2) * move.power * attack_stat / defense_stat) / 50) + 2
        
        # Apply type effectiveness
        base_damage *= effectiveness
        
        # STAB (Same Type Attack Bonus) - 50% bonus for matching types
        if move.type.lower() in [t.lower() for t in attacker.types]:
            base_damage *= 1.5
            
        # Critical hit calculation (1/16 chance for 2x damage)
        critical = 2.0 if random.random() < (1/16) else 1.0
        base_damage *= critical
        
        # Random factor (85-100% of calculated damage)
        random_factor = random.uniform(0.85, 1.0)
        base_damage *= random_factor
        
        return max(1, int(base_damage))

class StatusEffectManager:
    """Handles the three required status effects: Burn, Paralysis, and Poison"""
    def __init__(self):
        self.turn_counter = 0
        self.first_attacker_immunity = True
    
    def apply_burn(self, pokemon_data: dict) -> str:
        """Apply burn status - reduces attack and causes end-of-turn damage"""
        if not pokemon_data.get("_burned_applied"):
            # Halve physical attack stat
            pokemon_data["stats"]["attack"] = max(1, pokemon_data["stats"]["attack"] // 2)
            pokemon_data["_burned_applied"] = True
        
        # End-of-turn burn damage (1/16 of max HP)
        burn_damage = max(1, pokemon_data["max_hp"] // 16)
        pokemon_data["current_hp"] = max(0, pokemon_data["current_hp"] - burn_damage)
        return f"{pokemon_data['name']} is hurt by its burn! (-{burn_damage} HP)"

    def apply_paralysis(self, pokemon_data: dict, is_first_attacker: bool = False) -> str:
        """Apply paralysis - reduces speed and 25% chance to skip turn"""
        if self.turn_counter == 0 and is_first_attacker and self.first_attacker_immunity:
            self.first_attacker_immunity = False  # Use immunity once
            return None
        if not pokemon_data.get("_paralyzed_applied"):
            # Quarter the speed stat
            pokemon_data["stats"]["speed"] = max(1, pokemon_data["stats"]["speed"] // 4)
            pokemon_data["_paralyzed_applied"] = True
        
        # 25% chance to be fully paralyzed
        if random.random() < 0.25:
            return f"{pokemon_data['name']} is fully paralyzed and can't move!"
        return None
    
    def next_turn(self):
        """Advance to next turn"""
        self.turn_counter += 1

    def apply_poison(self, pokemon_data: dict) -> str:
        # Poison damage (1/8 of max HP)
        poison_damage = max(1, pokemon_data["max_hp"] // 8)
        pokemon_data["current_hp"] = max(0, pokemon_data["current_hp"] - poison_damage)
        return f"{pokemon_data['name']} is hurt by poison! (-{poison_damage} HP)"

class BattleSimulator:
    def __init__(self, type_effectiveness: Dict[str, Dict[str, float]] = None):
        self.type_chart = TypeEffectiveness()
        self.damage_calc = DamageCalculator()
        self.status_manager = StatusEffectManager()

    def determine_turn_order(self, pokemon1: Pokemon, pokemon2: Pokemon) -> Tuple[Pokemon, Pokemon]:
        """Determine who goes first based on speed stats"""
        if pokemon1.stats.speed > pokemon2.stats.speed:
            return pokemon1, pokemon2
        elif pokemon2.stats.speed > pokemon1.stats.speed:
            return pokemon2, pokemon1
        else:
            # Speed tie - random determination
            return (pokemon1, pokemon2) if random.random() < 0.5 else (pokemon2, pokemon1)

    def _convert_to_battle_format(self, pokemon: Pokemon) -> dict:
        """Convert Pokemon object to battle-ready dictionary format"""
        return {
            "name": pokemon.name,
            "types": pokemon.types,
            "stats": {
                "hp": pokemon.stats.hp,
                "attack": pokemon.stats.attack,
                "defense": pokemon.stats.defense,
                "special_attack": pokemon.stats.special_attack,
                "special_defense": pokemon.stats.special_defense,
                "speed": pokemon.stats.speed
            },
            "moves": [{"name": move.name, "type": move.type, "power": move.power} for move in pokemon.moves],
            "current_hp": pokemon.stats.hp,
            "max_hp": pokemon.stats.hp,
            "status_effects": []
        }

    async def simulate_battle(self, pokemon1: Pokemon, pokemon2: Pokemon) -> BattleResult:
        """Simulate a complete Pokemon battle with detailed mechanics"""
        # Convert to battle format
        p1_data = self._convert_to_battle_format(pokemon1)
        p2_data = self._convert_to_battle_format(pokemon2)
        
        battle_log = []
        turn = 1
        max_turns = 100

        # Battle introduction
        battle_log.append(f"🔥 POKEMON BATTLE BEGINS! 🔥")
        battle_log.append(f"{pokemon1.name} vs {pokemon2.name}")
        battle_log.append(f"{pokemon1.name}: {p1_data['current_hp']} HP | Types: {', '.join(pokemon1.types)}")
        battle_log.append(f"{pokemon2.name}: {p2_data['current_hp']} HP | Types: {', '.join(pokemon2.types)}")
        battle_log.append("")

        # Main battle loop
        while p1_data["current_hp"] > 0 and p2_data["current_hp"] > 0 and turn <= max_turns:
            battle_log.append(f"--- TURN {turn} ---")
            
            # Determine turn order based on speed
            first, second = self.determine_turn_order(pokemon1, pokemon2)
            first_data = p1_data if first == pokemon1 else p2_data
            second_data = p2_data if first == pokemon1 else p1_data
            
            # First Pokemon's turn
            if first_data["current_hp"] > 0:
                # Check for paralysis
                is_first_attacker = (turn == 1)
                paralysis_msg = self.status_manager.apply_paralysis(first_data, is_first_attacker)
                if paralysis_msg and "can't move" in paralysis_msg:
                    battle_log.append(paralysis_msg)
                else:
                    if paralysis_msg:
                        battle_log.append(f"{first_data['name']} is paralyzed but manages to attack!")
                    
                    # Execute attack
                    second_data, attack_log = self._execute_attack(first_data, second_data, first, second)
                    battle_log.extend(attack_log)
            
            # Second Pokemon's turn (if still alive)
            if second_data["current_hp"] > 0:
                # Check for paralysis
                paralysis_msg = self.status_manager.apply_paralysis(second_data)
                if paralysis_msg and "can't move" in paralysis_msg:
                    battle_log.append(paralysis_msg)
                else:
                    if paralysis_msg:
                        battle_log.append(f"{second_data['name']} is paralyzed but manages to attack!")
                    
                    # Execute attack
                    first_data, attack_log = self._execute_attack(second_data, first_data, second, first)
                    battle_log.extend(attack_log)

            # Apply end-of-turn status effects
            status_messages = []
            
            # Apply burn damage
            if "burn" in p1_data.get("status_effects", []):
                burn_msg = self.status_manager.apply_burn(p1_data)
                status_messages.append(burn_msg)
            
            if "burn" in p2_data.get("status_effects", []):
                burn_msg = self.status_manager.apply_burn(p2_data)
                status_messages.append(burn_msg)
            
            # Apply poison damage
            if "poison" in p1_data.get("status_effects", []):
                poison_msg = self.status_manager.apply_poison(p1_data)
                status_messages.append(poison_msg)
                
            if "poison" in p2_data.get("status_effects", []):
                poison_msg = self.status_manager.apply_poison(p2_data)
                status_messages.append(poison_msg)
            
            battle_log.extend(status_messages)
            
            # Turn summary
            battle_log.append(f"{pokemon1.name}: {p1_data['current_hp']}/{p1_data['max_hp']} HP")
            battle_log.append(f"{pokemon2.name}: {p2_data['current_hp']}/{p2_data['max_hp']} HP")
            battle_log.append("")
            
            self.status_manager.next_turn()
            turn += 1

        # Determine battle outcome
        if p1_data["current_hp"] <= 0:
            winner, loser = pokemon2.name, pokemon1.name
            battle_log.append(f"💀 {pokemon1.name} fainted!")
            battle_log.append(f"🏆 {pokemon2.name} wins the battle!")
        elif p2_data["current_hp"] <= 0:
            winner, loser = pokemon1.name, pokemon2.name
            battle_log.append(f"💀 {pokemon2.name} fainted!")
            battle_log.append(f"🏆 {pokemon1.name} wins the battle!")
        else:
            # Battle ended due to turn limit
            if p1_data["current_hp"] > p2_data["current_hp"]:
                winner, loser = pokemon1.name, pokemon2.name
            else:
                winner, loser = pokemon2.name, pokemon1.name
            battle_log.append(f"⏰ Battle ended after {turn-1} turns!")
            battle_log.append(f"🏆 {winner} wins by remaining HP!")

        return BattleResult(
            winner=winner,
            loser=loser,
            battle_log=battle_log,
            total_turns=turn-1,
            pokemon1_final_hp=max(0, p1_data["current_hp"]),
            pokemon2_final_hp=max(0, p2_data["current_hp"])
        )

    def _execute_attack(self, attacker_data: dict, defender_data: dict, 
                       attacker: Pokemon, defender: Pokemon) -> Tuple[dict, List[str]]:
        """Execute a single attack with detailed logging"""
        if not attacker_data.get('moves') or not attacker.moves:
            return defender_data, [f"{attacker_data['name']} has no moves to use!"]
            
        # Choose a random move
        move = random.choice(attacker.moves)
        move_dict = {"name": move.name, "type": move.type, "power": move.power}
        
        log = [f"{attacker_data['name']} uses {move.name}!"]
        
        # Calculate type effectiveness
        effectiveness = self.type_chart.get_effectiveness(move.type, defender.types)
        
        # Calculate damage
        damage = self.damage_calc.calculate_damage(attacker, defender, move, effectiveness)
        
        # Apply damage
        defender_data["current_hp"] = max(0, defender_data["current_hp"] - damage)
        
        # Add effectiveness messages
        if effectiveness > 1.5:
            log.append("It's super effective!")
        elif effectiveness < 0.75:
            log.append("It's not very effective...")
        elif effectiveness == 0.0:
            log.append("It doesn't affect the opponent!")
            damage = 0
            
        if damage > 0:
            log.append(f"⚡ {defender_data['name']} takes {damage} damage!")
            
            # Random chance to inflict status effects (10% each)
            if random.random() < 0.1:
                status_effect = random.choice(["burn", "poison", "paralysis"])
                if status_effect not in defender_data.get("status_effects", []):
                    defender_data.setdefault("status_effects", []).append(status_effect)
                    log.append(f"🔥 {defender_data['name']} is now {status_effect}ed!")
        
        return defender_data, log
