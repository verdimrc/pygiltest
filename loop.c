#include <stdio.h>
#include <limits.h>

int do_loop();

int main() {
   return do_loop(); 
}

int do_loop() {
    unsigned int i=0;
    unsigned int j=0;
    for (i=0; i < 2; i++)
        for (j=0; j < UINT_MAX; j++)
            ;
    return 0;
}
