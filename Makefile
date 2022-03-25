help:
	@echo "play             -- Open shell to play"
	@echo "test             -- Run tests"
	@echo "devshell         -- Open shell with development dependencies"


play:
	docker build --progress plain --target production --tag pythonium:latest .; \
	docker run --rm -ti pythonium pythonium

devshell:
	docker build --progress plain --target development --tag pythonium:development .; \
	docker run --rm -ti -v $(pwd):/opt/pythonium pythonium:development bash

test:
	docker build --progress plain --target development --tag pythonium:development .; \
	docker run --rm -ti pythonium:development pytest

clean:
	docker rmi pythonium:latest; \
	docker rmi pythonium:development;


.PHONY: help clean play test devshell
