// actual or intended publication of such source code.

#include <ctime>

#include <gtest/gtest.h>

GTEST_API_ int main(int argc, char **argv) {

  srand(static_cast<uint32_t>(time(0)));

  testing::InitGoogleTest(&argc, argv);
  auto result = RUN_ALL_TESTS();

  return result;
}
