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

set(BUILD_TESTING 0)

set(LIB_ONLY True)
add_subdirectory(thirdparty/onmt)
unset(LIB_ONLY)

unset(BUILD_TESTING)


find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

set(SOURCE_FILES
        src/annotator.cpp
        src/tglang.cpp
        )

set(LIB_LIST
        ${TORCH_LIBRARIES}
        OpenNMTTokenizer
        )

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/thirdparty")

target_include_directories(OpenNMTTokenizer SYSTEM PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/onmt/include")

include_directories(${CMAKE_BINARY_DIR})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES} src/tglang.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${LIB_LIST})

target_compile_options(tglang PRIVATE -g)