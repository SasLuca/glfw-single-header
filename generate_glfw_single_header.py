import os

win32_defines = ["#define _GLFW_WIN32 1",
                 "#ifdef _MSC_VER\n#define _CRT_SECURE_NO_WARNINGS\n#endif",
                 "#define LSH_GLFW_USE_HYBRID_HPG",
                 "#ifdef LSH_GLFW_USE_HYBRID_HPG\n#define _GLFW_USE_HYBRID_HPG 1\n#endif",
                 "#define _UNICODE",
                 "#ifdef MINGW\n#define UNICODE\n#define WINVER 0x0501\n#endif", ]

win32_headers = [ "internal.h", "mappings.h", "win32_platform.h", "win32_joystick.h", "wgl_context.h", "egl_context.h", "osmesa_context.h", ]
win32_sources = [ "win32_init.c", "win32_joystick.c", "win32_monitor.c", "win32_time.c", "win32_thread.c", "win32_window.c", "wgl_context.c", "egl_context.c", "osmesa_context.c", ]

osmesa_headers = [ "internal.h", "mappings.h","null_platform.h", "null_joystick.h", "posix_time.h", "posix_thread.h", "osmesa_context.h", ]
osmesa_sources = [ "null_init.c", "null_monitor.c", "null_window.c", "null_joystick.c", "posix_time.c", "posix_thread.c", "osmesa_context.c", ]

x11_headers     = [ "internal.h", "mappings.h", "x11_platform.h", "xkb_unicode.h", "posix_time.h", "posix_thread.h", "glx_context.h", "egl_context.h", "osmesa_context.h", "linux_joystick.h", ]
x11_sources     = [ "x11_init.c", "x11_monitor.c", "x11_window.c", "xkb_unicode.c", "posix_time.c", "posix_thread.c", "glx_context.c", "egl_context.c", "osmesa_context.c", "linux_joystick.c",  ]

wayland_headers = [ "internal.h", "mappings.h", "wl_platform.h", "posix_time.h", "posix_thread.h", "xkb_unicode.h", "egl_context.h", "osmesa_context.h", "linux_joystick.h", ]
wayland_sources = [ "wl_init.c", "wl_monitor.c", "wl_window.c", "posix_time.c", "posix_thread.c", "xkb_unicode.c", "egl_context.c", "osmesa_context.c", "linux_joystick.c",  ]

cocoa_headers   = [ "internal.h", "mappings.h", "cocoa_platform.h", "cocoa_joystick.h", "posix_thread.h", "nsgl_context.h", "egl_context.h", "osmesa_context.h", ]
cocoa_sources   = [ "cocoa_init.m", "cocoa_joystick.m", "cocoa_monitor.m", "cocoa_window.m", "cocoa_time.c", "posix_thread.c", "nsgl_context.m", "egl_context.c", "osmesa_context.c", ]

all_headers = list(set(win32_headers + osmesa_headers + x11_headers + wayland_headers + cocoa_headers))
shared_sources = [ "context.c", "init.c", "input.c", "monitor.c", "vulkan.c", "window.c", ]

# Get the file using this function since it might be cached
files_cache = {}
def lsh_get_file(it: str) -> str:
    global files_cache
    if it in files_cache.keys():
        return files_cache[it]

    guard = f"HEADER_GUARD_{it.replace('.', '_').upper()}"
    code = open(f"./glfw/src/{it}").read()
    files_cache[it] = f"\n#ifndef {guard}\n#define {guard}\n{code}\n#endif\n"

    return files_cache[it]

# Include the headers into a source
def include_headers(headers, source: str) -> str:
    if len(headers) == 0:
        return source

    for it in headers:
        if source.find(f"#include \"{it}\"") != -1:
            h = include_headers([i for i in headers if i != it], lsh_get_file(it))
            source = source.replace(f"#include \"{it}\"", f"\n{h}\n")
    return source

# Add shared code
shared_source_result = ""
for it in shared_sources:
    shared_source_result += include_headers(all_headers, lsh_get_file(it))

# Add win32 code
win32_source_result = "\n#if defined _WIN32 || defined LSH_GLFW_WIN32\n"
for it in win32_defines:
    win32_source_result += "\n" + it + "\n"
for it in win32_sources:
    win32_source_result += include_headers(all_headers, lsh_get_file(it))
win32_source_result += "\n#endif\n"

# Add osmesa code
osmesa_source_result = "\n#ifdef LSH_GLFW_OSMESA\n"
for it in osmesa_sources:
    osmesa_source_result += include_headers(all_headers, lsh_get_file(it))
osmesa_source_result += "\n#endif\n"

# Add x11 code
x11_source_result = "\n#ifdef LSH_GLFW_X11\n"
for it in x11_sources:
    x11_source_result += include_headers(all_headers, lsh_get_file(it))
x11_source_result += "\n#endif\n"

# Add wayland code
wayland_source_result = "\n#ifdef LSH_GLFW_WAYLAND\n"
for it in wayland_sources:
    wayland_source_result += include_headers(all_headers, lsh_get_file(it))
wayland_source_result += "\n#endif\n"

# Add cocoa code
cocoa_source_result = "\n#if defined LSH_GLFW_COCOA || defined __APPLE__\n"
for it in cocoa_sources:
    cocoa_source_result += include_headers(all_headers, lsh_get_file(it))
cocoa_source_result += "\n#endif\n"

# Get the glfw headers
headers_result = open("./glfw/include/GLFW/glfw3.h").read() + "\n" + open("./glfw/include/GLFW/glfw3native.h").read() + "\n"

# Add single header
source_result = "\n#ifdef LSH_GLFW_IMPLEMENTATION\n"
source_result += win32_source_result + osmesa_source_result + x11_source_result + wayland_source_result + cocoa_source_result + shared_source_result
source_result += "\n#endif\n"

# Comment out options macro error
source_result = source_result.replace("#error \"You must not define any header option macros when compiling GLFW\"",
                                      "//#error \"You must not define any header option macros when compiling GLFW\"")

# for it in win32_headers + osmesa_headers + x11_headers + wayland_headers + cocoa_headers:
#     source_result = source_result.replace(f"#include \"{it}\"", f"//#include \"{it}\"")

source_result = source_result.replace("#include \"../include/GLFW/glfw3.h\"", "//#include \"../include/GLFW/glfw3.h\"")

# Make dirs
if not os.path.exists("./generated-single-header"):
    os.makedirs("./generated-single-header")

if not os.path.exists("./generated-single-header-and-source"):
    os.makedirs("./generated-single-header-and-source")

# Make single header
open("./generated-single-header/glfw.h", "w+").write(headers_result + source_result)

# Make single header + single source
open("./generated-single-header-and-source/glfw.h", "w+").write(headers_result)
open("./generated-single-header-and-source/glfw.c", "w+").write(
    headers_result + "\n#define LSH_GLFW_IMPLEMENTATION\n" + source_result)
