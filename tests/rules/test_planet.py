import random

import pytest
from mockito import verify

from pythonium import Galaxy, cfg
from pythonium.rules.planet import (
    PlanetBuildMinesRule,
    PlanetBuildShipRule,
    PlanetSetTaxesRule,
)
from tests.factories import (
    PlanetFactory,
    PositiveTransferVectorFactory,
    ShipTypeFactory,
)


class TestPlanetBuildMinesRule:
    @pytest.fixture(autouse=True)
    def setup(self, faker):
        self.mines_cost = PositiveTransferVectorFactory(clans=0)
        self.available_mines = faker.pyint(
            min_value=1, max_value=cfg.planet_max_mines
        )

    @pytest.fixture
    def planet(self):
        return PlanetFactory(
            pythonium=self.mines_cost.pythonium * self.available_mines,
            megacredits=self.mines_cost.megacredits * self.available_mines,
            clans=self.available_mines,
            mines=0,
            mine_cost=self.mines_cost,
        )

    def test_no_new_mines(self, galaxy, planet):
        """
        If `new_mines` are zero or planet can not build more mines, planet mines do not change
        """
        empty_rule = PlanetBuildMinesRule(new_mines=0, planet=planet)
        empty_rule.execute(galaxy)
        assert not planet.mines

    def test_new_mines(self, galaxy, planet):
        """
        Planet mines increases according `new_mines`
        """
        rule = PlanetBuildMinesRule(
            new_mines=self.available_mines, planet=planet
        )
        rule.execute(galaxy)
        assert rule.planet.mines == self.available_mines

    def test_mines_cost(self, galaxy, planet):
        """
        Planet resources decrease according `mine_cost`
        """
        initial_pythonium = planet.pythonium
        initial_megacredits = planet.megacredits
        rule = PlanetBuildMinesRule(
            new_mines=self.available_mines, planet=planet
        )
        rule.execute(galaxy)
        assert (
            planet.pythonium
            == initial_pythonium
            - self.mines_cost.pythonium * self.available_mines
        )
        assert (
            planet.megacredits
            == initial_megacredits
            - self.mines_cost.megacredits * self.available_mines
        )

    def test_build_with_available_resources(self, galaxy, planet):
        """
        Planet adjust `new_mines` according available resources
        """
        rule = PlanetBuildMinesRule(
            new_mines=self.available_mines * 2, planet=planet
        )
        rule.execute(galaxy)
        assert planet.mines == self.available_mines


class TestplanetBuildShipRule:
    @pytest.fixture(autouse=True)
    def setup(self, galaxy, random_planet):
        self.ship_type = ShipTypeFactory()
        random_planet.pythonium = self.ship_type.cost.pythonium
        random_planet.megacredits = self.ship_type.cost.megacredits
        self.planet = random_planet
        self.planet_without_resources = PlanetFactory(
            pythonium=0,
            megacredits=0,
        )

    @pytest.fixture
    def build_ship_rule(self, galaxy, when):
        rule = PlanetBuildShipRule(
            ship_type=self.ship_type, planet=self.planet
        )
        return rule

    @pytest.fixture
    def execute_build_ship_rule(self, galaxy, build_ship_rule):
        build_ship_rule.execute(galaxy)

    @pytest.fixture
    @pytest.mark.usefixtures("execute_build_ship_rule")
    def new_ship(self, galaxy):
        return galaxy.ships[-1]

    def test_cant_build_ship(self, galaxy, when):
        """
        If planet can not build the ship, this does nothing
        """
        when(Galaxy).add_ship(...)
        rule = PlanetBuildShipRule(
            ship_type=self.ship_type, planet=self.planet_without_resources
        )
        rule.execute(galaxy)
        verify(Galaxy, times=0).add_ship(...)

    def test_new_ship(self, galaxy, build_ship_rule, when):
        """
        Planet build the ship
        """
        when(Galaxy).add_ship(...)
        build_ship_rule.execute(galaxy)
        verify(Galaxy).add_ship(...)

    @pytest.mark.usefixtures("execute_build_ship_rule")
    def test_ship_type_cost(self):
        """
        Planet resources decrease according `ship_type` cost
        """
        assert self.planet.pythonium == 0
        assert self.planet.megacredits == 0

    @pytest.mark.usefixtures("execute_build_ship_rule")
    def test_ship_position_in_planet(self, galaxy, new_ship):
        """
        Ship is placed in the planet
        """
        assert new_ship.position == self.planet.position


class TestPlanetSetTaxesRule:
    @pytest.fixture(autouse=True)
    def setup(self, faker):
        self.current_taxes = faker.pyint(min_value=10, max_value=49)
        self.planet = PlanetFactory(taxes=self.current_taxes)

    def test_taxes_dont_change(self, galaxy):
        """
        If set taxes are equal to current taxes, does nothing
        """
        rule = PlanetSetTaxesRule(
            planet=self.planet, taxes=self.current_taxes
        )
        rule.execute(galaxy)
        assert self.planet.taxes == self.current_taxes

    def test_taxes(self, galaxy, faker):
        """
        If set taxes are equal to current taxes, does nothing
        """
        new_taxes = faker.pyint(min_value=50, max_value=100)
        rule = PlanetSetTaxesRule(planet=self.planet, taxes=new_taxes)
        rule.execute(galaxy)
        assert self.planet.taxes == new_taxes

    def test_taxes_lower_than_zero(self, galaxy, faker):
        """
        If set taxes are lower than zero, taxes are set to zero
        """
        new_taxes = faker.pyint(max_value=0)
        rule = PlanetSetTaxesRule(planet=self.planet, taxes=new_taxes)
        rule.execute(galaxy)
        assert self.planet.taxes == 0

    def test_taxes_grather_than_100(self, galaxy, faker):
        """
        If set taxes are grather than 100, taxes are set to 100
        """
        new_taxes = faker.pyint(min_value=100)
        rule = PlanetSetTaxesRule(planet=self.planet, taxes=new_taxes)
        rule.execute(galaxy)
        assert self.planet.taxes == 100
