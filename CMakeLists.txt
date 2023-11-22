cmake_minimum_required(VERSION 3.10)
project(srt)

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
  set(STEINWURF_TOP_NAME ${PROJECT_NAME})
endif()



include(ExternalProject)
ExternalProject_add(project_srt
 SOURCE_DIR ${STEINWURF_RESOLVE}/srt-source
  BINARY_DIR ${STEINWURF_RESOLVE}/srt-source/cmake_build
  INSTALL_DIR ${STEINWURF_RESOLVE}/srt-source/install
  CONFIGURE_COMMAND ${CMAKE_COMMAND} ${STEINWURF_RESOLVE}/srt-source/
  BUILD_COMMAND ${CMAKE_COMMAND} --build ${STEINWURF_RESOLVE}/srt-source/cmake_build
  CMAKE_CACHE_ARGS -DENABLED_STATIC=ON -DENABLE_BONDING=ON -DENABLE_APPS=OFF -DENABLE_ENCRYPTION=OFF -DCMAKE_BUILD_TYPE=Debug
  EXCLUDE_FROM_ALL TRUE
  STEP_TARGETS build
  INSTALL_COMMAND ${CMAKE_COMMAND} --install ${STEINWURF_RESOLVE}/srt-source/cmake_build --prefix ${STEINWURF_RESOLVE}/srt-source/install
  
)
add_library(srt STATIC IMPORTED GLOBAL)
set_target_properties(srt PROPERTIES
   IMPORTED_LOCATION ${STEINWURF_RESOLVE}/srt-source/install/lib/libsrt.a
)
target_include_directories(srt INTERFACE ${STEINWURF_RESOLVE}/srt-source/install/include)
add_dependencies(srt project_srt)

add_library(steinwurf::srt ALIAS srt)


# # Include directories
# target_include_directories(steinwurf::srt INTERFACE ${STEINWURF_RESOLVE}/srt-source/install/include)

# Is top level project?
if (${PROJECT_NAME} STREQUAL ${STEINWURF_TOP_NAME})
    enable_testing()

    if (CMAKE_C_COMPILER_ID MATCHES "MSVC")
        # For Windows: Prevent overriding the parent project's compiler/linker
        # settings
        set(gtest_force_shared_crt
                ON
                CACHE BOOL "" FORCE)
    endif ()

    # Google Test dependency
    add_subdirectory("${STEINWURF_RESOLVE}/gtest-source" gtest_main
            EXCLUDE_FROM_ALL)

    # Define library
    file(GLOB_RECURSE srt_test_sources test/**/*.cpp)

    include_directories(${STEINWURF_RESOLVE}/srt-source/install/include)



    # Build test executable
    add_executable(srt_tests ${srt_test_sources})
    add_dependencies(srt_tests project_srt)
    target_link_libraries(srt_tests steinwurf::srt)
    target_link_libraries(srt_tests gtest_main)

    # Make sure we compile with C++17 and do not use compiler specific extensions
    set_property(TARGET srt_tests PROPERTY CXX_STANDARD 17)
    set_property(TARGET srt_tests PROPERTY CXX_EXTENSIONS OFF)

    # Enable pedantic errors
    if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        # GCC is throwing ISO errors from abseil that we can't fix
    else ()
        target_compile_options(srt_tests PUBLIC -pedantic-errors)
    endif ()

    add_test(srt_tests srt_tests)

endif ()
