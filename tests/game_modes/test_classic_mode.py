import pytest

from pythonium import ClassicMode, Galaxy


class TestClassicMode:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.game_mode = ClassicMode()

    @pytest.fixture
    def galaxy_name(self, fake):
        return fake.word()

    def test_get_players(self, agents, expected_players):
        players = self.game_mode.get_players(agents)
        assert [p.name for p in players] == expected_players

    def text_build_galaxy(self, agents, expected_players, galaxy_name):
        galaxy = self.game_mode.build_galaxy(galaxy_name, agents)
        assert isinstance(galaxy, Galaxy)
        assert galaxy.known_races == expected_players

    def test_galaxy_for_agents(self, galaxy, agents):
        for agent in agents:
            agent_galaxy = self.game_mode.galaxy_for_player(galaxy, agent)
            if agent.is_player:
                assert agent_galaxy != galaxy
            else:
                assert agent_galaxy == galaxy

    def test_get_score(self, galaxy, agents, spectator, expected_players):
        score = self.game_mode.get_score(galaxy, agents, galaxy.turn)
        players_in_score = [player['player'] for player in score]
        assert players_in_score == expected_players
        assert spectator.name not in players_in_score
