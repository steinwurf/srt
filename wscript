#! /usr/bin/env python
# encoding: utf-8

APPNAME = "asio"
VERSION = "2.0.1"


def configure(conf):
    conf.set_cxx_std(11)

    if conf.is_mkspec_platform("linux") and not conf.env["LIB_PTHREAD"]:
        conf.check_cxx(lib="pthread")


def build(bld):
    use_flags = ["ASIO"]
    if bld.is_mkspec_platform("linux"):
        use_flags += ["PTHREAD"]
    # Path to the source repo
    directory = bld.dependency_node("asio-source")

    includes = directory.find_node("asio").find_node("include")

    bld(name="asio_includes", export_includes=[includes], use=use_flags)

    if bld.is_toplevel():
        bld.recurse("examples")
