FROM debian:buster

RUN apt-get clean && apt-get update
COPY deb_packages.txt .
RUN apt-get install -y $(xargs -a deb_packages.txt)
RUN apt-get install -y zip

WORKDIR /app
COPY ./libtglang ./libtglang
COPY ./libtorch ./libtglang/libtorch

WORKDIR /app/libtglang/build
RUN Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make -j4

# create submission
WORKDIR /submission
RUN mv /app/libtglang/build/libtglang.so .
COPY ./libtglang ./src
#TODO COPY train files
#TODO COPY readme
#TODO COPY resources
COPY deb_packages.txt .
