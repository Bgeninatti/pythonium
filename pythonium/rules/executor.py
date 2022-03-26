import logging
from typing import List

import attr

from pythonium import Galaxy
from pythonium.rules.core import GalaxyRule, Rule
from pythonium.rules.order import PlanetOrder, ShipOrder

logger = logging.getLogger("game")


@attr.s
class OrdersExecutor:
    rules: List[Rule] = attr.ib()
    galaxy: Galaxy = attr.ib()

    def __call__(self, orders):
        for rule_class in self.rules:
            if issubclass(rule_class, GalaxyRule):
                rule = rule_class(self.galaxy)
                rule.execute()
            else:
                rule_orders = orders.get(rule_class.name, [])
                self.execute_rule(rule_class, rule_orders)

    def execute_rule(self, rule_class, orders):
        logger.info(
            "Executing rule", extra={"rule": rule_class, "orders": len(orders)}
        )
        for order in orders:
            kwargs = order.kwargs
            if isinstance(order, ShipOrder):
                obj = self.galaxy.search_ship(order.id)
            elif isinstance(order, PlanetOrder):
                obj = self.galaxy.search_planet(order.id)
            else:
                logger.warning(
                    "Unknown params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": order.player,
                        "kwargs": kwargs,
                    },
                )
                continue
            if not obj:
                logger.warning(
                    "Object not found",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": order.name,
                        "kwargs": kwargs,
                        "name": order.name,
                    },
                )
                continue

            logger.info(
                "Running action for player",
                extra={
                    "turn": self.galaxy.turn,
                    "player": obj.player,
                    "action": order.name,
                    "obj": type(obj),
                    "kwargs": kwargs,
                },
            )
            rule = rule_class(obj, **kwargs)
            try:
                rule.execute(self.galaxy)
            except Exception as e:
                logger.error(
                    "Unexpected error running player params",
                    extra={
                        "turn": self.galaxy.turn,
                        "player": obj.player,
                        "action": order.name,
                        "obj": type(obj),
                        "kwargs": kwargs,
                        "reason": e,
                    },
                )
