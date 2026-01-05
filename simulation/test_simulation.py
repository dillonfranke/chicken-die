import unittest
from unittest.mock import patch
import random
from simulation import Game, Card, Player

class TestGameMechanics(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=4, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]

    def test_initial_game_setup(self):
        """Test that the game initializes with the correct number of players and starting conditions."""
        self.assertEqual(len(self.game.players), 4)
        for player in self.game.players:
            self.assertEqual(len(player.hand), 5)
            self.assertEqual(player.egg_cards, 1)
            self.assertEqual(player.flock["Chicks"], 2)
            self.assertEqual(player.flock["Hens"], 1)

class TestPersonalGrowthCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]
        # Ensure players have resources for testing
        self.player1.egg_cards = 10
        self.player1.flock["Chicks"] = 3
        self.game.hen_supply = 10
        self.game.chick_supply = 10
        self.game.egg_supply = 50

    def test_farm_to_table_card(self):
        """Test that Farm to Table correctly adds 3 eggs to the player."""
        initial_eggs = self.player1.egg_cards
        card = Card("Farm to Table", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.egg_cards, initial_eggs + 3)

    def test_feeding_frenzy_card(self):
        """Test that Feeding Frenzy promotes up to 3 of a player's chicks to hens."""
        self.player1.flock["Chicks"] = 5
        card = Card("Feeding Frenzy", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        # Should promote 3 chicks
        self.assertEqual(self.player1.flock["Hens"], 1 + 3)
        self.assertEqual(self.player1.flock["Chicks"], 5 - 3)

    def test_resurrection_card(self):
        """Test that Resurrection brings back a specialty chicken from the graveyard."""
        self.game.graveyard = ["Robo-Hen"]
        card = Card("Resurrection", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Robo-Hens"], 1)
        self.assertEqual(len(self.game.graveyard), 0)

    def test_incubator_card(self):
        """Test that Incubator allows trading 2 eggs for 1 chick, up to 3 chicks."""
        self.player1.egg_cards = 10
        initial_chicks = self.player1.flock["Chicks"]
        card = Card("Incubator", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Chicks"], initial_chicks + 3)
        self.assertEqual(self.player1.egg_cards, 10 - (3 * 2))

class TestAttackCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]
        # Setup initial flock and resources
        self.player2.hand = []
        self.player2.egg_cards = 5

    def test_coyote_attack_card(self):
        """Test that Coyote Attack correctly kills an opponent's chicken."""
        initial_chickens = self.player2.total_chickens()
        card = Card("Coyote Attack", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.total_chickens(), initial_chickens - 1)

    def test_chicken_blaster_card(self):
        """Test that Chicken Blaster correctly kills an opponent's chicken."""
        initial_chickens = self.player2.total_chickens()
        card = Card("Chicken Blaster", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.total_chickens(), initial_chickens - 1)

    def test_eat_mor_chikin_card(self):
        """Test that Eat Mor Chikin kills a chicken and skips the roll."""
        initial_chickens = self.player2.total_chickens()
        card = Card("Eat Mor Chikin", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.total_chickens(), initial_chickens - 1)
        self.assertTrue(self.game.skip_roll)

    def test_hen_swap_card(self):
        """Test that Hen Swap correctly swaps hens between players (max 3 received)."""
        self.player1.flock["Hens"] = 1
        self.player2.flock["Hens"] = 5
        card = Card("Hen Swap", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Hens"], 3) # Capped at 3
        self.assertEqual(self.player2.flock["Hens"], 1)

    def test_bird_flu_card(self):
        """Test that Bird Flu eliminates chicks (max 3 per person)."""
        self.player2.flock["Chicks"] = 5
        card = Card("Bird Flu", "Instant Effect") # Note: Card is Instant Effect in rules
        # Mocking draw/play since it's instant
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.flock["Chicks"], 2) # 5 - 3

    def test_omelette_card(self):
        """Test that 3-Egg Omelette destroys 3 of an opponent's eggs."""
        initial_eggs = self.player2.egg_cards
        card = Card("3-Egg Omelette", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.egg_cards, initial_eggs - 3)

class TestInstantEffectCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]

    def test_demotion_card(self):
        """Test that Demotion turns all hens into chicks."""
        self.player1.flock["Hens"] = 2
        self.player2.flock["Hens"] = 1
        card = Card("Demotion", "Instant Effect")
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Hens"], 0)
        self.assertEqual(self.player1.flock["Chicks"], 2 + 2) # Start with 2
        self.assertEqual(self.player2.flock["Hens"], 0)
        self.assertEqual(self.player2.flock["Chicks"], 2 + 1)

    def test_foster_farms_card(self):
        """Test that Foster Farms removes hens from play (max 3 per person) but spares specialty hens."""
        self.player1.flock["Hens"] = 5
        self.player1.flock["Robo-Hens"] = 1
        card = Card("Foster Farms", "Instant Effect")
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Hens"], 2) # 5 - 3
        self.assertEqual(self.player1.flock["Robo-Hens"], 1) # Unaffected

    def test_chicken_bomb_card(self):
        """Test that Chicken Bomb kills a chicken of the player who drew it."""
        initial_chickens = self.player1.total_chickens()
        card = Card("Chicken Bomb", "Instant Effect")
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.total_chickens(), initial_chickens - 1)

class TestSpecialtyChickenCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]

    def test_robo_hen_production(self):
        """Test that Robo-Hen produces 2 eggs."""
        self.player1.flock["Robo-Hens"] = 1
        self.player1.flock["Hens"] = 0
        self.player1.egg_cards = 0
        
        # Mocking turn steps to only test egg collection
        with patch.object(self.game, 'perform_ai_actions'), \
             patch.object(self.game, 'roll_chicken_die'):
            self.game.take_turn(self.player1, silent=True)
            self.assertEqual(self.player1.egg_cards, 2)

    def test_punk_rock_chick_production(self):
        """Test that Punk Rock Chick produces 1 egg and cannot be promoted."""
        self.player1.flock["Punk Rock Chicks"] = 1
        self.player1.flock["Hens"] = 0
        self.player1.egg_cards = 0
        with patch.object(self.game, 'perform_ai_actions'), \
             patch.object(self.game, 'roll_chicken_die'):
            self.game.take_turn(self.player1, silent=True)
            self.assertEqual(self.player1.egg_cards, 1)

    def test_decoy_chicken_priority(self):
        """Test that Decoy Chicken is killed first."""
        self.player1.hand = [] # Ensure no Immunity card
        self.player1.flock["Decoy Chickens"] = 1
        self.player1.flock["Chicks"] = 1
        self.game._kill_a_chicken(self.player1, silent=True)
        self.assertEqual(self.player1.flock["Decoy Chickens"], 0)
        self.assertEqual(self.player1.flock["Chicks"], 1)

class TestProtectionCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]

    def test_immunity_card(self):
        """Test that Immunity saves a chicken."""
        card = Card("Immunity", "Protection")
        self.player2.hand = [card]
        initial_chickens = self.player2.total_chickens()
        self.game._kill_a_chicken(self.player2, silent=True)
        self.assertEqual(self.player2.total_chickens(), initial_chickens)
        self.assertNotIn(card, self.player2.hand)

    def test_cock_block_card(self):
        """Test that Cock Block stops an attack."""
        card = Card("Cock Block", "Protection")
        self.player2.hand = [card]
        initial_chickens = self.player2.total_chickens()
        
        # Coyote Attack should be blocked
        self.game._kill_a_chicken(self.player2, silent=True, attacker=self.player1)
        self.assertEqual(self.player2.total_chickens(), initial_chickens)
        self.assertNotIn(card, self.player2.hand)

if __name__ == '__main__':
    unittest.main()