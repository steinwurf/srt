
#include <cassert>
#include <gtest/gtest.h>
#include <iostream>
#include <platform/config.hpp>
#include <srt/srt.h>
#include <srt/udt.h>
#include <srt/version.h>

#if defined(PLATFORM_WINDOWS)
#include <Winsock2.h>
#define _WINSOCKAPI_
#include <io.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#endif

TEST(test_srt, lib) {
  int ret = srt_startup();
  assert(ret == SRT_SUCCESS);
  ret = srt_cleanup();
  assert(ret == SRT_SUCCESS);
  (void)ret; // suppress warning with nodebug
}
