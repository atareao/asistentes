user    := "atareao"
name    := "brokerbot"
version := `git tag -l  | tail -n1`

default:
    just --list

test:
    poetry run pytest -s --verbose

run:
    poetry run python broker/main.py

build:
    echo {{version}}
    echo {{name}}
    docker build -t {{user}}/{{name}}:{{version}} \
                 -t {{user}}/{{name}}:latest \
                 .

push:
    docker push {{user}}/{{name}}:{{version}}
    docker push {{user}}/{{name}}:latest


start:
    docker run --init \
               --rm \
               --detach \
               --name {{name}} \
               --env-file .env \
               {{user}}/{{name}}:latest
    docker logs {{name}} -f

stop:
    docker stop {{name}}
