#!/bin/bash -e
docker stack rm agents

docker build -t ai-agent .

docker stack deploy -c compose.yml agents