#include <assert.h>
#include <stdio.h>

#include "engine/core/nt_engine.h"

int main(void) {
    nt_result result = nt_engine_init();
    assert(result == NT_RESULT_OK);
    nt_engine_shutdown();
    return 0;
}
