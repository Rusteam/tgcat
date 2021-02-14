cmake_minimum_required(VERSION 3.1.0)

project(OpenNMTTokenizer)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

set(INCLUDE_DIRECTORIES
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${PROJECT_BINARY_DIR}
  )

set(PUBLIC_HEADERS
  include/onmt/Alphabet.h
  include/onmt/AnnotatedToken.h
  include/onmt/BPE.h
  include/onmt/BPELearner.h
  include/onmt/CaseModifier.h
  include/onmt/ITokenizer.h
  include/onmt/SpaceTokenizer.h
  include/onmt/SubwordEncoder.h
  include/onmt/SubwordLearner.h
  include/onmt/Tokenizer.h
  )

set(SOURCES
  src/Alphabet.cc
  src/AnnotatedToken.cc
  src/BPE.cc
  src/BPELearner.cc
  src/CaseModifier.cc
  src/ITokenizer.cc
  src/SpaceTokenizer.cc
  src/SubwordEncoder.cc
  src/SubwordLearner.cc
  src/Tokenizer.cc
  src/unicode/Unicode.cc
  )

list(APPEND LINK_LIBRARIES "")
list(APPEND SOURCES src/unicode/Data.cc)

find_library(SP_LIBRARY NAMES sentencepiece)
find_path(SP_INCLUDE_DIR NAMES sentencepiece_processor.h)
if(NOT SP_LIBRARY OR NOT SP_INCLUDE_DIR)
    message(WARNING "sentencepiece not found; will not be supported")
else()
    message(STATUS "Found sentencepiece: ${SP_LIBRARY}")
    add_definitions(-DWITH_SP)
    list(APPEND PUBLIC_HEADERS include/onmt/SentencePiece.h)
    list(APPEND SOURCES src/SentencePiece.cc)
    list(APPEND INCLUDE_DIRECTORIES ${SP_INCLUDE_DIR})
    list(APPEND LINK_LIBRARIES ${SP_LIBRARY})
    file(STRINGS ${SP_INCLUDE_DIR}/sentencepiece_processor.h HAS_SAMPLE_ENCODE REGEX "SampleEncode")
    if(HAS_SAMPLE_ENCODE)
        add_definitions(-DSP_HAS_SAMPLE_ENCODE)
    endif()
    file(STRINGS ${SP_INCLUDE_DIR}/sentencepiece_processor.h HAS_VOCAB_RESTRICTION REGEX "SetVocabulary")
    if(HAS_VOCAB_RESTRICTION)
        add_definitions(-DSP_HAS_VOCAB_RESTRICTION)
    endif()
endif()

add_library(${PROJECT_NAME} STATIC ${SOURCES})
include(GNUInstallDirs)
include(GenerateExportHeader)
string(TOLOWER ${PROJECT_NAME} PROJECT_NAME_LOWER)
generate_export_header(${PROJECT_NAME} EXPORT_FILE_NAME ${PROJECT_BINARY_DIR}/onmt/${PROJECT_NAME_LOWER}_export.h)
target_include_directories(${PROJECT_NAME} PUBLIC ${INCLUDE_DIRECTORIES})
target_link_libraries(${PROJECT_NAME} ${LINK_LIBRARIES})
