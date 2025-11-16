#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int greetuser(char *name);

int language = 0;

int main(const int argc,char **argv){
  char username [40];
  char lastname [32];

  if (argc == 3) {
    bzero(username, 40);
    bzero(lastname, 32);
    strncpy(username,argv[1],40);
    strncpy(lastname,argv[2],32);

    char *lang = getenv("LANG");
    if (lang) {
      if (memcmp(lang,"fi",2) == 0) {
        language = 1;
      } else if (memcmp(lang,"nl",2) == 0) {
        language = 2;
      }
    }
    return greetuser(username);
  }
    return 1;
}

int greetuser(char *str){
  char hello_in_lang [64];

  if (language == 1) {
    strcpy(hello_in_lang, "Hyvää päivää ");
  } else if (language == 2) {
    strcpy(hello_in_lang, "Goedemiddag! ");
  } else if (language == 0) {
    strcpy(hello_in_lang, "Hello ");
  }

  strcat(hello_in_lang, str);

  return puts(hello_in_lang);
}
