FROM debian:buster

RUN apt-get clean && apt-get update
RUN apt-get install -y cmake gcc g++ libboost-all-dev build-essential libjsoncpp-dev uuid-dev protobuf-compiler libprotobuf-dev
RUN apt-get install -y zip

RUN mkdir app
COPY ./inference /app/inference
COPY ./tester /app/tester

RUN cd /app/inference && mkdir build && cd build && Torch_DIR="../libtorch" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4
WORKDIR /app/inference/build
# RUN cp /app/inference/build/libtgcat.so /app/tester

# RUN cd /app/tester && mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4
# RUN cp /app/tester/build/tgcat-tester /app/tester
# WORKDIR /app/tester

# COPY run_cmd.sh ./
# RUN chmod 777 run_cmd.sh
# CMD ["./run_cmd.sh"]