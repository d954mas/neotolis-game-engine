#include <assert.h>

#include "engine/features/sample/nt_feature_sample.h"

int main(void) {
    nt_feature_sample_config config = {
        .enabled = 1
    };

    nt_feature_sample_status status = nt_feature_sample_init(&config);
    assert(status == NT_FEATURE_SAMPLE_STATUS_OK);

    nt_feature_sample_shutdown();
    return 0;
}
