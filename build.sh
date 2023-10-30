#!/bin/bash

set -e

export DOCKER_DEFAULT_PLATFORM=linux/amd64

docker build -t tglang:latest ./src

if [ $? -ne 0 ]
then
  echo "ERROR: docker build failed"
  exit 1
fi

mkdir -p resources
cp src/inference/libtorch/lib/libtorch.so \
    src/inference/libtorch/lib/libtorch_cpu.so \
    src/inference/libtorch/lib/libgomp-52f2fd74.so.1 \
    src/inference/libtorch/lib/libc10.so resources/

cp models/trained/tglang_l.pt resources/tglang.pt

docker run --rm --name tglang-tester \
               -v $(pwd)/resources:/app/inference/resources \
               tglang:latest
