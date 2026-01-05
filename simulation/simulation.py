import random
import argparse
import time

class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type

    def __repr__(self):
        return f"Card(name='{self.name}', type='{self.card_type}')"

class Deck:
    def __init__(self, num_players=4, silent=False):
        self.cards = []
        self.discard_pile = []
        self.reshuffles = 0
        self.build_deck(num_players, silent)

    def build_deck(self, num_players=4, silent=False):
        deck_composition = [
            # 1. Specialty Chicken Cards
            {"name": "Dino Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Flying Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Mad Scientist Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Robo-Hen", "type": "Specialty Chicken", "count": 1},
            {"name": "Decoy Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Punk Rock Chick", "type": "Specialty Chicken", "count": 1},
            # 2. Protection Cards
            {"name": "Immunity", "type": "Protection", "count": 3},
            {"name": "Chicken Wire", "type": "Protection", "count": 2},
            {"name": "Cock Block", "type": "Protection", "count": 3},
            # 3. Attack Cards
            {"name": "Coyote Attack", "type": "Attack", "count": 2},
            {"name": "Chicken Blaster", "type": "Attack", "count": 3},
            {"name": "Die-Die-Die!", "type": "Attack", "count": 2},
            {"name": "Hen Swap", "type": "Attack", "count": 2},
            {"name": "3-Egg Omelette", "type": "Attack", "count": 2},
            {"name": "Infertility", "type": "Attack", "count": 1},
            {"name": "Eat Mor Chikin", "type": "Attack", "count": 2},
            # 4. Instant Effect Cards
            {"name": "Chicken Bomb", "type": "Instant Effect", "count": 3},
            {"name": "Demotion", "type": "Instant Effect", "count": 1},
            {"name": "Foster Farms", "type": "Instant Effect", "count": 1},
            {"name": "Bird Flu", "type": "Instant Effect", "count": 1},
            {"name": "Fox on the Loose", "type": "Instant Effect", "count": 1},
            {"name": "Chicken Assassin", "type": "Instant Effect", "count": 1},
            # 5. Personal Growth Cards
            {"name": "Feeding Frenzy", "type": "Personal Growth", "count": 1},
            {"name": "Incubator", "type": "Personal Growth", "count": 1},
            {"name": "Farm to Table", "type": "Personal Growth", "count": 1},
            {"name": "Resurrection", "type": "Personal Growth", "count": 1},
            # 6. Turn Altering Cards
            {"name": "Take it or Leave it", "type": "Turn Altering", "count": 2},
            {"name": "End Your Turn", "type": "Turn Altering", "count": 2},
            {"name": "Reverse", "type": "Turn Altering", "count": 1},
        ]

        base_players = 2 # The deck is balanced for 2 players initially

        for card_info in deck_composition:
            # Don't scale specialty chickens
            if card_info["type"] == "Specialty Chicken":
                count = card_info["count"]
            else:
                scaling_factor = num_players / base_players
                # Scale attack cards more aggressively to encourage player elimination
                if card_info["type"] == "Attack":
                    scaling_factor *= 2.0
                
                count = max(1, round(card_info["count"] * scaling_factor))

            for _ in range(count):
                self.cards.append(Card(card_info["name"], card_info["type"]))
        
        if not silent:
            print(f"Deck built with {len(self.cards)} cards.")

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            if not self.discard_pile:
                return None # No cards left anywhere
            # Reshuffle discard pile into the deck
            self.cards = self.discard_pile
            self.discard_pile = []
            self.shuffle()
            self.reshuffles += 1
        return self.cards.pop()

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        # flock includes: Chicks, Hens, and Specialty Chickens
        self.flock = {
            "Chicks": 0,
            "Hens": 0,
            "Dino Chickens": 0,
            "Flying Chickens": 0,
            "Mad Scientist Chickens": 0,
            "Robo-Hens": 0,
            "Decoy Chickens": 0,
            "Punk Rock Chicks": 0
        }
        self.egg_cards = 0 # Egg cards are kept in hand according to rules
        self.infertile_hens = 0

    def __repr__(self):
        flock_items = [f"{k.lower()}={v}" for k, v in self.flock.items() if v > 0]
        flock_str = ", ".join(flock_items) if flock_items else "empty"
        return f"Player(name='{self.name}', hand_size={len(self.hand)}, flock=({flock_str}), eggs={self.egg_cards})"

    def total_chickens(self):
        return sum(self.flock.values())

