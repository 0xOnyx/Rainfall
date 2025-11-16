#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>

char c[68];

void m()
{
  time_t t;

  t = time((time_t *)0);
  printf("%s - %d\n",c,t);
  return;
}

int main(int argc,char **argv)
{
  char **A;
  char *tmp_pointer;
  char **B;
  FILE *password_file;

  A = (char **)malloc(8);
  A[0] = (char *)1;
  tmp_pointer = malloc(8);
  A[1] = tmp_pointer;

  B = (char **)malloc(8);
  B[0] = (char *)2;
  tmp_pointer = malloc(8);
  B[1] = tmp_pointer;

  strcpy(A[1],argv[1]);
  strcpy(B[1],argv[2]);

  password_file = fopen("/home/user/level8/.pass","r");
  fgets(c,68,password_file);
  puts("~~");

  return 0;
}
