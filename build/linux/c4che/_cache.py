AR = ['/usr/bin/ar']
ARFLAGS = 'rcs'
BINDIR = '//bin'
CC = ['/usr/bin/gcc']
CCLNK_SRC_F = []
CCLNK_TGT_F = ['-o']
CC_NAME = 'gcc'
CC_SRC_F = []
CC_TGT_F = ['-c', '-o']
CC_VERSION = ('13', '2', '1')
CFLAGS = ['-O2', '-ftree-vectorize', '-finline-functions', '-Wextra', '-Wall']
CFLAGS_MACBUNDLE = ['-fPIC']
CFLAGS_cshlib = ['-fPIC']
COMPILER_CXX = 'g++'
CPPPATH_ST = '-I%s'
CXX = ['/usr/bin/g++']
CXXFLAGS = ['-Wextra', '-Wall', '-O2', '-ftree-vectorize', '-finline-functions', '-std=c++11']
CXXFLAGS_MACBUNDLE = ['-fPIC']
CXXFLAGS_cxxshlib = ['-fPIC']
CXXLNK_SRC_F = []
CXXLNK_TGT_F = ['-o']
CXX_NAME = 'g++'
CXX_SRC_F = []
CXX_STD = 'c++11'
CXX_STD_ORIGIN = 'srt'
CXX_SUPPORTED_STDS = {'c++98': '-std=c++98', 'c++03': '-std=c++03', 'c++11': '-std=c++11', 'c++14': '-std=c++14', 'c++17': '-std=c++17', 'c++20': '-std=c++20', 'c++23': '-std=c++23'}
CXX_TGT_F = ['-c', '-o']
DEFINES_ST = '-D%s'
DEST_BINFMT = 'elf'
DEST_CPU = 'x86_64'
DEST_OS = 'linux'
G++ = ['/usr/bin/g++']
GCC = ['/usr/bin/gcc']
LIBDIR = '//lib'
LIBPATH_ST = '-L%s'
LIB_PTHREAD = ['pthread']
LIB_ST = '-l%s'
LINKFLAGS = ['-s']
LINKFLAGS_MACBUNDLE = ['-bundle', '-undefined', 'dynamic_lookup']
LINKFLAGS_cshlib = ['-shared']
LINKFLAGS_cstlib = ['-Wl,-Bstatic']
LINKFLAGS_cxxshlib = ['-shared']
LINKFLAGS_cxxstlib = ['-Wl,-Bstatic']
LINK_CC = ['/usr/bin/gcc']
LINK_CXX = ['/usr/bin/g++']
MKSPEC_PLATFORM = 'linux'
PREFIX = '/'
RPATH_ST = '-Wl,-rpath,%s'
SHLIB_MARKER = '-Wl,-Bdynamic'
SONAME_ST = '-Wl,-h,%s'
STLIBPATH_ST = '-L%s'
STLIB_MARKER = '-Wl,-Bstatic'
STLIB_ST = '-l%s'
cprogram_PATTERN = '%s'
cshlib_PATTERN = 'lib%s.so'
cstlib_PATTERN = 'lib%s.a'
cxxprogram_PATTERN = '%s'
cxxshlib_PATTERN = 'lib%s.so'
cxxstlib_PATTERN = 'lib%s.a'
macbundle_PATTERN = '%s.bundle'
stored_options = {'colors': 'auto', 'jobs': 32, 'keep': 0, 'verbose': 0, 'zones': '', 'profile': 0, 'pdb': 0, 'whelp': 0, 'out': '', 'top': '', 'no_lock_in_run': '', 'no_lock_in_out': '', 'no_lock_in_top': '', 'prefix': '', 'bindir': None, 'libdir': None, 'progress_bar': 0, 'targets': '', 'files': '', 'destdir': '/home/suhrm/projects/srt/asio_install', 'force': False, 'distcheck_args': None, 'no_resolve': False, 'skip_internal': False, 'standalone_archive': None, 'standalone_algo': 'zip', 'standalone_exclude': None, 'install_path': None, 'install_relative': None, 'install_shared_libs': None, 'install_static_libs': None, 'cxx_mkspec': None, 'cxx_debug': None, 'cxx_nodebug': None, 'cflags': None, 'cxxflags': None, 'linkflags': None, 'commonflags': None, 'android_sdk_dir': None, 'android_ndk_dir': None, 'ios_sdk_dir': None, 'ios_toolchain_dir': None, 'emscripten_path': None, 'poky_sdk_path': None, 'run_tests': None, 'run_silent': None, 'run_benchmarks': None, 'run_benchmark': None, 'print_benchmarks': None, 'print_benchmark_paths': None, 'run_cmd': None, 'result_file': None, 'result_folder': None, 'device_id': None, 'test_filter': None, 'ssh_runner': None, 'ssh_user': None, 'ssh_host': None, 'ssh_dest_dir': None, 'ssh_clean_dir': None, 'ssh_output_file': None, 'ssh_options': None, 'scp_options': None, 'resolve_path': None, 'git_protocol': None, 'symlinks_path': None, 'fast_resolve': None, 'lock_paths': None, 'lock_versions': None, 'waf_tools_path': None, 'waf_tools_checkout': None, 'srt_source_path': None, 'srt_source_checkout': None}