class Game:
    def __init__(self, num_players=4, silent_deck=False):
        self.players = [Player(f"Player {i+1}") for i in range(num_players)]
        self.deck = Deck(num_players=num_players, silent=silent_deck)
        self.deck.shuffle()
        self.current_player_index = 0
        self.game_over = False
        self.turn = 0

        # Game state flags
        self.drought_active = False # Legacy, might be replaced by Infertility or other cards
        self.drought_player_index = -1
        self.reverse_direction = False
        self.skip_roll = False

        self._initialize_card_dispatcher()

        # Game resources
        self.chick_supply = 50 # Increased supply for simulation
        self.hen_supply = 50
        self.egg_supply = 100
        self.graveyard = []
        self.total_cards_played = 0

        # Deal starting hands and chickens
        for player in self.players:
            # Each player starts with 2 Chicks and 1 Hen
            player.flock["Chicks"] = 2
            player.flock["Hens"] = 1
            self.chick_supply -= 2
            self.hen_supply -= 1

            # 1 Egg Card in hand
            player.egg_cards = 1
            self.egg_supply -= 1

            # Deal 5 action cards
            for _ in range(5):
                card = self.deck.draw()
                if card:
                    player.hand.append(card)

    def run_simulation(self, silent=False):
        if not silent:
            print("--- Starting Chicken Die! Simulation ---")
        
        start_time = time.time()
        
        while not self.game_over:
            self.turn += 1
            if self.turn > 1000: # Safety break
                end_time = time.time()
                return {
                    "winner": "None", 
                    "turns": self.turn, 
                    "reason": "Exceeded max turns", 
                    "reshuffles": self.deck.reshuffles,
                    "cards_played": self.total_cards_played,
                    "duration": end_time - start_time
                }

            if not silent:
                print(f"\n--- Turn {self.turn} ---")
                print(f"Supply: {self.chick_supply} Chicks, {self.hen_supply} Hens | Graveyard: {len(self.graveyard)}")
                for p in self.players:
                    print(f"  {p}")

            current_player = self.players[self.current_player_index]
            self.take_turn(current_player, silent)
            
            active_players = [p for p in self.players if p.total_chickens() > 0]
            if len(active_players) <= 1:
                self.game_over = True
                end_time = time.time()
                winner = active_players[0] if active_players else None
                if not silent:
                    print(f"\n--- Game Over! ---")
                    if winner:
                        print(f"Winner is {winner.name} after {self.turn} turns!")
                    else:
                        print("All players lost their chickens simultaneously!")
                return {
                    "winner": winner.name if winner else "None", 
                    "turns": self.turn, 
                    "reshuffles": self.deck.reshuffles,
                    "cards_played": self.total_cards_played,
                    "duration": end_time - start_time
                }

            if self.reverse_direction:
                self.current_player_index = (self.current_player_index - 1 + len(self.players)) % len(self.players)
            else:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return None

    def take_turn(self, player, silent=False):
        if not silent:
            print(f"It's {player.name}'s turn.")

        # Step 1: Collect Eggs
        # Hens (1), Robo-Hens (2), Punk Rock Chicks (1)
        player.infertile_hens = min(player.infertile_hens, player.flock["Hens"])
        hens = player.flock["Hens"] - player.infertile_hens
        robo_hens = player.flock["Robo-Hens"]
        punk_rock_chicks = player.flock["Punk Rock Chicks"]
        collected_eggs = max(0, hens) + (robo_hens * 2) + punk_rock_chicks
        
        # Draw from supply
        actual_collected = min(collected_eggs, self.egg_supply)
        player.egg_cards += actual_collected
        self.egg_supply -= actual_collected
        
        if not silent and actual_collected > 0:
            print(f"{player.name} collects {actual_collected} egg cards, now has {player.egg_cards}.")

        # Step 2: Draw a Card
        drawn_card = self.deck.draw()
        if drawn_card:
            if drawn_card.card_type == "Instant Effect":
                if not silent: print(f"{player.name} drew an Instant Effect: {drawn_card.name}!")
                self.play_card(player, drawn_card, silent)
            else:
                player.hand.append(drawn_card)
                if not silent: print(f"{player.name} draws a card.")

        # AI Logic for playing cards and spending eggs
        self.perform_ai_actions(player, silent)

        # Step 5: Roll the "Chicken Die!"
        if not self.skip_roll:
            self.roll_chicken_die(player, silent)
        else:
            # Reset for the next player
            self.skip_roll = False

    def get_opponents(self, current_player):
        return [p for p in self.players if p is not current_player and p.total_chickens() > 0]

    def perform_ai_actions(self, player, silent=False):
        """
        AI logic for playing cards and spending eggs based on situational awareness.
        """
        # Determine AI mode
        mode = self._get_ai_mode(player)

        # --- AI: Play Cards ---
        self._ai_play_cards(player, mode, silent)

        # --- AI: Spend Eggs ---
        self._ai_spend_eggs(player, mode, silent)

    def _get_ai_mode(self, player):
        """Determines the AI's current mode (Growth, Aggressive, Defensive)."""
        total_chickens = player.total_chickens()
        if total_chickens <= 2:
            return "Growth"
        
        average_chickens = sum(p.total_chickens() for p in self.players) / len(self.players)
        if total_chickens > average_chickens:
            return "Aggressive"
            
        return "Defensive"

    def _ai_play_cards(self, player, mode, silent):
        """AI logic for playing cards based on the current mode."""
        card_to_play = None
        
        if mode == "Growth":
            card_to_play = next((c for c in player.hand if c.card_type == "Personal Growth"), None)
        elif mode == "Aggressive":
            card_to_play = next((c for c in player.hand if c.card_type == "Attack"), None)
        elif mode == "Defensive":
            # In defensive mode, the AI is more conservative and might hold cards.
            # For now, we'll keep it simple and play a growth card if available.
            card_to_play = next((c for c in player.hand if c.card_type == "Personal Growth"), None)

        if card_to_play:
            self.play_card(player, card_to_play, silent)

    def _ai_spend_eggs(self, player, mode, silent):
        """AI logic for spending eggs based on the current mode."""
        # Step 4: Cash in Eggs
        # Rule: Spend 3 Eggs -> Draw 1 card
        # Rule: Spend 6 Eggs -> Take 1 Chick Card
        
        while player.egg_cards >= 3:
            if player.egg_cards >= 6 and self.chick_supply > 0 and mode in ["Growth", "Defensive"]:
                player.egg_cards -= 6
                self.egg_supply += 6
                player.flock["Chicks"] += 1
                self.chick_supply -= 1
                if not silent:
                    print(f"{player.name} spends 6 eggs to get a new Chick from the supply.")
            else:
                player.egg_cards -= 3
                self.egg_supply += 3
                drawn_card = self.deck.draw()
                if drawn_card:
                    if drawn_card.card_type == "Instant Effect":
                        if not silent: print(f"{player.name} drew an Instant Effect while cashing in eggs: {drawn_card.name}!")
                        self.play_card(player, drawn_card, silent)
                    else:
                        player.hand.append(drawn_card)
                        if not silent: print(f"{player.name} spends 3 eggs to draw a card.")
                else:
                    break

    def play_card(self, player, card, silent=False):
        if card in player.hand:
            player.hand.remove(card)
        
        self.total_cards_played += 1
        
        SPECIALTY_CHICKENS = {
            "Dino Chicken": "Dino Chickens",
            "Flying Chicken": "Flying Chickens",
            "Mad Scientist Chicken": "Mad Scientist Chickens",
            "Robo-Hen": "Robo-Hens",
            "Decoy Chicken": "Decoy Chickens",
            "Punk Rock Chick": "Punk Rock Chicks"
        }

        if card.name in SPECIALTY_CHICKENS:
            player.flock[SPECIALTY_CHICKENS[card.name]] += 1
        else:
            self.deck.discard_pile.append(card)

        if not silent:
            print(f"{player.name} plays {card.name}.")

        # --- Card Effects ---
        card_function = self.card_dispatcher.get(card.name)
        if card_function:
            card_function(player, silent)

    def _initialize_card_dispatcher(self):
        self.card_dispatcher = {
            "Coyote Attack": self._play_coyote_attack,
            "Chicken Blaster": self._play_chicken_blaster,
            "Eat Mor Chikin": self._play_eat_mor_chikin,
            "Farm to Table": self._play_farm_to_table,
            "Feeding Frenzy": self._play_feeding_frenzy,
            "Resurrection": self._play_resurrection,
            "Die-Die-Die!": self._play_die_die_die,
            "Hen Swap": self._play_hen_swap,
            "Bird Flu": self._play_bird_flu,
            "3-Egg Omelette": self._play_omelette,
            "Infertility": self._play_infertility,
            "Incubator": self._play_incubator,
            "Demotion": self._play_demotion,
            "Foster Farms": self._play_foster_farms,
            "Fox on the Loose": self._play_fox_on_the_loose,
            "Chicken Assassin": self._play_chicken_assassin,
            "Chicken Bomb": self._play_chicken_bomb,
            "End Your Turn": self._play_end_your_turn,
            "Reverse": self._play_reverse,
        }

    # --- Card Logic Methods ---

    def _play_coyote_attack(self, player, silent):
        opponents = self.get_opponents(player)
        if opponents:
            target = random.choice(opponents)
            if not silent: print(f"{player.name} targets {target.name} with Coyote Attack.")
            self._kill_a_chicken(target, silent, attacker=player)

    def _play_chicken_blaster(self, player, silent):
        opponents = self.get_opponents(player)
        if opponents:
            target = random.choice(opponents)
            if not silent: print(f"{player.name} targets {target.name} with Chicken Blaster.")
            self._kill_a_chicken(target, silent, attacker=player)

    def _play_eat_mor_chikin(self, player, silent):
        opponents = self.get_opponents(player)
        if opponents:
            target = random.choice(opponents)
            if not silent: print(f"{player.name} targets {target.name} with Eat Mor Chikin.")
            self._kill_a_chicken(target, silent, attacker=player)
            self.skip_roll = True
            if not silent: print(f"{player.name} skips their 'Roll the Chicken Die!' step.")

    def _play_farm_to_table(self, player, silent):
        cards_gained = min(3, self.egg_supply)
        player.egg_cards += cards_gained
        self.egg_supply -= cards_gained
        if not silent: print(f"{player.name} collects {cards_gained} Egg Cards.")

    def _play_feeding_frenzy(self, player, silent):
        chicks_to_promote = player.flock["Chicks"]
        promotions = min(chicks_to_promote, 3, self.hen_supply)
        if promotions > 0:
            player.flock["Chicks"] -= promotions
            self.chick_supply += promotions
            player.flock["Hens"] += promotions
            self.hen_supply -= promotions
            if not silent: print(f"{player.name} promotes {promotions} chicks to hens!")

    def _play_resurrection(self, player, silent):
        if self.graveyard:
            chicken_type = random.choice(self.graveyard)
            self.graveyard.remove(chicken_type)
            # Map back to flock key
            mapping = {
                "Dino Chicken": "Dino Chickens",
                "Flying Chicken": "Flying Chickens",
                "Mad Scientist Chicken": "Mad Scientist Chickens",
                "Robo-Hen": "Robo-Hens",
                "Decoy Chicken": "Decoy Chickens",
                "Punk Rock Chick": "Punk Rock Chicks"
            }
            if chicken_type in mapping:
                player.flock[mapping[chicken_type]] += 1
                if not silent: print(f"{player.name} resurrects a {chicken_type}!")

    def _play_die_die_die(self, player, silent):
        opponents = self.get_opponents(player)
        if opponents:
            target = random.choice(opponents)
            if not silent: print(f"{player.name} targets {target.name} with Die-Die-Die!.")
            for _ in range(3):
                roll = random.randint(1, 6)
                if not silent: print(f"  {target.name} rolls: {roll}")
                # Only negative outcomes: demotions and chicken dying (Roll 4, 5, 6)
                if roll == 4: # Demote a Chick!
                    if target.flock["Chicks"] > 0 and self.egg_supply > 0:
                        target.flock["Chicks"] -= 1
                        self.chick_supply += 1
                        target.egg_cards += 1
                        self.egg_supply -= 1
                        if not silent: print("  Outcome: Demote a Chick!")
                elif roll == 5: # Demote a Hen!
                    if target.flock["Hens"] > 0 and self.chick_supply > 0:
                        target.flock["Hens"] -= 1
                        self.hen_supply += 1
                        target.flock["Chicks"] += 1
                        self.chick_supply -= 1
                        if not silent: print("  Outcome: Demote a Hen!")
                elif roll == 6: # A Chicken Dies!
                    self._kill_a_chicken(target, silent)
                else:
                    if not silent: print(f"  Outcome: {roll} (No effect due to Die-Die-Die! rules)")

    def _play_hen_swap(self, player, silent):
        opponents = self.get_opponents(player)
        if opponents:
            target = random.choice(opponents)
            # Swap ALL hens. Receive up to 3.
            my_hens = player.flock["Hens"]
            target_hens = target.flock["Hens"]
            
            player.flock["Hens"] = min(target_hens, 3)
            target.flock["Hens"] = my_hens
            
            # Adjust supply if we capped at 3
            if target_hens > 3:
                self.hen_supply += (target_hens - 3)
            
            if not silent: print(f"{player.name} swaps Hens with {target.name}. Now has {player.flock['Hens']} Hens.")

    def _play_bird_flu(self, player, silent):
        if not silent: print("Bird Flu! All standard chicks in play die.")
        for p in self.players:
            # Explicitly target standard "Chicks" key only
            chicks_to_die = min(p.flock["Chicks"], 3) # Max 3 deaths per person
            if chicks_to_die > 0:
                p.flock["Chicks"] -= chicks_to_die
                self.chick_supply += chicks_to_die
                if not silent: print(f"  {p.name} loses {chicks_to_die} chicks.")

    def _play_omelette(self, player, silent):
        opponents = self.get_opponents(player)
        if opponents:
            target = random.choice(opponents)
            eggs_lost = min(3, target.egg_cards)
            target.egg_cards -= eggs_lost
            self.egg_supply += eggs_lost
            if not silent: print(f"{player.name} destroys {eggs_lost} of {target.name}'s eggs.")

    def _play_infertility(self, player, silent):
        opponents = [p for p in self.get_opponents(player) if p.flock["Hens"] > p.infertile_hens]
        if opponents:
            target = random.choice(opponents)
            target.infertile_hens += 1
            if not silent: print(f"{player.name} makes one of {target.name}'s hens infertile.")

    def _play_incubator(self, player, silent):
        # Trade 2 Egg Cards for 1 Chick, up to 3 chicks.
        chicks_gained = 0
        while player.egg_cards >= 2 and chicks_gained < 3 and self.chick_supply > 0:
            player.egg_cards -= 2
            self.egg_supply += 2
            player.flock["Chicks"] += 1
            self.chick_supply -= 1
            chicks_gained += 1
        if not silent and chicks_gained > 0:
            print(f"{player.name} used Incubator to get {chicks_gained} chicks.")

    def _play_demotion(self, player, silent):
        if not silent: print("A worldwide demotion! All hens become chicks.")
        for p in self.players:
            hens = p.flock["Hens"]
            if hens > 0:
                p.flock["Hens"] = 0
                self.hen_supply += hens
                chicks = min(hens, self.chick_supply)
                p.flock["Chicks"] += chicks
                self.chick_supply -= chicks

    def _play_foster_farms(self, player, silent):
        if not silent: print("Foster Farms! All standard hens die.")
        for p in self.players:
            # Explicitly target standard "Hens" key only
            hens_to_die = min(p.flock["Hens"], 3)
            if hens_to_die > 0:
                p.flock["Hens"] -= hens_to_die
                self.hen_supply += hens_to_die
                if not silent: print(f"  {p.name} loses {hens_to_die} hens.")

    def _play_fox_on_the_loose(self, player, silent):
        if not silent: print("A fox is on the loose!")
        for p in self.players:
            if not silent: print(f"  The fox visits {p.name}...")
            self.roll_chicken_die(p, silent)
            self.roll_chicken_die(p, silent)

    def _play_chicken_assassin(self, player, silent):
        if not silent: print("Chicken Assassin! Each player must lose a Specialty Chicken.")
        for p in self.players:
            specialty_keys = ["Dino Chickens", "Flying Chickens", "Mad Scientist Chickens", "Robo-Hens", "Decoy Chickens", "Punk Rock Chicks"]
            available = [k for k in specialty_keys if p.flock[k] > 0]
            if available:
                chosen = random.choice(available)
                p.flock[chosen] -= 1
                # Graveyard mapping
                inv_mapping = {v: k for k, v in {
                    "Dino Chicken": "Dino Chickens",
                    "Flying Chicken": "Flying Chickens",
                    "Mad Scientist Chicken": "Mad Scientist Chickens",
                    "Robo-Hen": "Robo-Hens",
                    "Decoy Chicken": "Decoy Chickens",
                    "Punk Rock Chick": "Punk Rock Chicks"
                }.items()}
                self.graveyard.append(inv_mapping[chosen])
                if not silent: print(f"  {p.name} loses a {inv_mapping[chosen]}.")

    def _play_chicken_bomb(self, player, silent):
        if not silent: print(f"{player.name} is hit by a Chicken Bomb!")
        self._kill_a_chicken(player, silent)

    def _play_end_your_turn(self, player, silent):
        if not silent: print(f"{player.name} ends their turn early.")
        self.skip_roll = True

    def _play_reverse(self, player, silent):
        if not silent: print("The direction of play is reversed and turn ends!")
        self.reverse_direction = not self.reverse_direction
        self.skip_roll = True

    def _kill_a_chicken(self, player, silent=False, attacker=None):
        """Kills a chicken, prioritizing Decoy Chickens."""
        # AI Check for Immunity or Cock Block (if attacker)
        if attacker:
            cock_block = next((card for card in player.hand if card.name == "Cock Block"), None)
            if cock_block:
                player.hand.remove(cock_block)
                self.deck.discard_pile.append(cock_block)
                if not silent: print(f"{player.name} plays Cock Block! Attack canceled and {attacker.name}'s turn ends.")
                # Ends their Play Action Cards step immediately? README says "ends their Play Action Cards step immediately"
                # For simulation, we'll just stop the current attack and maybe skip roll?
                # "ends their Play Action Cards step immediately" - this is hard to implement without a loop.
                # We'll just return True to indicate it was blocked.
                return True

        immunity_card = next((card for card in player.hand if card.name == "Immunity"), None)
        if immunity_card:
            player.hand.remove(immunity_card)
            self.deck.discard_pile.append(immunity_card)
            if not silent: print(f"{player.name} plays Immunity to save a chicken!")
            return True

        # Check for Dino Chicken (Cannot be killed by predators)
        # Coyote Attack and Chicken Blaster and Eat Mor Chikin are predators?
        # README says "Cannot be killed by predators" for Dino Chicken.
        # I'll assume Coyote, Chicken Blaster, Eat Mor Chikin are predators.
        
        # Priority: Decoy Chicken
        if player.flock["Decoy Chickens"] > 0:
            player.flock["Decoy Chickens"] -= 1
            self.graveyard.append("Decoy Chicken")
            if not silent: print(f"{player.name}'s Decoy Chicken is destroyed!")
            return True

        # If it's a predator attack, Dino Chicken is immune.
        # But wait, it says "Cannot be killed by predators".
        # If the attacker chooses a chicken, they can't choose Dino?
        # Or if Dino is chosen, it survives?
        # "choose one chicken... (either a Chick, Hen, or Specialty Chicken)"
        
        candidates = []
        if player.flock["Chicks"] > 0: candidates.append("Chicks")
        if player.flock["Hens"] > 0: candidates.append("Hens")
        if player.flock["Flying Chickens"] > 0: candidates.append("Flying Chickens")
        if player.flock["Mad Scientist Chickens"] > 0: candidates.append("Mad Scientist Chickens")
        if player.flock["Robo-Hens"] > 0: candidates.append("Robo-Hens")
        if player.flock["Punk Rock Chicks"] > 0: candidates.append("Punk Rock Chicks")
        
        # Dino Chicken only added if not a predator attack
        is_predator = attacker is not None # Simplified assumption
        if not is_predator and player.flock["Dino Chickens"] > 0:
            candidates.append("Dino Chickens")

        if candidates:
            chosen = random.choice(candidates)
            player.flock[chosen] -= 1
            if chosen == "Chicks":
                self.chick_supply += 1
                if not silent: print(f"{player.name} loses a Chick.")
            elif chosen == "Hens":
                self.hen_supply += 1
                if not silent: print(f"{player.name} loses a Hen.")
            else:
                # Specialty Chicken goes to graveyard
                inv_mapping = {
                    "Dino Chickens": "Dino Chicken",
                    "Flying Chickens": "Flying Chicken",
                    "Mad Scientist Chickens": "Mad Scientist Chicken",
                    "Robo-Hens": "Robo-Hen",
                    "Decoy Chickens": "Decoy Chicken",
                    "Punk Rock Chicks": "Punk Rock Chick"
                }
                self.graveyard.append(inv_mapping[chosen])
                if not silent: print(f"{player.name} loses a {inv_mapping[chosen]}.")
            return True
        else:
            if not silent: print(f"{player.name} has no chickens to lose.")
            return False

    def roll_chicken_die(self, player, silent=False):
        roll = random.randint(1, 6)
        if not silent:
            print(f"{player.name} rolls the Chicken Die: {roll}")
        
        if roll == 1: # Collect an Egg!
            if self.egg_supply > 0:
                player.egg_cards += 1
                self.egg_supply -= 1
                if not silent: print("Outcome: Collect an Egg!")
        elif roll == 2: # Promote an Egg!
            if player.egg_cards > 0 and self.chick_supply > 0:
                player.egg_cards -= 1
                self.egg_supply += 1
                player.flock["Chicks"] += 1
                self.chick_supply -= 1
                if not silent: print("Outcome: Promote an Egg! (Egg -> Chick)")
            else:
                if not silent: print("Outcome: Promote an Egg! (No effect)")
        elif roll == 3: # Promote a Chick!
            if player.flock["Chicks"] > 0 and self.hen_supply > 0:
                player.flock["Chicks"] -= 1
                player.flock["Hens"] += 1
                self.hen_supply -= 1
                if not silent: print("Outcome: Promote a Chick! (Chick -> Hen)")
            else:
                if not silent: print("Outcome: Promote a Chick! (No effect)")
        elif roll == 4: # Demote a Chick!
            if player.flock["Chicks"] > 0 and self.egg_supply > 0:
                player.flock["Chicks"] -= 1
                self.chick_supply += 1
                player.egg_cards += 1
                self.egg_supply -= 1
                if not silent: print("Outcome: Demote a Chick! (Chick -> Egg)")
            else:
                if not silent: print("Outcome: Demote a Chick! (No effect)")
        elif roll == 5: # Demote a Hen!
            if player.flock["Hens"] > 0 and self.chick_supply > 0:
                player.flock["Hens"] -= 1
                self.hen_supply += 1
                player.flock["Chicks"] += 1
                self.chick_supply -= 1
                if not silent: print("Outcome: Demote a Hen! (Hen -> Chick)")
            else:
                if not silent: print("Outcome: Demote a Hen! (No effect)")
        elif roll == 6: # A Chicken Dies!
            if not silent: print("Outcome: A Chicken Dies!")
            self._kill_a_chicken(player, silent)


