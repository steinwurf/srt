
#include <cassert>
#include <gtest/gtest.h>
#include <iostream>
#include <srt/srt.h>
#include <srt/udt.h>
#include <srt/version.h>
#include <platform/config.hpp>


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
}
