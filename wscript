#! /usr/bin/env python
# encoding: utf-8

import os
import shutil
import platform
from waflib import Build, Errors, Logs

APPNAME = "srt"
VERSION = "1.1.0"

CMAKE_BUILD_TYPE = "Debug"
lib_name = None

def configure(conf):
    if conf.has_tool_option("cxx_debug"):
        CMAKE_BUILD_TYPE = "Debug"




def pre(bld):
    bld.find_program("cmake", mandatory=True, quiet=1, output=0)
    bld.post_mode = Build.POST_LAZY
    root_dir = bld.dependency_node("srt-source")
    if platform.system() == "Windows":
        lib_name = "srt_static.lib"
    elif platform.system() == "Darwin":
        lib_name = "libsrt.a"
    elif platform.system() == "Linux":
        lib_name = "libsrt.a"
    else:
        Logs.error("Unsupported platform")
        return -1
    target = bld.bldnode.make_node("srt")
    bld(name="srt_lib",rule=CMakeBuildTask, target=target.make_node('flag.lock'), source=root_dir )



def post(bld):
    lib_path = bld.path.find_node("srt/lib")
    include_path = bld.path.find_node("srt/include")
    bld(name="srt_includes", export_includes=[include_path])

    bld.read_stlib(lib_name, paths=[lib_path], export_includes=[include_path])


    if bld.is_toplevel():
        bld.program(
            features="cxx test",
            source= bld.path.ant_glob(
            "test/**/*.cpp"),
            target="srt_test",
            use=["srt_static", "srt_includes", "gtest", "platform_includes" ],
        )

def build(bld):
    bld.add_pre_fun(pre)
    bld.add_post_fun(post)






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
