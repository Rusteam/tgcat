#!/bin/bash

mkdir -p submission/src
mkdir -p submission/resources

cp -R src/inference/libtorch src/inference/src src/inference/thirdparty src/inference/CMakeLists.txt submission/src
cp -R resources submission
cp src/deb_packages.txt submission
cp src/inference/build/libtglang.so submission

zip -r submission.zip submission