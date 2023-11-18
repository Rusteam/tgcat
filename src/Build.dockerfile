FROM debian:buster

RUN apt-get clean && apt-get update
COPY deb_packages.txt .
RUN apt-get install -y $(xargs -a deb_packages.txt)
RUN apt-get install -y zip

WORKDIR /app
COPY ./inference /app/inference

WORKDIR /app/inference/build
RUN Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make -j4

# create submission
WORKDIR /submission
RUN mv /app/inference/build/libtglang.so .
COPY ./inference ./src
COPY deb_packages.txt .
#TODO COPY train files
#TODO COPY readme
WORKDIR /submission/resources
COPY ./inference/libtorch/lib/libtorch.so .
COPY ./inference/libtorch/lib/libtorch_cpu.so .
COPY ./inference/libtorch/lib/libgomp-52f2fd74.so.1 .
COPY ./inference/libtorch/lib/libc10.so .
