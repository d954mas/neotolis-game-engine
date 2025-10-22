#include <stdio.h>
#include "engine/core/nt_engine.h"

int main(void) {
    nt_engine_config config = {
        .user_context = NULL,
        .application_name = "Speckit Sandbox"
    };

    if (nt_engine_init(&config) != NT_ENGINE_STATUS_OK) {
        fprintf(stderr, "Failed to initialize engine\n");
        return 1;
    }

    for (int frame = 0; frame < 3; ++frame) {
        nt_engine_frame();
        printf("Frame %d executed\n", frame);
    }

    nt_engine_shutdown();
    printf("Sandbox lifecycle complete\n");
    return 0;
}
