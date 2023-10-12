cmake_minimum_required(VERSION 3.10)
set(SRT_VERSION 1.5.3)
cmake_policy(SET CMP0048 NEW)
# Also sets SRT_VERSION_MAJOR, SRT_VERSION_MINOR, SRT_VERSION_PATCH
project(SRT VERSION ${SRT_VERSION} LANGUAGES C CXX)

find_package(Python COMPONENTS Interpreter)

# Use waf to resolve dependencies
if(NOT DEFINED STEINWURF_RESOLVE)
  message(STATUS "Resolving dependencies...")
  execute_process(
    COMMAND ${Python_EXECUTABLE} waf resolve ${STEINWURF_RESOLVE_OPTIONS}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    RESULT_VARIABLE STATUS)

  if(STATUS AND NOT STATUS EQUAL 0)
    message(FATAL_ERROR "Failed: ${STATUS}")
  endif()

  set(STEINWURF_RESOLVE "${CMAKE_CURRENT_SOURCE_DIR}/resolve_symlinks")
  set(STEINWURF_TOP_NAME srt)
endif()

configure_file(
  "${STEINWURF_RESOLVE}/srt-source/srtcore/version.h.in"
  "${STEINWURF_RESOLVE}/srt-source/srtcore/version.h")

add_definitions(-DLINUX)
add_definitions(
	-D_GNU_SOURCE
	-DHAI_PATCH=1
	-DHAI_ENABLE_SRT=1
	-DSRT_VERSION="${SRT_VERSION}"
    -DENABLE_BONDING=1
    -DENABLE_MONOTONIC_CLOCK_DEFAULT=1
    -DHAVE_CXX_STD_PUT_TIME=1

    
)

# add_definitions(-DENABLE_MONOTONIC_CLOCK=1 -DENABLE_SOCK_CLOEXEC=1 
# -DHAI_ENABLE_SRT=1 -DHAI_PATCH=1 -DHAVE_CXX_STD_PUT_TIME=1 -DHAVE_INET_PTON=1 -DHA
# VE_PTHREAD_GETNAME_NP=1 -DHAVE_PTHREAD_SETNAME_NP=1 -DLINUX=1 -DNDEBUG -DSRT_DYNAM
# IC -DSRT_ENABLE_APP_READER -DSRT_ENABLE_BINDTODEVICE -DSRT_ENABLE_CLOSE_SYNCH -DSR
# T_ENABLE_ENCRYPTION -DSRT_EXPORTS -DSRT_LOG_SLOWDOWN_FREQ_MS=1000 -DUSE_OPENSSL=1 -D_GNU_SOURCE

# Use application-defined group reader
# (currently the only one implemented)
add_definitions(-DSRT_ENABLE_APP_READER)

# XXX This was added once as experimental, it is now in force for
# write-blocking-mode sockets. Still unclear if all issues around
# closing while data still not written are eliminated.
add_definitions(-DSRT_ENABLE_CLOSE_SYNCH)

if (LINUX)
# This is an option supported only on Linux
	add_definitions(-DSRT_ENABLE_BINDTODEVICE)
endif()

# Define library
file(GLOB_RECURSE SRT_SOURCES "${STEINWURF_RESOLVE}/srt-source/srtcore/*.cpp" "${STEINWURF_RESOLVE}/srt-source/srtcore/*.c")

# file(GLOB_RECURSE HAICRYPT_SOURCES "${STEINWURF_RESOLVE}/srt-source/haicrypt/*.cpp" "${STEINWURF_RESOLVE}/srt-source/haicrypt/*.c")


include_directories("${STEINWURF_RESOLVE}/srt-source/srtcore" "${STEINWURF_RESOLVE}/srt-source/haicrypt")

add_library(srt STATIC ${SRT_SOURCES} ${HAICRYPT_SOURCES})

target_compile_features(srt PUBLIC cxx_std_14)


target_include_directories(
  srt INTERFACE "${STEINWURF_RESOLVE}/srt-source/srtcore" "${STEINWURF_RESOLVE}/srt-source/haicrypt")

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
target_link_libraries(srt INTERFACE Threads::Threads)


add_library(steinwurf::srt ALIAS srt)

# Install headers
install(
  DIRECTORY "${STEINWURF_RESOLVE}/srt-source/srtcore/"
  DESTINATION ${CMAKE_INSTALL_PREFIX}/include
  FILES_MATCHING
  PATTERN *.h)

# # Is top level project?
# if(${CMAKE_PROJECT_NAME} STREQUAL ${PROJECT_NAME})
#   # Build executables
#   add_executable(hello_srt examples/hello_srt.cpp)
#   target_link_libraries(hello_srt srt)
# endif()
