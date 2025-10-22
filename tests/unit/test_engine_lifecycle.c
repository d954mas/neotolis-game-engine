#include <assert.h>
#include <stdio.h>

#include "engine/core/nt_engine.h"

int main(void) {
    nt_engine_config config = {
        .user_context = NULL,
        .application_name = "sandbox"
    };

    nt_engine_status status = nt_engine_init(&config);
    assert(status == NT_ENGINE_STATUS_OK);

    nt_engine_frame();
    nt_engine_shutdown();

    printf("Lifecycle smoke test completed.\n");
    return 0;
}
