# 1. Build, run and testing
## 1.1 Prerequisites
### 1.1.1 Submodules
```bash
git submodule add https://github.com/IlyaGusev/Tokenizer src/inference/thirdparty/onmt
git submodule update --init --recursive
cp src/inference/thirdparty/CMakeLists.txt src/inference/thirdparty/onmt/CMakeLists.txt 
```
### 1.1.2 Libtorch
```
cd src/inference
wget https://download.pytorch.org/libtorch/cpu/libtorch-cxx11-abi-shared-with-deps-2.1.0%2Bcpu.zip
unzip libtorch-cxx11-abi-shared-with-deps-2.1.0+cpu.zip
```
## 1.2 Build
### 1.2.1 Tglang
```bash
cd src/inference && mkdir build && cd build && Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4
```
### 1.2.2 Tgtester
```
cp src/inference/build/libtglang.so src/tester
cd src/tester && mkdir build && cd build && Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4
cp src/tester/build/tglang-tester .
```
### 1.2.3 Run tester
Put tglang.pt to /resources folder

```
./tglang-tester test.sh
```

## 2 Docker
### 2.1 Build
Complete Prerequisites before building

```bash
make build
```
build buster image with libtgcat and run inference, compare to python outputs