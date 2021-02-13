#/bin/bash
set -e
# build and run test container
docker build -t clean_buster src/ -f ./src/TestDockerfile
docker run --rm -it \
          -v $(pwd)/data:/data \
          --network none \
          clean_buster bash