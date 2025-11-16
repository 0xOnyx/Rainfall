#include <stdlib.h>
#include <stdio.h>
#include <string.h>

void n(void)
{
  system("/bin/cat /home/user/level7/.pass");
  return;
}

void m()
{
  puts("Nope");
  return;
}

void main(int argc,char **argv)

{
  char *buffer;
  void (*hook)(void);

  buffer = (char *)malloc(64);
  hook = malloc(4);
  hook = &m;
  strcpy(buffer,argv[1]);
  hook();
  return;
}
