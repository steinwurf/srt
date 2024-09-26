

set(CMAKE_C_COMPILER "zig" cc -target ${ZIG_TARGET})
set(CMAKE_CXX_COMPILER "zig" c++ -target ${ZIG_TARGET})
set(CMAKE_AR "${CMAKE_CURRENT_LIST_DIR}/zig-ar.sh")
set(CMAKE_RANLIB "${CMAKE_CURRENT_LIST_DIR}/zig-ranlib.sh")
