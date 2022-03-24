from pythonium.orders.extractor import OrdersExtractor


class TestOrdersExtractor:

    def setup(self, game_mode):
        self.extract = OrdersExtractor(game_mode)

    def stub_player_next_turn(self, player, when):
        when(player).next_turn(...).thenReturn()
