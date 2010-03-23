#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <time.h>

static void w(const char *msg) {
  time_t t = time((time_t *) NULL);
  char *t_str = ctime(& t);
  FILE *f = fopen("sig.log", "a");
  fprintf(f, "%s: %s", msg, t_str);
  fclose(f);
}

void do_at_exit(int s) {
  w("Received SIGTERM!");
}

int main(void) {
  time_t prev_t=0;
  void (*prev)() = signal(SIGTERM, do_at_exit);
  w("Program started!");
  while(1) {
    time_t t = time((time_t *) NULL);
    if (t != prev_t) w("Time is passing...");
    prev_t = t;
  }
  exit(EXIT_SUCCESS);
}
