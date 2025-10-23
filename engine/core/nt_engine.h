#ifndef NT_ENGINE_H
#define NT_ENGINE_H

#include <stddef.h>

typedef enum {
    NT_RESULT_OK = 0,
    NT_RESULT_ERROR = 1
} nt_result;

nt_result nt_engine_init();
void nt_engine_shutdown();

#endif /* NT_ENGINE_H */
