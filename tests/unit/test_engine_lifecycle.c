#include <assert.h>
#include <stdio.h>

#include "engine/core/nt_engine.h"

int main(void) {
    assert(nt_engine_init() == NT_RESULT_OK);
    nt_engine_shutdown();
    return 0;
}
