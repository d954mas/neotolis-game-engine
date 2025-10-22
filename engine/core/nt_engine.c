#include "nt_engine.h"

static nt_engine_config g_engine_config = {0};
static int g_engine_initialized = 0;

nt_engine_status nt_engine_init(const nt_engine_config *config) {
    if (g_engine_initialized) {
        return NT_ENGINE_STATUS_OK;
    }
    if (config == NULL) {
        return NT_ENGINE_STATUS_ERROR_CONFIG;
    }
    g_engine_config = *config;
    g_engine_initialized = 1;
    return NT_ENGINE_STATUS_OK;
}

void nt_engine_frame(void) {
    if (!g_engine_initialized) {
        return;
    }
    /* Stub: future subsystems will run per-frame work here */
}

void nt_engine_shutdown(void) {
    if (!g_engine_initialized) {
        return;
    }
    g_engine_initialized = 0;
    g_engine_config.user_context = NULL;
    g_engine_config.application_name = NULL;
}
