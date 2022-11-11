ifeq ($(USE_POETRY),1)
	EXEC_CMD := poetry run
else
	EXEC_CMD :=
endif


.PHONY: console migrate migrations server dependencies

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

console:
	$(EXEC_CMD) python manage.py shell_plus

migrate:
	$(EXEC_CMD) python manage.py migrate

migrations:
	$(EXEC_CMD) python manage.py makemigrations

server:
	$(EXEC_CMD) python manage.py runserver

dependencies:
	poetry lock; poetry run poe export; poetry run poe export_dev

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality fix pylint
quality:
	$(EXEC_CMD) black --check apps
	$(EXEC_CMD) isort --check apps
	$(EXEC_CMD) flake8 apps --count --show-source --statistics
	$(EXEC_CMD) djhtml --check $(shell find apps/templates -name "*.html")

fix:
	$(EXEC_CMD) black apps
	$(EXEC_CMD) isort apps
	$(EXEC_CMD) flake8 apps
	$(EXEC_CMD) djhtml --in-place $(shell find apps/templates -name "*.html")

pylint:
	$(EXEC_CMD) pylint apps

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

# SETUP
# ~~~~~
.PHONY: createsuperuser
createsuperuser:
	poetry run python manage.py createsuperuser
