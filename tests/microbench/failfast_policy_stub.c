#include <stdint.h>
#include <stdio.h>
#include "engine/core/nt_engine.h"

/*
 * Placeholder microbenchmark that simply exercises the fail-fast policy bootstrap.
 * Real benchmarks will replace this once runtime guards are wired in.
 */
int main(void) {
    nt_failfast_policy policy;
    nt_failfast_policy_defaults(&policy);
    printf("fail-fast policy hash: %s\n", policy.policy_hash ? policy.policy_hash : "<unset>");
    return 0;
}
