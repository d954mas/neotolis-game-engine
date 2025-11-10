#include <stdio.h>
#include "engine/core/nt_engine.h"

int main(void) {
    if (nt_engine_init() != NT_RESULT_OK){
        fprintf_s(stderr, "Failed to initialize engine\n");
        return 1;
    }
    nt_engine_shutdown();
    printf("Sandbox lifecycle complete\n");
    return 0;
}
