FROM debian:buster

RUN apt-get clean && apt-get update
COPY deb_packages.txt .
RUN apt-get install -y $(xargs -a deb_packages.txt)
RUN apt-get install -y zip

RUN mkdir app
COPY ./inference /app/inference
COPY ./tester /app/tester

RUN cd /app/inference && mkdir build && cd build && Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4

WORKDIR /app/inference
COPY zip_cmd.sh ./
RUN chmod 777 zip_cmd.sh
CMD ["./zip_cmd.sh"]