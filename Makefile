ifeq ($(DJANGO_SETTINGS),)
    SETTINGS :=
else
    SETTINGS := --settings=$(DJANGO_SETTINGS)
endif

.PHONY: testy
testy:
	echo "$(SETTINGS)"


.PHONY: console migrate migrations server

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

console:
	poetry run python manage.py shell $(SETTINGS)

migrate:
	poetry run python manage.py migrate $(SETTINGS)

migrations:
	poetry run python manage.py makemigrations $(SETTINGS)

server:
	poetry run python manage.py runserver $(SETTINGS)


# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality pylint black flake8 isort
quality:
	poetry run black --check apps
	poetry run isort --check --profile black apps
	poetry run flake8 apps --count --show-source --statistics

pylint:
	poetry run pylint apps

black:
	poetry run black apps

flake8:
	poetry run flake8 apps

isort:
	poetry run isort --profile black apps

# Docker shell.
# =============================================================================

.PHONY: shell_on_postgres_container

shell_on_postgres_container:
	docker exec -ti postgres /bin/bash


# Postgres CLI.
# =============================================================================

.PHONY: psql psql_root

# Connect to postgres client as user.
psql:
	docker exec -ti -e PGPASSWORD=password postgres psql -U postgres

# Connect to postgres client as the `root` user.
psql_root:
	docker exec -ti -e PGPASSWORD=password postgres psql -U postgres


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
