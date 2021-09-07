SHELL=/bin/bash
.PHONY: all help translate install make_migrations migrate test run_server check_style
# target: all - Setup of project.
all: install migrate compile_messages

# target: help - Display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: make_messages - Make messages for django translate
make_messages:
	@python3 manage.py makemessages -l fa -i 'venv'

# target: compile_messages - Compile messages for django translate
compile_messages:
	@python3 manage.py compilemessages

# target: install - Install requirements
install:
	@apt-get update; apt-get install libpq-dev; pip install -r requirements.txt; apt-get install -y gettext

# target: make_migrations - Make migrations
make_migrations:
	@python3 manage.py makemigrations

# target: migrate - Migrate database changes
migrate:
	@python3 manage.py migrate

# target: run_server - Run server of project
run_server: compile_messages migrate
	@python3 manage.py runserver 0.0.0.0:8000

# target: test - Check tests
test: compile_messages migrate
	@python3 manage.py test

# target: check_style - Style checking of project
check_style:
	@pycodestyle . --exclude="venv/","*/migrations" --max-line-length=120

# target: COVERAGE - Calculates coverage
coverage: compile_messages migrate
	@coverage run --source='.' --omit="*venv/*","*/migrations*"  manage.py test

# target: COVERAGE_REPORT - report coverage data
coverage_report:
	@coverage report

# If the first argument is "docker-compose"...
ifeq (docker-compose, $(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "docker-compose"
  COMPOSE_TYPE := $(word 2,$(MAKECMDGOALS))
  COMPOSE_ARGS := $(wordlist 3,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(COMPOSE_TYPE):;@:)
  $(eval $(COMPOSE_ARGS):;@:)
endif

# target: docker-compose
docker-compose:
ifeq ($(COMPOSE_TYPE),$(filter $(COMPOSE_TYPE), prod dev))
	@echo docker-compose -f docker-compose.yml -f docker-compose.$(COMPOSE_TYPE).yml $(subst *,=,$(COMPOSE_ARGS))
	@docker-compose -f docker-compose.yml -f docker-compose.$(COMPOSE_TYPE).yml $(subst *,=,$(COMPOSE_ARGS))
else
	@echo wrong compose type: $(COMPOSE_TYPE)
	@echo use dev or prod instead
endif
