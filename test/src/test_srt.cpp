
#include <gtest/gtest.h>
#include <srt/srt.h>
#include <srt/udt.h>
#include <srt/version.h>

TEST(test_srt, lib) {
  srt_startup();
  srt_cleanup();
}
