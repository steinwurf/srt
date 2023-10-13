#! /usr/bin/env python
# encoding: utf-8

import os

APPNAME = "srt"
VERSION = "1.1.0"


def configure(conf):
    conf.set_cxx_std(11)




def build(bld):
    

    #check if cmake is installed
    bld.find_program("cmake", mandatory=True)
    
    root_dir = bld.path.relpath()
    print(root_dir)


    #check if cmake_build folder exists
    if not os.path.isdir(f"{root_dir}/cmake_build"):
        bld.cmd_and_log(f"mkdir {root_dir}/cmake_build")
    os.system(f"cmake -GNinja -S . -B {root_dir}/cmake_build")
    os.system(f"cmake --build {root_dir}/cmake_build")
    
    if not os.path.isdir(f"{root_dir}/install"):
        os.system(f"mkdir {root_dir}/install")
    os.system(f"cmake --install {root_dir}/cmake_build --prefix {root_dir}/install")


    bld.read_shlib('srt', paths=[f"{root_dir}/install/lib"], export_includes=[f"{root_dir}/install/include"])
        







   
    
