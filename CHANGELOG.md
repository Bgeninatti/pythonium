## 0.2.0b1 (2021-06-19)

## 0.2.0b0 (2021-06-19)

### Fix

- fixes version references
- **ClassicMode**: get_galaxy_for_player copies turn from game galaxy (#36)
- Removes obsolete bots (#35)
- **reports**: fixes report after uuid implementation (#33)
- **bin**: fixes pythonium executable

### Refactor

- **repr**: a more pythonic repr
- **galaxy**: make the turn number a galaxy attribute (#20)
- **loggger**: refactor logger to be global variable in files. Uses dictconfig (#19)
- **ship**: make speed a Ship and shipType attribute (#18)
- Remove old pyproject.toml

### Feat

- **debugger**: adds debugger.terminate to exit form ipdb infinite loop
- human redeable __repr__ for Galaxy, Planet and Ship (#32)
- Adds automatic version detection patterns
- adds pyproject.toml
- Makes the repo commitizen-friendly

## 0.2.0a0 (2020-11-24)

### Feat

- Adds automatic version detection patterns
- adds pyproject.toml
- Makes the repo commitizen-friendly

### Refactor

- Remove old pyproject.toml

## 0.1.0 (2020-11-24)

### Feat
- Implements ``Planet`` class. Represents a planet in the galaxy that can or can not be owned by a player.
- Implements ``Ship`` class. Represents a ship that is owned by a player and can move along space and planets and transfer resources.
- Implements ``Galaxy`` class. Represents the map of the game, contains all the known states of things (planets, ships, and explosions).
- Implements ``AbstractPlayer`` class. Is the class where all the players inherit from.
- Implements ``Game`` class. The main iterator of the game. Where the magic happens.
- Implements ``GameMode`` class. The interface that defines the game rules such as initial conditions for planets, initial conditions for players, game-ended logic.
- Implements ``ClassicMode`` game mode. The default game mode:
    * 500 planets randomly located,
    * 1M of total pythonium in the galaxy,
    * 10% of pythonium is in planets surface,
    * Avg concentration: 50%,
    * Avg temperature: 50º,
    * Player starting ships: 2 carriers,
    * Player starting planets: 1 planet (a.k.a. homeworld),
    * Player starting resources in homeworld: 10k clans, 2k pythonium, 5k megacredits,
    * The Maximum number of turns: 150 turns.
- Implements ``bot.standard_player`` bot. Explore and colonize nearby planets randomly. Builds 50% of warships and 50% of carriers.
- Implements ``bot.pacific_player`` bot. Same as ``bot.standard_player``, but do not build warships. Carriers only.
- Implements ``bot.random_walk`` bot. Just moves the available ships randomly.
- Implements helper classes:
    * ``Explosion`` class. Represent the explosion of a ship and same some information about the conflict.
    * ``Transfer`` class. Represent a transfer between ships and planets, planets and ships or planets, and the game itself (a.k.a. cost vectors, such as ships or structures costs).
- Implements ``MetricsCollector`` class. Builds a report with game metrics based on the log file.
- Implements ``GifRenderer`` class. Renders a gif with the state of the game turn by turn.
