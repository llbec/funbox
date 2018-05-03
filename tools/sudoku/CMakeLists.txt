cmake_minimum_required (VERSION 2.6)

project (SUDOKU)

set(SRC_LIST test.cpp)
#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/bin)
#set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/lib)

#include_directories(lib)

file(GLOB LIB_SUDOKU lib/*.cpp)
add_library(sudoku STATIC ${LIB_SUDOKU})

add_executable(test ${SRC_LIST})

target_link_libraries(test sudoku)

