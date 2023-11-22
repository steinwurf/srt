#! /usr/bin/env python
# encoding: utf-8

import os
import shutil
from waflib import Build, Errors, Logs

APPNAME = "srt"
VERSION = "1.1.0"






def build(bld):
    bld.find_program("cmake", mandatory=True, quiet=1, output=0)
    bld.post_mode = Build.POST_LAZY
    root_dir = bld.dependency_node("srt-source")
    
    target = bld.bldnode.make_node("srt")
    bld(rule=CMakeBuildTask, target=target.make_node('flag.lock'), source=root_dir)
    bld.add_group()
    lib_path = target.find_node("lib")
    include_path = target.find_node("include")
    bld.read_stlib('srt', paths=[lib_path], export_includes=[include_path])
    
    
    if bld.is_toplevel():
        bld.program(
            features="cxx test",
            source= bld.path.ant_glob(
            "test/**/*.cpp"),
            target="srt_test",
            use=["srt", "srt_includes", "gtest"],
        )


def CMakeBuildTask(task):
    output = task.outputs[0].parent
    source_dir = task.inputs[0]
    shutil.rmtree(output.abspath())
    if not os.path.isdir(output.abspath()):
        os.makedirs(output.abspath())
        #check if cmake_build folder exists
        if os.path.isdir(f"{source_dir}/cmake_build"):
            task.generator.bld.cmd_and_log(f"rm -rf {source_dir}/cmake_build", quiet=0, output=0)
        task.generator.bld.cmd_and_log(f"mkdir {source_dir}/cmake_build", quiet=0, output=0)
        # SRT cmake flags
        flags = " ".join([
            "-DENABLE_SHARED=ON",
            "-DENABLE_STATIC=ON",
            "-DENABLE_APPS=OFF",
            "-DENABLE_ENCRYPTION=OFF",
            "-DENABLE_BONDING=ON",
            "-DCMAKE_BUILD_TYPE=Debug",
        ])
        try:
            task.generator.bld.cmd_and_log(f"cmake {flags} -S {source_dir} -B {source_dir}/cmake_build", quiet=0, output=0)
            task.generator.bld.cmd_and_log(f"cmake --build {source_dir}/cmake_build --parallel", quiet=0, output=0)
            task.generator.bld.cmd_and_log(f"cmake --install {source_dir}/cmake_build --prefix {output}", quiet=0, output=0)
        except Errors.WafError as e:
            Logs.error(e.stderr)
            return -1
        Logs.info(f"Installed srt lib to {output}")
    else:
        Logs.info(f"Found srt lib in {output}")

    task.outputs[0].write("ok")
