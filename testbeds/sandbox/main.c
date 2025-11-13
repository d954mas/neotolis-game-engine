#include <stdio.h>

#include "engine/core/nt_engine.h"

#define GLFW_INCLUDE_NONE  // keep GLFW from pulling in desktop GL headers (required for Emscripten/Web builds)
#include <GLFW/glfw3.h>

#include "engine/render/glfw3webgpu.h"
#include <webgpu/webgpu.h>

int main(void) {
    if (nt_engine_init() != NT_RESULT_OK) {
        fputs("Failed to initialize engine\n", stderr);
        return 1;
    }

    if (!glfwInit()) {
        fputs("GLFW init failed\n", stderr);
        nt_engine_shutdown();
        return 1;
    }

    glfwWindowHint(GLFW_CLIENT_API, GLFW_NO_API);
    GLFWwindow* window = glfwCreateWindow(640, 480, "nt_engine WebGPU check", NULL, NULL);
    if (!window) {
        fputs("Failed to create GLFW window\n", stderr);
        glfwTerminate();
        nt_engine_shutdown();
        return 1;
    }

    // Init WebGPU
	WGPUInstanceDescriptor desc;
	desc.nextInChain = NULL;
	WGPUInstance instance = wgpuCreateInstance(&desc);
    if (!instance) {
        fputs("wgpuCreateInstance failed\n", stderr);
        glfwDestroyWindow(window);
        glfwTerminate();
        nt_engine_shutdown();
        return 1;
    }

    WGPUSurface surface = glfwCreateWindowWGPUSurface(instance, window);
    printf("WebGPU surface = %p\n", (void*)surface);

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
    }

    if (surface) {
        wgpuSurfaceRelease(surface);
    }
    if (instance) {
        wgpuInstanceRelease(instance);
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    nt_engine_shutdown();
    printf("Sandbox lifecycle complete\n");
    return 0;
}
