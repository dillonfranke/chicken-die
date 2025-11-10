import random
import argparse

class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type

    def __repr__(self):
        return f"Card(name='{self.name}', type='{self.card_type}')"

class Deck:
    def __init__(self, silent=False):
        self.cards = []
        self.discard_pile = []
        self.build_deck(silent)

    def build_deck(self, silent=False):
        deck_composition = [
            # Specialty Chicken
            {"name": "Dino Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Flying Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Mad Scientist Chicken", "type": "Specialty Chicken", "count": 1},
            {"name": "Robo-Hen", "type": "Specialty Chicken", "count": 1},
            {"name": "Decoy Chick", "type": "Specialty Chicken", "count": 1},
            # Protection
            {"name": "Immunity", "type": "Protection", "count": 1},
            {"name": "Chicken Wire", "type": "Protection", "count": 1},
            {"name": "Cock Block", "type": "Protection", "count": 1},
            # Attack
            {"name": "Coyote Attack", "type": "Attack", "count": 1},
            {"name": "Die-Die-Die!", "type": "Attack", "count": 1},
            {"name": "Hen Swap", "type": "Attack", "count": 1},
            {"name": "Bird Flu", "type": "Attack", "count": 1},
            {"name": "Omelette", "type": "Attack", "count": 1},
            {"name": "Infertility", "type": "Attack", "count": 1},
            # World Altering
            {"name": "Demotion", "type": "World Altering", "count": 1},
            {"name": "Foster Farms", "type": "World Altering", "count": 1},
            {"name": "Drought", "type": "World Altering", "count": 1},
            {"name": "Fox on the Loose", "type": "World Altering", "count": 1},
            # Personal Growth
            {"name": "Feeding Frenzy", "type": "Personal Growth", "count": 1},
            {"name": "Incubator", "type": "Personal Growth", "count": 1},
            {"name": "Farm to Table", "type": "Personal Growth", "count": 1},
            {"name": "Resurrection", "type": "Personal Growth", "count": 1},
            {"name": "Hatch Egg", "type": "Personal Growth", "count": 1}, # New card
            # Turn Altering
            {"name": "Take it or Leave it", "type": "Turn Altering", "count": 1},
            {"name": "End Your Turn", "type": "Turn Altering", "count": 1},
            {"name": "Reverse", "type": "Turn Altering", "count": 1},
        ]

        for card_info in deck_composition:
            for _ in range(card_info["count"]):
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
        return self.cards.pop()

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.flock = {"Chicks": 3, "Hens": 0}
        self.eggs = 1

    def __repr__(self):
        return f"Player(name='{self.name}', hand_size={len(self.hand)}, chicks={self.flock['Chicks']}, hens={self.flock['Hens']}, eggs={self.eggs})"

