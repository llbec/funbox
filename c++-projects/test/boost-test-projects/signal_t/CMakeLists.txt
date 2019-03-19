cmake_minimum_required (VERSION 2.6)

project (TEST)

set(SRC_LIST signal2_test.cpp)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/lib)

#
# cmake -DCMAKE_BUILD_TYPE=Debug ..
# cmake -DCMAKE_BUILD_TYPE=Release ..
# 
# default: Release
#

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

message("CMAKE_BUILD_TYPE = ${CMAKE_BUILD_TYPE}")
IF(CMAKE_BUILD_TYPE MATCHES Debug)
  message("Debug build.")
  set(CMAKE_CXX_FLAGS "-g -O0 -Wall")
ELSEIF(CMAKE_BUILD_TYPE MATCHES Release)
  message("Release build.")
  set(CMAKE_CXX_FLAGS "-O2 -Wall")
ELSE()
  message("Some other build type.")
ENDIF()

set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_C_COMPILER "gcc")
set(CMAKE_CXX_COMPILER_ARG1 "-std=c++0x ")

#set libs
#find_package(Boost  COMPONENTS thread filesystem system program_options REQUIRED)
#if(NOT Boost_FOUND)
#  message(FATAL_ERROR "Boost not found!")
#endif(NOT Boost_FOUND)

#include_directories(${Boost_INCLUDE_DIRS})

#file(GLOB LIB_HELLO lib/*.cpp)
#add_library(hello STATIC ${LIB_HELLO})

#set(THIRD_LIBRARIES ${Boost_LIBRARIES})

add_executable(test ${SRC_LIST})

#target_link_libraries(test  ${THIRD_LIBRARIES})

