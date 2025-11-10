#include <assert.h>

#include "engine/features/sample/nt_feature_sample.h"

int main(void) {
    assert(nt_feature_sample_init() == NT_RESULT_OK);
    nt_feature_sample_shutdown();
    return 0;
}
