# CMakeList.txt: 顶层 CMake 项目文件，在此处执行全局配置
# 并包含子项目。
#
cmake_minimum_required (VERSION 3.8)


set(CMAKE_CXX_STANDARD 17)
project ("Arknights-Tile-Pos-Cpp")
add_executable(Arknights-Tile-Pos-Cpp main.cpp "src/TileCalc.cpp")
include_directories(src 3rdparty/include)

if (WIN32)
    find_library(OpenCV NAMES opencv_world455 PATHS 3rdparty/lib)
else ()
    find_package(OpenCV REQUIRED)
endif ()

target_link_libraries(Arknights-Tile-Pos-Cpp ${OpenCV})
