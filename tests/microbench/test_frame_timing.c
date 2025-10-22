#include <stdio.h>

#include "engine/core/nt_engine.h"

#ifdef _WIN32
#include <windows.h>
static double now_ms(void) {
    LARGE_INTEGER freq;
    LARGE_INTEGER counter;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart * 1000.0 / (double)freq.QuadPart;
}
#else
#include <time.h>
static double now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1000.0 + (double)ts.tv_nsec / 1e6;
}
#endif

int main(void) {
    nt_engine_config config = {
        .user_context = NULL,
        .application_name = "microbench"
    };

    if (nt_engine_init(&config) != NT_ENGINE_STATUS_OK) {
        fprintf(stderr, "engine init failed\n");
        return 1;
    }

    const int frames = 1000;
    double start = now_ms();
    for (int i = 0; i < frames; ++i) {
        nt_engine_frame();
    }
    double elapsed = now_ms() - start;

    nt_engine_shutdown();

    double per_frame = elapsed / (double)frames;
    printf("Microbench stub: %d frames in %.3f ms (%.6f ms/frame)\n", frames, elapsed, per_frame);
    return 0;
}
