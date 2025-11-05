#include <stdio.h>

#include "engine/core/nt_engine.h"

int main(void) {
    if (nt_engine_init() != NT_RESULT_OK) {
        fprintf(stderr, "engine init failed\n");
        return 1;
    }

    const int frames = 1000;
    double start = 0;
    for (int i = 0; i < frames; ++i) {
        //nt_engine_frame();
    }
    double elapsed = 0 - start;

    nt_engine_shutdown();

    double per_frame = elapsed / (double)frames;
    printf("Microbench stub: %d frames in %.3f ms (%.6f ms/frame)\n", frames, elapsed, per_frame);
    return 0;
}
