cmake_minimum_required (VERSION 2.6)

project (Tool)

set(CMAKE_BUILD_TYPE DEBUG)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()

message("CMAKE_BUILD_TYPE = ${CMAKE_BUILD_TYPE}")
IF(CMAKE_BUILD_TYPE MATCHES Debug)
  set(CMAKE_CXX_FLAGS_DEBUG "-O0")
  message("Debug build.")
ELSEIF(CMAKE_BUILD_TYPE MATCHES Release)
  set(CMAKE_CXX_FLAGS_RELEASE "-O2 -finline-limit=1000 -DNDEBUG")
  message("Release build.")
ELSE()
  message("Some other build type.")
ENDIF()

message(STATUS "PROJECT_BINARY_DIR="  ${PROJECT_BINARY_DIR} )
message(STATUS "PROJECT_SOURCE_DIR="  ${PROJECT_SOURCE_DIR} )
message(STATUS "CMAKE_SOURCE_DIR="  ${CMAKE_SOURCE_DIR} )
message(STATUS "CMAKE_MODULE_PATH="  ${CMAKE_MODULE_PATH} )

set(CXX_FLAGS
 -g
 -DCHECK_PTHREAD_RETURN_VALUE
 -D_FILE_OFFSET_BITS=64
 -Wall
 -Wextra
 -Wsign-compare
# -Werror
# -Wconversion
-Wunused-variable
 -Wno-unused-parameter
# -Wold-style-cast
 -Woverloaded-virtual
 -Wpointer-arith
# -Wshadow
 -Wwrite-strings
 -march=native
 # -MMD
 -std=c++0x
 -rdynamic
 -pthread
# -fPIC
 )

if(CMAKE_BUILD_BITS EQUAL 32)
  list(APPEND CXX_FLAGS "-m32")
endif()

string(REPLACE ";" " " CMAKE_CXX_FLAGS "${CXX_FLAGS}")

set(CMAKE_CXX_COMPILER "g++")

#set output files path
#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
#set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

#set source files
set(SRC_LIST src/main.cpp)

#set inlude libs
include_directories(lib)
file(GLOB LIB_TIMESTAMP lib/*.cpp)
add_library(timestamp STATIC ${LIB_TIMESTAMP})

#compiled
add_executable(test ${SRC_LIST})
#link
target_link_libraries(test timestamp)

