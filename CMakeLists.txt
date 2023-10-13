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


option(ENABLE_SHARED "Build shared library" ON)
option(ENABLE_APPS "Build apps" OFF)
option(ENABLE_BONDING "Build bonding" ON)
add_subdirectory(${STEINWURF_RESOLVE}/srt-source srt)
