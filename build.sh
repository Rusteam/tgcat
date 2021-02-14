#!/bin/bash

docker stop tgcat-tester

docker build -t tgcat:latest ./src

if [ $? -ne 0 ]
then
  echo "ERROR: docker build failed"
  exit 1
fi

cp resources/external/lid.176.bin resources/lid.176.bin
cp resources/trained/tgcat/*.pt resources/
docker run --rm --name tgcat-tester \
               -v $(pwd)/data:/app/tester/data \
               -v $(pwd)/resources:/app/tester/resources \
               tgcat:latest


docker run --rm --name tgcat-tester \
               -v $(pwd)/data:/app/tester/data \
               -v $(pwd)/models:/app/tester/models \
               tgcat:latest zip -r data/submission.zip libtgcat.so models/lang_detect_v10.ftz models/*.pt
