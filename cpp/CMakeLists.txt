# CMakeList.txt: 顶层 CMake 项目文件，在此处执行全局配置
# 并包含子项目。
#
cmake_minimum_required (VERSION 3.8)

set(CMAKE_CXX_STANDARD 17)
project ("Arknights-Tile-Pos-Cpp")
include_directories(include 3rdparty/include)

add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")
add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/W4;/WX>")
add_compile_options("$<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall;-Wextra;-Wpedantic;-Werror>")

if (WIN32)
    find_library(OpenCV NAMES opencv_world455 PATHS 3rdparty/lib)
else ()
    find_package(OpenCV REQUIRED)
endif ()

add_executable(Arknights-Tile-Pos-Cpp sample.cpp)
target_link_libraries(Arknights-Tile-Pos-Cpp ${OpenCV})
