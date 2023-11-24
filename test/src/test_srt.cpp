
#include <cassert>
#include <gtest/gtest.h>
#include <iostream>
#include <srt/srt.h>
#include <srt/udt.h>
#include <srt/version.h>

TEST(test_srt, lib) {
  int ret = srt_startup();
  assert(ret == SRT_SUCCESS);
  ret = srt_cleanup();
  assert(ret == SRT_SUCCESS);
}
