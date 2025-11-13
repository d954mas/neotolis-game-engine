#ifndef NT_RENDER_H
#define NT_RENDER_H

#include "engine/core/nt_engine.h"

typedef enum {
    NT_RENDER_BACKEND_GL = 0,
    NT_RENDER_BACKEND_WEBGPU
} nt_render_backend;

nt_result nt_render_init(nt_render_backend backend);
void nt_render_shutdown(void);
nt_render_backend nt_render_get_backend(void);

#endif /* NT_RENDER_H */
