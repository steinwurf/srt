#! /usr/bin/env python
# encoding: utf-8

import os

APPNAME = "srt"
VERSION = "1.1.0"






def build(bld):
    

    #check if cmake is installed
    # bld.find_program("cmake", mandatory=True)
    root_dir = bld.dependency_node("srt-source")
    print(root_dir)
    

    #check if cmake_build folder exists
    if os.path.isdir(f"{root_dir}/cmake_build"):
        bld.cmd_and_log(f"rm -rf {root_dir}/cmake_build")
    bld.cmd_and_log(f"mkdir {root_dir}/cmake_build")
    # SRT cmake flags
    flags = " ".join([
        "-DENABLE_SHARED=OFF",
        "-DENABLE_STATIC=ON",
        "-DENABLE_APPS=OFF",
        "-DENABLE_ENCRYPTION=OFF",
        "-DENABLE_BONDING=ON",
    ])

    os.system(f"cmake -GNinja {flags} -S {root_dir} -B {root_dir}/cmake_build")
    os.system(f"cmake --build {root_dir}/cmake_build")

    if not os.path.isdir(f"{root_dir}/install"):
        os.system(f"mkdir {root_dir}/install")
    os.system(f"cmake --install {root_dir}/cmake_build --prefix {root_dir}/install")

    
    print(f"{root_dir}/install/lib")
    includes = root_dir.find_node("install/include")
    libs = root_dir.find_node("install/lib")
    bld.read_stlib('srt', paths=[libs])
    bld(name="srt_includes", export_includes=[includes])
    
    if bld.is_toplevel():
        bld.program(
            features="cxx test",
            source= bld.path.ant_glob(
            "test/**/*.cpp"),
            target="srt_test",
            use=["srt", "srt_includes", "gtest"],
        )

