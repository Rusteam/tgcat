#!/bin/bash

mkdir /src
cp -R libtorch src thirdparty CMakeLists.txt /src
cp /deb_packages.txt .
cp /app/inference/build/libtglang.so .
zip -f -r resources/submission.zip libtglang.so deb_packages.txt resources/ /src