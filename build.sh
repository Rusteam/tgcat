#!/bin/bash

docker stop tgcat-tester

docker build -t tgcat:latest ./src

if [ $? -ne 0 ]
then
  echo "ERROR: docker build failed"
  exit 1
fi

cp models/external/lid.176.bin models/lang_detect_v10.ftz
cp models/trained/tgcat/*.pt models/
docker run --rm --name tgcat-tester \
               -v $(pwd)/data:/app/tester/data \
               -v $(pwd)/models:/app/tester/models \
               tgcat:latest
