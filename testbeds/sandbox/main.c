#include <stdio.h>

#include "engine/core/nt_engine.h"

#define GLFW_INCLUDE_NONE  // keep GLFW from pulling in desktop GL headers (required for Emscripten/Web builds)
#include <GLFW/glfw3.h>

#include "engine/render/glfw3webgpu.h"
#include <webgpu/webgpu.h>
#ifdef __EMSCRIPTEN__
#include <emscripten/html5.h>
#endif

#ifndef WGPU_INSTANCE_DESCRIPTOR_INIT
#define WGPU_INSTANCE_DESCRIPTOR_INIT (WGPUInstanceDescriptor){0}
#endif

typedef struct SandboxApp {
    GLFWwindow* window;
    WGPUInstance instance;
    WGPUSurface surface;
    int cleaned_up;
} SandboxApp;

static SandboxApp g_sandbox_app;

static void sandbox_cleanup(SandboxApp* app) {
    if (!app || app->cleaned_up) {
        return;
    }

    if (app->surface) {
        wgpuSurfaceRelease(app->surface);
        app->surface = NULL;
    }
    if (app->instance) {
        wgpuInstanceRelease(app->instance);
        app->instance = NULL;
    }
    if (app->window) {
        glfwDestroyWindow(app->window);
        app->window = NULL;
    }

    glfwTerminate();
    nt_engine_shutdown();
    app->cleaned_up = 1;
    puts("Sandbox lifecycle complete");
}

static void sandbox_update(void* user_data) {
    SandboxApp* app = (SandboxApp*)user_data;
    if (!app || app->cleaned_up) {
#ifdef __EMSCRIPTEN__
        emscripten_cancel_main_loop();
#endif
        return;
    }

    if (!app->window || glfwWindowShouldClose(app->window)) {
        sandbox_cleanup(app);
#ifdef __EMSCRIPTEN__
        emscripten_cancel_main_loop();
#endif
        return;
    }

    glfwPollEvents();
}

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
    WGPUInstanceDescriptor desc = WGPU_INSTANCE_DESCRIPTOR_INIT;
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

    g_sandbox_app.window = window;
    g_sandbox_app.instance = instance;
    g_sandbox_app.surface = surface;
    g_sandbox_app.cleaned_up = 0;

#ifdef __EMSCRIPTEN__
    emscripten_set_main_loop_arg(sandbox_update, &g_sandbox_app, 0, true);
    return 0;
#else
    while (!glfwWindowShouldClose(window)) {
        sandbox_update(&g_sandbox_app);
    }

    sandbox_cleanup(&g_sandbox_app);

    return 0;
#endif
}
