#include <stddef.h>

int unsafe_length(const char *ptr) {
    return ptr[0]; /* potential null dereference */
}

int main(void) {
    char *maybe_null = NULL;
    if (maybe_null == NULL) {
        return unsafe_length(maybe_null); /* intentional bug for clang-tidy */
    }
    return 0;
}
