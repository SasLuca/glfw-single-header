cmake_minimum_required(VERSION 3.1)

project(example)

set(CMAKE_C_STANDARD 99)

include_directories(../generated-single-header)
include_directories(./)
#include_directories(../generated-single-header-and-source)

add_executable(test test.c glad.c)