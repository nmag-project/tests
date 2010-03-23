

#include <stdio.h>

extern int bar(double* data, int len) {
   int i;
   printf("data = %p\n", (void*) data);
   for (i = 0; i < len; i++) {
      printf("data[%d] = %f\n", i, data[i]);
   }
   printf("len = %d\n", len);
   return len + 1;
}

extern double* test(double* data, int len) {
   int i;
   printf("data = %p\n", (void*) data);
   for (i = 0; i < len; i++) {
      printf("data[%d] = %f\n", i, data[i]);
      data[i] *= 2;
   }
   printf("len = %d\n", len);
   return data;
}

