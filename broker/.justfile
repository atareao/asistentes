default:
    just --list

test:
    poetry run pytest -s --verbose

run:
    poetry run python broker/main.py
