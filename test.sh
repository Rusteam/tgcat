#!/bin/bash
set -e

cp resources/submission.zip src/

export DOCKER_DEFAULT_PLATFORM=linux/amd64

docker build -t clean_buster src/ -f ./src/Test.dockerfile

docker run --rm -it \
          -v $(pwd)/data:/app/data \
          --network none \
          clean_buster