default:
    just --list

test:
    poetry run pytest -s
