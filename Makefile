COMPOSE = docker compose -f docker-compose.yml
DEV_COMPOSE = $(COMPOSE) -f docker-compose.develop.yml
ARGS = $(filter-out $@,$(MAKECMDGOALS))

help:
	@echo "play             -- Open shell to play"
	@echo "test             -- Run tests"
	@echo "devshell         -- Open shell with development dependencies"

play:
	$(COMPOSE) run --rm pserver /bin/bash

devshell:
	$(DEV_COMPOSE) run --rm pserver /bin/bash

test:
	$(DEV_COMPOSE) run --rm pserver pytest $(ARGS)

check-imports:
	$(DEV_COMPOSE) run --rm pserver isort **/*.py

check-style:
	$(DEV_COMPOSE) run --rm pserver black **/*.py

build:
	$(COMPOSE) build

build-dev:
	$(DEV_COMPOSE) build

.PHONY: help play test devshell
