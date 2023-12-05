#! /usr/bin/env python
# encoding: utf-8

import os
import shutil
import platform
from waflib import Build, Errors, Logs

APPNAME = "srt"
VERSION = "1.1.0"

CMAKE_BUILD_TYPE = "Release"
SRT_ENABLE_DEBUG = "OFF"
lib_name = None


def configure(conf):
    if conf.has_tool_option("cxx_debug"):
        CMAKE_BUILD_TYPE = "Debug"
        SRT_ENABLE_DEBUG = "ON"


def build(bld):
    bld.post_mode = Build.POST_LAZY

    # Find the source directory for the external library
    src_dir = bld.dependency_node("srt-source")

    # Declare the temporary build directory for the external library
    # it is best to keep it under the project build directory
    build_dir = bld.bldnode.make_node("cmake_build")

    # Declare the install directory for the external library
    install_dir = build_dir.make_node("install")

    # Declare the include directory for the external library
    include_dir = install_dir.make_node("include")

    # Declare the lib directory for the external library
    lib_dir = install_dir.make_node("lib")

    # build the external library through an external process
    bld(
        rule=CMakeBuildTask,
        target=build_dir.make_node("flag.lock"),
        install_dir=install_dir,
        source=src_dir,
    )

    # once it is done create a second build group
    bld.add_group()

    if platform.system() == "Windows":
        lib_name = "srt_static"
    else:
        lib_name = "srt"

    bld.read_stlib(lib_name, paths=[lib_dir], export_includes=[include_dir])

    if bld.is_toplevel():
        bld.program(
            features="cxx test",
            source=bld.path.ant_glob("test/**/*.cpp"),
            target="srt_test",
            use=[lib_name, "gtest", "platform_includes"],
        )


def CMakeBuildTask(task):
    # This is the directory where the external library will be installed the
    # task.outputs[0] is the flag file that will be created once the external
    # library is installed
    output_dir = task.outputs[0].parent

    # This is the directory where the external library source code is located
    source_dir = task.inputs[0]

    # The install dir is passed as a parameter to the task
    install_dir = task.generator.install_dir

    # remove the output directory if it exists
    shutil.rmtree(output_dir.abspath())

    # create the output directory
    os.makedirs(output_dir.abspath())

    # SRT cmake flags
    flags = " ".join(
        [
            "-DENABLE_SHARED=OFF",
            "-DENABLE_STATIC=ON",
            "-DENABLE_APPS=OFF",
            "-DENABLE_ENCRYPTION=OFF",
            "-DENABLE_BONDING=ON",
            f"-DENABLE_DEBUG={SRT_ENABLE_DEBUG}",
            f"-DCMAKE_BUILD_TYPE={CMAKE_BUILD_TYPE}",
        ]
    )

    # Run all commands in the output directory
    cwd = output_dir.abspath()

    try:
        task.generator.bld.cmd_and_log(
            f"cmake {flags} -S {source_dir}", cwd=cwd, quiet=0, output=0
        )
        task.generator.bld.cmd_and_log(
            f"cmake --build . --parallel --config {CMAKE_BUILD_TYPE}",
            cwd=cwd,
            quiet=0,
            output=0,
        )

        task.generator.bld.cmd_and_log(
            f"cmake --install . --prefix {install_dir} --config {CMAKE_BUILD_TYPE}",
            cwd=cwd,
            quiet=0,
            output=0,
        )

    except Errors.WafError as e:
        Logs.error(e.stderr)
        return -1

    Logs.info(f"Installed srt lib to {output_dir}")

    # write a lock file so that a rebuild occurs if files are removed manually
    task.outputs[0].write("ok")
