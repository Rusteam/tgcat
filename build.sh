#!/bin/bash

docker stop tgcat-tester

docker build -t tgcat:latest ./src

if [ $? -ne 0 ]
then
  echo "ERROR: docker build failed"
  exit 1
fi

cp models/external/lid.176.bin resources/
cp models/trained/tgcat/*.pt resources/
cp src/inference/libtorch/lib/libtorch.so src/inference/libtorch/lib/libgomp-75eea7e8.so.1 src/inference/libtorch/lib/libc10.so resources/
#docker run --rm --name tgcat-tester \
#               -v $(pwd)/data:/app/tester/data \
#               -v $(pwd)/resources:/app/tester/resources \
#               tgcat:latest


docker run --rm --name tgcat-tester \
               -v $(pwd)/resources:/app/inference/build/resources \
               tgcat:latest zip -r resources/submission.zip libtgcat.so resources/
