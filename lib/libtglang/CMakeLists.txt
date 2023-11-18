cmake_minimum_required(VERSION 3.5 FATAL_ERROR)

project(tglang VERSION 2.0.0 LANGUAGES C)

add_library(tglang SHARED tglang.c)
