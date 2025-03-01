cmake_minimum_required(VERSION 3.10)
project(OptimColGen)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)

# Find Clp and CoinUtils
include_directories(/opt/homebrew/Cellar/clp/1.17.10/include/clp)
include_directories(/opt/homebrew/Cellar/coinutils/2.11.12/include/coinutils/coin)
link_directories(/opt/homebrew/lib)

# Define the executable
add_executable(OptimColGen prod_main.cpp flight_loader.cpp)

# Link Clp and CoinUtils libraries
target_link_libraries(OptimColGen Clp CoinUtils)
