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

unset(CMAKE_CXX_COMPILER)
unset(CMAKE_C_COMPILER)

if (DEFINED CMAKE_TOOLCHAIN_FILE)
    set(TOOLCHAIN_OPTION "-DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}")
endif()

message(STATUS "TOOLCHAIN_OPTION: ${TOOLCHAIN_OPTION}")

if (DEFINED ZIG_TARGET)
    set(ZIG_TARGET_OPTION "-DZIG_TARGET=${ZIG_TARGET}")
endif()

message(STATUS "ZIG_TARGET_OPTION: ${ZIG_TARGET_OPTION}")




if (NOT CMAKE_BUILD_TYPE)
    message(STATUS "CMAKE_BUILD_TYPE not defined, using Debug")
    set (CMAKE_BUILD_TYPE "Debug")
    set (SRT_ENABLE_DEBUG ON)
else ()
    message(STATUS "CMAKE_BUILD_TYPE is defined, using ${CMAKE_BUILD_TYPE}")
    set (BUILD_TYPE ${CMAKE_BUILD_TYPE})
    if (CMAKE_BUILD_TYPE MATCHES "Debug")
        set (SRT_ENABLE_DEBUG ON)
    else ()
        set (SRT_ENABLE_DEBUG OFF)
    endif ()
endif()

if (UNIX AND NOT APPLE)
    # Linux-specific code
    set(LIB_NAME "libsrt.a")
elseif (APPLE)
    # Apple-Darwin-specific code
    set(LIB_NAME "libsrt.a")
elseif (WIN32)
    # Windows-specific code
    set(LIB_NAME "srt_static.lib")
endif ()


include(GNUInstallDirs)
include(ExternalProject)
ExternalProject_add(project_srt
  SOURCE_DIR ${STEINWURF_RESOLVE}/srt-source
  BINARY_DIR ${STEINWURF_RESOLVE}/srt-source/cmake_build
  INSTALL_DIR ${STEINWURF_RESOLVE}/srt-source/install
  CONFIGURE_COMMAND ${CMAKE_COMMAND} ${STEINWURF_RESOLVE}/srt-source/ ${TOOLCHAIN_OPTION} ${ZIG_TARGET_OPTION} -DENABLE_BONDING=ON -DENABLE_APPS=OFF -DENABLE_ENCRYPTION=OFF -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DENABLE_SHARED=ON -DENABLE_STATIC=ON -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} -DENABLE_DEBUG=${SRT_ENABLE_DEBUG}
  BUILD_COMMAND ${CMAKE_COMMAND} --build ${STEINWURF_RESOLVE}/srt-source/cmake_build --config ${CMAKE_BUILD_TYPE}
  EXCLUDE_FROM_ALL TRUE
  STEP_TARGETS build
  INSTALL_COMMAND ${CMAKE_COMMAND} --install ${STEINWURF_RESOLVE}/srt-source/cmake_build --prefix ${STEINWURF_RESOLVE}/srt-source/install --config ${CMAKE_BUILD_TYPE}
  BUILD_BYPRODUCTS ${STEINWURF_RESOLVE}/srt-source/install/${CMAKE_INSTALL_LIBDIR}/${LIB_NAME}
)

# message(STATUS "CMAKE_BUILD_TYPE: ${CMAKE_BUILD_TYPE}")
add_library(srt STATIC IMPORTED GLOBAL)
add_dependencies(srt project_srt)
add_library(steinwurf::srt ALIAS srt)

# Make the include directory before we set the target properties otherwise cmake will complain
# as this is resolved at configure time rather than build time where the header files are generated
file(MAKE_DIRECTORY ${STEINWURF_RESOLVE}/srt-source/install/include)
set(SRT_GENERATED_INCLUDE_DIR ${STEINWURF_RESOLVE}/srt-source/install/include)
set_target_properties(srt PROPERTIES
   IMPORTED_LOCATION ${STEINWURF_RESOLVE}/srt-source/install/${CMAKE_INSTALL_LIBDIR}/${LIB_NAME}
   INTERFACE_INCLUDE_DIRECTORIES ${SRT_GENERATED_INCLUDE_DIR}
)




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
    # platform dependency
    if (NOT TARGET steinwurf::platform)
        add_subdirectory("${STEINWURF_RESOLVE}/platform" platform EXCLUDE_FROM_ALL)
    endif ()

    # Define library
    file(GLOB_RECURSE srt_test_sources test/**/*.cpp)




    # Build test executable
    add_executable(srt_tests ${srt_test_sources})
    add_dependencies(srt_tests steinwurf::srt)
    target_link_libraries(srt_tests steinwurf::srt)
    target_link_libraries(srt_tests gtest_main)
    target_link_libraries(srt_tests steinwurf::platform)

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
