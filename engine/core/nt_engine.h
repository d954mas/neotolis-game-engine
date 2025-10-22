#ifndef NT_ENGINE_H
#define NT_ENGINE_H

#include <stddef.h>

typedef enum nt_engine_status {
    NT_ENGINE_STATUS_OK = 0,
    NT_ENGINE_STATUS_ERROR_TOOLCHAIN = 1,
    NT_ENGINE_STATUS_ERROR_CONFIG = 2
} nt_engine_status;

typedef struct nt_engine_config {
    void *user_context;
    const char *application_name;
} nt_engine_config;

nt_engine_status nt_engine_init(const nt_engine_config *config);
void nt_engine_frame(void);
void nt_engine_shutdown(void);

#endif // NT_ENGINE_H
