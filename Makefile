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
	@pip install -r requirements.txt; apt update; apt-get install -y gettext

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

