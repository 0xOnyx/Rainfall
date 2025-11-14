# Bonus 3 Walkthrough

## Overview
- Opens `/home/user/end/.pass`, reads 66 bytes into a 132-byte stack buffer, and ensures byte 65 is `\0`.
- Converts `argv[1]` with `atoi` and writes a null byte at `buffer[atoi(argv[1])]`.
- Reads another 65 bytes into `buffer+66`, closes the file, and runs `strcmp(buffer, argv[1])`.
- If the comparison succeeds, it executes `/bin/sh`; otherwise it prints the remaining file chunk.

## Vulnerability
- `atoi` returns `0` for an empty string. Supplying an empty argument (`''`) causes the program to write `buffer[0] = '\0'`, effectively blanking the flag portion loaded from disk.
- Because our argument is also the empty string, `strcmp("", "")` returns zero and the privileged branch executes.
- No memory corruption is required; this is purely a logic flaw.

## Exploit Strategy
1. Invoke the binary with an empty argument: `./bonus3 ''`.
2. `atoi('')` → `0`, so byte zero of the buffer becomes `\0`.
3. `strcmp` now compares two empty strings, so it returns 0.
4. The program calls `execl("/bin/sh", "sh", NULL)` and drops us into a shell running as `end`.
5. Read `/home/user/end/.pass`.

## Flag
```bash
$ ./bonus3 ''
$ cat /home/user/end/.pass
3321b6f81659f9a71c76616f606e4b50189cecfea611393d5d649f75e157353c
```

