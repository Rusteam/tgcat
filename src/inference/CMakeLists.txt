cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

project(tglang)

add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")
add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
SET (CMAKE_SHARED_LINKER_FLAGS
        "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-rpath,'$ORIGIN/resources'" )
set(TGNEWS_CXX_FLAGS "-pthread;-Wall;-Wextra;-Wno-sign-compare;-fno-omit-frame-pointer;-fPIC")
set(TGNEWS_CXX_DEBUG_FLAGS "-g;-O2;-fsanitize=address")
set(TGNEWS_LNK_DEBUG_FLAGS "-fsanitize=address")
set(TGNEWS_CXX_RELEASE_FLAGS "-funroll-loops;-Ofast;-march=x86-64;-mtune=generic;-msse3;-mssse3;-msse4;-msse4.1;-msse4.2")

set(BUILD_TESTING 0)
add_subdirectory(thirdparty/fasttext)
add_subdirectory(thirdparty/eigen)

set(LIB_ONLY True)
add_subdirectory(thirdparty/onmt)
unset(LIB_ONLY)

unset(BUILD_TESTING)

find_package(Boost COMPONENTS program_options locale regex filesystem unit_test_framework REQUIRED)
include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIR})

find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

find_package(Protobuf REQUIRED)

set(SOURCE_FILES
        src/annotator.cpp
        src/json.cpp
        src/json-builder.cpp

        src/thread_pool.cpp
        src/util.cpp
        src/tglang.cpp
        )

file(GLOB PROTO_FILES "${CMAKE_CURRENT_SOURCE_DIR}/src/proto/*.proto")

set(LIB_LIST
        ${Boost_LIBRARIES}
        ${Protobuf_LIBRARIES}
        ${TORCH_LIBRARIES}
        fasttext-static
        OpenNMTTokenizer
        eigen
        )

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/thirdparty")

target_include_directories(fasttext-static SYSTEM PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/fasttext/src")
target_include_directories(OpenNMTTokenizer SYSTEM PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/onmt/include")

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILES})
include_directories(${CMAKE_BINARY_DIR})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES} ${PROTO_SRCS} src/tglang.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${LIB_LIST})
target_compile_options(${PROJECT_NAME} PUBLIC "${TGNEWS_CXX_FLAGS}")
target_compile_options(${PROJECT_NAME} PUBLIC "$<$<CONFIG:Debug>:${TGNEWS_CXX_DEBUG_FLAGS}>")
target_link_libraries(${PROJECT_NAME} PUBLIC "$<$<CONFIG:Debug>:${TGNEWS_LNK_DEBUG_FLAGS}>")
target_compile_options(${PROJECT_NAME} PUBLIC "$<$<CONFIG:Release>:${TGNEWS_CXX_RELEASE_FLAGS}>")

