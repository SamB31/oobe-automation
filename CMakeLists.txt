cmake_minimum_required(VERSION 3.5)
project(YOLOv8CPP)

# Set paths
set(OpenCV_DIR "C:/opencv2/build")
set(OpenCV_BIN_DIR "C:/opencv2/build/x64/mingw/bin")
set(OpenCV_INCLUDE_DIR "${OpenCV_DIR}/include")

set(ONNXRUNTIME_DIR "C:/onnxruntime-win-x64-1.18.1")
set(ONNXRUNTIME_INCLUDE_DIR "${ONNXRUNTIME_DIR}/include")

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Use MinGW
set(CMAKE_C_COMPILER "C:/msys64/mingw64/bin/gcc.exe")
set(CMAKE_CXX_COMPILER "C:/msys64/mingw64/bin/g++.exe")

# Define Microsoft-specific annotations as empty for MinGW
if(MINGW)
    add_definitions(-D_Frees_ptr_opt_=)
endif()

# Set debug mode
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")
endif()

set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libgcc -static-libstdc++")

# Find OpenCV
find_package(OpenCV REQUIRED core imgproc highgui dnn)

# Include directories
include_directories(include "${ONNXRUNTIME_DIR}/include" ${OpenCV_INCLUDE_DIRS})

# Recursively collect all source files under 'src' directory
file(GLOB_RECURSE CURR_SOURCES src/*.cpp)

# Create the executable
add_executable(YOLOv8CPP ${CURR_SOURCES})

# Link libraries
target_link_libraries(YOLOv8CPP ${OpenCV_LIBS})
target_link_libraries(YOLOv8CPP "${ONNXRUNTIME_DIR}/lib/onnxruntime.lib")

# Post-build commands to copy DLLs
add_custom_command(TARGET YOLOv8CPP POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    "${ONNXRUNTIME_DIR}/lib/onnxruntime.dll"
    "$<TARGET_FILE_DIR:YOLOv8CPP>"
)

add_custom_command(TARGET YOLOv8CPP POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    "${OpenCV_BIN_DIR}/${OpenCV_DEBUG_DLL_FILENAME}"
    "$<TARGET_FILE_DIR:YOLOv8CPP>"
)

add_custom_command(TARGET YOLOv8CPP POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    "${OpenCV_BIN_DIR}/${OpenCV_RELEASE_DLL_FILENAME}"
    "$<TARGET_FILE_DIR:YOLOv8CPP>"
)

# Copy all OpenCV DLLs
file(GLOB OpenCV_DLLS "${OpenCV_BIN_DIR}/*.dll")
foreach(OpenCV_DLL ${OpenCV_DLLS})
    add_custom_command(TARGET YOLOv8CPP POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${OpenCV_DLL}
        "$<TARGET_FILE_DIR:YOLOv8CPP>"
    )
endforeach()
