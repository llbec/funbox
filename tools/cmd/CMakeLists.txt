cmake_minimum_required (VERSION 2.6)

project (CMDTOOL)

###################################### Options ######################################
message("") # empty line
message("------------------------------- Options -------------------------------")

#
# Build Type: -DCMAKE_BUILD_TYPE=Debug|Release
# Default: Debug
#
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
message("-- Build Type: ${CMAKE_BUILD_TYPE} (-DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE})")
IF(CMAKE_BUILD_TYPE MATCHES Debug)
  set(CMAKE_CXX_FLAGS "-g -O0 -Wall")
  message("-- Debug build.")
ELSEIF(CMAKE_BUILD_TYPE MATCHES Release)
  set(CMAKE_CXX_FLAGS "-g -O2 -Wall")
  message("-- Release build.")
ELSE()
  set(CMAKE_CXX_FLAGS "-g -Wall")
  message("-- Some other build type.")
ENDIF()

# compiler options
set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_C_COMPILER "gcc")
add_definitions(
    "-std=c++0x"
)

#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/bin)                                                                                                                                                                                                                  
#set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/lib)

###################################### Libs ######################################
message("") # empty line
message("------------------------------- Libs -------------------------------")

#file(GLOB LIB_SUDOKU lib/*.cpp)
#add_library(sudoku ${LIB_SUDOKU})

###################################### Targets ######################################
message("") # empty line
message("------------------------------- Targets -------------------------------")
include_directories(lib)
set(SRC_LIST *.cpp)
add_executable(cmdtool ${SRC_LIST})
#target_link_libraries(test_sudoku sudoku)

