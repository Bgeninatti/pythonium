from faker import Faker

from pythonium import Planet


class PlanetFactory:

    faker: Faker

    def __call__(
        self,
        faker,
    ):
        return Planet(
            pid=self.faker.pyint(),
            position=(self.faker.pyint(), self.faker.pyint()),
            temperature=self.faker.pyint(),
            underground_pythonium=self.faker.pyint(),
            concentration=self.faker.pyfloat(),
            pythonium=self.faker.pyint(),
        )
