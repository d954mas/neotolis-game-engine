#include "render.h"

static nt_render_backend g_render_backend = NT_RENDER_BACKEND_GL;

nt_result nt_render_init(nt_render_backend backend) {
    g_render_backend = backend;
    return NT_RESULT_OK;
}

void nt_render_shutdown(void) {
    g_render_backend = NT_RENDER_BACKEND_GL;
}

nt_render_backend nt_render_get_backend(void) {
    return g_render_backend;
}
