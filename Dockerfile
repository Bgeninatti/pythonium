# `python-base` sets up all our shared environment variables
FROM python:3.9 as python-base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.1.12 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # paths
    # this is where our requirements + virtual environment will live
    PYTHONIUM_PATH="/opt/pythonium"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYTHONIUM_PATH

COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry export --without-hashes | pip install -r /dev/stdin

COPY . .


# `development` image is used during development / testing
FROM builder-base as development

WORKDIR $PYTHONIUM_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYTHONIUM_PATH $PYTHONIUM_PATH

# quicker install as runtime deps are already installed
RUN poetry export --without-hashes --dev | pip install -r /dev/stdin

RUN pip install --no-dependencies --editable .


# FROM builder-base as docs
# 
# WORKDIR $PYTHONIUM_PATH
# 
# RUN poetry export --without-hashes --extras docs | pip install -r /dev/stdin


# `production` image used for runtime
FROM builder-base as production

WORKDIR $PYTHONIUM_PATH

RUN pip install --no-dependencies .

CMD ["pythonium"]
