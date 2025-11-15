#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(const int argc,char **argv){
    FILE *fd;
    char flag [132];

    fd = fopen("/home/user/end/.pass","r");

    bzero(flag, 132);

    if (fd == (FILE *)0x0 || argc != 2) {
        return -1;
    }

    fread(flag, 1, 66, fd);
    flag[65] = '\0';
    flag[atoi(argv[1])] = '\0';
    fread(flag + 66, 1, 65, fd);
    fclose(fd);

    if (strcmp(flag, argv[1]) == 0) {
        execl("/bin/sh","sh",0);
    } else {
        puts(flag + 66);
    }

    return 0;
}
