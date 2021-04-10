# glfw-single-header
A python3 script that generates a single-header and single-header+single-source version of GLFW.
Currently it compiles on windows easily, here is an example with gcc:
```
gcc example/*.c -I example/ -lgdi32
```

And also MacOS,

```
export SDKROOT=$(xcrun --show-sdk-path)
gcc -ObjC example/*.c -I example/ -framework Cocoa -framework IOkit
```