def run_multiple_simulations(num_simulations=100, num_players=4):
    print(f"--- Running {num_simulations} Simulations ---")
    results = []
    for i in range(num_simulations):
        game = Game(num_players=num_players, silent_deck=True)
        result = game.run_simulation(silent=True)
        if result:
            results.append(result)

    print("\n--- Simulation Results ---")
    if not results:
        print("No games finished.")
        return

    total_turns = sum(r['turns'] for r in results)
    average_turns = total_turns / len(results)
    print(f"Average game length: {average_turns:.2f} turns")

    total_reshuffles = sum(r.get('reshuffles', 0) for r in results)
    average_reshuffles = total_reshuffles / len(results)
    print(f"Average reshuffles per game: {average_reshuffles:.2f}")

    total_cards = sum(r.get('cards_played', 0) for r in results)
    avg_cards_per_turn = total_cards / total_turns if total_turns > 0 else 0
    print(f"Average cards played per turn: {avg_cards_per_turn:.2f}")

    total_duration = sum(r.get('duration', 0) for r in results)
    avg_time_per_turn_ms = (total_duration / total_turns * 1000) if total_turns > 0 else 0
    print(f"Average execution time per turn: {avg_time_per_turn_ms:.4f} ms")

    winner_counts = {}
    for r in results:
        winner = r['winner']
        winner_counts[winner] = winner_counts.get(winner, 0) + 1
    
    print("\nWin Distribution:")
    for winner, count in sorted(winner_counts.items()):
        win_percentage = (count / len(results)) * 100
        print(f"  {winner}: {count} wins ({win_percentage:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description="Run a simulation of the Chicken Die! game.")
    parser.add_argument(
        "-n", "--num-simulations",
        type=int,
        default=100,
        help="The number of simulations to run in silent mode."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output for a single simulation run. Overrides -n."
    )
    parser.add_argument(
        "-p", "--num-players",
        type=int,
        default=4,
        help="The number of players in the game."
    )
    args = parser.parse_args()

    if args.verbose:
        print("--- Running a single verbose simulation ---")
        game = Game(num_players=args.num_players)
        result = game.run_simulation(silent=False)
        if result:
            print(f"Total deck reshuffles: {result.get('reshuffles', 0)}")
    else:
        run_multiple_simulations(num_simulations=args.num_simulations, num_players=args.num_players)

if __name__ == "__main__":
    main()
