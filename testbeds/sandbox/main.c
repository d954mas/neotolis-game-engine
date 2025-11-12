#include <stdio.h>
#include "engine/core/nt_engine.h"

#include <GLFW/glfw3.h>

int main(void) {
    if (nt_engine_init() != NT_RESULT_OK){
        fputs("Failed to initialize engine\n", stderr);
        return 1;
    }

    if (!glfwInit()) {
        fputs("GLFW init failed\n", stderr);
        return 1;
    }
    printf("GLFW init success\n");
    glfwTerminate();

    nt_engine_shutdown();
    printf("Sandbox lifecycle complete\n");
    return 0;
}
