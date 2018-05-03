cmake_minimum_required (VERSION 2.6)

project (SUDOKU)

set(SRC_LIST sudoku_x.cpp)
#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/bin)
#set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/lib)

#include_directories(lib)

#file(GLOB LIB_HELLO lib/*.cpp)
#add_library(hello STATIC ${LIB_HELLO})

add_executable(sudoku ${SRC_LIST})

#target_link_libraries(test hello)