class Game:
    def __init__(self, num_players=4, silent_deck=False):
        self.players = [Player(f"Player {i+1}") for i in range(num_players)]
        self.deck = Deck(silent=silent_deck)
        self.deck.shuffle()
        self.current_player_index = 0
        self.game_over = False
        self.turn = 0

        # Game state flags
        self.drought_active = False
        self.drought_player_index = -1

        # Game resources
        self.chick_supply = 10
        self.hen_supply = 10
        self.graveyard = []

        # Deal starting hands and chicks
        for player in self.players:
            # Assign starting chicks from the supply
            player.flock["Chicks"] = 0 # Reset default
            start_chicks = min(3, self.chick_supply)
            player.flock["Chicks"] = start_chicks
            self.chick_supply -= start_chicks

            # Deal cards
            for _ in range(5):
                card = self.deck.draw()
                if card:
                    player.hand.append(card)

    def run_simulation(self, silent=False):
        if not silent:
            print("--- Starting Chicken Die! Simulation ---")
        
        while not self.game_over:
            self.turn += 1
            if self.turn > 1000: # Safety break
                return {"winner": "None", "turns": self.turn, "reason": "Exceeded max turns"}

            if not silent:
                print(f"\n--- Turn {self.turn} ---")
                print(f"Supply: {self.chick_supply} Chicks, {self.hen_supply} Hens | Graveyard: {len(self.graveyard)}")
                for p in self.players:
                    print(f"  {p.name}: {p.flock['Chicks']} Chicks, {p.flock['Hens']} Hens, {p.eggs} Eggs, {len(p.hand)} Cards")

            current_player = self.players[self.current_player_index]
            self.take_turn(current_player, silent)
            
            active_players = [p for p in self.players if (p.flock["Chicks"] + p.flock["Hens"]) > 0]
            if len(active_players) <= 1:
                self.game_over = True
                winner = active_players[0] if active_players else None
                if not silent:
                    print(f"\n--- Game Over! ---")
                    if winner:
                        print(f"Winner is {winner.name} after {self.turn} turns!")
                    else:
                        print("All players lost their chickens simultaneously!")
                return {"winner": winner.name if winner else "None", "turns": self.turn}

            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return None

    def take_turn(self, player, silent=False):
        if not silent:
            print(f"It's {player.name}'s turn.")

        # Check if drought ends
        if self.drought_active and self.current_player_index == self.drought_player_index:
            self.drought_active = False
            self.drought_player_index = -1
            if not silent:
                print("The drought has ended!")
        
        # Step 1: Collect Eggs
        if not self.drought_active:
            player.eggs += player.flock["Hens"]
            if not silent:
                print(f"{player.name} collects {player.flock['Hens']} eggs, now has {player.eggs}.")
        else:
            if not silent:
                print(f"{player.name} collects no eggs due to drought.")

        drawn_card = self.deck.draw()
        if drawn_card:
            player.hand.append(drawn_card)
            if not silent:
                print(f"{player.name} draws a card.")

        # AI Logic for playing cards and spending eggs
        self.perform_ai_actions(player, silent)

        self.roll_chicken_die(player, silent)

    def get_opponents(self, current_player):
        return [p for p in self.players if p is not current_player and (p.flock["Chicks"] + p.flock["Hens"]) > 0]

    def perform_ai_actions(self, player, silent=False):
        # --- AI: Play Cards ---
        # Simple AI: Play the first useful card
        card_to_play = None
        for card in player.hand:
            # Prioritize playing growth cards if we have few chickens, or attack cards otherwise
            if card.card_type == "Personal Growth":
                card_to_play = card
                break
            if card.card_type == "Attack":
                card_to_play = card
                # Don't break, see if there's a growth card
        
        if card_to_play:
            self.play_card(player, card_to_play, silent)

        # --- AI: Spend Eggs ---
        if player.eggs >= 6 and self.chick_supply > 0:
            player.eggs -= 6
            player.flock["Chicks"] += 1
            self.chick_supply -= 1
            if not silent:
                print(f"{player.name} spends 6 eggs to get a new Chick from the supply.")

    def play_card(self, player, card, silent=False):
        player.hand.remove(card)
        self.deck.discard_pile.append(card)
        if not silent:
            print(f"{player.name} plays {card.name}.")

        # --- Card Effects ---
        if card.name == "Coyote Attack":
            opponents = self.get_opponents(player)
            if opponents:
                target = random.choice(opponents)
                if not silent: print(f"{player.name} targets {target.name} with Coyote Attack.")
                if target.flock["Chicks"] > 0:
                    target.flock["Chicks"] -= 1
                    self.graveyard.append("Chick")
                elif target.flock["Hens"] > 0:
                    target.flock["Hens"] -= 1
                    self.graveyard.append("Hen")
        
        elif card.name == "Farm to Table":
            player.eggs += 3

        elif card.name == "Feeding Frenzy":
            chicks_to_promote = player.flock["Chicks"]
            promotions_possible = min(chicks_to_promote, self.hen_supply)
            if promotions_possible > 0:
                player.flock["Chicks"] -= promotions_possible
                player.flock["Hens"] += promotions_possible
                self.hen_supply -= promotions_possible
                for _ in range(promotions_possible):
                    self.graveyard.append("Chick")
                if not silent: print(f"{player.name} promotes {promotions_possible} chicks to hens!")
        
        elif card.name == "Hatch Egg":
            if player.eggs > 0 and self.chick_supply > 0:
                player.eggs -= 1
                player.flock["Chicks"] += 1
                self.chick_supply -= 1
                if not silent: print(f"{player.name} hatches an egg into a new Chick!")

        elif card.name == "Resurrection":
            resurrect_count = 0
            for _ in range(2): # Try to resurrect up to 2
                if "Chick" in self.graveyard:
                    self.graveyard.remove("Chick")
                    player.flock["Chicks"] += 1
                    resurrect_count += 1
                elif "Hen" in self.graveyard:
                    self.graveyard.remove("Hen")
                    player.flock["Hens"] += 1
                    resurrect_count += 1
            if not silent and resurrect_count > 0:
                print(f"{player.name} resurrects {resurrect_count} chicken(s) from the graveyard.")

        elif card.name == "Die-Die-Die!":
            opponents = self.get_opponents(player)
            if opponents:
                target = random.choice(opponents)
                if not silent: print(f"{player.name} targets {target.name} with Die-Die-Die!.")
                for _ in range(3):
                    self.roll_chicken_die(target, silent)

        elif card.name == "Hen Swap":
            opponents_with_hens = [p for p in self.get_opponents(player) if p.flock["Hens"] > 0]
            if player.flock["Hens"] > 0 and opponents_with_hens:
                target = random.choice(opponents_with_hens)
                player.flock["Hens"] -= 1
                target.flock["Hens"] += 1
                player.flock["Hens"] += 1
                target.flock["Hens"] -= 1
                if not silent: print(f"{player.name} swaps a Hen with {target.name}.")

        elif card.name == "Bird Flu":
            opponents = self.get_opponents(player)
            if opponents:
                target = random.choice(opponents)
                chicks_lost = target.flock["Chicks"]
                if chicks_lost > 0:
                    target.flock["Chicks"] = 0
                    for _ in range(chicks_lost):
                        self.graveyard.append("Chick")
                    if not silent: print(f"{target.name} loses {chicks_lost} chicks to Bird Flu!")

        elif card.name == "Omelette":
            # Target any player, including self for simplicity in AI
            target = random.choice(self.players)
            eggs_lost = min(3, target.eggs)
            target.eggs -= eggs_lost
            if not silent: print(f"{player.name} destroys {eggs_lost} of {target.name}'s eggs.")

        # World Altering
        elif card.name == "Demotion":
            if not silent: print("A worldwide demotion! All hens become chicks.")
            for p in self.players:
                if p.flock["Hens"] > 0:
                    demoted_hens = p.flock["Hens"]
                    p.flock["Hens"] = 0
                    # Hens return to supply
                    self.hen_supply += demoted_hens
                    # Get new chicks from supply
                    new_chicks = min(demoted_hens, self.chick_supply)
                    p.flock["Chicks"] += new_chicks
                    self.chick_supply -= new_chicks
                    if not silent: print(f"{p.name}'s {demoted_hens} hens are replaced with {new_chicks} chicks.")

        elif card.name == "Foster Farms":
            if not silent: print("Foster Farms takes all the hens!")
            for p in self.players:
                hens_lost = p.flock["Hens"]
                if hens_lost > 0:
                    p.flock["Hens"] = 0
                    for _ in range(hens_lost):
                        self.graveyard.append("Hen")
                    if not silent: print(f"{p.name} loses {hens_lost} hens.")

        elif card.name == "Drought":
            if not silent: print("A drought begins! No eggs will be collected.")
            self.drought_active = True
            self.drought_player_index = self.current_player_index

        elif card.name == "Fox on the Loose":
            if not silent: print("A fox is on the loose!")
            start_index = self.current_player_index
            for i in range(len(self.players)):
                player_index = (start_index + i) % len(self.players)
                p = self.players[player_index]
                if not silent: print(f"The fox visits {p.name}...")
                self.roll_chicken_die(p, silent)
                self.roll_chicken_die(p, silent)

    def roll_chicken_die(self, player, silent=False):
        roll = random.randint(1, 6)
        if not silent:
            print(f"{player.name} rolls the Chicken Die...")
        
        if roll <= 2: # A Chicken Dies!
            if not silent: print("Outcome: A Chicken Dies!")
            if player.flock["Chicks"] > 0:
                player.flock["Chicks"] -= 1
                self.graveyard.append("Chick")
                if not silent: print(f"{player.name} loses a Chick.")
            elif player.flock["Hens"] > 0:
                player.flock["Hens"] -= 1
                self.graveyard.append("Hen")
                if not silent: print(f"{player.name} loses a Hen.")
            else:
                if not silent: print(f"{player.name} has no chickens to lose.")
        elif roll == 3: # Promote!
            if not silent: print("Outcome: Promote!")
            if player.flock["Chicks"] > 0 and self.hen_supply > 0:
                player.flock["Chicks"] -= 1
                player.flock["Hens"] += 1
                self.hen_supply -= 1
                self.graveyard.append("Chick")
                if not silent: print(f"{player.name} promotes a Chick to a Hen.")
            else:
                if not silent: print(f"{player.name} has no Chicks to promote or no Hens in supply.")
        elif roll == 4: # Roll Again!
            if not silent: print("Outcome: Roll Again!")
            self.roll_chicken_die(player, silent)
        elif roll == 5: # Draw a Card!
            if not silent: print("Outcome: Draw a Card!")
            drawn_card = self.deck.draw()
            if drawn_card:
                player.hand.append(drawn_card)
        elif roll == 6: # Collect an Egg!
            if not silent: print("Outcome: Collect an Egg!")
            player.eggs += 1

def run_multiple_simulations(num_simulations=100):
    print(f"--- Running {num_simulations} Simulations ---")
    results = []
    for i in range(num_simulations):
        game = Game(num_players=4, silent_deck=True)
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
    args = parser.parse_args()

    if args.verbose:
        print("--- Running a single verbose simulation ---")
        game = Game(num_players=4)
        game.run_simulation(silent=False)
    else:
        run_multiple_simulations(num_simulations=args.num_simulations)

if __name__ == "__main__":
    main()
