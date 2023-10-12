// Copyright (c) 2023 Steinwurf ApS
// All Rights Reserved

#include <asio/version.hpp>

#include <asio.hpp>
#include <iostream>

int main()
{
    std::cout << "ASIO version: " << ASIO_VERSION << std::endl;
    return 0;
}
