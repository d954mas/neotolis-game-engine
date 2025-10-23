#include <assert.h>

#include "engine/features/sample/nt_feature_sample.h"

int main(void) {
    nt_result result = nt_feature_sample_init();
    assert(result == NT_RESULT_OK);
    nt_feature_sample_shutdown();
    return 0;
}
