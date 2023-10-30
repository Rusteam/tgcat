cd src/inference/build/
Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4
cd ../../../
cp src/inference/build/libtglang.so src/tester
cd src/tester/build/
Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4
cd ../../../
cp src/tester/build/tglang-tester .