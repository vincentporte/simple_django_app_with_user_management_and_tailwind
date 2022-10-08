ifeq ($(USE_POETRY),1)
	EXEC_CMD := poetry run
else
	EXEC_CMD :=
endif

ifeq ($(DJANGO_SETTINGS),)
    SETTINGS :=
else
    SETTINGS := --settings=$(DJANGO_SETTINGS)
endif

.PHONY: console migrate migrations server requirements

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

console:
	$(EXEC_CMD) python manage.py shell $(SETTINGS)

migrate:
	$(EXEC_CMD) python manage.py migrate $(SETTINGS)

migrations:
	$(EXEC_CMD) python manage.py makemigrations $(SETTINGS)

server:
	$(EXEC_CMD) python manage.py runserver $(SETTINGS)

requirements:
	$(EXEC_CMD) poe export; $(EXEC_CMD) poe export_dev

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality pylint black flake8 isort
quality:
	$(EXEC_CMD) black --check apps
	$(EXEC_CMD) isort --check --profile black apps
	$(EXEC_CMD) flake8 apps --count --show-source --statistics

pylint:
	$(EXEC_CMD) pylint apps

black:
	$(EXEC_CMD) black apps

flake8:
	$(EXEC_CMD) flake8 apps

isort:
	$(EXEC_CMD) isort --profile black apps

# Docker shell.
# =============================================================================

.PHONY: shell_on_postgres_container

shell_on_postgres_container:
	docker exec -ti postgres /bin/bash


# Postgres CLI.
# =============================================================================

.PHONY: psql psql_root

# Connect to the `postgres` container as the POSTGRES_USER user.
psql:
	docker exec -ti -e PGPASSWORD=$(POSTGRES_PASSWORD) postgres psql -U $(POSTGRES_USER)


# TESTING
# ~~~~~~~
# The following rules can be used to trigger tests execution and produce coverage reports.
# --------------------------------------------------------------------------------------------------

.PHONY: tests
## Run the Python test suite.
tests:
	poetry run py.test

.PHONY: coverage
## Collects code coverage data.
coverage:
	poetry run py.test --cov-report term-missing --cov $(PROJECT_PACKAGE)

.PHONY: spec
## Run the tests in "spec" mode.
spec:
	poetry run py.test --spec -p no:sugar
