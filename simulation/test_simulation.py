import unittest
from unittest.mock import patch
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
            self.assertEqual(player.eggs, 1)
        # Initial chicks are distributed, so we check the total
        total_chicks = sum(p.flock["Chicks"] for p in self.game.players)
        self.assertLessEqual(total_chicks, 10) # Supply starts at 10

class TestPersonalGrowthCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]
        # Ensure players have resources for testing
        self.player1.eggs = 10
        self.player1.flock["Chicks"] = 3
        self.game.hen_supply = 5
        self.game.chick_supply = 5

    def test_farm_to_table_card(self):
        """Test that Farm to Table correctly adds 3 eggs to the player."""
        initial_eggs = self.player1.eggs
        card = Card("Farm to Table", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.eggs, initial_eggs + 3)

    def test_feeding_frenzy_card(self):
        """Test that Feeding Frenzy promotes all of a player's chicks to hens."""
        initial_chicks = self.player1.flock["Chicks"]
        card = Card("Feeding Frenzy", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Hens"], initial_chicks)
        self.assertEqual(self.player1.flock["Chicks"], 0)
        self.assertEqual(self.game.hen_supply, 5 - initial_chicks)

    def test_hatch_egg_card(self):
        """Test that Hatch Egg correctly uses an egg to gain a chick."""
        initial_eggs = self.player1.eggs
        initial_chicks = self.player1.flock["Chicks"]
        initial_chick_supply = self.game.chick_supply
        card = Card("Hatch Egg", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.eggs, initial_eggs - 1)
        self.assertEqual(self.player1.flock["Chicks"], initial_chicks + 1)
        self.assertEqual(self.game.chick_supply, initial_chick_supply - 1)

    def test_resurrection_card(self):
        """Test that Resurrection brings back chickens from the graveyard."""
        self.game.graveyard = ["Chick", "Hen"]
        initial_chicks = self.player1.flock["Chicks"]
        initial_hens = self.player1.flock["Hens"]
        card = Card("Resurrection", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Chicks"], initial_chicks + 1)
        self.assertEqual(self.player1.flock["Hens"], initial_hens + 1)
        self.assertEqual(len(self.game.graveyard), 0)

    def test_incubator_card(self):
        """Test that Incubator allows spending eggs to gain chicks."""
        self.player1.eggs = 7 # Spends 3, gains 1 chick (7 // 2 = 3)
        initial_chicks = self.player1.flock["Chicks"]
        card = Card("Incubator", "Personal Growth")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Chicks"], initial_chicks + 1)
        self.assertEqual(self.player1.eggs, 7 - 2)

class TestAttackCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]
        # Setup initial flock and resources
        self.player1.flock = {"Chicks": 2, "Hens": 1, "Robo-Hens": 0, "Decoy-Chicks": 0}
        self.player2.flock = {"Chicks": 2, "Hens": 1, "Robo-Hens": 0, "Decoy-Chicks": 0}
        self.player2.eggs = 5

    def test_coyote_attack_card(self):
        """Test that Coyote Attack correctly kills an opponent's chicken."""
        self.player2.hand = [] # Ensure no Immunity card
        initial_chick_count = self.player2.flock["Chicks"]
        card = Card("Coyote Attack", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        # The target is random, so we check if either a chick or hen was lost
        final_chick_count = self.player2.flock["Chicks"]
        final_hen_count = self.player2.flock["Hens"]
        self.assertTrue(
            final_chick_count == initial_chick_count - 1 or
            final_hen_count == 0
        )

    @patch('random.choice')
    def test_die_die_die_card(self, mock_choice):
        """Test that Die-Die-Die! forces an opponent to roll the die three times."""
        mock_choice.return_value = self.player2
        with patch.object(self.game, 'roll_chicken_die') as mock_roll:
            card = Card("Die-Die-Die!", "Attack")
            self.player1.hand.append(card)
            self.game.play_card(self.player1, card, silent=True)
            self.assertEqual(mock_roll.call_count, 3)
            # Check that the target was the opponent
            mock_roll.assert_called_with(self.player2, True)

    def test_hen_swap_card(self):
        """Test that Hen Swap correctly swaps hens between players."""
        p1_hens = self.player1.flock["Hens"]
        p2_hens = self.player2.flock["Hens"]
        card = Card("Hen Swap", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        # Since it's a swap, the number of hens for each player should remain the same
        self.assertEqual(self.player1.flock["Hens"], p1_hens)
        self.assertEqual(self.player2.flock["Hens"], p2_hens)

    def test_bird_flu_card(self):
        """Test that Bird Flu eliminates all of an opponent's chicks."""
        card = Card("Bird Flu", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.flock["Chicks"], 0)
        self.assertIn("Chick", self.game.graveyard)

    def test_omelette_card(self):
        """Test that Omelette destroys 3 of an opponent's eggs."""
        initial_eggs = self.player2.eggs
        with patch('random.choice', return_value=self.player2):
            card = Card("Omelette", "Attack")
            self.player1.hand.append(card)
            self.game.play_card(self.player1, card, silent=True)
            self.assertEqual(self.player2.eggs, initial_eggs - 3)

    def test_infertility_card(self):
        """Test that Infertility makes an opponent's hen unable to lay eggs."""
        self.player2.flock["Hens"] = 2
        card = Card("Infertility", "Attack")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player2.infertile_hens, 1)
        # Test egg collection
        initial_eggs = self.player2.eggs
        with patch.object(self.game, 'perform_ai_actions', return_value=None) as mock_ai, \
             patch.object(self.game, 'roll_chicken_die', return_value=None) as mock_roll:
            self.game.take_turn(self.player2, silent=True)
            # Should only collect 1 egg from the 1 fertile hen
            self.assertEqual(self.player2.eggs, initial_eggs + 1)

class TestWorldAlteringCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]
        # Setup flocks
        self.player1.flock = {"Chicks": 1, "Hens": 2, "Robo-Hens": 0, "Decoy-Chicks": 0}
        self.player2.flock = {"Chicks": 2, "Hens": 1, "Robo-Hens": 0, "Decoy-Chicks": 0}
        self.game.chick_supply = 10
        self.game.hen_supply = 10

    def test_demotion_card(self):
        """Test that Demotion turns all hens into chicks."""
        card = Card("Demotion", "World Altering")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Hens"], 0)
        self.assertEqual(self.player1.flock["Chicks"], 1 + 2) # Initial chicks + demoted hens
        self.assertEqual(self.player2.flock["Hens"], 0)
        self.assertEqual(self.player2.flock["Chicks"], 2 + 1)

    def test_foster_farms_card(self):
        """Test that Foster Farms removes all hens from play."""
        card = Card("Foster Farms", "World Altering")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Hens"], 0)
        self.assertEqual(self.player2.flock["Hens"], 0)
        self.assertEqual(len(self.game.graveyard), 3) # 2 from p1, 1 from p2

    def test_drought_card(self):
        """Test that Drought prevents egg collection for one round."""
        card = Card("Drought", "World Altering")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertTrue(self.game.drought_active)
        
        # Player 2's turn, should not collect eggs
        p2_initial_eggs = self.player2.eggs
        self.game.current_player_index = 1
        with patch.object(self.game, 'perform_ai_actions', return_value=None) as mock_ai, \
             patch.object(self.game, 'roll_chicken_die', return_value=None) as mock_roll:
            self.game.take_turn(self.player2, silent=True)
            self.assertEqual(self.player2.eggs, p2_initial_eggs)

        # Player 1's turn again, drought should end, and they should collect eggs
        p1_initial_eggs = self.player1.eggs
        self.game.current_player_index = 0
        with patch.object(self.game, 'perform_ai_actions', return_value=None) as mock_ai, \
             patch.object(self.game, 'roll_chicken_die', return_value=None) as mock_roll:
            self.game.take_turn(self.player1, silent=True)
            self.assertFalse(self.game.drought_active)
            self.assertEqual(self.player1.eggs, p1_initial_eggs + self.player1.flock["Hens"])

    def test_fox_on_the_loose_card(self):
        """Test that Fox on the Loose makes each player roll the die twice."""
        with patch.object(self.game, 'roll_chicken_die') as mock_roll:
            card = Card("Fox on the Loose", "World Altering")
            self.player1.hand.append(card)
            self.game.play_card(self.player1, card, silent=True)
            self.assertEqual(mock_roll.call_count, 4) # 2 players * 2 rolls

class TestTurnAlteringCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=3, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]
        self.player3 = self.game.players[2]

    def test_end_your_turn_card(self):
        """Test that End Your Turn skips the die roll."""
        card = Card("End Your Turn", "Turn Altering")
        self.player1.hand.append(card)

        # Mock the AI to ensure it plays the card we want to test
        def mock_ai_logic(player, silent):
            if card in player.hand:
                self.game.play_card(player, card, silent)

        with patch.object(self.game, 'perform_ai_actions', side_effect=mock_ai_logic), \
             patch.object(self.game, 'roll_chicken_die') as mock_roll:
            self.game.take_turn(self.player1, silent=True)
            mock_roll.assert_not_called()

    def test_reverse_card(self):
        """Test that Reverse changes the direction of play."""
        self.game.current_player_index = 0
        card = Card("Reverse", "Turn Altering")
        self.player1.hand.append(card)
        
        # Play the card and check the next player
        self.game.play_card(self.player1, card, silent=True)
        self.assertTrue(self.game.reverse_direction)
        
        # Simulate the end of the turn to see who is next
        self.game.current_player_index = (self.game.current_player_index - 1 + len(self.game.players)) % len(self.game.players)
        self.assertEqual(self.game.players[self.game.current_player_index].name, self.player3.name)

class TestSpecialtyChickenCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]
        self.player2 = self.game.players[1]

    def test_robo_hen_card(self):
        """Test that Robo-Hen is added to the flock and produces 2 eggs."""
        card = Card("Robo-Hen", "Specialty Chicken")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Robo-Hens"], 1)

        # Test egg collection
        initial_eggs = self.player1.eggs
        with patch.object(self.game, 'perform_ai_actions', return_value=None), \
             patch.object(self.game, 'roll_chicken_die', return_value=None):
            self.game.take_turn(self.player1, silent=True)
            self.assertEqual(self.player1.eggs, initial_eggs + 2)

    def test_decoy_chick_card(self):
        """Test that Decoy Chick is sacrificed first."""
        card = Card("Decoy Chick", "Specialty Chicken")
        self.player1.hand.append(card)
        self.game.play_card(self.player1, card, silent=True)
        self.assertEqual(self.player1.flock["Decoy-Chicks"], 1)

        # Test that it's killed first
        self.player1.hand = [] # Ensure no Immunity
        self.player1.flock["Chicks"] = 1
        self.game._kill_a_chicken(self.player1, silent=True)
        self.assertEqual(self.player1.flock["Decoy-Chicks"], 0)
        self.assertEqual(self.player1.flock["Chicks"], 1) # The normal chick should survive

class TestProtectionCards(unittest.TestCase):

    def setUp(self):
        """Set up a new game for each test."""
        self.game = Game(num_players=2, silent_deck=True)
        self.player1 = self.game.players[0]

    def test_immunity_card(self):
        """Test that Immunity saves a chicken from dying."""
        self.player1.flock = {"Chicks": 1, "Hens": 0, "Robo-Hens": 0, "Decoy-Chicks": 0}
        card = Card("Immunity", "Protection")
        self.player1.hand.append(card)

        initial_chickens = self.player1.total_chickens()
        self.game._kill_a_chicken(self.player1, silent=True)
        
        self.assertEqual(self.player1.total_chickens(), initial_chickens)
        self.assertIsNone(next((c for c in self.player1.hand if c.name == "Immunity"), None))

if __name__ == '__main__':
    unittest.main()
