#! /usr/bin/env python
# encoding: utf-8

import os
import shutil
from waflib import Build, Errors, Logs

APPNAME = "srt"
VERSION = "1.1.0"

CMAKE_BUILD_TYPE = "Debug"

def configure(conf):
    if conf.has_tool_option("cxx_debug"):
        CMAKE_BUILD_TYPE = "Debug"





def build(bld):
    bld.find_program("cmake", mandatory=True, quiet=1, output=0)
    bld.post_mode = Build.POST_LAZY
    root_dir = bld.dependency_node("srt-source")
    
    target = bld.bldnode.make_node("srt")
    bld(rule=CMakeBuildTask, target=target.make_node('flag.lock'), source=root_dir)
    bld.add_group()
    lib_path = target.find_node("lib")
    include_path = target.find_node("include")
    print("lib path: ", lib_path)
    print("include path: ", include_path)
    bld(name="srt_includes", export_includes=[include_path])
    bld.read_stlib('srt_static', paths=[lib_path], export_includes=[include_path])
    
    
    if bld.is_toplevel():
        bld.program(
            features="cxx test",
            source= bld.path.ant_glob(
            "test/**/*.cpp"),
            target="srt_test",
            use=["srt_static", "srt_includes", "gtest", "platform_includes" ],
        )


def CMakeBuildTask(task):
    output = task.outputs[0].parent
    source_dir = task.inputs[0]
    shutil.rmtree(output.abspath())
    if not os.path.isdir(output.abspath()):
        os.makedirs(output.abspath())
        #check if cmake_build folder exists
        if os.path.isdir(f"{source_dir}/cmake_build"):
            shutil.rmtree(f"{source_dir}/cmake_build")
        os.makedirs (f"{source_dir}/cmake_build")
        print(CMAKE_BUILD_TYPE)
        # SRT cmake flags
        flags = " ".join([
            "-DENABLE_SHARED=ON",
            "-DENABLE_STATIC=ON",
            "-DENABLE_APPS=OFF",
            "-DENABLE_ENCRYPTION=OFF",
            "-DENABLE_BONDING=ON",
            f"-DCMAKE_BUILD_TYPE={CMAKE_BUILD_TYPE}",
        ])
        try:
            task.generator.bld.cmd_and_log(f"cmake {flags} -S {source_dir} -B {source_dir}/cmake_build", quiet=0, output=0)
            task.generator.bld.cmd_and_log(f"cmake --build {source_dir}/cmake_build --parallel --config {CMAKE_BUILD_TYPE}", quiet=0, output=0)
            task.generator.bld.cmd_and_log(f"cmake --install {source_dir}/cmake_build --prefix {output} --config {CMAKE_BUILD_TYPE}", quiet=0, output=0)
        except Errors.WafError as e:
            Logs.error(e.stderr)
            return -1
        Logs.info(f"Installed srt lib to {output}")
    else:
        Logs.info(f"Found srt lib in {output}")

    task.outputs[0].write("ok")
