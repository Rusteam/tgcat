#!/bin/bash

mkdir /src
cp -R libtorch src thirdparty CMakeLists.txt /src
cp /deb_packages.txt .
cp /app/inference/build/libtgcat.so .
zip -r resources/submission.zip libtgcat.so deb_packages.txt resources/ /src