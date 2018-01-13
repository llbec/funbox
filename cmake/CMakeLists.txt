cmake_minimum_required (VERSION 2.6)

project (T1)

set(SRC_LIST test/main.cpp)
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/build/lib)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/Modules/")

include_directories(src src/leveldb/include src/config)

#file(GLOB LIB_BNET src/*.cpp)
#add_library(bnet STATIC ${LIB_BNET})

set(secp256k1_DIR "${CMAKE_SOURCE_DIR}/src/bitcoin/secp256k1")
set(secp256k1_LIBRARIES "${secp256k1_DIR}/.libs/libsecp256k1.a")
if (NOT EXISTS ${secp256k1_LIBRARIES})
  message(STATUS "build secp256k1...")
  execute_process(WORKING_DIRECTORY "${secp256k1_DIR}" COMMAND ./autogen.sh)
  execute_process(WORKING_DIRECTORY "${secp256k1_DIR}" COMMAND ./configure)
  execute_process(WORKING_DIRECTORY "${secp256k1_DIR}" COMMAND make)
endif()
if (NOT EXISTS ${secp256k1_LIBRARIES})
  message(FATAL_ERROR "build secp256k1 failed!")
endif()

find_package(OpenSSL)
if(NOT OPENSSL_FOUND)
  message(FATAL_ERROR "OpenSSL not found!")
endif(NOT OPENSSL_FOUND)

find_package(LibConfig)
if(NOT LIBCONFIG_FOUND)
  message(FATAL_ERROR "LibConfig not found!")
endif(NOT LIBCONFIG_FOUND)

find_package(Glog)
if(NOT GLOG_FOUND)
message(FATAL_ERROR "Glog not found!")
endif(NOT GLOG_FOUND)

find_package(libzmq)
if(NOT LIBZMQ_FOUND)
  message(FATAL_ERROR "libzmq not found!")
endif(NOT LIBZMQ_FOUND)

find_package(CURL)
if(NOT CURL_FOUND)
  message(FATAL_ERROR "libcurl not found!")
endif(NOT CURL_FOUND)

find_package(LibEvent)
if(NOT LibEvent_FOUND)
  message(FATAL_ERROR "libevent2 not found!")
endif(NOT LibEvent_FOUND)

find_package(Boost 1.36.0 COMPONENTS thread filesystem system regex program_options)
if(NOT Boost_FOUND)
  message(FATAL_ERROR "Boost not found!")
endif(NOT Boost_FOUND)

find_package(ZookeeperC)
if(NOT ZOOKEEPER_FOUND)
  message(FATAL_ERROR "libzookeeper-mt not found!")
endif(NOT ZOOKEEPER_FOUND)

find_package(KafkaC)
if(NOT KAFKA_FOUND)
  message(FATAL_ERROR "librdkafka not found!")
endif(NOT KAFKA_FOUND)

include_directories(src test src/bitcoin src/bitcoin/secp256k1/include ${OPENSSL_INCLUDE_DIR} ${Boost_INCLUDE_DIRS} ${LIBZMQ_INCLUDE_DIR} ${GLOG_INCLUDE_DIRS} ${LIBEVENT_INCLUDE_DIR} ${MYSQL_INCLUDE})
set(THIRD_LIBRARIES ${OPENSSL_CRYPTO_LIBRARY} ${OPENSSL_SSL_LIBRARY} ${Boost_LIBRARIES} ${LIBCONFIGPP_LIBRARY} ${LIBZMQ_LIBRARIES} ${GLOG_LIBRARIES} ${CURL_LIBRARIES} ${ZOOKEEPER_LIBRARIES} ${KAFKA_LIBRARIES} ${LIBEVENT_LIB} ${LIBEVENT_PTHREADS_LIB} ${secp256k1_LIBRARIES} pthread mysqlclient gmp)

add_definitions(-DHAVE_CONFIG_H)

add_executable(test ${SRC_LIST})

target_link_libraries(test ${THIRD_LIBRARIES})

