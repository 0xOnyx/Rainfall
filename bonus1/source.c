#include <stdlib.h>
#include <unistd.h>
#include <string.h>

int main(int argc,char **argv){
  int size;
  char buffer [40];
  
  size = atoi(argv[1]);
  if (size < 10) {
    memcpy(buffer, argv[2], size * 4);
    if (size == 0x574f4c46) {
      execl("/bin/sh","sh",0);
    }
    size = 0;
  } else {
    size = 1;
  }

  return size;
}

