cmake_minimum_required (VERSION 2.6)

project (Test)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")

#
# System Type:
#
MESSAGE(STATUS "Current platform: ${CMAKE_SYSTEM_NAME}")

#
# Build Type: -DCMAKE_BUILD_TYPE=Debug|Release
# Default: Release
#
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
message("-- Build Type: ${CMAKE_BUILD_TYPE} (-DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE})")
IF(CMAKE_BUILD_TYPE MATCHES Debug)
  set(CMAKE_CXX_FLAGS "-g -O0 -Wall")
ELSEIF(CMAKE_BUILD_TYPE MATCHES Release)
  set(CMAKE_CXX_FLAGS "-g -O2 -Wall")
ELSE()
  set(CMAKE_CXX_FLAGS "-g -Wall")
ENDIF()

# compiler options
set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_C_COMPILER "gcc")
set(CMAKE_CXX_COMPILER_ARG1 "-std=c++0x")


find_package(Boost 1.36.0 COMPONENTS log system filesystem program_options thread regex timer chrono serialization)
if(NOT Boost_FOUND)
  message(FATAL_ERROR "Boost not found!")
endif()

include_directories(src ${Boost_INCLUDE_DIRS})

set(THIRD_LIBRARIES ${Boost_LIBRARIES})

#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
#set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/lib)

file(GLOB TEST_SOURCES src/*.cc)
file(GLOB TEST_HEAD src/*.h)

add_executable(mytest ${TEST_SOURCES} ${TEST_HEAD})
target_link_libraries(mytest ${THIRD_LIBRARIES})
