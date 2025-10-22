#include "nt_feature_sample.h"

static int g_sample_enabled = 0;

nt_feature_sample_status nt_feature_sample_init(const nt_feature_sample_config *config) {
    if (config == NULL || !config->enabled) {
        g_sample_enabled = 0;
        return NT_FEATURE_SAMPLE_STATUS_DISABLED;
    }

    g_sample_enabled = 1;
    return NT_FEATURE_SAMPLE_STATUS_OK;
}

void nt_feature_sample_shutdown(void) {
    g_sample_enabled = 0;
}
