#include "nt_feature_sample.h"
#include <assert.h>

static int g_feature_initialized = 0;

nt_result nt_feature_sample_init() {
    assert(g_feature_initialized == 0);
    g_feature_initialized = 1;
    return NT_RESULT_OK;
}

void nt_feature_sample_shutdown() {
    assert(g_feature_initialized == 1);
    g_feature_initialized = 0;
}
