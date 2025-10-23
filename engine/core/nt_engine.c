#include "nt_engine.h"

static int g_engine_initialized = 0;

nt_result nt_engine_init() {
    assert(g_engine_initialized == 0);
    g_engine_initialized = 1;
    return NT_RESULT_OK;
}

void nt_engine_shutdown(void) {
    assert(g_engine_initialized == 1);
    g_engine_initialized = 0;
}
