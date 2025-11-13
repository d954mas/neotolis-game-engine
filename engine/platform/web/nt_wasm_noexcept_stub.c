#include <stdio.h>
#include <stdlib.h>

#if defined(__EMSCRIPTEN__)

// Dawn's emdawnwebgpu port is built with -fno-exceptions, but upstream
// translation units may still attempt to throw. Provide a fail-fast stub so
// we can link without enabling the Emscripten exception runtime.
__attribute__((noreturn)) void __cxa_throw(void* exception, void* type_info, void (*destructor)(void*)) {
    (void)exception;
    (void)type_info;
    (void)destructor;

    fputs("Fatal: C++ exception throw attempted on a no-exception wasm build\n", stderr);
    abort();
}

#endif // __EMSCRIPTEN__
