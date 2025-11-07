int returns_value(void) {
    int x = 42;
    x += 1;
    /* Warning: control reaches end of non-void function */
}

int main(void) {
    return returns_value();
}
